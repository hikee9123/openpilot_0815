import math
import numpy as np

from common.numpy_fast import clip
from common.realtime import DT_CTRL
from cereal import log
from selfdrive.controls.lib.latcontrol import LatControl, MIN_STEER_SPEED

from selfdrive.controls.lib.latcontrol_torque import LatControlTorque
from selfdrive.controls.lib.latcontrol_lqr import LatControlLQR


class LatControlATOM(LatControl):
  def __init__(self, CP, CI):
    super().__init__(CP, CI)

    self.torque = CP.lateralTuning.atom.torque
    self.lqr = CP.lateralTuning.atom.lqr

    self.LaLqr = LatControlLQR( CP,  CI )
    self.LaToq = LatControlTorque( CP, CI )

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
