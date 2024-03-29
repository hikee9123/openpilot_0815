#!/usr/bin/env python3
from enum import Enum
from cereal import car
from common.params import Params

from selfdrive.car import  get_method_config

MethodModel = car.CarParams.MethodModel


class TunType(Enum):
  LAT_PID = 0
  LAT_INDI = 1
  LAT_LQR = 2
  LAT_TOROUE = 3
  LAT_HYBRID = 4
  LAT_MULTI = 5
  LAT_DEFAULT = 6


class LongTunes(Enum):
  PEDAL = 0
  TSS2 = 1
  TSS = 2

class LatTunes(Enum):
  INDI_PRIUS = 0
  LQR_RAV4 = 1
  PID_A = 2
  PID_B = 3
  PID_C = 4
  PID_D = 5
  PID_E = 6
  PID_F = 7
  PID_G = 8
  PID_I = 9
  PID_H = 10
  PID_J = 11
  PID_K = 12
  PID_L = 13
  PID_M = 14
  PID_N = 15
  TORQUE = 16
  LQR_GRANDEUR = 17
  HYBRID = 18
  MULTI = 19






###### LONG ######
def set_long_tune(tune, name):
  # Improved longitudinal tune
  if name == LongTunes.TSS2 or name == LongTunes.PEDAL:
    tune.deadzoneBP = [0., 8.05]
    tune.deadzoneV = [.0, .14]
    tune.kpBP = [0., 5., 20.]
    tune.kpV = [1.3, 1.0, 0.7]
    tune.kiBP = [0., 5., 12., 20., 27.]
    tune.kiV = [.35, .23, .20, .17, .1]
  # Default longitudinal tune
  elif name == LongTunes.TSS:
    tune.deadzoneBP = [0., 9.]
    tune.deadzoneV = [0., .15]
    tune.kpBP = [0., 5., 35.]
    tune.kiBP = [0., 35.]
    tune.kpV = [3.6, 2.4, 1.5]
    tune.kiV = [0.54, 0.36]
  else:
    raise NotImplementedError('This longitudinal tune does not exist')

