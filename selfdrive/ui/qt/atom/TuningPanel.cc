
#include <string>
#include <iostream>
#include <sstream>
#include <cassert>
// #include <QPushButton>


#include "selfdrive/ui/qt/widgets/input.h"
#include "selfdrive/ui/qt/widgets/toggle.h"
#include "selfdrive/ui/qt/widgets/offroad_alerts.h"
#include "selfdrive/ui/qt/widgets/controls.h"

#include "selfdrive/common/params.h"
#include "selfdrive/common/util.h"
#include "selfdrive/ui/ui.h"


#include "selfdrive/ui/qt/atom/Tuning/opkr.h"

#include "TuningPanel.h"

// 일부 코드 OPKR 참고.



TuningPanel::TuningPanel(QWidget *parent) : QFrame(parent) {
  QVBoxLayout *layout = new QVBoxLayout(this);

  layout->setContentsMargins(50, 0, 50, 0);
  layout->setSpacing(30);

  // OPKR
  layout->addWidget(new LabelControl("〓〓〓〓〓〓〓〓【 TUNING 】〓〓〓〓〓〓〓〓", ""));
  layout->addWidget(new CameraOffset());
  layout->addWidget(new PathOffset());
  layout->addWidget(new LiveSteerRatioToggle());
  layout->addWidget(new LiveSRPercent());
  layout->addWidget(new SRBaseControl());
  layout->addWidget(new SRMaxControl());
  layout->addWidget(new SteerActuatorDelay());
  layout->addWidget(new SteerRateCost());
  layout->addWidget(new SteerLimitTimer());
  layout->addWidget(new TireStiffnessFactor());
  layout->addWidget(new VariableSteerMaxToggle());
  layout->addWidget(new SteerMax());
  layout->addWidget(new VariableSteerDeltaToggle());
  layout->addWidget(new SteerDeltaUp());
  layout->addWidget(new SteerDeltaDown());
  layout->addWidget(new ToAvoidLKASFaultBeyondToggle());
  layout->addWidget(new SteerThreshold());
  layout->addWidget(new DesiredCurvatureLimit());

  layout->addWidget(horizontal_line());

  layout->addWidget(new LabelControl("〓〓〓〓〓〓〓〓【 CONTROL 】〓〓〓〓〓〓〓〓", ""));
  layout->addWidget(new LateralControl());
  layout->addWidget(new LiveTunePanelToggle());
  QString lat_control = QString::fromStdString(Params().get("LateralControlMethod", false));
  if (lat_control == "0") {
    layout->addWidget(new PidKp());
    layout->addWidget(new PidKi());
    layout->addWidget(new PidKd());
    layout->addWidget(new PidKf());
  } else if (lat_control == "1") {
    layout->addWidget(new InnerLoopGain());
    layout->addWidget(new OuterLoopGain());
    layout->addWidget(new TimeConstant());
    layout->addWidget(new ActuatorEffectiveness());
  } else if (lat_control == "2") {
    layout->addWidget(new Scale());
    layout->addWidget(new LqrKi());
    layout->addWidget(new DcGain());
  } else if (lat_control == "3") {
    layout->addWidget(new TorqueMaxLatAccel());
    layout->addWidget(new TorqueKp());
    layout->addWidget(new TorqueKf());
    layout->addWidget(new TorqueKi());
    layout->addWidget(new TorqueFriction());
    layout->addWidget(new TorqueUseAngle());
  } else if (lat_control == "4") {
    layout->addWidget(new MultipleLatSelect());
    layout->addWidget(new MultipleLateralSpeed());
    layout->addWidget(new MultipleLateralAngle());
    layout->addWidget(new TorqueMaxLatAccel());
    layout->addWidget(new TorqueKp());
    layout->addWidget(new TorqueKf());
    layout->addWidget(new TorqueKi());
    layout->addWidget(new TorqueFriction());
    layout->addWidget(new TorqueUseAngle());
    layout->addWidget(new Scale());
    layout->addWidget(new LqrKi());
    layout->addWidget(new DcGain());
    layout->addWidget(new InnerLoopGain());
    layout->addWidget(new OuterLoopGain());
    layout->addWidget(new TimeConstant());
    layout->addWidget(new ActuatorEffectiveness());
    layout->addWidget(new PidKp());
    layout->addWidget(new PidKi());
    layout->addWidget(new PidKd());
    layout->addWidget(new PidKf());
  }

  layout->addWidget(horizontal_line());

  layout->addWidget(new LabelControl("〓〓〓〓〓〓〓【 LONGCONTROL 】〓〓〓〓〓〓〓", ""));
  layout->addWidget(new CustomTRToggle());
  layout->addWidget(new CruiseGapTR());
  layout->addWidget(new DynamicTRGap());
  layout->addWidget(new DynamicTRUD());
  layout->addWidget(new DynamicTRBySpeed());
  layout->addWidget(new RadarLongHelperOption());
  layout->addWidget(new StoppingDistAdjToggle());
  layout->addWidget(new StoppingDist());
  layout->addWidget(new E2ELongToggle());
  layout->addWidget(new StockDecelonCamToggle());
  //layout->addWidget(new RadarDisableToggle());
  //layout->addWidget(new UseRadarTrackToggle());
}