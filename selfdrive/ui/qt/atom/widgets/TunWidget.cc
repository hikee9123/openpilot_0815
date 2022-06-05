
#include <QDialog>
#include <QDateTime>
#include <QHBoxLayout>
#include <QMouseEvent>
#include <QVBoxLayout>

#include "selfdrive/ui/qt/atom/widgets/TunWidget.h"



CTunWidget::CTunWidget(QWidget *parent) : QFrame(parent) 
{
  m_bShow = 0;

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


  FrameSmooth( parent );
  FrameNormal( parent );


  main_layout->addStretch();
  refresh();
}

CTunWidget::~CTunWidget()
{

}


void CTunWidget::FrameSmooth(QWidget *parent) 
{
 // 1. layer#1 menu
  m_pChildFrame1 = new QFrame(); 
  m_pChildFrame1->setContentsMargins(40, 10, 40, 50);
  m_pChildFrame1->setStyleSheet(R"(
    * {
      padding: 0;
      border-radius: 50px;
      font-size: 35px;
      font-weight: 500;
      color: #E4E4E4;
      background-color: black;
    } 
  )");
  
  main_layout->addWidget(m_pChildFrame1);


  QVBoxLayout *menu_layout = new QVBoxLayout(m_pChildFrame1);
 // menu_layout->setContentsMargins(32, 5, 32, 32);


  MenuControl *pMenu1 = new MenuControl( 
    "OpkrMaxSteeringAngle",
    "Driver to Steer Angle",
    "mprove the edge between the driver and the openpilot.",
    "../assets/offroad/icon_shell.png"    
    );
  pMenu1->SetControl( 10, 180, 5 );
  menu_layout->addWidget( pMenu1 );

  
   MenuControl *pMenu2 = new MenuControl( 
    "OpkrMaxDriverAngleWait",
    "Driver to Steer",
    "Controls smooth torque by the driver  From OpkrMaxSteeringAngle. def:0.002(5sec)",
    "../assets/offroad/icon_shell.png"    
    );
  pMenu2->SetControl( 0, 1, 0.001 );
  pMenu2->SetString( 0, "Not");
  menu_layout->addWidget( pMenu2 ); 


   MenuControl *pMenu3 = new MenuControl( 
    "OpkrMaxSteerAngleWait" ,
    "Steer angle",
    "Controls torque by steering angle From OpkrMaxSteeringAngle. def:0.001(10sec)",
    "../assets/offroad/icon_shell.png"    
    );
  pMenu3->SetControl( 0, 1, 0.001 );
  pMenu3->SetString( 0, "Not");
  menu_layout->addWidget( pMenu3 ); 

   MenuControl *pMenu4 = new MenuControl( 
    "OpkrDriverAngleWait" ,
    "Normal driver to Steer",
    "Controls torque limitation due to normal driver handle intervention. def:0.001(10sec)",
    "../assets/offroad/icon_shell.png"
    );
  pMenu4->SetControl( 0, 1, 0.001 );
  pMenu4->SetString( 0, "Not");
  menu_layout->addWidget( pMenu4 ); 

}

void CTunWidget::FrameNormal(QWidget *parent) 
{
 // 1. layer#2 menu
  m_pChildFrame2 = new QFrame(); 
  m_pChildFrame2->setContentsMargins(40, 10, 40, 50);
  m_pChildFrame2->setStyleSheet(R"(
    * {
      padding: 0;
      border-radius: 50px;
      font-size: 35px;
      font-weight: 500;
      color: #E4E4E4;
      background-color: black;
    } 
  )");
  
  main_layout->addWidget(m_pChildFrame2);
  QVBoxLayout *menu_layout = new QVBoxLayout(m_pChildFrame2);  
  MenuControl *pMenu1 = new MenuControl( 
    "OpkrMaxAngleLimit",
    "Max Steering Angle",
    "Set the maximum steering angle of the handle where the openpilot is possible. Please note that some vehicles may experience errors if the angle is set above 90 degrees."
    //"../assets/offroad/icon_chevron_right.png"    
    );
  pMenu1->SetControl( 80, 360, 10 );
  pMenu1->SetString( 80, "NoLimit");
  menu_layout->addWidget( pMenu1 );
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
    // pmyWidget->setVisible(false);
    m_pChildFrame1->hide();
    m_pChildFrame2->hide();
    icon_label->setPixmap(pix_plus);
  }
  else
  {
     if( m_nMethod == 0 )
     {
       m_pChildFrame2->show();
        m_pChildFrame1->hide();
     }
     else
     {
       m_pChildFrame1->show();
       m_pChildFrame2->hide();
     }

    
    icon_label->setPixmap(pix_minus);
    //pmyWidget->setVisible(true);
  }

}



