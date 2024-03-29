# Form implementation generated from reading ui file 'c:\Users\Justin\Mi-Create\src\window.ui'
#
# Created by: PyQt6 UI code generator 6.6.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets
from translate import QCoreApplication

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1049, 700)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(550, 550))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/Images/MiCreate48x48.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setAnimated(True)
        MainWindow.setTabShape(QtWidgets.QTabWidget.TabShape.Rounded)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setMinimumSize(QtCore.QSize(200, 0))
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setContentsMargins(0, 4, 0, 0)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.workspace = QtWidgets.QTabWidget(parent=self.centralwidget)
        self.workspace.setDocumentMode(False)
        self.workspace.setTabsClosable(True)
        self.workspace.setMovable(True)
        self.workspace.setObjectName("workspace")
        self.gridLayout_2.addWidget(self.workspace, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1049, 22))
        self.menubar.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.NoContextMenu)
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(parent=self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuHelp = QtWidgets.QMenu(parent=self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        self.menuAbout = QtWidgets.QMenu(parent=self.menuHelp)
        self.menuAbout.setObjectName("menuAbout")
        self.menuView = QtWidgets.QMenu(parent=self.menubar)
        self.menuView.setObjectName("menuView")
        self.menuToolbars = QtWidgets.QMenu(parent=self.menuView)
        self.menuToolbars.setObjectName("menuToolbars")
        self.menuZoom = QtWidgets.QMenu(parent=self.menuView)
        self.menuZoom.setObjectName("menuZoom")
        self.menuEdit = QtWidgets.QMenu(parent=self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        self.menuLayers = QtWidgets.QMenu(parent=self.menuEdit)
        self.menuLayers.setObjectName("menuLayers")
        self.menuTools = QtWidgets.QMenu(parent=self.menubar)
        self.menuTools.setObjectName("menuTools")
        self.menuInsert = QtWidgets.QMenu(parent=self.menubar)
        self.menuInsert.setTearOffEnabled(False)
        self.menuInsert.setObjectName("menuInsert")
        MainWindow.setMenuBar(self.menubar)
        self.explorerWidget = QtWidgets.QDockWidget(parent=MainWindow)
        self.explorerWidget.setMinimumSize(QtCore.QSize(300, 150))
        self.explorerWidget.setStyleSheet("")
        self.explorerWidget.setObjectName("explorerWidget")
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.explorerWidget.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.explorerWidget)
        self.propertiesWidget = QtWidgets.QDockWidget(parent=MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.propertiesWidget.sizePolicy().hasHeightForWidth())
        self.propertiesWidget.setSizePolicy(sizePolicy)
        self.propertiesWidget.setMinimumSize(QtCore.QSize(300, 150))
        self.propertiesWidget.setStyleSheet("")
        self.propertiesWidget.setObjectName("propertiesWidget")
        self.dockWidgetContents_2 = QtWidgets.QWidget()
        self.dockWidgetContents_2.setObjectName("dockWidgetContents_2")
        self.gridLayout = QtWidgets.QGridLayout(self.dockWidgetContents_2)
        self.gridLayout.setObjectName("gridLayout")
        self.propertiesWidget.setWidget(self.dockWidgetContents_2)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.propertiesWidget)
        self.fileToolbar = QtWidgets.QToolBar(parent=MainWindow)
        self.fileToolbar.setMovable(True)
        self.fileToolbar.setIconSize(QtCore.QSize(18, 18))
        self.fileToolbar.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.fileToolbar.setObjectName("fileToolbar")
        MainWindow.addToolBar(QtCore.Qt.ToolBarArea.TopToolBarArea, self.fileToolbar)
        self.statusBar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.actionsToolbar = QtWidgets.QToolBar(parent=MainWindow)
        self.actionsToolbar.setIconSize(QtCore.QSize(18, 18))
        self.actionsToolbar.setObjectName("actionsToolbar")
        MainWindow.addToolBar(QtCore.Qt.ToolBarArea.TopToolBarArea, self.actionsToolbar)
        self.toolBar = QtWidgets.QToolBar(parent=MainWindow)
        self.toolBar.setIconSize(QtCore.QSize(18, 18))
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.ToolBarArea.TopToolBarArea, self.toolBar)
        self.dockWidget = QtWidgets.QDockWidget(parent=MainWindow)
        self.dockWidget.setMinimumSize(QtCore.QSize(200, 262))
        self.dockWidget.setObjectName("dockWidget")
        self.dockWidgetContents_3 = QtWidgets.QWidget()
        self.dockWidgetContents_3.setObjectName("dockWidgetContents_3")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.dockWidgetContents_3)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setSpacing(2)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.reloadResource = QtWidgets.QToolButton(parent=self.dockWidgetContents_3)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/Dark/refresh-cw.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.reloadResource.setIcon(icon1)
        self.reloadResource.setObjectName("reloadResource")
        self.gridLayout_3.addWidget(self.reloadResource, 2, 4, 1, 1)
        self.openResourceFolder = QtWidgets.QToolButton(parent=self.dockWidgetContents_3)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/Dark/folder.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.openResourceFolder.setIcon(icon2)
        self.openResourceFolder.setObjectName("openResourceFolder")
        self.gridLayout_3.addWidget(self.openResourceFolder, 2, 6, 1, 1)
        self.resourceSearch = QtWidgets.QLineEdit(parent=self.dockWidgetContents_3)
        self.resourceSearch.setInputMask("")
        self.resourceSearch.setText("")
        self.resourceSearch.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
        self.resourceSearch.setClearButtonEnabled(True)
        self.resourceSearch.setObjectName("resourceSearch")
        self.gridLayout_3.addWidget(self.resourceSearch, 0, 0, 1, 7)
        self.resourceList = QtWidgets.QListWidget(parent=self.dockWidgetContents_3)
        self.resourceList.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.resourceList.setProperty("showDropIndicator", False)
        self.resourceList.setDragEnabled(True)
        self.resourceList.setIconSize(QtCore.QSize(64, 64))
        self.resourceList.setFlow(QtWidgets.QListView.Flow.TopToBottom)
        self.resourceList.setProperty("isWrapping", False)
        self.resourceList.setResizeMode(QtWidgets.QListView.ResizeMode.Adjust)
        self.resourceList.setViewMode(QtWidgets.QListView.ViewMode.ListMode)
        self.resourceList.setUniformItemSizes(False)
        self.resourceList.setWordWrap(True)
        self.resourceList.setObjectName("resourceList")
        self.gridLayout_3.addWidget(self.resourceList, 1, 0, 1, 7)
        self.addResource = QtWidgets.QToolButton(parent=self.dockWidgetContents_3)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/Dark/image-plus.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.addResource.setIcon(icon3)
        self.addResource.setObjectName("addResource")
        self.gridLayout_3.addWidget(self.addResource, 2, 5, 1, 1)
        self.dockWidget.setWidget(self.dockWidgetContents_3)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.dockWidget)
        self.actionSave = QtGui.QAction(parent=MainWindow)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/Dark/save.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.actionSave.setIcon(icon4)
        self.actionSave.setObjectName("actionSave")
        self.actionSave_as = QtGui.QAction(parent=MainWindow)
        self.actionSave_as.setObjectName("actionSave_as")
        self.actionAbout_MiFaceStudio = QtGui.QAction(parent=MainWindow)
        self.actionAbout_MiFaceStudio.setObjectName("actionAbout_MiFaceStudio")
        self.actionPreferences = QtGui.QAction(parent=MainWindow)
        self.actionPreferences.setObjectName("actionPreferences")
        self.actionBuild = QtGui.QAction(parent=MainWindow)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/Dark/package.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.actionBuild.setIcon(icon5)
        self.actionBuild.setObjectName("actionBuild")
        self.actionExplorer = QtGui.QAction(parent=MainWindow)
        self.actionExplorer.setCheckable(True)
        self.actionExplorer.setChecked(True)
        self.actionExplorer.setObjectName("actionExplorer")
        self.actionAttributes = QtGui.QAction(parent=MainWindow)
        self.actionAttributes.setCheckable(True)
        self.actionAttributes.setChecked(True)
        self.actionAttributes.setObjectName("actionAttributes")
        self.actionExit = QtGui.QAction(parent=MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionEdit = QtGui.QAction(parent=MainWindow)
        self.actionEdit.setCheckable(True)
        self.actionEdit.setChecked(True)
        self.actionEdit.setObjectName("actionEdit")
        self.actionFile = QtGui.QAction(parent=MainWindow)
        self.actionFile.setCheckable(True)
        self.actionFile.setChecked(True)
        self.actionFile.setObjectName("actionFile")
        self.actionLayout = QtGui.QAction(parent=MainWindow)
        self.actionLayout.setCheckable(True)
        self.actionLayout.setChecked(True)
        self.actionLayout.setObjectName("actionLayout")
        self.actionNewFile = QtGui.QAction(parent=MainWindow)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/Dark/file-plus.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.actionNewFile.setIcon(icon6)
        self.actionNewFile.setObjectName("actionNewFile")
        self.actionOpenFile = QtGui.QAction(parent=MainWindow)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/Dark/folder-open.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.actionOpenFile.setIcon(icon7)
        self.actionOpenFile.setObjectName("actionOpenFile")
        self.actionUndo = QtGui.QAction(parent=MainWindow)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(":/Dark/undo-2.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.actionUndo.setIcon(icon8)
        self.actionUndo.setMenuRole(QtGui.QAction.MenuRole.NoRole)
        self.actionUndo.setObjectName("actionUndo")
        self.actionRedo = QtGui.QAction(parent=MainWindow)
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(":/Dark/redo-2.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.actionRedo.setIcon(icon9)
        self.actionRedo.setMenuRole(QtGui.QAction.MenuRole.NoRole)
        self.actionRedo.setObjectName("actionRedo")
        self.actionAbout_Qt = QtGui.QAction(parent=MainWindow)
        self.actionAbout_Qt.setObjectName("actionAbout_Qt")
        self.actionThirdPartyNotice = QtGui.QAction(parent=MainWindow)
        self.actionThirdPartyNotice.setObjectName("actionThirdPartyNotice")
        self.actionUnpack = QtGui.QAction(parent=MainWindow)
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap(":/Dark/package-open.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.actionUnpack.setIcon(icon10)
        self.actionUnpack.setObjectName("actionUnpack")
        self.actionCut = QtGui.QAction(parent=MainWindow)
        icon11 = QtGui.QIcon()
        icon11.addPixmap(QtGui.QPixmap(":/Dark/scissors.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.actionCut.setIcon(icon11)
        self.actionCut.setObjectName("actionCut")
        self.actionCopy = QtGui.QAction(parent=MainWindow)
        icon12 = QtGui.QIcon()
        icon12.addPixmap(QtGui.QPixmap(":/Dark/copy(1).png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.actionCopy.setIcon(icon12)
        self.actionCopy.setObjectName("actionCopy")
        self.actionPaste = QtGui.QAction(parent=MainWindow)
        icon13 = QtGui.QIcon()
        icon13.addPixmap(QtGui.QPixmap(":/Dark/clipboard-paste.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.actionPaste.setIcon(icon13)
        self.actionPaste.setObjectName("actionPaste")
        self.actionProject_XML_File = QtGui.QAction(parent=MainWindow)
        icon14 = QtGui.QIcon()
        icon14.addPixmap(QtGui.QPixmap(":/Dark/file-code-2.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.actionProject_XML_File.setIcon(icon14)
        self.actionProject_XML_File.setObjectName("actionProject_XML_File")
        self.actionResize_Images = QtGui.QAction(parent=MainWindow)
        self.actionResize_Images.setObjectName("actionResize_Images")
        self.actionImage = QtGui.QAction(parent=MainWindow)
        icon15 = QtGui.QIcon()
        icon15.addPixmap(QtGui.QPixmap(":/Dark/image.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.actionImage.setIcon(icon15)
        self.actionImage.setObjectName("actionImage")
        self.actionImage_List = QtGui.QAction(parent=MainWindow)
        icon16 = QtGui.QIcon()
        icon16.addPixmap(QtGui.QPixmap(":/Dark/image-list.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.actionImage_List.setIcon(icon16)
        self.actionImage_List.setObjectName("actionImage_List")
        self.actionDigital_Number = QtGui.QAction(parent=MainWindow)
        icon17 = QtGui.QIcon()
        icon17.addPixmap(QtGui.QPixmap(":/Dark/numbers.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.actionDigital_Number.setIcon(icon17)
        self.actionDigital_Number.setObjectName("actionDigital_Number")
        self.actionAnalog_Display = QtGui.QAction(parent=MainWindow)
        icon18 = QtGui.QIcon()
        icon18.addPixmap(QtGui.QPixmap(":/Dark/analog.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.actionAnalog_Display.setIcon(icon18)
        self.actionAnalog_Display.setObjectName("actionAnalog_Display")
        self.actionArc_Progress = QtGui.QAction(parent=MainWindow)
        icon19 = QtGui.QIcon()
        icon19.addPixmap(QtGui.QPixmap(":/Dark/progress.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.actionArc_Progress.setIcon(icon19)
        self.actionArc_Progress.setObjectName("actionArc_Progress")
        self.actionDocumentation = QtGui.QAction(parent=MainWindow)
        self.actionDocumentation.setObjectName("actionDocumentation")
        self.actionConsole = QtGui.QAction(parent=MainWindow)
        self.actionConsole.setObjectName("actionConsole")
        self.actionFull_Screen = QtGui.QAction(parent=MainWindow)
        self.actionFull_Screen.setObjectName("actionFull_Screen")
        self.actionDelete = QtGui.QAction(parent=MainWindow)
        icon20 = QtGui.QIcon()
        icon20.addPixmap(QtGui.QPixmap(":/Dark/x_dim.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.actionDelete.setIcon(icon20)
        self.actionDelete.setObjectName("actionDelete")
        self.actionBring_to_Front = QtGui.QAction(parent=MainWindow)
        icon21 = QtGui.QIcon()
        icon21.addPixmap(QtGui.QPixmap(":/Dark/bring-to-front.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.actionBring_to_Front.setIcon(icon21)
        self.actionBring_to_Front.setObjectName("actionBring_to_Front")
        self.actionBring_Forwards = QtGui.QAction(parent=MainWindow)
        self.actionBring_Forwards.setObjectName("actionBring_Forwards")
        self.actionSend_to_Back = QtGui.QAction(parent=MainWindow)
        icon22 = QtGui.QIcon()
        icon22.addPixmap(QtGui.QPixmap(":/Dark/send-to-back.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.actionSend_to_Back.setIcon(icon22)
        self.actionSend_to_Back.setObjectName("actionSend_to_Back")
        self.actionSend_Backwards = QtGui.QAction(parent=MainWindow)
        self.actionSend_Backwards.setObjectName("actionSend_Backwards")
        self.actionZoom_In = QtGui.QAction(parent=MainWindow)
        icon23 = QtGui.QIcon()
        icon23.addPixmap(QtGui.QPixmap(":/Dark/zoom-in.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.actionZoom_In.setIcon(icon23)
        self.actionZoom_In.setObjectName("actionZoom_In")
        self.actionZoom_Out = QtGui.QAction(parent=MainWindow)
        icon24 = QtGui.QIcon()
        icon24.addPixmap(QtGui.QPixmap(":/Dark/zoom-out.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.actionZoom_Out.setIcon(icon24)
        self.actionZoom_Out.setObjectName("actionZoom_Out")
        self.menuFile.addAction(self.actionNewFile)
        self.menuFile.addAction(self.actionOpenFile)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuAbout.addAction(self.actionAbout_MiFaceStudio)
        self.menuAbout.addAction(self.actionAbout_Qt)
        self.menuAbout.addAction(self.actionThirdPartyNotice)
        self.menuHelp.addAction(self.actionDocumentation)
        self.menuHelp.addSeparator()
        self.menuHelp.addAction(self.menuAbout.menuAction())
        self.menuToolbars.addAction(self.actionEdit)
        self.menuToolbars.addAction(self.actionFile)
        self.menuToolbars.addAction(self.actionLayout)
        self.menuZoom.addAction(self.actionZoom_In)
        self.menuZoom.addAction(self.actionZoom_Out)
        self.menuView.addAction(self.actionExplorer)
        self.menuView.addAction(self.actionAttributes)
        self.menuView.addSeparator()
        self.menuView.addAction(self.menuZoom.menuAction())
        self.menuView.addSeparator()
        self.menuView.addAction(self.menuToolbars.menuAction())
        self.menuView.addSeparator()
        self.menuView.addAction(self.actionFull_Screen)
        self.menuLayers.addAction(self.actionBring_to_Front)
        self.menuLayers.addAction(self.actionBring_Forwards)
        self.menuLayers.addSeparator()
        self.menuLayers.addAction(self.actionSend_to_Back)
        self.menuLayers.addAction(self.actionSend_Backwards)
        self.menuEdit.addAction(self.actionUndo)
        self.menuEdit.addAction(self.actionRedo)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionCut)
        self.menuEdit.addAction(self.actionCopy)
        self.menuEdit.addAction(self.actionPaste)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.menuLayers.menuAction())
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
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuInsert.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuTools.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.fileToolbar.addAction(self.actionNewFile)
        self.fileToolbar.addAction(self.actionOpenFile)
        self.fileToolbar.addAction(self.actionSave)
        self.actionsToolbar.addAction(self.actionDelete)
        self.actionsToolbar.addAction(self.actionUndo)
        self.actionsToolbar.addAction(self.actionRedo)
        self.actionsToolbar.addAction(self.actionCut)
        self.actionsToolbar.addAction(self.actionCopy)
        self.actionsToolbar.addAction(self.actionPaste)
        self.toolBar.addAction(self.actionBuild)

        self.retranslateUi(MainWindow)
        self.workspace.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Mi Create"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.menuAbout.setTitle(_translate("MainWindow", "About"))
        self.menuView.setTitle(_translate("MainWindow", "View"))
        self.menuToolbars.setTitle(_translate("MainWindow", "Toolbars"))
        self.menuZoom.setTitle(_translate("MainWindow", "Zoom"))
        self.menuEdit.setTitle(_translate("MainWindow", "Edit"))
        self.menuLayers.setTitle(_translate("MainWindow", "Layers"))
        self.menuTools.setTitle(_translate("MainWindow", "Tools"))
        self.menuInsert.setTitle(_translate("MainWindow", "Create"))
        self.explorerWidget.setWindowTitle(_translate("MainWindow", "Explorer"))
        self.propertiesWidget.setWindowTitle(_translate("MainWindow", "Properties"))
        self.fileToolbar.setWindowTitle(_translate("MainWindow", "File Toolbar"))
        self.actionsToolbar.setWindowTitle(_translate("MainWindow", "toolBar_2"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.dockWidget.setWindowTitle(_translate("MainWindow", "Resources"))
        self.reloadResource.setText(_translate("MainWindow", "Reload"))
        self.openResourceFolder.setText(_translate("MainWindow", "..."))
        self.resourceSearch.setPlaceholderText(_translate("MainWindow", "Search..."))
        self.addResource.setText(_translate("MainWindow", "addImage"))
        self.actionSave.setText(_translate("MainWindow", "Save..."))
        self.actionSave.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.actionSave_as.setText(_translate("MainWindow", "Save as..."))
        self.actionSave_as.setShortcut(_translate("MainWindow", "Ctrl+Shift+S"))
        self.actionAbout_MiFaceStudio.setText(_translate("MainWindow", "About Mi Create"))
        self.actionPreferences.setText(_translate("MainWindow", "Settings"))
        self.actionPreferences.setShortcut(_translate("MainWindow", "Ctrl+P"))
        self.actionBuild.setText(_translate("MainWindow", "Build..."))
        self.actionBuild.setToolTip(_translate("MainWindow", "Build"))
        self.actionBuild.setShortcut(_translate("MainWindow", "Ctrl+K"))
        self.actionExplorer.setText(_translate("MainWindow", "Explorer"))
        self.actionAttributes.setText(_translate("MainWindow", "Attributes"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))
        self.actionEdit.setText(_translate("MainWindow", "Edit"))
        self.actionFile.setText(_translate("MainWindow", "File"))
        self.actionLayout.setText(_translate("MainWindow", "Layout"))
        self.actionNewFile.setText(_translate("MainWindow", "New..."))
        self.actionNewFile.setToolTip(_translate("MainWindow", "New File"))
        self.actionNewFile.setShortcut(_translate("MainWindow", "Ctrl+N"))
        self.actionOpenFile.setText(_translate("MainWindow", "Open..."))
        self.actionOpenFile.setToolTip(_translate("MainWindow", "Open File"))
        self.actionOpenFile.setShortcut(_translate("MainWindow", "Ctrl+O"))
        self.actionUndo.setText(_translate("MainWindow", "Undo"))
        self.actionUndo.setShortcut(_translate("MainWindow", "Ctrl+Z"))
        self.actionRedo.setText(_translate("MainWindow", "Redo"))
        self.actionRedo.setShortcut(_translate("MainWindow", "Ctrl+Y"))
        self.actionAbout_Qt.setText(_translate("MainWindow", "About Qt"))
        self.actionThirdPartyNotice.setText(_translate("MainWindow", "Third Party Notices"))
        self.actionUnpack.setText(_translate("MainWindow", "Unpack..."))
        self.actionCut.setText(_translate("MainWindow", "Cut"))
        self.actionCut.setShortcut(_translate("MainWindow", "Ctrl+X"))
        self.actionCopy.setText(_translate("MainWindow", "Copy"))
        self.actionCopy.setShortcut(_translate("MainWindow", "Ctrl+C"))
        self.actionPaste.setText(_translate("MainWindow", "Paste"))
        self.actionPaste.setShortcut(_translate("MainWindow", "Ctrl+V"))
        self.actionProject_XML_File.setText(_translate("MainWindow", "Project Source Code"))
        self.actionResize_Images.setText(_translate("MainWindow", "Resize Images"))
        self.actionImage.setText(_translate("MainWindow", "Image"))
        self.actionImage_List.setText(_translate("MainWindow", "Image List"))
        self.actionDigital_Number.setText(_translate("MainWindow", "Digital Number"))
        self.actionAnalog_Display.setText(_translate("MainWindow", "Analog Display"))
        self.actionArc_Progress.setText(_translate("MainWindow", "Arc Progress"))
        self.actionDocumentation.setText(_translate("MainWindow", "Documentation"))
        self.actionDocumentation.setShortcut(_translate("MainWindow", "Ctrl+H"))
        self.actionConsole.setText(_translate("MainWindow", "Console"))
        self.actionFull_Screen.setText(_translate("MainWindow", "Full Screen"))
        self.actionFull_Screen.setShortcut(_translate("MainWindow", "F11"))
        self.actionDelete.setText(_translate("MainWindow", "Delete"))
        self.actionDelete.setShortcut(_translate("MainWindow", "Backspace"))
        self.actionBring_to_Front.setText(_translate("MainWindow", "Bring to Front"))
        self.actionBring_Forwards.setText(_translate("MainWindow", "Bring Forwards"))
        self.actionSend_to_Back.setText(_translate("MainWindow", "Send to Back"))
        self.actionSend_Backwards.setText(_translate("MainWindow", "Send Backwards"))
        self.actionZoom_In.setText(_translate("MainWindow", "Zoom In"))
        self.actionZoom_In.setShortcut(_translate("MainWindow", "Ctrl+="))
        self.actionZoom_Out.setText(_translate("MainWindow", "Zoom Out"))
        self.actionZoom_Out.setShortcut(_translate("MainWindow", "Ctrl+-"))
