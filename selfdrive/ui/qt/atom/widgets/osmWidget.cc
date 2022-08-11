
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


  MenuControl *pMenu2 = new MenuControl( 
    "OpkrOSMDebug",
    "Debug Option",
    "0.None 1.Debug"
     );

  pMenu2->SetControl( 0, 1, 1 );
  layout->pMenu2( pMenu2 );
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

////////////////////////////////////////////////////////////////////////////////////////////////////
//
//
//

CWidgetosmConfig::CWidgetosmConfig( TuningPanel *panel ) : CGroupWidget( "OSM Config" ) 
{
  m_pPanel = panel;
  QString str_param = "OpkrOSMConfigEnable";
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


void  CWidgetosmConfig::FrameOSM(QVBoxLayout *layout)
{


  // 1.
  MenuControl *pMenu2 = new MenuControl( 
    "OpkrOSM_QUERY_RADIUS",
    "Query radius",
    "QUERY_RADIUS Radius to use on OSM data queries.(mts) def:3000"
     );

  pMenu2->SetControl( 100, 9000, 10 );
  layout->addWidget( pMenu2 );

  // 2.
  MenuControl *pMenu3 = new MenuControl( 
    "OpkrOSM_MIN_DISTANCE_FOR_NEW_QUERY",
    "Min distance for new query",
    "MIN_DISTANCE_FOR_NEW_QUERY Minimum distance to query area edge before issuing a new query.(mts) def:1000"
     );

  pMenu3->SetControl( 100, 9000, 10 );
  layout->addWidget( pMenu3 );  

  // 3.
  MenuControl *pMenu4 = new MenuControl( 
    "OpkrOSM_FULL_STOP_MAX_SPEED",
    "Full stop max speed",
    "FULL_STOP_MAX_SPEED Max speed for considering car is stopped.(m/s) def:1.39"
     );

  pMenu4->SetControl( 0, 100, 0.1 );
  layout->addWidget( pMenu4 );

  // 4.
  MenuControl *pMenu5 = new MenuControl( 
    "OpkrOSM_LOOK_AHEAD_HORIZON_TIME",
    "Look ahead horizon time",
    "LOOK_AHEAD_HORIZON_TIME Time horizon for look ahead of turn speed sections to provide on liveMapData msg.(s) def:15"
     );

  pMenu5->SetControl( 0, 100, 0.1 );
  layout->addWidget( pMenu5 );  

  // 5.
  MenuControl *pMenu6 = new MenuControl( 
    "OpkrOSM_LANE_WIDTH",
    "Lane width",
    "LANE_WIDTH Lane width estimate. Used for detecting departures from way. def:3.7"
     );

  pMenu6->SetControl( 2, 4, 0.1 );
  layout->addWidget( pMenu6 ); 
}



void CWidgetosmConfig::refresh( int nID )
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



////////////////////////////////////////////////////////////////////////////////////////////////////
//
//
//

CWidgetosmNodesData::CWidgetosmNodesData( TuningPanel *panel ) : CGroupWidget( "OSM NodesData" ) 
{
  m_pPanel = panel;
  QString str_param = "OpkrOSMNodesDataEnable";
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


void  CWidgetosmNodesData::FrameOSM(QVBoxLayout *layout)
{

   // NodesData
   // 1.
  MenuControl *pMenu1 = new MenuControl( 
    "OpkrOSM_TURN_CURVATURE_THRESHOLD",
    "Turn curvature threshold",
    "_TURN_CURVATURE_THRESHOLD A curvature over this value will generate a speed limit section. 1/mts. def:0.002"
     );

  pMenu1->SetControl( 0, 1, 0.001 );
  layout->addWidget( pMenu1 );  

  // 2.
  MenuControl *pMenu2 = new MenuControl( 
    "OpkrOSM_MAX_LAT_ACC",
    "Max lat acc",
    "_MAX_LAT_ACC Maximum lateral acceleration in turns. def:2.3"
     );

  pMenu2->SetControl( 1, 5, 0.1 );
  layout->addWidget( pMenu2 );


  // 7.
  MenuControl *pMenu3 = new MenuControl( 
    "OpkrOSM_SPLINE_EVAL_STEP",
    "Spline eval step",
    "_SPLINE_EVAL_STEP mts for spline evaluation for curvature calculation. def:5"
     );

  pMenu3->SetControl( 1, 10, 0.1 );
  layout->addWidget( pMenu3 );
  
  // 7.
  MenuControl *pMenu4 = new MenuControl( 
    "OpkrOSM_MIN_SPEED_SECTION_LENGTH",
    "Min speed section length",
    "_MIN_SPEED_SECTION_LENGTH  Sections below this value will not be split in smaller sections. mts. def:100"
     );

  pMenu4->SetControl( 0, 200, 1 );
  layout->addWidget( pMenu4 );

   // 7.
  MenuControl *pMenu5 = new MenuControl( 
    "OpkrOSM_MAX_CURV_DEVIATION_FOR_SPLIT",
    "Max curv deviation for split",
    "_MAX_CURV_DEVIATION_FOR_SPLIT Split a speed section if the max curvature deviates from mean by this factor. def:2"
     );

  pMenu5->SetControl( 0, 5, 0.1 );
  layout->addWidget( pMenu5 );

   // 7.
  MenuControl *pMenu6 = new MenuControl( 
    "OpkrOSM_MAX_CURV_SPLIT_ARC_ANGLE",
    "Max curv split arc angle",
    "_MAX_CURV_SPLIT_ARC_ANGLE degrees. Arc section to split into new speed section around max curvature.. def:90"
     );

  pMenu6->SetControl( 50, 200, 1 );
  layout->addWidget( pMenu6 ); 


   // 7.
  MenuControl *pMenu7 = new MenuControl( 
    "OpkrOSM_MIN_NODE_DISTANCE",
    "Min mode distance",
    "_MIN_NODE_DISTANCE Minimum distance between nodes for spline evaluation. Data is enhanced if not met. mts.  def:50"
     );

  pMenu7->SetControl( 10, 100, 1 );
  layout->addWidget( pMenu7 );          


   // 7.
  MenuControl *pMenu8 = new MenuControl( 
    "OpkrOSM_ADDED_NODES_DIST",
    "Added nodes dist",
    "_ADDED_NODES_DIST Distance between added nodes when data is enhanced for spline evaluation. mts.  def:15"
     );

  pMenu8->SetControl( 0, 50, 1 );
  layout->addWidget( pMenu8 );


   // 7.
  MenuControl *pMenu9 = new MenuControl( 
    "OpkrOSM_DIVERTION_SEARCH_RANGE1",
    "Divertion search range1",
    "_DIVERTION_SEARCH_RANGE1 Range of distance to current location for divertion search.  mt. def:-200"
     );

  pMenu9->SetControl( -500, 0, 1 );
  layout->addWidget( pMenu9 );
  
  MenuControl *pMenu10 = new MenuControl( 
    "OpkrOSM_DIVERTION_SEARCH_RANGE2",
    "Divertion search range2",
    "_DIVERTION_SEARCH_RANGE2 Range of distance to current location for divertion search. mt.  def:50"
     );

  pMenu10->SetControl( 40, 60, 1 );
  layout->addWidget( pMenu10 );                     



}



void CWidgetosmNodesData::refresh( int nID )
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
