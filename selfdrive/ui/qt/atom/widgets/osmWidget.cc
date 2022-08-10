
#include <QDialog>
#include <QDateTime>
#include <QHBoxLayout>
#include <QMouseEvent>
#include <QVBoxLayout>


#include "selfdrive/ui/qt/atom/widgets/osmWidget.h"



CosmWidget::CosmWidget( TuningPanel *panel ) : CGroupWidget( "OSM Enable" ) 
{
  m_pPanel = panel;
  QString str_param = "OpkrOSMEnable";
  auto str = QString::fromStdString( params.get( str_param.toStdString() ) );
  int value = str.toInt();
  m_nMethod = value;    

  // label
  method_label = new QPushButton("method"); // .setAlignment(Qt::AlignVCenter|Qt::AlignHCenter);
  method_label->setStyleSheet(R"(
    padding: 0;
    border-radius: 50px;
    font-size: 35px;
    font-weight: 500;
    color: #E4E4E4;
    background-color: #00A12E;
  )");
  method_label->setFixedSize( 500, 100);
  hlayout->addWidget(method_label);
  
  connect(method_label, &QPushButton::clicked, [=]() {
    m_nMethod += 1;
    if( m_nMethod >= TP_ALL )
      m_nMethod = 0;

    QString values = QString::number(m_nMethod);
    params.put( str_param.toStdString(), values.toStdString());      
    refresh();
  });
  main_layout->addLayout(hlayout);


  FrameOSM( CreateBoxLayout(TP_USES) );
  refresh();
}  


