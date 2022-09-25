#include "selfdrive/ui/qt/offroad/settings.h"

#include <cassert>
#include <cmath>
#include <string>

#include <QDebug>
#include <QLabel>

#include "common/params.h"
#include "common/util.h"
#include "selfdrive/ui/ui.h"
#include "selfdrive/ui/qt/util.h"
#include "selfdrive/ui/qt/widgets/controls.h"
#include "selfdrive/ui/qt/widgets/input.h"
#include "selfdrive/hardware/hw.h"


SoftwarePanel::SoftwarePanel(QWidget* parent) : ListWidget(parent) {
  gitRemoteLbl = new LabelControl(tr("Git Remote"));
  gitBranchLbl = new LabelControl(tr("Git Branch"));
  gitCommitLbl = new LabelControl(tr("Git Commit"));
  osVersionLbl = new LabelControl(tr("OS Version"));
  versionLbl = new LabelControl(tr("Version"), "", QString::fromStdString(params.get("ReleaseNotes")).trimmed());
  lastUpdateLbl = new LabelControl(tr("Last Update Check"), "", tr("The last time openpilot successfully checked for an update. The updater only runs while the car is off."));
  updateBtn = new ButtonControl(tr("Check for Update"), "");
  connect(updateBtn, &ButtonControl::clicked, [=]() {
    if (params.getBool("IsOffroad")) {
      fs_watch->addPath(QString::fromStdString(params.getParamPath("LastUpdateTime")));
      fs_watch->addPath(QString::fromStdString(params.getParamPath("UpdateFailedCount")));
      updateBtn->setText(tr("CHECKING"));
      updateBtn->setEnabled(false);
    }
    std::system("pkill -1 -f selfdrive.updated");
  });

  connect(uiState(), &UIState::offroadTransition, updateBtn, &QPushButton::setEnabled);

  branchSwitcherBtn = new ButtonControl(tr("Switch Branch"), tr("ENTER"), tr("The new branch will be pulled the next time the updater runs."));
  connect(branchSwitcherBtn, &ButtonControl::clicked, [=]() {
    QString branch = InputDialog::getText(tr("Enter branch name"), this, tr("The new branch will be pulled the next time the updater runs."),
                                          false, -1, QString::fromStdString(params.get("SwitchToBranch")));
    if (branch.isEmpty()) {
      params.remove("SwitchToBranch");
    } else {
      params.put("SwitchToBranch", branch.toStdString());
    }
    std::system("pkill -1 -f selfdrive.updated");
  });
  connect(uiState(), &UIState::offroadTransition, branchSwitcherBtn, &QPushButton::setEnabled);


  auto uninstallBtn = new ButtonControl(tr("Uninstall ") + getBrand(), tr("UNINSTALL"));
  connect(uninstallBtn, &ButtonControl::clicked, [&]() {
    if (ConfirmationDialog::confirm(tr("Are you sure you want to uninstall?"), this)) {
      params.putBool("DoUninstall", true);
    }
  });
  connect(uiState(), &UIState::offroadTransition, uninstallBtn, &QPushButton::setEnabled);

  QWidget *widgets[] = {versionLbl, lastUpdateLbl, updateBtn, branchSwitcherBtn, gitRemoteLbl, gitBranchLbl, gitCommitLbl, osVersionLbl, uninstallBtn};
  for (QWidget* w : widgets) {
    if (w == branchSwitcherBtn && params.getBool("IsTestedBranch")) {
      continue;
    }    
    addItem(w);
  }

  fs_watch = new QFileSystemWatcher(this);
  QObject::connect(fs_watch, &QFileSystemWatcher::fileChanged, [=](const QString path) {
    if (path.contains("UpdateFailedCount") && std::atoi(params.get("UpdateFailedCount").c_str()) > 0) {
      lastUpdateLbl->setText(tr("failed to fetch update"));
      updateBtn->setText(tr("CHECK"));
      updateBtn->setEnabled(true);
    } else if (path.contains("LastUpdateTime")) {
      updateLabels();
    }
  });
}

void SoftwarePanel::showEvent(QShowEvent *event) {
  updateLabels();
}

void SoftwarePanel::updateLabels() {
  QString lastUpdate = "";
  auto tm = params.get("LastUpdateTime");
  if (!tm.empty()) {
    lastUpdate = timeAgo(QDateTime::fromString(QString::fromStdString(tm + "Z"), Qt::ISODate));
  }

  versionLbl->setText(getBrandVersion());
  lastUpdateLbl->setText(lastUpdate);
  updateBtn->setText(tr("CHECK"));
  updateBtn->setEnabled(true);
  gitRemoteLbl->setText(QString::fromStdString(params.get("GitRemote").substr(19)));  
  gitBranchLbl->setText(QString::fromStdString(params.get("GitBranch")));
  gitCommitLbl->setText(QString::fromStdString(params.get("GitCommit")).left(10));
  osVersionLbl->setText(QString::fromStdString(Hardware::get_os_version()).trimmed());
}
