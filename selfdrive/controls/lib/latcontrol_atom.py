import math
import numpy as np

from cereal import log
from common.numpy_fast import clip
from common.realtime import DT_CTRL
from common.numpy_fast import interp


from selfdrive.controls.lib.latcontrol import LatControl, MIN_STEER_SPEED
from selfdrive.controls.lib.pid import PIDController
from selfdrive.controls.lib.vehicle_model import ACCELERATION_DUE_TO_GRAVITY


LOW_SPEED_FACTOR = 200
JERK_THRESHOLD = 0.2


class LatControlToqATOM(LatControl):
  def __init__(self, CP, CI, TORQUE):
    super().__init__(CP, CI )
    self.CP = CP
    self.pid = PIDController(TORQUE.kp, TORQUE.ki,
                             k_f=TORQUE.kf, pos_limit=self.steer_max, neg_limit=-self.steer_max)
    self.get_steer_feedforward = CI.get_steer_feedforward_function()
    self.use_steering_angle = TORQUE.useSteeringAngle
    self.friction = TORQUE.friction
    self.kf = TORQUE.kf

  def reset(self):
    super().reset()
    self.pid.reset()

  def update(self, active, CS, VM, params, last_actuators, desired_curvature, desired_curvature_rate, llk):
    pid_log = log.ControlsState.LateralTorqueState.new_message()

    if CS.vEgo < MIN_STEER_SPEED or not active:
      output_torque = 0.0
      pid_log.active = False
      if not active:
        self.pid.reset()
    else:
      if self.use_steering_angle:
        actual_curvature = -VM.calc_curvature(math.radians(CS.steeringAngleDeg - params.angleOffsetDeg), CS.vEgo, params.roll)
      else:
        actual_curvature = llk.angularVelocityCalibrated.value[2] / CS.vEgo
      desired_lateral_accel = desired_curvature * CS.vEgo ** 2
      desired_lateral_jerk = desired_curvature_rate * CS.vEgo ** 2
      actual_lateral_accel = actual_curvature * CS.vEgo ** 2

      setpoint = desired_lateral_accel + LOW_SPEED_FACTOR * desired_curvature
      measurement = actual_lateral_accel + LOW_SPEED_FACTOR * actual_curvature
      error = setpoint - measurement
      pid_log.error = error

      ff = desired_lateral_accel - params.roll * ACCELERATION_DUE_TO_GRAVITY
      # convert friction into lateral accel units for feedforward
      friction_compensation = interp(desired_lateral_jerk, [-JERK_THRESHOLD, JERK_THRESHOLD], [-self.friction, self.friction])
      ff += friction_compensation / self.kf
      output_torque = self.pid.update(error,
                                      override=CS.steeringPressed, feedforward=ff,
                                      speed=CS.vEgo,
                                      freeze_integrator=CS.steeringRateLimited)

      pid_log.active = True
      pid_log.p = self.pid.p
      pid_log.i = self.pid.i
      pid_log.d = self.pid.d
      pid_log.f = self.pid.f
      pid_log.output = -output_torque
      pid_log.saturated = self._check_saturation(self.steer_max - abs(output_torque) < 1e-3, CS)
      pid_log.actualLateralAccel = actual_lateral_accel
      pid_log.desiredLateralAccel = desired_lateral_accel

    # TODO left is positive in this convention
    return -output_torque, 0.0, pid_log


