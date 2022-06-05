

#pragma once

#include <QFrame>
#include <QLabel>
#include <QPushButton>
#include <QStackedLayout>
#include <QTimer>
#include <QWidget>

#include "selfdrive/ui/qt/widgets/controls.h"
#include "selfdrive/ui/ui.h"



class CTunWidget : public QFrame 
{
  Q_OBJECT

public:
  explicit CTunWidget(QWidget *parent = 0);
  ~CTunWidget();

  enum LayoutID {
    LID_PID = 0,
    LID_INDI,
    LID_LQR,
    LID_TOROUE,
    LID_HYBRID,
    LID_MULTI,
    LID_DEFAULT,
    LID_ALL,
  };

private:
  void showEvent(QShowEvent *event) override;
  void hideEvent(QHideEvent *event) override;

public slots:  
  void refresh();


private:
  void  FramePID(QVBoxLayout *parent=nullptr);
  void  FrameINDI(QVBoxLayout *parent=nullptr);
  void  FrameLQR(QVBoxLayout *parent=nullptr);
  void  FrameTOROUE(QVBoxLayout *parent=nullptr);
  void  FrameHYBRID(QVBoxLayout *parent=nullptr);

  void  FrameHide( int nID = -1 );
  void  FrameShow( int nID );
  QVBoxLayout *CreateBoxLayout( int nID );

 private:
  Params params; 
  QLabel *icon_label;
  QPixmap  pix_plus;
  QPixmap  pix_minus;


  QVBoxLayout *main_layout;
  QPushButton *title_label;
  QHBoxLayout *hlayout;
  QLabel *description = nullptr;  


  QPushButton  *method_label;
  int    m_nMethod;
  int    m_bShow;




   QFrame *m_pChildFrame[LID_ALL];


};

