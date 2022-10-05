
from cereal import car, log
from common.conversions import Conversions as CV
from selfdrive.car.hyundai.values import Buttons
from common.numpy_fast import interp
import cereal.messaging as messaging



VisionTurnControllerState = log.LongitudinalPlan.VisionTurnControllerState
EventName = car.CarEvent.EventName


_ENTERING_PRED_LAT_ACC_TH = 0.3  #  1.3 Predicted Lat Acc threshold to trigger entering turn state.
_ABORT_ENTERING_PRED_LAT_ACC_TH = 0.1  # 1.1 Predicted Lat Acc threshold to abort entering state if speed drops.

_TURNING_LAT_ACC_TH = 0.6  # 1.6 Lat Acc threshold to trigger turning turn state.

_LEAVING_LAT_ACC_TH = 0.3  #  1.3Lat Acc threshold to trigger leaving turn state.
_FINISH_LAT_ACC_TH = 0.1  # 1.1 Lat Acc threshold to trigger end of turn cycle.

class NaviControl():
  def __init__(self, p , CP ):
    self.p = p
    self.CP = CP
    
    self.sm = messaging.SubMaster(['liveNaviData','lateralPlan','radarState','modelV2','liveMapData','longitudinalPlan']) 

    self.btn_cnt = 0
    self.seq_command = 0
    self.target_speed = 0
    self.set_point = 0
    self.wait_timer2 = 0
    self.set_speed_kph = 0
 


    self.gasPressed_time = 0


    self.frame_camera = 0
    self.VSetDis = 30
    self.frame_VSetDis = 30


    self.last_lead_distance = 0


    self.turnSpeedLimitsAhead = 0
    self.turnSpeedLimitsAheadDistances = 0
    self.turnSpeedLimitsAheadDistancesOld = 0

    self.event_navi_alert = None

    self._frame_inc = 0
    self._frame_dec = 0
    self._visionTurnSpeed = 0
    self._current_lat_acc = 0
    self._max_pred_lat_acc = 0
    self.state = VisionTurnControllerState.disabled

    self.auto_resume_time = 0



  def update_lateralPlan( self ):
    self.sm.update(0)
    path_plan = self.sm['lateralPlan']
    return path_plan



  def button_status(self, CS ): 
    if not CS.acc_active or CS.cruise_buttons != Buttons.NONE or CS.out.brakePressed or CS.out.gasPressed: 
      self.wait_timer2 = 50 
    elif self.wait_timer2: 
      self.wait_timer2 -= 1
    else:
      return 1
    return 0


  # buttn acc,dec control
  def switch(self, seq_cmd, CS ):
      self.case_name = "case_" + str(seq_cmd)
      self.case_func = getattr( self, self.case_name, lambda:"default")
      return self.case_func( CS )



  def case_default(self, CS):
      self.seq_command = 0
      return None

  def case_0(self, CS):
      self.btn_cnt = 0
      self.target_speed = self.set_point
      delta_speed = self.target_speed - self.VSetDis

      standstill = CS.out.cruiseState.standstill

      if standstill:
        self.last_lead_distance = 0
        self.seq_command = 5
      elif delta_speed > 1:
        self.seq_command = 1
      elif delta_speed < -1:
        self.seq_command = 2
      return None

  def case_1(self, CS):  # acc
      self.btn_cnt += 1
      if self.target_speed == self.VSetDis:
        self.btn_cnt = 0
        self.seq_command = 3
      elif self.btn_cnt > 10:
        self.btn_cnt = 0
        self.seq_command = 3
      return Buttons.RES_ACCEL


  def case_2(self, CS):  # dec
      self.btn_cnt += 1
      if self.target_speed == self.VSetDis:
        self.btn_cnt = 0
        self.seq_command = 3            
      elif self.btn_cnt > 10:
        self.btn_cnt = 0
        self.seq_command = 3
      return Buttons.SET_DECEL

  def case_3(self, CS):  # None
      self.btn_cnt += 1
      if self.btn_cnt > 6: 
        self.seq_command = 0
      return None

  def case_5(self, CS):  #  standstill
      standstill = CS.out.cruiseState.standstill
      if not standstill:
        self.seq_command = 0
      elif CS.lead_distance < 4:
        self.last_lead_distance = 0
      elif self.last_lead_distance == 0:  
        self.last_lead_distance = CS.lead_distance
      elif CS.lead_distance > self.last_lead_distance:
        self.seq_command = 6
        self.btn_cnt = 0
      return  None


  def case_6(self, CS):  # resume
      self.btn_cnt += 1
      if self.btn_cnt > 5:
        self.btn_cnt = 0
        self.seq_command = 3
      return Buttons.SET_DECEL


  def ascc_button_control( self, CS, set_speed ):
    self.set_point = max(30,set_speed)
    self.curr_speed = CS.out.vEgo * CV.MS_TO_KPH
    self.VSetDis   = CS.VSetDis



    btn_signal = self.switch( self.seq_command, CS )
    return btn_signal


  def get_dRel(self):
      radarState = self.sm['radarState']
      lead_0 = radarState.leadOne
      lead_1 = radarState.leadTwo

      model_v2 = self.sm['modelV2']
      leads_v3 = model_v2.leadsV3
      if lead_0.status:
        dRel1 = self.lead_0.dRel
      else:
        dRel1 = leads_v3[0].x[0]

      if len(leads_v3) > 1:
        dRel2 = leads_v3[1].x[0]
      else:
        dRel2 = 0

      return dRel1, dRel2


  def get_auto_resume(self, CS):
    v_ego_kph = CS.out.vEgo * CV.MS_TO_KPH 
    model_v2 = self.sm['modelV2']
    lanePos = model_v2.position
    distance = 0
    if len(lanePos.x) > 0:
      distance = lanePos.x[-1]

    if distance < 2:
      self.auto_resume_time = 10
    elif  self.auto_resume_time > 0:
      self.auto_resume_time -= 1


    if self.auto_resume_time <= 1 and v_ego_kph < 1:
      self.event_navi_alert = EventName.manualRestart



    return  distance


  def get_cut_in_car(self):
    cut_in = 0
    d_rel1 = 0
    d_rel2 = 0
    d_rel  = 150
    model_v2 = self.sm['modelV2']
    leads_v3 = model_v2.leadsV3
    if len(leads_v3) > 1:
      d_rel1 = leads_v3[0].x[0]
      d_rel2 = leads_v3[1].x[0]
      d_rel = min( d_rel1, d_rel2 )
      if leads_v3[0].prob > 0.5 and leads_v3[1].prob > 0.5:
        cut_in = d_rel1 - d_rel2  # > 3

    return cut_in, d_rel


  def get_cut_in_radar(self):
    self.lead_0 = self.sm['radarState'].leadOne
    self.lead_1 = self.sm['radarState'].leadTwo
    delta_Rel = self.lead_0.dRel - self.lead_1.dRel
    d_rel = self.lead_0.dRel
    self.cut_in = True if self.lead_1.status and delta_Rel > 3.0 else False

    return self.cut_in, d_rel


  def get_navi_speed(self, sm, CS, cruiseState_speed, frame ):
    cruise_set_speed_kph = cruiseState_speed
    v_ego_kph = CS.out.vEgo * CV.MS_TO_KPH    
    self.liveNaviData = sm['liveNaviData']
    speedLimit = self.liveNaviData.speedLimit
    speedLimitDistance = self.liveNaviData.arrivalDistance  #speedLimitDistance
    #safetySign  = self.liveNaviData.safetySign
    mapValid = self.liveNaviData.mapValid
    trafficType = self.liveNaviData.trafficType
    
    if not mapValid or trafficType == 0:  # ACC
      if cruise_set_speed_kph >  self.VSetDis:
        #if frame % 10 == 0:
        #  cruise_set_speed_kph = self.VSetDis + 1
        if v_ego_kph < (self.VSetDis-5):
          self.frame_camera = frame
          self.frame_VSetDis = self.VSetDis
          cruise_set_speed_kph = self.VSetDis
        else:
          frame_delta = abs(frame - self.frame_camera)
          cruise_set_speed_kph = interp( frame_delta, [0, 2000], [ self.frame_VSetDis, cruise_set_speed_kph ] )
      else:
        self.frame_camera = frame
        self.frame_VSetDis = self.VSetDis

      return  cruise_set_speed_kph

    elif CS.is_highway or speedLimit < 30:
      return  cruise_set_speed_kph
    elif v_ego_kph < 80:
      if speedLimit <= 60:
        spdTarget = interp( speedLimitDistance, [150, 600], [ speedLimit, speedLimit + 30 ] )
      else:      
        spdTarget = interp( speedLimitDistance, [200, 800], [ speedLimit, speedLimit + 40 ] )
    elif speedLimitDistance >= 50:
        spdTarget = interp( speedLimitDistance, [300, 900], [ speedLimit, speedLimit + 50 ] )
    else:
      spdTarget = speedLimit

    if v_ego_kph < speedLimit:
      v_ego_kph = speedLimit

    cruise_set_speed_kph = min( spdTarget, v_ego_kph )
    return  cruise_set_speed_kph

  def osm_turnLimit_alert( self, CS ):

    steeringAngleDeg = abs(CS.out.steeringAngleDeg)
    liveMapData = self.sm['liveMapData']
    longitudinalPlan = self.sm['longitudinalPlan']
  
    turnSpeedLimitsAheadDistances = 0
    turnSpeedLimitsAhead = 0

    self._max_pred_lat_acc = longitudinalPlan.maxPredLatAcc
    self._current_lat_acc = longitudinalPlan.currentLatAcc
    self._visionTurnSpeed = longitudinalPlan.visionTurnSpeed

    turnAheadLen = len(liveMapData.turnSpeedLimitsAheadDistances)
    if turnAheadLen > 0:
      turnSpeedLimitsAheadDistances = liveMapData.turnSpeedLimitsAheadDistances[-1]
      turnSpeedLimitsAhead = liveMapData.turnSpeedLimitsAhead[-1]
    else:
      turnSpeedLimitsAhead = liveMapData.turnSpeedLimit
      turnSpeedLimitsAheadDistances = liveMapData.turnSpeedLimitEndDistance     

    # In any case, if system is disabled or the feature is disabeld or gas is pressed, disable.
    if CS.out.vEgo < 1:
      self.state = VisionTurnControllerState.disabled
      return

    # DISABLED
    if self.state == VisionTurnControllerState.disabled:
      # Do not enter a turn control cycle if speed is low.
      if CS.out.vEgo < 10:
        pass
      # If substantial lateral acceleration is predicted ahead, then move to Entering turn state.
      elif self._max_pred_lat_acc >= _ENTERING_PRED_LAT_ACC_TH:
        self.state = VisionTurnControllerState.entering
        self._frame_inc = 100
        self._frame_dec = 500
      elif turnAheadLen > 0:
        if turnSpeedLimitsAheadDistances > 300 and turnSpeedLimitsAhead < 130:
          self.turnSpeedLimitsAheadDistancesOld = turnSpeedLimitsAheadDistances
        elif self.turnSpeedLimitsAheadDistancesOld == 0:
          pass
        elif self.turnSpeedLimitsAheadDistancesOld != turnSpeedLimitsAheadDistances:
          self.state = VisionTurnControllerState.entering
          self._frame_inc = 100
          self._frame_dec = 500
      else:
        self.turnSpeedLimitsAheadDistancesOld = 0
        self._frame_inc = 10

    # ENTERING
    elif self.state == VisionTurnControllerState.entering:

      # Transition to Turning if current lateral acceleration is over the threshold.
      if self._max_pred_lat_acc >= _TURNING_LAT_ACC_TH  or steeringAngleDeg > 3 or turnSpeedLimitsAheadDistances < 30:
        if self._frame_inc < 1:
          self._frame_inc = 500
          self.state = VisionTurnControllerState.turning
      # Abort if the predicted lateral acceleration drops
      elif self._max_pred_lat_acc < _ABORT_ENTERING_PRED_LAT_ACC_TH:
        if self._frame_dec < 1:
          self.state = VisionTurnControllerState.disabled
      else:
        self._frame_dec = 500

    # TURNING
    elif self.state == VisionTurnControllerState.turning:
      if turnSpeedLimitsAheadDistances > 0:
        self._frame_inc = 200

      # Transition to Leaving if current lateral acceleration drops drops below threshold.
      elif self._max_pred_lat_acc == 0:
        self._frame_inc = 500
      elif self._max_pred_lat_acc <= _LEAVING_LAT_ACC_TH or steeringAngleDeg < 2:
        if self._frame_inc < 1:
          self.state = VisionTurnControllerState.leaving
          self._frame_inc = 100
          self._frame_dec = 200
      else:
        self._frame_inc = 50
  

    # LEAVING
    elif self.state == VisionTurnControllerState.leaving:
      # Transition back to Turning if current lateral acceleration goes back over the threshold.
      if self._max_pred_lat_acc >= _TURNING_LAT_ACC_TH:
        if self._frame_dec < 1:
          self._frame_inc = 500
          self.state = VisionTurnControllerState.turning
      # Finish if current lateral acceleration goes below threshold.
      elif self._max_pred_lat_acc < _FINISH_LAT_ACC_TH:
        if self._frame_inc < 1:
          self.state = VisionTurnControllerState.disabled
      else:
        self._frame_inc = 100


    if self._frame_dec > 0:
      self._frame_dec -= 1
    
    if self._frame_inc > 0:
      self._frame_inc -= 1


    if self.state == VisionTurnControllerState.disabled:
      self.event_navi_alert = None
    elif self.state == VisionTurnControllerState.entering:
      self.event_navi_alert = EventName.curvSpeedEntering
    elif self.state == VisionTurnControllerState.turning:
      self.event_navi_alert = EventName.curvSpeedTurning
    elif self.state == VisionTurnControllerState.leaving:
      self.event_navi_alert = EventName.curvSpeedLeaving


    self.turnSpeedLimitsAhead = turnSpeedLimitsAhead * CV.MS_TO_KPH
    self.turnSpeedLimitsAheadDistances = turnSpeedLimitsAheadDistances

  def osm_speed_control( self, c, CS, ctrl_speed ):
    if self.turnSpeedLimitsAheadDistances > 30 and CS.out.vEgo > 8.3:
      turnSpeedLimit = self.turnSpeedLimitsAhead
      turnSpeedLimit = max( turnSpeedLimit, ctrl_speed - 10 )

    else:
      turnSpeedLimit = ctrl_speed

    return turnSpeedLimit

  def auto_speed_control( self, c, CS, ctrl_speed, path_plan ):
    cruise_set_speed = 0
    if CS.gasPressed:
      self.gasPressed_time = 100
    elif self.gasPressed_time > 0:
      self.gasPressed_time -= 1
      if self.gasPressed_time <= 0:
        cruise_set_speed = CS.clu_Vanz - 5
    elif CS.cruise_set_mode == 1:  # osm control speed.
      osm_speed = self.osm_speed_control( c, CS, ctrl_speed )
      ctrl_speed = min( osm_speed, ctrl_speed )
    elif CS.cruise_set_mode == 2:  # comma long control speed.
      vFuture = c.hudControl.vFuture * CV.MS_TO_KPH
      ctrl_speed = min( vFuture, ctrl_speed )
    elif CS.cruise_set_mode == 3:  # vision + model speed  감속.
      modelSpeed = path_plan.modelSpeed * CV.MS_TO_KPH
      vision_speed = interp( modelSpeed, [80, 250], [ 60, 120 ] )
      ctrl_speed = min( vision_speed, ctrl_speed )


    if cruise_set_speed > 30:
      CS.set_cruise_speed( cruise_set_speed )  

    return  ctrl_speed






  def update(self, c, CS, path_plan, frame ):  
    # send scc to car if longcontrol enabled and SCC not on bus 0 or ont live
    btn_signal = None
    if not self.button_status( CS  ):
      pass
    elif CS.acc_active:
      cruiseState_speed = CS.out.cruiseState.speed * CV.MS_TO_KPH      
      kph_set_vEgo = self.get_navi_speed(  self.sm , CS, cruiseState_speed, frame )
      self.ctrl_speed = min( cruiseState_speed, kph_set_vEgo)

      if CS.cruise_set_mode:
        self.ctrl_speed = self.auto_speed_control( c, CS, self.ctrl_speed, path_plan )


      self.set_speed_kph = self.ctrl_speed
      btn_signal = self.ascc_button_control( CS, self.ctrl_speed )

    return btn_signal