def update_lat_tune_patam(tune, MAX_LAT_ACCEL=2.5, steering_angle_deadzone_deg=0.0):
  params = Params()

  OpkrLateralControlMethod = int( params.get("OpkrLateralControlMethod", encoding="utf8") )
  method = TunType( OpkrLateralControlMethod )
  print( 'OpkrLateralControlMethod = {}'.format( method ))
  if method ==  TunType.LAT_PID:
      Kp = float( params.get("PidKp", encoding="utf8") )
      Ki = float( params.get("PidKi", encoding="utf8") )
      Kf = float( params.get("PidKf", encoding="utf8") )

      tune.init('pid')
      tune.pid.kiBP = [0.0]
      tune.pid.kpBP = [0.0]
      tune.pid.kpV = [Kp]
      tune.pid.kiV = [Ki]
      tune.pid.kf = Kf
  elif method ==  TunType.LAT_LQR:
      scale = float( params.get("LqrScale", encoding="utf8") )
      Ki = float( params.get("LqrKi", encoding="utf8") )
      dcGain = float( params.get("LqrDcGain", encoding="utf8") )    

      tune.init('lqr')
      tune.lqr.scale = scale  #1900     #1700.0
      tune.lqr.ki = Ki #0.01      #0.01
      tune.lqr.dcGain = dcGain # 0.0027  #0.0027
      # 호야  1500, 0.015, 0.0027
      #  1700, 0.01, 0.0029
      #  2000, 0.01, 0.003
      # toyota  1500, 0.05,   0.002237852961363602

      tune.lqr.a = [0., 1., -0.22619643, 1.21822268]
      tune.lqr.b = [-1.92006585e-04, 3.95603032e-05]
      tune.lqr.c = [1., 0.]
      tune.lqr.k = [-110.73572306, 451.22718255]
      tune.lqr.l = [0.3233671, 0.3185757]
  elif method ==  TunType.LAT_TOROUE:
      FRICTION      = float( params.get("TorqueFriction", encoding="utf8") )
      Kp            = float( params.get("TorqueKp", encoding="utf8") )
      Ki            = float( params.get("TorqueKi", encoding="utf8") )
      Kf            = float( params.get("TorqueKf", encoding="utf8") )
      UseAngle      = True  #params.getBool("TorqueUseAngle", encoding="utf8")
      steering_angle_deadzone_deg  = float( params.get("Torquedeadzone", encoding="utf8") )

      tune.init('torque')
      tune.torque.useSteeringAngle = UseAngle  #  False
      tune.torque.kp = Kp / MAX_LAT_ACCEL        # 1.0 / 2.5 = 0.4
      tune.torque.kf = Kf / MAX_LAT_ACCEL        # 1.0 / 2.5 = 0.4
      tune.torque.ki = Ki / MAX_LAT_ACCEL        # 0.1 / 2.5 = 0.04
      tune.torque.friction = FRICTION
      tune.torque.steeringAngleDeadzoneDeg = steering_angle_deadzone_deg
  elif method ==  TunType.LAT_HYBRID:
      tune.init('atom')
      tune.atom.methodConfigs = [ get_method_config( MethodModel.torque, 0), 
                                  get_method_config( MethodModel.lqr, 50) ]

      # 1. torque 
      FRICTION      = float( params.get("TorqueFriction", encoding="utf8") )
      torq_Kp       = float( params.get("TorqueKp", encoding="utf8") )
      torq_Ki       = float( params.get("TorqueKi", encoding="utf8") )
      torq_Kf       = float( params.get("TorqueKf", encoding="utf8") )
      UseAngle      = True  # params.getBool("TorqueUseAngle", encoding="utf8")
      steering_angle_deadzone_deg  = float( params.get("Torquedeadzone", encoding="utf8") )

      tune.atom.torque.useSteeringAngle = UseAngle  #UseAngle  #  False
      tune.atom.torque.kp = torq_Kp / MAX_LAT_ACCEL        # 2.0 / 2.5 = 0.8
      tune.atom.torque.kf = torq_Ki / MAX_LAT_ACCEL        # 1.0 / 2.5 = 0.4
      tune.atom.torque.ki = torq_Kf / MAX_LAT_ACCEL        # 0.5 / 2.5 = 0.2
      tune.atom.torque.friction = FRICTION
      tune.atom.torque.steeringAngleDeadzoneDeg = steering_angle_deadzone_deg

      # 2. lqr
      lqr_scale = float( params.get("LqrScale", encoding="utf8") )
      lqr_Ki = float( params.get("LqrKi", encoding="utf8") )
      lqr_dcGain = float( params.get("LqrDcGain", encoding="utf8") )         

      tune.atom.lqr.scale = lqr_scale     #1700.0
      tune.atom.lqr.ki = lqr_Ki      #0.01
      tune.atom.lqr.dcGain =  lqr_dcGain  #0.0027
      tune.atom.lqr.a = [0., 1., -0.22619643, 1.21822268]
      tune.atom.lqr.b = [-1.92006585e-04, 3.95603032e-05]
      tune.atom.lqr.c = [1., 0.]
      tune.atom.lqr.k = [-110.73572306, 451.22718255]
      tune.atom.lqr.l = [0.3233671, 0.3185757]

  else:
      print( 'OpkrLateralControlMethod = tune.init(lqr)')
      tune.init('lqr')
      tune.lqr.scale = 1900     #1700.0
      tune.lqr.ki = 0.01      #0.01
      tune.lqr.dcGain =  0.0027  #0.0027
      # 호야  1500, 0.015, 0.0027
      #  1700, 0.01, 0.0029
      #  2000, 0.01, 0.003
      # toyota  1500, 0.05,   0.002237852961363602

      tune.lqr.a = [0., 1., -0.22619643, 1.21822268]
      tune.lqr.b = [-1.92006585e-04, 3.95603032e-05]
      tune.lqr.c = [1., 0.]
      tune.lqr.k = [-110.73572306, 451.22718255]
      tune.lqr.l = [0.3233671, 0.3185757]
  
  return  method

