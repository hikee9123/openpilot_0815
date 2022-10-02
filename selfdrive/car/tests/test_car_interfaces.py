#!/usr/bin/env python3
import unittest
import importlib
from parameterized import parameterized

from cereal import car
from selfdrive.car.fingerprints import all_known_cars
from selfdrive.car.car_helpers import interfaces
from selfdrive.car.fingerprints import _FINGERPRINTS as FINGERPRINTS
import cereal.messaging as messaging

from selfdrive.car.hyundai.values import CAR

from selfdrive.controls.lib.latcontrol_pid import LatControlPID
from selfdrive.controls.lib.latcontrol_indi import LatControlINDI
from selfdrive.controls.lib.latcontrol_lqr import LatControlLQR
from selfdrive.controls.lib.latcontrol_angle import LatControlAngle
from selfdrive.controls.lib.latcontrol_torque import LatControlTorque
from selfdrive.controls.lib.latcontrol_atom import LatControlATOM
from selfdrive.controls.lib.latcontrol_multi import LatControlMULTI


MethodModel = car.CarParams.MethodModel

class TestCarInterfaces(unittest.TestCase):

  @parameterized.expand([(car,) for car in all_known_cars()])
  def test_car_interfaces(self, car_name):
    if car_name in FINGERPRINTS:
      fingerprint = FINGERPRINTS[car_name][0]
    else:
      fingerprint = {}

    CarInterface, CarController, CarState = interfaces[car_name]
    fingerprints = {
      0: fingerprint,
      1: fingerprint,
      2: fingerprint,
    }

    self.pm = messaging.PubMaster(['sendcan', 'controlsState', 'carState',
                                    'carControl', 'carEvents', 'carParams'])

    car_fw = []

    car_params = CarInterface.get_params(car_name, fingerprints, car_fw)
    car_interface = CarInterface(car_params, CarController, CarState)
    assert car_params
    assert car_interface

    self.assertGreater(car_params.mass, 1)
    self.assertGreater(car_params.maxLateralAccel, 0)

    print( 'test car name = {}'.format( car_name ) )
    self.LaC = None
    if car_params.steerControlType != car.CarParams.SteerControlType.angle:
      tuning = car_params.lateralTuning.which()
      if tuning == 'pid':
        self.assertTrue(len(car_params.lateralTuning.pid.kpV))
        self.LaC = LatControlPID( car_params, car_interface)
      elif tuning == 'torque':
        self.assertTrue(car_params.lateralTuning.torque.kf > 0)
        self.LaC = LatControlTorque( car_params, car_interface)
      elif tuning == 'indi':
        self.assertTrue(len(car_params.lateralTuning.indi.outerLoopGainV))
        self.LaC = LatControlINDI( car_params, car_interface)
      elif tuning == 'lqr':
        self.LaC = LatControlLQR( car_params, car_interface)
      elif tuning == 'atom':
        self.assertTrue(car_params.lateralTuning.atom.torque.kf > 0)
        self.LaC = LatControlATOM( car_params, car_interface)        
      elif tuning == 'multi':
        self.assertTrue(len(car_params.lateralTuning.multi.pid.kpV))
        self.LaC = LatControlMULTI( car_params, car_interface)


    car_interface.get_tunning_params( car_params )
    if self.LaC is not None:
      self.LaC.live_tune( car_params )

    cp_send = messaging.new_message('carParams')
    cp_send.carParams = car_params
    #print(  cp_send )
    self.pm.send('carParams', cp_send)

    # Run car interface
    CC = car.CarControl.new_message()
    for _ in range(10):
      car_interface.update(CC, [])
      car_interface.apply(CC)
      car_interface.apply(CC)

    CC = car.CarControl.new_message()
    CC.enabled = True
    for _ in range(10):
      car_interface.update(CC, [])
      car_interface.apply(CC)
      car_interface.apply(CC)

    # Test radar interface
    RadarInterface = importlib.import_module(f'selfdrive.car.{car_params.carName}.radar_interface').RadarInterface
    radar_interface = RadarInterface(car_params)
    assert radar_interface

    # Run radar interface once
    radar_interface.update([])
    if not car_params.radarOffCan and radar_interface.rcp is not None and \
       hasattr(radar_interface, '_update') and hasattr(radar_interface, 'trigger_msg'):
      radar_interface._update([radar_interface.trigger_msg])

if __name__ == "__main__":
  unittest.main()
