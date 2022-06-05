
#include <QDialog>
#include <QDateTime>
#include <QHBoxLayout>
#include <QMouseEvent>
#include <QVBoxLayout>

#include "TunWidget.h"

#include "opkr.h"

CTunWidget::CTunWidget(QWidget *parent) : QFrame(parent) 
{
  m_bShow = 0;
  memset( m_pChildFrame, NULL, sizeof(m_pChildFrame) );

  auto str = QString::fromStdString( params.get("OpkrLateralControlMethod") );
  int value = str.toInt();
  m_nMethod = value; 

  main_layout = new QVBoxLayout(this);
  main_layout->setMargin(0);


  hlayout = new QHBoxLayout;
  hlayout->setMargin(0);
  hlayout->setSpacing(20);

  // left icon 
  pix_plus =  QPixmap( "../assets/offroad/icon_plus.png" ).scaledToWidth(80, Qt::SmoothTransformation);
  pix_minus =  QPixmap( "../assets/offroad/icon_minus.png" ).scaledToWidth(80, Qt::SmoothTransformation);


  icon_label = new QLabel();
  icon_label->setPixmap(pix_plus );
  icon_label->setSizePolicy(QSizePolicy(QSizePolicy::Fixed, QSizePolicy::Fixed));
  hlayout->addWidget(icon_label);

  // title
  QString  title = "Tunning control Method";
  title_label = new QPushButton(title);
  title_label->setFixedHeight(120);
  title_label->setStyleSheet("font-size: 50px; font-weight: 400; text-align: left");
  hlayout->addWidget(title_label);

  connect(title_label, &QPushButton::clicked, [=]() {

    if( m_bShow )  m_bShow = 0;
    else   m_bShow = 1;
    refresh();
  });

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
    if( m_nMethod > 5 )
      m_nMethod = 0;

    QString values = QString::number(m_nMethod);
    params.put("OpkrSteerMethod", values.toStdString());      
    refresh();
  });

  main_layout->addLayout(hlayout);


  FramePID( parent );
  FrameINDI( parent );
  FrameLQR( parent );
  FrameTOROUE( parent );
  FrameHYBRID( parent );


  main_layout->addStretch();
  refresh();
}

CTunWidget::~CTunWidget()
{

}


void CTunWidget::FramePID(QWidget *parent) 
{
 // 1. layer#1 menu
  QFrame  *pFrame = CreateFrame(0); 


  QVBoxLayout *menu_layout = new QVBoxLayout(pFrame);

  menu_layout->addWidget(new PidKp());
  menu_layout->addWidget(new PidKi());
  menu_layout->addWidget(new PidKd());
  menu_layout->addWidget(new PidKf());
  
  /*
  MenuControl *pMenu2 = new MenuControl( 
    "OpkrMaxDriverAngleWait",
    "Driver to Steer",
    "Controls smooth torque by the driver  From OpkrMaxSteeringAngle. def:0.002(5sec)",
    "../assets/offroad/icon_shell.png"    
    );
  pMenu2->SetControl( 0, 1, 0.001 );
  pMenu2->SetString( 0, "Not");
  menu_layout->addWidget( pMenu2 ); 
*/

}

void CTunWidget::FrameINDI(QWidget *parent) 
{
 // 1. layer#2 menu
 // QFrame  *pFrame = CreateFrame(1); 

  //QVBoxLayout *menu_layout = new QVBoxLayout(pFrame);  
  //menu_layout->addWidget(new InnerLoopGain());
  //menu_layout->addWidget(new OuterLoopGain());
  //menu_layout->addWidget(new TimeConstant());
  //menu_layout->addWidget(new ActuatorEffectiveness());
}


void  CTunWidget::FrameLQR(QWidget *parent)
{
 // QFrame  *pFrame = CreateFrame(2); 
  //QVBoxLayout *menu_layout = new QVBoxLayout(pFrame);  

  //menu_layout->addWidget(new Scale());
  //menu_layout->addWidget(new LqrKi());
  //menu_layout->addWidget(new DcGain());   
}


void  CTunWidget::FrameTOROUE(QWidget *parent)
{
//  QFrame  *pFrame = CreateFrame(3); 
 // QVBoxLayout *menu_layout = new QVBoxLayout(pFrame);  

  //menu_layout->addWidget(new TorqueMaxLatAccel());
  //menu_layout->addWidget(new TorqueKp());
  //menu_layout->addWidget(new TorqueKf());
  //menu_layout->addWidget(new TorqueKi());
  //menu_layout->addWidget(new TorqueFriction());
  //menu_layout->addWidget(new TorqueUseAngle());
}

void  CTunWidget::FrameHYBRID(QWidget *parent)
{
 // QFrame  *pFrame = CreateFrame(4); 
 // QVBoxLayout *menu_layout = new QVBoxLayout(pFrame);  

}


QFrame *CTunWidget::CreateFrame( int nID )
{
  QFrame  *pFrame = new QFrame(); 
  m_pChildFrame[nID] = pFrame;
  pFrame->setContentsMargins(40, 10, 40, 50);
  pFrame->setStyleSheet(R"(
    * {
      padding: 0;
      border-radius: 50px;
      font-size: 35px;
      font-weight: 500;
      color: #E4E4E4;
      background-color: black;
    } 
  )");
  
  main_layout->addWidget(pFrame);

  return  pFrame;
}

void  CTunWidget::FrameHide( int nID )
{
  for( int i = 0; i<10; i++ )
  {
    if( nID >= 0 && i != nID ) continue; 
    if( m_pChildFrame[i] )
      m_pChildFrame[i]->hide();
  }
}


void  CTunWidget::FrameShow( int nID )
{
  for( int i = 0; i<10; i++ )
  {
    if( i != nID ) continue;
    if( m_pChildFrame[i] )
      m_pChildFrame[i]->show();
  }
}


void CTunWidget::showEvent(QShowEvent *event) 
{
  refresh();
}

void CTunWidget::hideEvent(QHideEvent *event) 
{
  m_bShow = 0;
  refresh();
}

void CTunWidget::refresh() 
{
  QString str;

  switch( m_nMethod )
  {
    case 0 : str = "0.PID"; break;
    case 1 : str = "1.INDI"; break;
    case 2 : str = "2.LQR";  break;
    case 3 : str = "3.TORQUE";  break;
    case 4 : str = "4.HYBRID";  break;
    case 5 : str = "5.MULTI";  break;
    default: str = "None"; break;
  }


  method_label->setText( str );


  if(  m_bShow == 0 )
  {
    FrameHide();
    icon_label->setPixmap(pix_plus);
  }
  else
  {
    FrameHide();
    FrameShow( m_nMethod );
    icon_label->setPixmap(pix_minus);
  }

}



