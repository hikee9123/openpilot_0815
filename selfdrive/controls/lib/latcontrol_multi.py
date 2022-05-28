import math
import numpy as np

from cereal import car, log
from common.realtime import DT_CTRL
from common.numpy_fast import clip, interp


from selfdrive.controls.lib.latcontrol import LatControl, MIN_STEER_SPEED
from selfdrive.controls.lib.pid import PIDController

from selfdrive.controls.lib.latcontrol_torque import LatControlTorque
from selfdrive.controls.lib.latcontrol_lqr import LatControlLQR
from selfdrive.controls.lib.latcontrol_pid import LatControlPID




class LatCtrlToqMULTI(LatControlTorque):
  def __init__(self, CP, CI, TORQUE):
    self.sat_count_rate = 1.0 * DT_CTRL
    self.sat_limit = CP.steerLimitTimer
    self.sat_count = 0. 
    
    # we define the steer torque scale as [-1.0...1.0] 
    self.steer_max = 1.0

    self.pid = PIDController(TORQUE.kp, TORQUE.ki,
                             k_f=TORQUE.kf, pos_limit=self.steer_max, neg_limit=-self.steer_max)
    self.get_steer_feedforward = CI.get_steer_feedforward_function()
    self.use_steering_angle = TORQUE.useSteeringAngle
    self.friction = TORQUE.friction
    self.kf = TORQUE.kf



class LatCtrlLqrMULTI(LatControlLQR):
  def __init__(self, CP, CI, LQR):
    self.sat_count_rate = 1.0 * DT_CTRL 
    self.sat_limit = CP.steerLimitTimer 
    self.sat_count = 0. 
    
    # we define the steer torque scale as [-1.0...1.0]
    self.steer_max = 1.0


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


class LatCtrlPIDMULTI(LatControlPID):
  def __init__(self, CP, CI, PID):
    self.sat_count_rate = 1.0 * DT_CTRL
    self.sat_limit = CP.steerLimitTimer
    self.sat_count = 0.

    # we define the steer torque scale as [-1.0...1.0]
    self.steer_max = 1.0

    self.pid = PIDController((PID.kpBP, PID.kpV),
                             (PID.kiBP, PID.kiV),
                             k_f=PID.kf, pos_limit=self.steer_max, neg_limit=-self.steer_max)

    self.get_steer_feedforward = CI.get_steer_feedforward_function()




MethodModel = car.CarParams.MethodModel

class LatControlMULTI(LatControl):
  def __init__(self, CP, CI):
    super().__init__(CP, CI)

    self.CP = CP
    self.lqr = CP.lateralTuning.atom.lqr
    self.torque = CP.lateralTuning.atom.torque
    self.pid1 = CP.lateralTuning.atom.pid

    self.LaLqr = LatCtrlLqrMULTI( CP, CI, self.lqr )
    self.LaToq = LatCtrlToqMULTI( CP, CI, self.torque )
    self.LaPid = LatCtrlPIDMULTI( CP, CI, self.pid1 )

    self.output_torque = 0
    self.reset()


    self.lat_funs = []
    self.lat_params = []
    methods = CP.lateralTuning.atom.methods
    for BP in methods:
      self.lat_funs += self.method_func( BP )
      self.lat_params += BP.methodParam


  def method_func(self, BP ):
    lat_fun = None
    if BP.methodModel == MethodModel.lqr:
      lat_fun  = self.LaLqr.update
    elif BP.methodModel == MethodModel.torque:
      lat_fun  = self.LaToq.update
    if BP.methodModel == MethodModel.pid:
      lat_fun  = self.LaPid.update

    return lat_fun

  def reset(self):
    super().reset()
    self.LaLqr.reset()
    self.LaToq.reset()
    self.LaPid.reset()


  def update(self, active, CS, VM, params, last_actuators, desired_curvature, desired_curvature_rate, llk):
    atom_log = log.ControlsState.LateralATOMState.new_message()


    if CS.vEgo < MIN_STEER_SPEED or not active:
      output_torque = 0.0
      desired_angle = 0.
      atom_log.active = False
      if not active:
        self.reset()
    else:
      output_torques = []
      desired_angles = []      
      for funcs in self.lat_funs:
        output_torque, desired_angle, temp_log = funcs( active, CS, VM, params, last_actuators, desired_curvature, desired_curvature_rate, llk )
        output_torques += output_torque
        desired_angles += desired_angle


      steer_ang = abs(CS.steeringAngleDeg)
      output_torque = interp( steer_ang, self.lat_params, output_torques )
      output_torque = clip( output_torque, -self.steer_max, self.steer_max )

      if len(desired_angles) > 0:
        desired_angle = desired_angles[0]
      else:
        desired_angle = 0

      # 2. log
      atom_log.active = True    
      atom_log.steeringAngleDeg = desired_angle
      atom_log.output = output_torque

      #atom_log.i = lqr_log.i
      #atom_log.saturated = lqr_log.saturated      
      #atom_log.lqrOutput = lqr_log.lqrOutput
      #atom_log.p1 = toq_log.p
      #atom_log.i1 = toq_log.i
      #atom_log.d1 = toq_log.d
      #atom_log.f1 = toq_log.f
      #atom_log.selected = selected
    
    self.output_torque = output_torque
    

    return output_torque, desired_angle, atom_log
