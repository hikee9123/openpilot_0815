

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

private:
  void showEvent(QShowEvent *event) override;
  void hideEvent(QHideEvent *event) override;

public slots:  
  void refresh();


private:
  void  FramePID(QWidget *parent);
  void  FrameINDI(QWidget *parent);
  void  FrameLQR(QWidget *parent);
  void  FrameTOROUE(QWidget *parent);
  void  FrameHYBRID(QWidget *parent);

  void  FrameHide( int nID = -1 );
  void  FrameShow( int nID );
  QFrame *CreateFrame( int nID );

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

   QFrame *m_pChildFrame[10];


};

