
#include <string>
#include <iostream>
#include <sstream>
#include <cassert>
// #include <QPushButton>


#include "selfdrive/ui/qt/widgets/input.h"
#include "selfdrive/ui/qt/widgets/toggle.h"
#include "selfdrive/ui/qt/widgets/offroad_alerts.h"
#include "selfdrive/ui/qt/widgets/controls.h"

#include "selfdrive/ui/qt/atom/widgets/steerWidget.h"
#include "selfdrive/ui/qt/atom/widgets/TunWidget.h"

#include "common/params.h"
#include "common/util.h"
#include "selfdrive/ui/ui.h"


#include "widgets/opkr.h"

#include "TuningPanel.h"

// 일부 코드 OPKR 참고.



TuningPanel::TuningPanel(QWidget *parent) : QFrame(parent) 
{
  QVBoxLayout *main_layout = new QVBoxLayout(this);
  main_layout->setContentsMargins(50, 0, 50, 0);
  main_layout->setSpacing(30);


  // OPKR
  main_layout->addWidget(new CTunWidget());    
  main_layout->addWidget(new CSteerWidget());  
  main_layout->addWidget(new CLaneWidget());  
  

}