void  CosmWidget::FrameOSM(QVBoxLayout *layout)
{
  // QVBoxLayout *pBoxLayout = CreateBoxLayout(TP_NONE);
  // layout->addWidget(new PidKp());
  // layout->addWidget(new PidKi());
  // layout->addWidget(new PidKd());
  // layout->addWidget(new PidKf());

 // 1.
  MenuControl *pMenu1 = new MenuControl( 
    "OpkrOSMCurvDecelOption",
    "Curv Decel Option",
    "0.None 1.Vision+OSM 2.Vision Only  3.OSM only"
     );

  pMenu1->SetControl( 0, 3, 1 );
 // pMenu1->SetString( "None,Vision+OSM,Vision,OSM" );
  //pMenu1->SetString( 0, "None");
  layout->addWidget( pMenu1 );

  // 1.
  MenuControl *pMenu2 = new MenuControl( 
    "OpkrOSM_QUERY_RADIUS",
    "QUERY_RADIUS",
    "Radius to use on OSM data queries.(mts) def:3000"
     );

  pMenu2->SetControl( 100, 9000, 10 );
  layout->addWidget( pMenu2 );

  // 2.
  MenuControl *pMenu3 = new MenuControl( 
    "OpkrOSM_MIN_DISTANCE_FOR_NEW_QUERY",
    "MIN_DISTANCE_FOR_NEW_QUERY",
    "Minimum distance to query area edge before issuing a new query.(mts) def:1000"
     );

  pMenu3->SetControl( 100, 9000, 10 );
  layout->addWidget( pMenu3 );  

  // 3.
  MenuControl *pMenu4 = new MenuControl( 
    "OpkrOSM_FULL_STOP_MAX_SPEED",
    "FULL_STOP_MAX_SPEED",
    "Max speed for considering car is stopped.(m/s) def:1.39"
     );

  pMenu4->SetControl( 0, 100, 0.1 );
  layout->addWidget( pMenu4 );

  // 4.
  MenuControl *pMenu5 = new MenuControl( 
    "OpkrOSM_LOOK_AHEAD_HORIZON_TIME",
    "LOOK_AHEAD_HORIZON_TIME",
    "Time horizon for look ahead of turn speed sections to provide on liveMapData msg.(s) def:15"
     );

  pMenu5->SetControl( 0, 100, 0.1 );
  layout->addWidget( pMenu5 );  

  // 5.
  MenuControl *pMenu6 = new MenuControl( 
    "OpkrOSM_LANE_WIDTH",
    "LANE_WIDTH",
    "Lane width estimate. Used for detecting departures from way. def:3.7"
     );

  pMenu6->SetControl( 2, 4, 0.1 );
  layout->addWidget( pMenu6 ); 

   // NodesData
  
  // 6.
  MenuControl *pMenu7 = new MenuControl( 
    "OpkrOSM_TURN_CURVATURE_THRESHOLD",
    "_TURN_CURVATURE_THRESHOLD",
    "1/mts. A curvature over this value will generate a speed limit section. def:0.002"
     );

  pMenu7->SetControl( 0, 1, 0.001 );
  layout->addWidget( pMenu7 );  

  // 7.
  MenuControl *pMenu8 = new MenuControl( 
    "OpkrOSM_MAX_LAT_ACC",
    "_MAX_LAT_ACC",
    "Maximum lateral acceleration in turns. def:2.3"
     );

  pMenu8->SetControl( 1, 5, 0.1 );
  layout->addWidget( pMenu8 );


  // 7.
  MenuControl *pMenu9 = new MenuControl( 
    "OpkrOSM_SPLINE_EVAL_STEP",
    "_SPLINE_EVAL_STEP",
    "mts for spline evaluation for curvature calculation. def:5"
     );

  pMenu9->SetControl( 1, 10, 0.1 );
  layout->addWidget( pMenu9 );
  
  // 7.
  MenuControl *pMenu10 = new MenuControl( 
    "OpkrOSM_MIN_SPEED_SECTION_LENGTH",
    "_MIN_SPEED_SECTION_LENGTH",
    "mts. Sections below this value will not be split in smaller sections. def:100"
     );

  pMenu10->SetControl( 0, 200, 1 );
  layout->addWidget( pMenu10 );

   // 7.
  MenuControl *pMenu11 = new MenuControl( 
    "OpkrOSM_MAX_CURV_DEVIATION_FOR_SPLIT",
    "_MAX_CURV_DEVIATION_FOR_SPLIT",
    "Split a speed section if the max curvature deviates from mean by this factor. def:2"
     );

  pMenu11->SetControl( 0, 5, 0.1 );
  layout->addWidget( pMenu11 );

   // 7.
  MenuControl *pMenu12 = new MenuControl( 
    "OpkrOSM_MAX_CURV_SPLIT_ARC_ANGLE",
    "_MAX_CURV_SPLIT_ARC_ANGLE",
    "degrees. Arc section to split into new speed section around max curvature.. def:90"
     );

  pMenu12->SetControl( 50, 200, 1 );
  layout->addWidget( pMenu12 ); 


   // 7.
  MenuControl *pMenu13 = new MenuControl( 
    "OpkrOSM_MIN_NODE_DISTANCE",
    "_MIN_NODE_DISTANCE",
    "mts. Minimum distance between nodes for spline evaluation. Data is enhanced if not met. def:50"
     );

  pMenu13->SetControl( 10, 100, 1 );
  layout->addWidget( pMenu13 );          


   // 7.
  MenuControl *pMenu14 = new MenuControl( 
    "OpkrOSM_ADDED_NODES_DIST",
    "_ADDED_NODES_DIST",
    "mts. Distance between added nodes when data is enhanced for spline evaluation. def:15"
     );

  pMenu14->SetControl( 0, 50, 1 );
  layout->addWidget( pMenu14 );


   // 7.
  MenuControl *pMenu15 = new MenuControl( 
    "OpkrOSM_DIVERTION_SEARCH_RANGE1",
    "_DIVERTION_SEARCH_RANGE1",
    "mt. Range of distance to current location for divertion search. def:-200"
     );

  pMenu15->SetControl( -500, 0, 1 );
  layout->addWidget( pMenu15 );
  
  MenuControl *pMenu16 = new MenuControl( 
    "OpkrOSM_DIVERTION_SEARCH_RANGE2",
    "_DIVERTION_SEARCH_RANGE2",
    "mt. Range of distance to current location for divertion search. def:50"
     );

  pMenu16->SetControl( 40, 60, 1 );
  layout->addWidget( pMenu16 );                     


}



void CosmWidget::refresh( int nID )
{
  CGroupWidget::refresh( m_nMethod );
 

  QString  str;
  switch( m_nMethod )
  {
    case TP_NONE :  str = "0.미사용";    break;
    case TP_USES :  str = "1.사용";      break;
  }

  if( m_nMethod == TP_NONE )
    method_label->setStyleSheet("background-color: #393939;");
  else
    method_label->setStyleSheet("background-color: #E22C2C;");

  method_label->setText( str ); 
}
