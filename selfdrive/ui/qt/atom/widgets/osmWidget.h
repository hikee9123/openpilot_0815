

#pragma once

#include <QFrame>
#include <QLabel>
#include <QPushButton>
#include <QStackedLayout>
#include <QTimer>
#include <QWidget>

//#include "selfdrive/ui/qt/widgets/controls.h"
//#include "selfdrive/ui/ui.h"

#include "selfdrive/ui/qt/atom/TuningPanel.h"
#include "selfdrive/ui/qt/widgets/groupWidget.h"



class CosmWidget : public CGroupWidget 
{
  Q_OBJECT

public:
  explicit CosmWidget( TuningPanel *panel );

  enum emType {
    TP_NONE = 0,
    TP_USES,
    TP_ALL,
  };  

 private:
  TuningPanel  *m_pPanel;
  QPushButton  *method_label;
  int    m_nMethod;
  Params params;
  
  void  FrameOSM(QVBoxLayout *parent=nullptr);
//  void  FrameINDI(QVBoxLayout *parent=nullptr);
//  void  FrameLQR(QVBoxLayout *parent=nullptr);
//  void  FrameTORQUE(QVBoxLayout *parent=nullptr);
//  void  FrameMULTI(QVBoxLayout *parent=nullptr);

  

public slots:  
  virtual void refresh(int nID = 0);  
};



class CWidgetosmConfig : public CGroupWidget 
{
  Q_OBJECT

public:
  explicit CWidgetosmConfig( TuningPanel *panel );

  enum emType {
    TP_NONE = 0,
    TP_USES,
    TP_ALL,
  };  

 private:
  TuningPanel  *m_pPanel;
  QPushButton  *method_label;
  int    m_nMethod;
  Params params;
  
  void  FrameOSM(QVBoxLayout *parent=nullptr);

  

public slots:  
  virtual void refresh(int nID = 0);  
};



class CWidgetosmNodesData : public CGroupWidget 
{
  Q_OBJECT

public:
  explicit CWidgetosmNodesData( TuningPanel *panel );

  enum emType {
    TP_NONE = 0,
    TP_USES,
    TP_ALL,
  };  

 private:
  TuningPanel  *m_pPanel;
  QPushButton  *method_label;
  int    m_nMethod;
  Params params;
  
  void  FrameOSM(QVBoxLayout *parent=nullptr);

  

public slots:  
  virtual void refresh(int nID = 0);  
};
