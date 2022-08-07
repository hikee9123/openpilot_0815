
#include <QDialog>
#include <QDateTime>
#include <QHBoxLayout>
#include <QMouseEvent>
#include <QVBoxLayout>

#include "selfdrive/ui/qt/atom/widgets/osmWidget.h"



COSMWidget::COSMWidget() : CGroupWidget( "OSM Enable" ) 
{
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
    //params.put( str_param.toStdString(), values.toStdString());      
    refresh();
  });
  main_layout->addLayout(hlayout);

  //FramePID( CreateBoxLayout(TP_NONE) );

}  

/*
void  COSMWidget::FramePID(QVBoxLayout *layout)
{
  // QVBoxLayout *pBoxLayout = CreateBoxLayout(TP_NONE);

    layout->addWidget(new PidKp());
    layout->addWidget(new PidKi());
    layout->addWidget(new PidKd());
    layout->addWidget(new PidKf());
}
*/


void COSMWidget::refresh( int nID )
{
  CGroupWidget::refresh( m_nMethod );
 

  QString  str;
  switch( m_nMethod )
  {
    case TP_NONE : str = "0.미사용"; break;
    case TP_USES : str = "1.사용";  break;
  }

  method_label->setText( str ); 
}