###### LAT ######
def set_lat_tune(tune, name, MAX_LAT_ACCEL=2.5, FRICTION=0.01, steering_angle_deadzone_deg=0.0):
  if name == LatTunes.HYBRID:
    tune.init('atom')
    tune.atom.methodConfigs = [ get_method_config( MethodModel.torque, 5), 
                                get_method_config( MethodModel.lqr, 50) ]

    # 1. torque
    tune.atom.torque.useSteeringAngle = True  #  False
    tune.atom.torque.kp = 1.0 / MAX_LAT_ACCEL        # 2.0 / 2.5 = 0.8
    tune.atom.torque.kf = 1.0 / MAX_LAT_ACCEL        # 1.0 / 2.5 = 0.4
    tune.atom.torque.ki = 0.1 / MAX_LAT_ACCEL        # 0.5 / 2.5 = 0.2
    tune.atom.torque.friction = FRICTION
    tune.atom.torque.steeringAngleDeadzoneDeg = steering_angle_deadzone_deg

    # 2. lqr
    tune.atom.lqr.scale = 1900     #1700.0
    tune.atom.lqr.ki = 0.01      #0.01
    tune.atom.lqr.dcGain =  0.0028  #0.0027
    tune.atom.lqr.a = [0., 1., -0.22619643, 1.21822268]
    tune.atom.lqr.b = [-1.92006585e-04, 3.95603032e-05]
    tune.atom.lqr.c = [1., 0.]
    tune.atom.lqr.k = [-110.73572306, 451.22718255]
    tune.atom.lqr.l = [0.3233671, 0.3185757]
  elif name == LatTunes.MULTI:
    tune.init('multi')
    tune.multi.methodConfigs = [get_method_config( MethodModel.lqr, 2), 
                                get_method_config( MethodModel.torque, 10), 
                                get_method_config( MethodModel.pid, 20) ]

    # 1. lqr
    tune.multi.lqr.scale = 1900     #1700.0
    tune.multi.lqr.ki = 0.01      #0.01
    tune.multi.lqr.dcGain =  0.0027  #0.0027

    tune.multi.lqr.a = [0., 1., -0.22619643, 1.21822268]
    tune.multi.lqr.b = [-1.92006585e-04, 3.95603032e-05]
    tune.multi.lqr.c = [1., 0.]
    tune.multi.lqr.k = [-110.73572306, 451.22718255]
    tune.multi.lqr.l = [0.3233671, 0.3185757]

    # 2. torque
    tune.multi.torque.useSteeringAngle = True  #  False
    tune.multi.torque.kp = 1.0 / MAX_LAT_ACCEL        # 2.0 / 2.5 = 0.8
    tune.multi.torque.kf = 1.0 / MAX_LAT_ACCEL        # 1.0 / 2.5 = 0.4
    tune.multi.torque.ki = 0.1 / MAX_LAT_ACCEL        # 0.5 / 2.5 = 0.2
    tune.multi.torque.friction = FRICTION
    tune.multi.torque.steeringAngleDeadzoneDeg = steering_angle_deadzone_deg

    # 3. pid
    tune.multi.pid.kf = 0.000005
    tune.multi.pid.kpBP, tune.multi.pid.kpV = [[0.], [0.25]]
    tune.multi.pid.kiBP, tune.multi.pid.kiV = [[0.], [0.05]]
  elif name == LatTunes.TORQUE:
    tune.init('torque')
    tune.torque.useSteeringAngle = True  #  False
    tune.torque.kp = 1.0 / MAX_LAT_ACCEL        # 2.0 / 2.5 = 0.8
    tune.torque.kf = 1.0 / MAX_LAT_ACCEL        # 1.0 / 2.5 = 0.4
    tune.torque.ki = 0.1 / MAX_LAT_ACCEL        # 0.5 / 2.5 = 0.2
    tune.torque.friction = FRICTION
    tune.torque.steeringAngleDeadzoneDeg = steering_angle_deadzone_deg
  elif name == LatTunes.LQR_GRANDEUR:  
    tune.init('lqr')
    tune.lqr.scale = 1900     #1700.0
    tune.lqr.ki = 0.01      #0.01
    tune.lqr.dcGain =  0.0027  #0.0027
    # 호야  1500, 0.015, 0.0027
    #  1700, 0.01, 0.0029
    #  2000, 0.01, 0.003
    # toyota  1500, 0.05,   0.002237852961363602

    tune.lqr.a = [0., 1., -0.22619643, 1.21822268]
    tune.lqr.b = [-1.92006585e-04, 3.95603032e-05]
    tune.lqr.c = [1., 0.]
    tune.lqr.k = [-110.73572306, 451.22718255]
    tune.lqr.l = [0.3233671, 0.3185757]    
  elif name == LatTunes.INDI_PRIUS:
    tune.init('indi')
    tune.indi.innerLoopGainBP = [0.]
    tune.indi.innerLoopGainV = [4.0]
    tune.indi.outerLoopGainBP = [0.]
    tune.indi.outerLoopGainV = [3.0]
    tune.indi.timeConstantBP = [0.]
    tune.indi.timeConstantV = [1.0]
    tune.indi.actuatorEffectivenessBP = [0.]
    tune.indi.actuatorEffectivenessV = [1.0]
  elif 'PID' in str(name):
    tune.init('pid')
    tune.pid.kiBP = [0.0]
    tune.pid.kpBP = [0.0]
    if name == LatTunes.PID_A:
      tune.pid.kpV = [0.2]
      tune.pid.kiV = [0.05]
      tune.pid.kf = 0.00003
    elif name == LatTunes.PID_C:
      tune.pid.kpV = [0.6]
      tune.pid.kiV = [0.1]
      tune.pid.kf = 0.00006
    elif name == LatTunes.PID_D:
      tune.pid.kpV = [0.6]
      tune.pid.kiV = [0.1]
      tune.pid.kf = 0.00007818594
    elif name == LatTunes.PID_F:
      tune.pid.kpV = [0.723]
      tune.pid.kiV = [0.0428]
      tune.pid.kf = 0.00006
    elif name == LatTunes.PID_G:
      tune.pid.kpV = [0.18]
      tune.pid.kiV = [0.015]
      tune.pid.kf = 0.00012
    elif name == LatTunes.PID_H:
      tune.pid.kpV = [0.17]
      tune.pid.kiV = [0.03]
      tune.pid.kf = 0.00006
    elif name == LatTunes.PID_I:
      tune.pid.kpV = [0.15]
      tune.pid.kiV = [0.05]
      tune.pid.kf = 0.00004
    elif name == LatTunes.PID_J:
      tune.pid.kpV = [0.19]
      tune.pid.kiV = [0.02]
      tune.pid.kf = 0.00007818594
    elif name == LatTunes.PID_L:
      tune.pid.kpV = [0.3]
      tune.pid.kiV = [0.05]
      tune.pid.kf = 0.00006
    elif name == LatTunes.PID_M:
      tune.pid.kpV = [0.3]
      tune.pid.kiV = [0.05]
      tune.pid.kf = 0.00007
    elif name == LatTunes.PID_N:
      tune.pid.kpV = [0.35]
      tune.pid.kiV = [0.15]
      tune.pid.kf = 0.00007818594
    else:
      raise NotImplementedError('This PID tune does not exist')
  else:
    raise NotImplementedError('This lateral tune does not exist')
