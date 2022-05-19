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

    self.reset()

  def reset(self):
    super().reset()
    self.LaLqr.reset()
    self.LaToq.reset()

  def update(self, active, CS, VM, params, last_actuators, desired_curvature, desired_curvature_rate, llk):
    atom_log = log.ControlsState.LateralATOMState.new_message()

    lqr_output_steer, lqr_desired_angle, lqr_log  = self.LaLqr.update( active, CS, VM, params, last_actuators, desired_curvature, desired_curvature_rate, llk )
    toq_output_steer, toq_desired_angle, toq_log  = self.LaToq.update( active, CS, VM, params, last_actuators, desired_curvature, desired_curvature_rate, llk )

    #output_steer = lqr_output_steer

    abs_lqr = abs( lqr_output_steer ) 
    abs_toq = abs( toq_output_steer ) 
    if abs_lqr > abs_toq:
      output_steer = toq_output_steer
    else:
      output_steer = lqr_output_steer

    desired_angle = lqr_desired_angle
    atom_log.steeringAngleDeg = lqr_log.steeringAngleDeg
    atom_log.i = lqr_log.i
    atom_log.output = output_steer
    atom_log.lqrOutput = lqr_log.lqrOutput
    atom_log.saturated = lqr_log.saturated
    return output_steer, desired_angle, atom_log
