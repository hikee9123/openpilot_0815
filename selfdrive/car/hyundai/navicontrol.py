import math
import numpy as np



from common.conversions import Conversions as CV
from selfdrive.car.hyundai.values import Buttons
from common.numpy_fast import clip, interp
import cereal.messaging as messaging

import common.loger as trace1
import common.MoveAvg as mvAvg

#from selfdrive.road_speed_limiter import  road_speed_limiter_get_active, get_road_speed_limiter


class NaviControl():
  def __init__(self, p = None ):
    self.p = p
    
    self.sm = messaging.SubMaster(['liveNaviData','lateralPlan','radarState','modelV2']) 

    self.btn_cnt = 0
    self.seq_command = 0
    self.target_speed = 0
    self.set_point = 0
    self.wait_timer2 = 0
    self.set_speed_kph = 0
 
    self.moveAvg = mvAvg.MoveAvg()

    self.gasPressed_time = 0
    self.gasWait_time = 0

    self.frame_camera = 0
    self.VSetDis = 30
  




  def update_lateralPlan( self ):
    self.sm.update(0)
    path_plan = self.sm['lateralPlan']
    return path_plan



  def button_status(self, CS ): 
    if not CS.acc_active or CS.cruise_buttons != Buttons.NONE: 
      self.wait_timer2 = 50 
    elif self.wait_timer2: 
      self.wait_timer2 -= 1
    else:
      return 1
    return 0


  # buttn acc,dec control
  def switch(self, seq_cmd):
      self.case_name = "case_" + str(seq_cmd)
      self.case_func = getattr( self, self.case_name, lambda:"default")
      return self.case_func()

  def reset_btn(self):
      if self.seq_command != 3:
        self.seq_command = 0


  def case_default(self):
      self.seq_command = 0
      return None

  def case_0(self):
      self.btn_cnt = 0
      self.target_speed = self.set_point
      delta_speed = self.target_speed - self.VSetDis
      if delta_speed > 1:
        self.seq_command = 1
      elif delta_speed < -1:
        self.seq_command = 2
      return None

  def case_1(self):  # acc
      btn_signal = Buttons.RES_ACCEL
      self.btn_cnt += 1
      if self.target_speed == self.VSetDis:
        self.btn_cnt = 0
        self.seq_command = 3
      elif self.btn_cnt > 10:
        self.btn_cnt = 0
        self.seq_command = 3
      return btn_signal


  def case_2(self):  # dec
      btn_signal = Buttons.SET_DECEL
      self.btn_cnt += 1
      if self.target_speed == self.VSetDis:
        self.btn_cnt = 0
        self.seq_command = 3            
      elif self.btn_cnt > 10:
        self.btn_cnt = 0
        self.seq_command = 3
      return btn_signal

  def case_3(self):  # None
      btn_signal = None  # Buttons.NONE
      
      self.btn_cnt += 1
      #if self.btn_cnt <= 1:
      # btn_signal = None  #Buttons.NONE
      if self.btn_cnt > 6: 
        self.seq_command = 0
      return btn_signal


  def ascc_button_control( self, CS, set_speed ):
    self.set_point = max(30,set_speed)
    self.curr_speed = CS.out.vEgo * CV.MS_TO_KPH
    self.VSetDis   = CS.VSetDis
    btn_signal = self.switch( self.seq_command )
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
        frame_delta = abs(frame - self.frame_camera)
        cruise_set_speed_kph = interp( frame_delta, [0, 500], [ self.VSetDis, cruise_set_speed_kph ] )
      else:
        self.frame_camera = frame

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


  def auto_speed_control( self, c, CS, ctrl_speed, path_plan ):
    cruise_speed = False
    if CS.cruise_set_mode == 2:
      vFuture = c.hudControl.vFuture * CV.MS_TO_KPH
      ctrl_speed = min( vFuture, ctrl_speed )
    elif CS.gasPressed:
      self.gasPressed_time += 1
      if self.gasPressed_time > 100:
        self.gasPressed_time = 0
        cruise_speed = True
    elif self.gasPressed_time:
      self.gasPressed_time = 0
      self.gasWait_time = 500      
      cruise_speed = True
    elif CS.cruise_set_mode == 3:
      if self.gasWait_time > 0:
        self.gasWait_time -= 1
      elif ctrl_speed > 90:
        modelSpeed = path_plan.modelSpeed * CV.MS_TO_KPH
        dRate = interp( modelSpeed, [80,200], [ 0.9, 1 ] )
        ctrl_speed *= dRate
        if ctrl_speed < 90:
          ctrl_speed = 90

    clu_Vanz = CS.clu_Vanz


    if cruise_speed:
      ctrl_speed = max( ctrl_speed, clu_Vanz )
      CS.set_cruise_speed( ctrl_speed )  

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