class LatControlLqrATOM(LatControl):
  def __init__(self, CP, CI, LQR):
    super().__init__(CP, CI)
    self.scale = LQR.scale
    self.ki = LQR.ki

    self.A = np.array(LQR.a).reshape((2, 2))
    self.B = np.array(LQR.b).reshape((2, 1))
    self.C = np.array(LQR.c).reshape((1, 2))
    self.K = np.array(LQR.k).reshape((1, 2))
    self.L = np.array(LQR.l).reshape((2, 1))
    self.dc_gain = LQR.dcGain

    self.x_hat = np.array([[0], [0]])
    self.i_unwind_rate = 0.3 * DT_CTRL
    self.i_rate = 1.0 * DT_CTRL

    self.reset()

  def reset(self):
    super().reset()
    self.i_lqr = 0.0

  def update(self, active, CS, VM, params, last_actuators, desired_curvature, desired_curvature_rate, llk):
    lqr_log = log.ControlsState.LateralLQRState.new_message()

    torque_scale = (0.45 + CS.vEgo / 60.0)**2  # Scale actuator model with speed

    # Subtract offset. Zero angle should correspond to zero torque
    steering_angle_no_offset = CS.steeringAngleDeg - params.angleOffsetAverageDeg

    desired_angle = math.degrees(VM.get_steer_from_curvature(-desired_curvature, CS.vEgo, params.roll))

    instant_offset = params.angleOffsetDeg - params.angleOffsetAverageDeg
    desired_angle += instant_offset  # Only add offset that originates from vehicle model errors
    lqr_log.steeringAngleDesiredDeg = desired_angle

    # Update Kalman filter
    angle_steers_k = float(self.C.dot(self.x_hat))
    e = steering_angle_no_offset - angle_steers_k
    self.x_hat = self.A.dot(self.x_hat) + self.B.dot(CS.steeringTorqueEps / torque_scale) + self.L.dot(e)

    if CS.vEgo < MIN_STEER_SPEED or not active:
      lqr_log.active = False
      lqr_output = 0.
      output_steer = 0.
      self.reset()
    else:
      lqr_log.active = True

      # LQR
      u_lqr = float(desired_angle / self.dc_gain - self.K.dot(self.x_hat))
      lqr_output = torque_scale * u_lqr / self.scale

      # Integrator
      if CS.steeringPressed:
        self.i_lqr -= self.i_unwind_rate * float(np.sign(self.i_lqr))
      else:
        error = desired_angle - angle_steers_k
        i = self.i_lqr + self.ki * self.i_rate * error
        control = lqr_output + i

        if (error >= 0 and (control <= self.steer_max or i < 0.0)) or \
           (error <= 0 and (control >= -self.steer_max or i > 0.0)):
          self.i_lqr = i

      output_steer = lqr_output + self.i_lqr
      output_steer = clip(output_steer, -self.steer_max, self.steer_max)

    lqr_log.steeringAngleDeg = angle_steers_k
    lqr_log.i = self.i_lqr
    lqr_log.output = output_steer
    lqr_log.lqrOutput = lqr_output
    lqr_log.saturated = self._check_saturation(self.steer_max - abs(output_steer) < 1e-3, CS)
    return output_steer, desired_angle, lqr_log



class LatControlATOM(LatControl):
  def __init__(self, CP, CI):
    super().__init__(CP, CI)

    self.lqr = CP.lateralTuning.atom.lqr
    self.torque = CP.lateralTuning.atom.torque



    self.LaLqr = LatControlLqrATOM( CP, CI, self.lqr )
    self.LaToq = LatControlToqATOM( CP, CI, self.torque )

    self.output_torque = 0
    self.reset()

  def reset(self):
    super().reset()
    self.LaLqr.reset()
    self.LaToq.reset()

  def update(self, active, CS, VM, params, last_actuators, desired_curvature, desired_curvature_rate, llk):
    atom_log = log.ControlsState.LateralATOMState.new_message()

    if CS.vEgo < MIN_STEER_SPEED or not active:
      output_torque = 0.0
      atom_log.active = False
      if not active:
        self.reset()
    else:
      lqr_output_torque, lqr_desired_angle, lqr_log  = self.LaLqr.update( active, CS, VM, params, last_actuators, desired_curvature, desired_curvature_rate, llk )
      toq_output_torque, toq_desired_angle, toq_log  = self.LaToq.update( active, CS, VM, params, last_actuators, desired_curvature, desired_curvature_rate, llk )

      #output_torque = lqr_output_torque
      lqr_delta = lqr_output_torque - self.output_torque
      toq_delta = toq_output_torque - self.output_torque

      # 1. 전과 비교하여 변화량이 적은 부분 선택.
      abs_lqr = abs( lqr_delta ) 
      abs_toq = abs( toq_delta ) 
      if abs_lqr > abs_toq:
        selected = 1.0
        output_torque = toq_output_torque
      else:
        selected = -1.0
        output_torque = lqr_output_torque


      # 2. log
      atom_log.active = True    
      atom_log.steeringAngleDeg = lqr_log.steeringAngleDeg
      atom_log.i = lqr_log.i
      atom_log.output = output_torque
      atom_log.lqrOutput = lqr_log.lqrOutput
      atom_log.saturated = lqr_log.saturated
      atom_log.steeringAngleDesiredDeg
      atom_log.error
      atom_log.errorRate
      atom_log.p1 = toq_log.p
      atom_log.i1 = toq_log.i
      atom_log.d1 = toq_log.d
      atom_log.f1 = toq_log.f

      atom_log.selected = selected
   

    self.output_torque = output_torque
    desired_angle = lqr_desired_angle


    return output_torque, desired_angle, atom_log
