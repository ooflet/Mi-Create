# MainWindow
# ooflet <ooflet@proton.me>from PyQt6.QtCore import QMetaObject, Qt, QRect, QSize
from PyQt6.QtCore import QMetaObject, Qt, QRect, QSize
from PyQt6.QtGui import QAction, QIcon, QKeySequence
from PyQt6.QtWidgets import (
    QMainWindow, QDockWidget, QMenuBar, QMenu, QStatusBar, QToolBar,
    QWidget, QTabWidget, QGridLayout, QLineEdit, QListWidget, QFrame,
    QAbstractItemView, QListView, QToolButton
)
from utils.translate import QCoreApplication

class MainWindow(object):
    def setupUi(self, MainWindow):
        self.initWindow(MainWindow)
        self.createCentralWidget(MainWindow)
        self.createDockWidgets(MainWindow)
        self.createMenuBar(MainWindow)
        self.createToolBar(MainWindow)
        self.createActions(MainWindow)
        self.assembleMenus()
        self.populateToolBar()

        self.retranslateUi(MainWindow)
        self.workspace.setCurrentIndex(-1)
        QMetaObject.connectSlotsByName(MainWindow)

    def initWindow(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setMinimumSize(1000, 600)
        MainWindow.setWindowIcon(QIcon(":/Images/MiCreate48x48.png"))
        MainWindow.setAnimated(True)
        MainWindow.setDocumentMode(False)
        MainWindow.setTabShape(QTabWidget.TabShape.Rounded)

    def createCentralWidget(self, MainWindow):
        self.centralWidget = QWidget(MainWindow)
        self.centralWidget.setMinimumSize(200, 0)
        layout = QGridLayout(self.centralWidget)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(0)

        self.workspace = QTabWidget(self.centralWidget)
        self.workspace.setTabsClosable(True)
        self.workspace.setMovable(True)
        layout.addWidget(self.workspace)

        MainWindow.setCentralWidget(self.centralWidget)

    def createDockWidgets(self, MainWindow):
        self.createExplorerDock(MainWindow)
        self.createPropertiesDock(MainWindow)
        self.createResourcesDock(MainWindow)

    def createExplorerDock(self, MainWindow):
        self.explorerWidget = QDockWidget("Explorer", MainWindow)
        self.explorerWidget.setMinimumSize(300, 150)
        self.explorerWidget.setWidget(QWidget())
        MainWindow.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.explorerWidget)

    def createPropertiesDock(self, MainWindow):
        self.propertiesWidget = QDockWidget("Properties", MainWindow)
        self.propertiesWidget.setMinimumSize(300, 150)
        container = QWidget()
        container.setLayout(QGridLayout())
        self.propertiesWidget.setWidget(container)
        MainWindow.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.propertiesWidget)

    def createResourcesDock(self, MainWindow):
        self.resourcesWidget = QDockWidget("Resources", MainWindow)
        self.resourcesWidget.setMinimumSize(204, 262)

        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setHorizontalSpacing(0)
        layout.setVerticalSpacing(2)

        self.resourceSearch = QLineEdit()
        self.resourceSearch.setPlaceholderText("Search...")
        self.resourceSearch.setClearButtonEnabled(True)
        layout.addWidget(self.resourceSearch, 0, 0, 1, 7)

        self.resourceList = QListWidget()
        self.resourceList.setFrameShape(QFrame.Shape.NoFrame)
        self.resourceList.setDragEnabled(True)
        self.resourceList.setIconSize(QSize(64, 64))
        self.resourceList.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.resourceList.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.resourceList.setViewMode(QListView.ViewMode.ListMode)
        layout.addWidget(self.resourceList, 1, 0, 1, 7)

        self.reloadResource = QToolButton()
        self.reloadResource.setText("Reload")
        self.reloadResource.setIcon(QIcon.fromTheme("view-refresh"))
        layout.addWidget(self.reloadResource, 2, 4)

        self.addResource = QToolButton()
        self.addResource.setText("Add Image")
        self.addResource.setIcon(QIcon.fromTheme("insert-image"))
        layout.addWidget(self.addResource, 2, 5)

        self.openResourceFolder = QToolButton()
        self.openResourceFolder.setText("Open Folder")
        self.openResourceFolder.setIcon(QIcon.fromTheme("folder"))
        layout.addWidget(self.openResourceFolder, 2, 6)

        self.resourcesWidget.setWidget(widget)
        MainWindow.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.resourcesWidget)

    def createMenuBar(self, MainWindow):
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setGeometry(QRect(0, 0, 1000, 22))
        MainWindow.setMenuBar(self.menuBar)

        self.menuLogo = QMenu("Logo", self.menuBar)
        self.menuFile = QMenu("&File", self.menuBar)
        self.menuEdit = QMenu("&Edit", self.menuBar)
        self.menuView = QMenu("&View", self.menuBar)
        self.menuAlign = QMenu("&Align", self.menuBar)
        self.menuProject = QMenu("&Project", self.menuBar)
        self.menuZoom = QMenu("Zoom", self.menuView)
        self.menuLayers = QMenu("Layers", self.menuEdit)
        self.menuBuild = QMenu("Build", self.menuBar)
        self.menuAbout = QMenu("About", self.menuLogo)

        self.menuLogo.addMenu(self.menuAbout)
        self.menuView.addMenu(self.menuZoom)

        self.menuBar.addMenu(self.menuLogo)
        self.menuBar.addMenu(self.menuFile)
        self.menuBar.addMenu(self.menuEdit)
        self.menuBar.addMenu(self.menuView)
        self.menuBar.addMenu(self.menuBuild)

    def createToolBar(self, MainWindow):
        self.toolBar = QToolBar("toolBar", MainWindow)
        self.toolBar.setMovable(False)
        self.toolBar.setFloatable(True)
        self.toolBar.setIconSize(QSize(16, 16))
        MainWindow.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolBar)

    def createActions(self, MainWindow):
        # File actions
        self.actionNewFile = QAction(QIcon.fromTheme("document-new"), "New File", MainWindow)
        self.actionNewFile.setShortcut(QKeySequence.StandardKey.New)

        self.actionOpenFile = QAction(QIcon.fromTheme("document-open"), "Open File", MainWindow)
        self.actionOpenFile.setShortcut(QKeySequence.StandardKey.Open)

        self.actionSave = QAction(QIcon.fromTheme("document-save"), "Save", MainWindow)
        self.actionSave.setShortcut(QKeySequence.StandardKey.Save)

        self.actionExport = QAction(QIcon.fromTheme("document-export"), "Export", MainWindow)
        self.actionExit = QAction(QIcon.fromTheme("application-exit"), "Exit", MainWindow)
        self.actionExit.setShortcut(QKeySequence.StandardKey.Quit)

        # Edit actions
        self.actionUndo = QAction(QIcon.fromTheme("edit-undo"), "Undo", MainWindow)
        self.actionUndo.setShortcut(QKeySequence.StandardKey.Undo)

        self.actionRedo = QAction(QIcon.fromTheme("edit-redo"), "Redo", MainWindow)
        self.actionRedo.setShortcut(QKeySequence.StandardKey.Redo)

        self.actionCut = QAction(QIcon.fromTheme("edit-cut"), "Cut", MainWindow)
        self.actionCut.setShortcut(QKeySequence.StandardKey.Cut)

        self.actionCopy = QAction(QIcon.fromTheme("edit-copy"), "Copy", MainWindow)
        self.actionCopy.setShortcut(QKeySequence.StandardKey.Copy)

        self.actionPaste = QAction(QIcon.fromTheme("edit-paste"), "Paste", MainWindow)
        self.actionPaste.setShortcut(QKeySequence.StandardKey.Paste)

        self.actionDelete = QAction(QIcon.fromTheme("edit-delete"), "Delete", MainWindow)
        self.actionDelete.setShortcut(QKeySequence.StandardKey.Delete)

        # Align actions
        self.actionAlignLeft = QAction(QIcon.fromTheme("format-justify-left"), "Align Left", MainWindow)
        self.actionAlignTop = QAction(QIcon.fromTheme("align-vertical-top"), "Align Top", MainWindow)
        self.actionAlignRight = QAction(QIcon.fromTheme("format-justify-right"), "Align Right", MainWindow)
        self.actionAlignBottom = QAction(QIcon.fromTheme("align-vertical-bottom"), "Align Bottom", MainWindow)
        self.actionAlignVertical = QAction(QIcon.fromTheme("format-justify-center"), "Align Vertical", MainWindow)
        self.actionAlignHorizontal = QAction(QIcon.fromTheme("format-justify-fill"), "Align Horizontal", MainWindow)

        # Project actions
        self.actionManage_Project = QAction(QIcon.fromTheme("system-run"), "Manage Project", MainWindow)
        self.actionClose_Project = QAction(QIcon.fromTheme("window-close"), "Close Project", MainWindow)
        self.actionProject_XML_File = QAction(QIcon.fromTheme("text-xml"), "Project XML File", MainWindow)
        self.actionPreferences = QAction(QIcon.fromTheme("preferences-system"), "Preferences", MainWindow)
        self.actionPreferences.setShortcut(QKeySequence.StandardKey.Preferences)

        # Layer actions
        self.actionBring_to_Front = QAction(QIcon.fromTheme("go-top"), "Bring to Front", MainWindow)
        self.actionBring_Forwards = QAction(QIcon.fromTheme("go-up"), "Bring Forwards", MainWindow)
        self.actionSend_to_Back = QAction(QIcon.fromTheme("go-bottom"), "Send to Back", MainWindow)
        self.actionSend_Backwards = QAction(QIcon.fromTheme("go-down"), "Send Backwards", MainWindow)

        # View actions
        self.actionToggleExplorer = QAction(QIcon.fromTheme("view-list-tree"), "Explorer", MainWindow)
        self.actionToggleExplorer.setCheckable(True)

        self.actionToggleResources = QAction(QIcon.fromTheme("folder"), "Resources", MainWindow)
        self.actionToggleResources.setCheckable(True)

        self.actionToggleProperties = QAction(QIcon.fromTheme("document-properties"), "Properties", MainWindow)
        self.actionToggleProperties.setCheckable(True)

        self.actionToggleToolbar = QAction(QIcon.fromTheme("preferences-desktop-toolbar"), "Toolbar", MainWindow)
        self.actionToggleToolbar.setCheckable(True)

        # Add actions to menus
        self.menuFile.addAction(self.actionNewFile)
        self.menuFile.addAction(self.actionOpenFile)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionExport)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)

        self.menuEdit.addAction(self.actionUndo)
        self.menuEdit.addAction(self.actionRedo)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionCut)
        self.menuEdit.addAction(self.actionCopy)
        self.menuEdit.addAction(self.actionPaste)
        self.menuEdit.addAction(self.actionDelete)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionBring_to_Front)
        self.menuEdit.addAction(self.actionBring_Forwards)
        self.menuEdit.addAction(self.actionSend_to_Back)
        self.menuEdit.addAction(self.actionSend_Backwards)

        self.menuAlign.addAction(self.actionAlignLeft)
        self.menuAlign.addAction(self.actionAlignTop)
        self.menuAlign.addAction(self.actionAlignRight)
        self.menuAlign.addAction(self.actionAlignBottom)
        self.menuAlign.addAction(self.actionAlignVertical)
        self.menuAlign.addAction(self.actionAlignHorizontal)

        self.menuProject.addAction(self.actionManage_Project)
        self.menuProject.addAction(self.actionClose_Project)
        self.menuProject.addAction(self.actionProject_XML_File)
        self.menuProject.addAction(self.actionPreferences)

        self.menuView.addAction(self.actionToggleExplorer)
        self.menuView.addAction(self.actionToggleResources)
        self.menuView.addAction(self.actionToggleProperties)
        self.menuView.addAction(self.actionToggleToolbar)

        # Toolbar actions
        self.toolBar.addAction(self.actionNewFile)
        self.toolBar.addAction(self.actionOpenFile)
        self.toolBar.addAction(self.actionSave)
        self.toolBar.addAction(self.actionExport)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionUndo)
        self.toolBar.addAction(self.actionRedo)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionCut)
        self.toolBar.addAction(self.actionCopy)
        self.toolBar.addAction(self.actionPaste)

        QMetaObject.connectSlotsByName(MainWindow)

    def assembleMenus(self):
        self.menuFile.addActions([self.actionNewFile, self.actionOpenFile, self.actionSave])
        self.menuEdit.addActions([
            self.actionUndo, self.actionRedo,
            self.actionCut, self.actionCopy,
            self.actionPaste, self.actionDelete
        ])
        self.menuZoom.addActions([])  # Add zoom-related actions later
        self.menuView.addActions([])  # Add toggle views, full screen, etc.
        self.menuBuild.addActions([])  # Add build/run/export actions here

    def populateToolBar(self):
        self.toolBar.addActions([
            self.actionNewFile,
            self.actionOpenFile,
            self.actionSave,
            self.actionUndo,
            self.actionRedo,
            self.actionCut,
            self.actionCopy,
            self.actionPaste,
            self.actionDelete
        ])

    def retranslateUi(self, MainWindow):
        _ = QCoreApplication.translate
        MainWindow.setWindowTitle(_("MainWindow", "Mi Create"))
