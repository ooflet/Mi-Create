# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'window.ui'
##
## Created by: Qt User Interface Compiler version 6.6.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from coreGettext import QCoreApplication

from PySide6.QtCore import (QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QDockWidget, QFrame, QGridLayout,
    QHeaderView, QLabel, QMainWindow, QMenu,
    QMenuBar, QSizePolicy, QSpacerItem, QStatusBar,
    QTabWidget, QToolBar, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1050, 700)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QSize(550, 550))
        icon = QIcon()
        icon.addFile(u":/Images/MiCreate48x48.png", QSize(), QIcon.Normal, QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setAnimated(True)
        MainWindow.setTabShape(QTabWidget.Rounded)
        self.actionSave = QAction(MainWindow)
        self.actionSave.setObjectName(u"actionSave")
        icon1 = QIcon()
        icon1.addFile(u":/Dark/save.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionSave.setIcon(icon1)
        self.actionSave_as = QAction(MainWindow)
        self.actionSave_as.setObjectName(u"actionSave_as")
        self.actionAbout_MiFaceStudio = QAction(MainWindow)
        self.actionAbout_MiFaceStudio.setObjectName(u"actionAbout_MiFaceStudio")
        self.actionPreferences = QAction(MainWindow)
        self.actionPreferences.setObjectName(u"actionPreferences")
        self.actionBuild = QAction(MainWindow)
        self.actionBuild.setObjectName(u"actionBuild")
        icon2 = QIcon()
        icon2.addFile(u":/Dark/package.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionBuild.setIcon(icon2)
        self.actionExplorer = QAction(MainWindow)
        self.actionExplorer.setObjectName(u"actionExplorer")
        self.actionExplorer.setCheckable(True)
        self.actionExplorer.setChecked(True)
        self.actionAttributes = QAction(MainWindow)
        self.actionAttributes.setObjectName(u"actionAttributes")
        self.actionAttributes.setCheckable(True)
        self.actionAttributes.setChecked(True)
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        self.actionEdit = QAction(MainWindow)
        self.actionEdit.setObjectName(u"actionEdit")
        self.actionEdit.setCheckable(True)
        self.actionEdit.setChecked(True)
        self.actionFile = QAction(MainWindow)
        self.actionFile.setObjectName(u"actionFile")
        self.actionFile.setCheckable(True)
        self.actionFile.setChecked(True)
        self.actionLayout = QAction(MainWindow)
        self.actionLayout.setObjectName(u"actionLayout")
        self.actionLayout.setCheckable(True)
        self.actionLayout.setChecked(True)
        self.actionNewFile = QAction(MainWindow)
        self.actionNewFile.setObjectName(u"actionNewFile")
        icon3 = QIcon()
        icon3.addFile(u":/Dark/file-plus.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionNewFile.setIcon(icon3)
        self.actionOpenFile = QAction(MainWindow)
        self.actionOpenFile.setObjectName(u"actionOpenFile")
        icon4 = QIcon()
        icon4.addFile(u":/Dark/folder-open.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionOpenFile.setIcon(icon4)
        self.actionUndo = QAction(MainWindow)
        self.actionUndo.setObjectName(u"actionUndo")
        icon5 = QIcon()
        icon5.addFile(u":/Dark/undo-2.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionUndo.setIcon(icon5)
        self.actionUndo.setMenuRole(QAction.NoRole)
        self.actionRedo = QAction(MainWindow)
        self.actionRedo.setObjectName(u"actionRedo")
        icon6 = QIcon()
        icon6.addFile(u":/Dark/redo-2.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionRedo.setIcon(icon6)
        self.actionRedo.setMenuRole(QAction.NoRole)
        self.actionAbout_Qt = QAction(MainWindow)
        self.actionAbout_Qt.setObjectName(u"actionAbout_Qt")
        self.actionThirdPartyNotice = QAction(MainWindow)
        self.actionThirdPartyNotice.setObjectName(u"actionThirdPartyNotice")
        self.actionUnpack = QAction(MainWindow)
        self.actionUnpack.setObjectName(u"actionUnpack")
        icon7 = QIcon()
        icon7.addFile(u":/Dark/package-open.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionUnpack.setIcon(icon7)
        self.actionCut = QAction(MainWindow)
        self.actionCut.setObjectName(u"actionCut")
        icon8 = QIcon()
        icon8.addFile(u":/Dark/scissors.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionCut.setIcon(icon8)
        self.actionCopy = QAction(MainWindow)
        self.actionCopy.setObjectName(u"actionCopy")
        icon9 = QIcon()
        icon9.addFile(u":/Dark/copy(1).png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionCopy.setIcon(icon9)
        self.actionPaste = QAction(MainWindow)
        self.actionPaste.setObjectName(u"actionPaste")
        icon10 = QIcon()
        icon10.addFile(u":/Dark/clipboard-paste.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionPaste.setIcon(icon10)
        self.actionProject_XML_File = QAction(MainWindow)
        self.actionProject_XML_File.setObjectName(u"actionProject_XML_File")
        icon11 = QIcon()
        icon11.addFile(u":/Dark/file-code-2.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionProject_XML_File.setIcon(icon11)
        self.actionResize_Images = QAction(MainWindow)
        self.actionResize_Images.setObjectName(u"actionResize_Images")
        self.actionImage = QAction(MainWindow)
        self.actionImage.setObjectName(u"actionImage")
        icon12 = QIcon()
        icon12.addFile(u":/Dark/image.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionImage.setIcon(icon12)
        self.actionImage_List = QAction(MainWindow)
        self.actionImage_List.setObjectName(u"actionImage_List")
        icon13 = QIcon()
        icon13.addFile(u":/Dark/gallery-horizontal.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionImage_List.setIcon(icon13)
        self.actionDigital_Number = QAction(MainWindow)
        self.actionDigital_Number.setObjectName(u"actionDigital_Number")
        icon14 = QIcon()
        icon14.addFile(u":/Dark/numbers.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionDigital_Number.setIcon(icon14)
        self.actionAnalog_Display = QAction(MainWindow)
        self.actionAnalog_Display.setObjectName(u"actionAnalog_Display")
        icon15 = QIcon()
        icon15.addFile(u":/Dark/analog.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionAnalog_Display.setIcon(icon15)
        self.actionArc_Progress = QAction(MainWindow)
        self.actionArc_Progress.setObjectName(u"actionArc_Progress")
        icon16 = QIcon()
        icon16.addFile(u":/Dark/progress.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionArc_Progress.setIcon(icon16)
        self.actionDocumentation = QAction(MainWindow)
        self.actionDocumentation.setObjectName(u"actionDocumentation")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy1)
        self.centralwidget.setMinimumSize(QSize(200, 0))
        self.gridLayout_2 = QGridLayout(self.centralwidget)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(6, 4, 0, 0)
        self.workspace = QTabWidget(self.centralwidget)
        self.workspace.setObjectName(u"workspace")
        self.workspace.setDocumentMode(False)
        self.workspace.setTabsClosable(True)
        self.workspace.setMovable(True)
        self.Welcome = QWidget()
        self.Welcome.setObjectName(u"Welcome")
        self.gridLayout_3 = QGridLayout(self.Welcome)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(32, -1, -1, -1)
        self.OpenProject = QLabel(self.Welcome)
        self.OpenProject.setObjectName(u"OpenProject")

        self.gridLayout_3.addWidget(self.OpenProject, 3, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 176, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_3.addItem(self.verticalSpacer, 4, 0, 1, 1)

        self.WelcomeText = QLabel(self.Welcome)
        self.WelcomeText.setObjectName(u"WelcomeText")
        self.WelcomeText.setStyleSheet(u"QLabel { font-size: 18pt;}")

        self.gridLayout_3.addWidget(self.WelcomeText, 1, 0, 1, 1)

        self.NewProject = QLabel(self.Welcome)
        self.NewProject.setObjectName(u"NewProject")

        self.gridLayout_3.addWidget(self.NewProject, 2, 0, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 177, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_3.addItem(self.verticalSpacer_2, 0, 0, 1, 1)

        icon17 = QIcon()
        icon17.addFile(u":/Dark/MiFaceStudioFavicon.png", QSize(), QIcon.Normal, QIcon.Off)
        self.workspace.addTab(self.Welcome, icon17, "")

        self.gridLayout_2.addWidget(self.workspace, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1050, 22))
        self.menubar.setContextMenuPolicy(Qt.NoContextMenu)
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        self.menuAbout = QMenu(self.menuHelp)
        self.menuAbout.setObjectName(u"menuAbout")
        self.menuView = QMenu(self.menubar)
        self.menuView.setObjectName(u"menuView")
        self.menuToolbars = QMenu(self.menuView)
        self.menuToolbars.setObjectName(u"menuToolbars")
        self.menuEdit = QMenu(self.menubar)
        self.menuEdit.setObjectName(u"menuEdit")
        self.menuTools = QMenu(self.menubar)
        self.menuTools.setObjectName(u"menuTools")
        self.menuInsert = QMenu(self.menubar)
        self.menuInsert.setObjectName(u"menuInsert")
        self.menuInsert.setTearOffEnabled(False)
        MainWindow.setMenuBar(self.menubar)
        self.explorerWidget = QDockWidget(MainWindow)
        self.explorerWidget.setObjectName(u"explorerWidget")
        self.explorerWidget.setMinimumSize(QSize(300, 150))
        self.explorerWidget.setStyleSheet(u"")
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setObjectName(u"dockWidgetContents")
        self.verticalLayout = QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.Explorer = QTreeWidget(self.dockWidgetContents)
        self.Explorer.setObjectName(u"Explorer")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.Explorer.sizePolicy().hasHeightForWidth())
        self.Explorer.setSizePolicy(sizePolicy2)
        self.Explorer.setFrameShape(QFrame.NoFrame)
        self.Explorer.setUniformRowHeights(True)
        self.Explorer.setHeaderHidden(True)

        self.verticalLayout.addWidget(self.Explorer)

        self.explorerWidget.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(Qt.RightDockWidgetArea, self.explorerWidget)
        self.propertiesWidget = QDockWidget(MainWindow)
        self.propertiesWidget.setObjectName(u"propertiesWidget")
        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.propertiesWidget.sizePolicy().hasHeightForWidth())
        self.propertiesWidget.setSizePolicy(sizePolicy3)
        self.propertiesWidget.setMinimumSize(QSize(300, 150))
        self.propertiesWidget.setStyleSheet(u"")
        self.dockWidgetContents_2 = QWidget()
        self.dockWidgetContents_2.setObjectName(u"dockWidgetContents_2")
        self.gridLayout = QGridLayout(self.dockWidgetContents_2)
        self.gridLayout.setObjectName(u"gridLayout")
        self.propertiesWidget.setWidget(self.dockWidgetContents_2)
        MainWindow.addDockWidget(Qt.RightDockWidgetArea, self.propertiesWidget)
        self.fileToolbar = QToolBar(MainWindow)
        self.fileToolbar.setObjectName(u"fileToolbar")
        self.fileToolbar.setMovable(True)
        self.fileToolbar.setIconSize(QSize(18, 18))
        self.fileToolbar.setToolButtonStyle(Qt.ToolButtonIconOnly)
        MainWindow.addToolBar(Qt.TopToolBarArea, self.fileToolbar)
        self.statusBar = QStatusBar(MainWindow)
        self.statusBar.setObjectName(u"statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.actionsToolbar = QToolBar(MainWindow)
        self.actionsToolbar.setObjectName(u"actionsToolbar")
        self.actionsToolbar.setIconSize(QSize(18, 18))
        MainWindow.addToolBar(Qt.TopToolBarArea, self.actionsToolbar)
        self.toolBar = QToolBar(MainWindow)
        self.toolBar.setObjectName(u"toolBar")
        self.toolBar.setIconSize(QSize(18, 18))
        MainWindow.addToolBar(Qt.TopToolBarArea, self.toolBar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuInsert.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuTools.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionNewFile)
        self.menuFile.addAction(self.actionOpenFile)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSave_as)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuHelp.addAction(self.actionDocumentation)
        self.menuHelp.addSeparator()
        self.menuHelp.addAction(self.menuAbout.menuAction())
        self.menuAbout.addAction(self.actionAbout_MiFaceStudio)
        self.menuAbout.addAction(self.actionAbout_Qt)
        self.menuAbout.addAction(self.actionThirdPartyNotice)
        self.menuView.addAction(self.actionExplorer)
        self.menuView.addAction(self.actionAttributes)
        self.menuView.addSeparator()
        self.menuView.addAction(self.menuToolbars.menuAction())
        self.menuToolbars.addAction(self.actionEdit)
        self.menuToolbars.addAction(self.actionFile)
        self.menuToolbars.addAction(self.actionLayout)
        self.menuEdit.addAction(self.actionUndo)
        self.menuEdit.addAction(self.actionRedo)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionCut)
        self.menuEdit.addAction(self.actionCopy)
        self.menuEdit.addAction(self.actionPaste)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionProject_XML_File)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionPreferences)
        self.menuTools.addAction(self.actionBuild)
        self.menuTools.addAction(self.actionUnpack)
        self.menuTools.addSeparator()
        self.menuInsert.addAction(self.actionImage)
        self.menuInsert.addAction(self.actionImage_List)
        self.menuInsert.addSeparator()
        self.menuInsert.addAction(self.actionDigital_Number)
        self.menuInsert.addAction(self.actionAnalog_Display)
        self.menuInsert.addAction(self.actionArc_Progress)
        self.fileToolbar.addAction(self.actionNewFile)
        self.fileToolbar.addAction(self.actionOpenFile)
        self.fileToolbar.addAction(self.actionSave)
        self.actionsToolbar.addAction(self.actionUndo)
        self.actionsToolbar.addAction(self.actionRedo)
        self.actionsToolbar.addAction(self.actionCut)
        self.actionsToolbar.addAction(self.actionCopy)
        self.actionsToolbar.addAction(self.actionPaste)
        self.toolBar.addAction(self.actionBuild)

        self.retranslateUi(MainWindow)

        self.workspace.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Mi Create", None))
        self.actionSave.setText(QCoreApplication.translate("MainWindow", u"Save...", None))
#if QT_CONFIG(shortcut)
        self.actionSave.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+S", None))
#endif // QT_CONFIG(shortcut)
        self.actionSave_as.setText(QCoreApplication.translate("MainWindow", u"Save as...", None))
#if QT_CONFIG(shortcut)
        self.actionSave_as.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Shift+S", None))
#endif // QT_CONFIG(shortcut)
        self.actionAbout_MiFaceStudio.setText(QCoreApplication.translate("MainWindow", u"About Mi Create", None))
        self.actionPreferences.setText(QCoreApplication.translate("MainWindow", u"Settings", None))
#if QT_CONFIG(shortcut)
        self.actionPreferences.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+P", None))
#endif // QT_CONFIG(shortcut)
        self.actionBuild.setText(QCoreApplication.translate("MainWindow", u"Build...", None))
#if QT_CONFIG(tooltip)
        self.actionBuild.setToolTip(QCoreApplication.translate("MainWindow", u"Build", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.actionBuild.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+K", None))
#endif // QT_CONFIG(shortcut)
        self.actionExplorer.setText(QCoreApplication.translate("MainWindow", u"Explorer", None))
        self.actionAttributes.setText(QCoreApplication.translate("MainWindow", u"Attributes", None))
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
        self.actionEdit.setText(QCoreApplication.translate("MainWindow", u"Edit", None))
        self.actionFile.setText(QCoreApplication.translate("MainWindow", u"File", None))
        self.actionLayout.setText(QCoreApplication.translate("MainWindow", u"Layout", None))
        self.actionNewFile.setText(QCoreApplication.translate("MainWindow", u"New...", None))
#if QT_CONFIG(tooltip)
        self.actionNewFile.setToolTip(QCoreApplication.translate("MainWindow", u"New File", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.actionNewFile.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+N", None))
#endif // QT_CONFIG(shortcut)
        self.actionOpenFile.setText(QCoreApplication.translate("MainWindow", u"Open...", None))
#if QT_CONFIG(tooltip)
        self.actionOpenFile.setToolTip(QCoreApplication.translate("MainWindow", u"Open File", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.actionOpenFile.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+O", None))
#endif // QT_CONFIG(shortcut)
        self.actionUndo.setText(QCoreApplication.translate("MainWindow", u"Undo", None))
#if QT_CONFIG(shortcut)
        self.actionUndo.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Z", None))
#endif // QT_CONFIG(shortcut)
        self.actionRedo.setText(QCoreApplication.translate("MainWindow", u"Redo", None))
#if QT_CONFIG(shortcut)
        self.actionRedo.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Y", None))
#endif // QT_CONFIG(shortcut)
        self.actionAbout_Qt.setText(QCoreApplication.translate("MainWindow", u"About Qt", None))
        self.actionThirdPartyNotice.setText(QCoreApplication.translate("MainWindow", u"Third Party Notices", None))
        self.actionUnpack.setText(QCoreApplication.translate("MainWindow", u"Unpack...", None))
        self.actionCut.setText(QCoreApplication.translate("MainWindow", u"Cut", None))
#if QT_CONFIG(shortcut)
        self.actionCut.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+X", None))
#endif // QT_CONFIG(shortcut)
        self.actionCopy.setText(QCoreApplication.translate("MainWindow", u"Copy", None))
#if QT_CONFIG(shortcut)
        self.actionCopy.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+C", None))
#endif // QT_CONFIG(shortcut)
        self.actionPaste.setText(QCoreApplication.translate("MainWindow", u"Paste", None))
#if QT_CONFIG(shortcut)
        self.actionPaste.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+V", None))
#endif // QT_CONFIG(shortcut)
        self.actionProject_XML_File.setText(QCoreApplication.translate("MainWindow", u"Project Source Code", None))
        self.actionResize_Images.setText(QCoreApplication.translate("MainWindow", u"Resize Images", None))
        self.actionImage.setText(QCoreApplication.translate("MainWindow", u"Image", None))
        self.actionImage_List.setText(QCoreApplication.translate("MainWindow", u"Image List", None))
        self.actionDigital_Number.setText(QCoreApplication.translate("MainWindow", u"Digital Number", None))
        self.actionAnalog_Display.setText(QCoreApplication.translate("MainWindow", u"Analog Display", None))
        self.actionArc_Progress.setText(QCoreApplication.translate("MainWindow", u"Arc Progress", None))
        self.actionDocumentation.setText(QCoreApplication.translate("MainWindow", u"Documentation", None))
#if QT_CONFIG(shortcut)
        self.actionDocumentation.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+H", None))
#endif // QT_CONFIG(shortcut)
        self.OpenProject.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><img src=\":/Dark/folder-open.png\"/> <a href=\"\\&quot;\\&quot;\"><span style=\" text-decoration: underline; color:#55aaff;\">Open Project...</span></a></p></body></html>", None))
        self.WelcomeText.setText(QCoreApplication.translate("MainWindow", u"Welcome", None))
        self.NewProject.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><img src=\":/Dark/file-plus.png\"/> <a href=\"\\&quot;\\&quot;\"><span style=\" text-decoration: underline; color:#55aaff;\">New Project...</span></a></p></body></html>", None))
        self.workspace.setTabText(self.workspace.indexOf(self.Welcome), QCoreApplication.translate("MainWindow", u"Welcome", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
        self.menuAbout.setTitle(QCoreApplication.translate("MainWindow", u"About", None))
        self.menuView.setTitle(QCoreApplication.translate("MainWindow", u"View", None))
        self.menuToolbars.setTitle(QCoreApplication.translate("MainWindow", u"Toolbars", None))
        self.menuEdit.setTitle(QCoreApplication.translate("MainWindow", u"Edit", None))
        self.menuTools.setTitle(QCoreApplication.translate("MainWindow", u"Tools", None))
        self.menuInsert.setTitle(QCoreApplication.translate("MainWindow", u"Create", None))
        self.explorerWidget.setWindowTitle(QCoreApplication.translate("MainWindow", u"Explorer", None))
        ___qtreewidgetitem = self.Explorer.headerItem()
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("MainWindow", u"Project", None));
        self.propertiesWidget.setWindowTitle(QCoreApplication.translate("MainWindow", u"Properties", None))
        self.fileToolbar.setWindowTitle(QCoreApplication.translate("MainWindow", u"File Toolbar", None))
        self.actionsToolbar.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar_2", None))
        self.toolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar", None))
    # retranslateUi

