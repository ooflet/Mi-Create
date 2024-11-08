# Stacked Widget with animation
# From Spinn TV https://www.youtube.com/c/SpinnTV

from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtCore import QTimeLine
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import json

class QStackedWidget(QtWidgets.QStackedWidget):
    def __init__(self, parent=None):
        super(QStackedWidget, self).__init__(parent)
        # Fade transition
        self.fadeTransition = False
        # Slide transition
        self.slideTransition = False
        # Default transition direction
        self.transitionDirection = "Horizontal"
        # Default transition animation time
        self.transitionTime = 500
        # Default fade animation time
        self.fadeTime = 500
        # Default transition animation easing curve
        self.transitionEasingCurve = QtCore.QEasingCurve.Type.OutBack
        # Default transition animation easing curve
        self.fadeEasingCurve = QtCore.QEasingCurve.Type.Linear
        # Default current widget index
        self.currentWidget = 0
        # Default next widget index
        self.nextWidget = 0
        # Default widget position
        self._currentWidgetPosition = QtCore.QPoint(0, 0)
        # Default boolean for active widget
        self.widgetActive = False
                            

    def setTransitionDirection(self, direction):
        self.transitionDirection = direction

    def setTransitionSpeed(self, speed):
        self.transitionTime = speed

    def setFadeSpeed(self, speed):
        self.fadeTime = speed

    def setTransitionEasingCurve(self, aesingCurve):
        self.transitionEasingCurve = aesingCurve

    def setFadeCurve(self, aesingCurve):
        self.fadeEasingCurve = aesingCurve

    def setFadeTransition(self, fadeState):
        if isinstance(fadeState, bool):
            self.fadeTransition = fadeState
        else:
            raise Exception("setFadeTransition() only accepts boolean variables")

    def setSlideTransition(self, slideState):
        if isinstance(slideState, bool):
            self.slideTransition = slideState
        else:
            raise Exception("setSlideTransition() only accepts boolean variables")

    def slideToPreviousWidget(self):
        currentWidgetIndex = self.currentIndex()
        if currentWidgetIndex > 0:
            self.slideToWidgetIndex(currentWidgetIndex - 1)

    def slideToNextWidget(self):
        currentWidgetIndex = self.currentIndex()
        if currentWidgetIndex < (self.count() - 1):
            self.slideToWidgetIndex(currentWidgetIndex + 1)

    def slideToWidgetIndex(self, index):
        if index > (self.count() - 1):
            index = index % self.count()
        elif index < 0:
            index = (index + self.count()) % self.count()
        if self.slideTransition:
            self.slideToWidget(self.widget(index))
        else:
            self.setCurrentIndex(index)

    def slideToWidget(self, newWidget):
        # If the widget is active, exit the function
        if self.widgetActive:
            return

        # Update widget active bool
        self.widgetActive = True

        # Get current and next widget index
        _currentWidgetIndex = self.currentIndex()
        _nextWidgetIndex = self.indexOf(newWidget)

        # If current widget index is equal to next widget index, exit function
        if _currentWidgetIndex == _nextWidgetIndex:
            self.widgetActive = False
            return

        # Get X and Y position of QStackedWidget
        offsetX, offsetY = self.frameRect().width() + 9, self.frameRect().height() + 9
        # Set the next widget geometry
        self.widget(_nextWidgetIndex).setGeometry(self.frameRect())

        # Set left right(horizontal) or up down(vertical) transition
        if not self.transitionDirection == "Horizontal":
            if _currentWidgetIndex < _nextWidgetIndex:
                # Down up transition
                offsetX, offsetY = 0, -offsetY
            else:
                # Up down transition
                offsetX = 0
        else:
            # Right left transition
            if _currentWidgetIndex < _nextWidgetIndex:
                offsetX, offsetY = -offsetX, 0
            else:
                # Left right transition
                offsetY = 0

        nextWidgetPosition = self.widget(_nextWidgetIndex).pos()
        currentWidgetPosition = self.widget(_currentWidgetIndex).pos()
        self._currentWidgetPosition = currentWidgetPosition

        # Animate transition
        offset = QtCore.QPoint(offsetX, offsetY)
        self.widget(_nextWidgetIndex).move(nextWidgetPosition - offset)
        self.widget(_nextWidgetIndex).show()
        self.widget(_nextWidgetIndex).raise_()

        anim_group = QtCore.QParallelAnimationGroup(
            self, finished=self.animationDoneSlot
        )

        for index, start, end in zip(
            (_currentWidgetIndex, _nextWidgetIndex), 
            (currentWidgetPosition, nextWidgetPosition - offset), 
            (currentWidgetPosition + offset, nextWidgetPosition)
        ):
            animation = QtCore.QPropertyAnimation(
                self.widget(index),
                b"pos",
                duration=self.transitionTime,
                easingCurve=self.transitionEasingCurve,
                startValue=start,
                endValue=end,
            )
            anim_group.addAnimation(animation)

        self.nextWidget = _nextWidgetIndex
        self.currentWidget = _currentWidgetIndex

        self.widgetActive = True
        anim_group.start(QtCore.QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

        # Play fade animation
        if self.fadeTransition:
            FadeWidgetTransition(self, self.widget(_currentWidgetIndex), self.widget(_nextWidgetIndex))

    def animationDoneSlot(self):
        self.setCurrentIndex(self.nextWidget)
        self.widget(self.currentWidget).hide()
        self.widget(self.currentWidget).move(self._currentWidgetPosition)
        self.widgetActive = False

    def setCurrentWidget(self, widget):
        currentIndex = self.currentIndex()
        nextIndex = self.indexOf(widget)
        # print(currentIndex, nextIndex)
        if self.currentIndex() == self.indexOf(widget):
            return
        if self.slideTransition:
            self.slideToWidgetIndex(nextIndex)

        if self.fadeTransition:
            self.fader_widget = FadeWidgetTransition(self, self.widget(self.currentIndex()), self.widget(self.indexOf(widget)))
            if not self.slideTransition:
                self.setCurrentIndex(nextIndex)

        if not self.slideTransition and not self.fadeTransition:
            self.setCurrentIndex(nextIndex)

class FadeWidgetTransition(QWidget):
    def __init__(self, animationSettings, oldWidget, newWidget):
    
        QWidget.__init__(self, newWidget)
        
        self.oldPixmap = QPixmap(newWidget.size())
        oldWidget.render(self.oldPixmap)
        self.pixmapOpacity = 1.0
        
        self.timeline = QTimeLine()
        self.timeline.valueChanged.connect(self.animate)
        self.timeline.finished.connect(self.close)
        self.timeline.setDuration(animationSettings.fadeTime)
        self.timeline.setEasingCurve(animationSettings.fadeEasingCurve)
        self.timeline.start()
        
        self.resize(newWidget.size())
        self.show()
    
    def paintEvent(self, event):
    
        painter = QPainter()
        painter.begin(self)
        painter.setOpacity(self.pixmapOpacity)
        painter.drawPixmap(0, 0, self.oldPixmap)
        painter.end()
    
    def animate(self, value):    
        self.pixmapOpacity = 1.0 - value
        self.repaint()

def loadJsonStyle(self):
    file = open('data/stackWidgetAnim.json',)
    data = json.load(file)

    if "QStackedWidget" in data:
        for stackedWidget in data['QStackedWidget']:
            if "name" in stackedWidget and len(str(stackedWidget["name"])) > 0:
                if hasattr(self, str(stackedWidget["name"])):
                    widget = getattr(self, str(stackedWidget["name"]))                    
                    if widget.objectName() == stackedWidget["name"]:
                        if "transitionAnimation" in stackedWidget:
                            for transitionAnimation in stackedWidget["transitionAnimation"]:
                                if "fade" in transitionAnimation:
                                    for fade in transitionAnimation["fade"]:
                                        if "active" in fade and fade["active"]:
                                            widget.fadeTransition = True
                                            if "duration" in fade and fade["duration"] > 0:
                                                widget.fadeTime = fade["duration"]
                                            if "easingCurve" in fade and len(str(fade["easingCurve"])) > 0:
                                                widget.fadeEasingCurve = returnAnimationEasingCurve(fade["easingCurve"])

                                if "slide" in transitionAnimation:
                                    for slide in transitionAnimation["slide"]:
                                        if "active" in slide and slide["active"]:
                                            widget.slideTransition = True
                                            if "duration" in slide and slide["duration"] > 0:
                                                widget.transitionTime = slide["duration"]
                                            if "easingCurve" in slide and len(str(slide["easingCurve"])) > 0:
                                                widget.transitionEasingCurve = returnAnimationEasingCurve(slide["easingCurve"])
                                            if "direction" in slide and len(str(slide["direction"])) > 0:
                                                widget.transitionDirection = returnQtDirection(slide["direction"])

                        if "navigation" in stackedWidget:
                            for navigation in stackedWidget["navigation"]:
                                if "nextPage" in navigation:
                                    if hasattr(self, str(navigation["nextPage"])):
                                        button = getattr(self, str(navigation["nextPage"]))
                                        button.clicked.connect(lambda: widget.slideToNextWidget())
                                    else:
                                        print("No button found")

                                if "previousPage" in navigation:
                                    if hasattr(self, str(navigation["previousPage"])):
                                        button = getattr(self, str(navigation["previousPage"]))
                                        button.clicked.connect(lambda: widget.slideToPreviousWidget())
                                    else:
                                        print("No button found")

                                if "navigationButtons" in navigation:
                                    for navigationButton in navigation["navigationButtons"]:
                                        for button in navigationButton:
                                            widgetPage = navigationButton[button]
                                            if not hasattr(self, str(widgetPage)):
                                                raise Exception("Unknown widget '" +str(widgetPage)+ "'. Please check your JSon file")
                                            if not hasattr(self, str(button)):
                                                raise Exception("Unknown button '" +str(button)+ "'. Please check your JSon file")

                                            pushBtn = getattr(self, str(button))
                                            widgetPg = getattr(self, str(widgetPage))
                                            navigationButtons(widget, pushBtn, widgetPg)


def navigationButtons(stackedWidget, pushButton, widgetPage):    
    pushButton.clicked.connect(lambda: stackedWidget.setCurrentWidget(widgetPage))

def returnAnimationEasingCurve(easingCurveName):
    if len(str(easingCurveName)) > 0:
        if str(easingCurveName) == "OutQuad":               
            return QtCore.QEasingCurve.Type.OutQuad
        elif str(easingCurveName) == "Linear":              
            return QtCore.QEasingCurve.Type.Linear
        elif str(easingCurveName) == "InQuad":              
            return QtCore.QEasingCurve.Type.InQuad
        elif str(easingCurveName) == "InOutQuad":           
            return QtCore.QEasingCurve.Type.InOutQuad
        elif str(easingCurveName) == "OutInQuad":           
            return QtCore.QEasingCurve.Type.OutInQuad
        elif str(easingCurveName) == "InCubic":           
            return QtCore.QEasingCurve.Type.InCubic
        elif str(easingCurveName) == "OutCubic":           
            return QtCore.QEasingCurve.Type.OutCubic
        elif str(easingCurveName) == "InOutCubic":          
            return QtCore.QEasingCurve.Type.InOutCubic
        elif str(easingCurveName) == "OutInCubic":          
            return QtCore.QEasingCurve.Type.OutInCubic
        elif str(easingCurveName) == "InQuart":          
            return QtCore.QEasingCurve.Type.InQuart
        elif str(easingCurveName) == "OutQuart":          
            return QtCore.QEasingCurve.Type.OutQuart
        elif str(easingCurveName) == "InOutQuart":          
            return QtCore.QEasingCurve.Type.InOutQuart
        elif str(easingCurveName) == "OutInQuart":          
            return QtCore.QEasingCurve.Type.OutInQuart
        elif str(easingCurveName) == "InQuint":          
            return QtCore.QEasingCurve.Type.InQuint
        elif str(easingCurveName) == "OutQuint":          
            return QtCore.QEasingCurve.Type.OutQuint
        elif str(easingCurveName) == "InOutQuint":          
            return QtCore.QEasingCurve.Type.InOutQuint
        elif str(easingCurveName) == "InSine":          
            return QtCore.QEasingCurve.Type.InSine
        elif str(easingCurveName) == "OutSine":          
            return QtCore.QEasingCurve.Type.OutSine
        elif str(easingCurveName) == "InOutSine":          
            return QtCore.QEasingCurve.Type.InOutSine
        elif str(easingCurveName) == "OutInSine":          
            return QtCore.QEasingCurve.Type.OutInSine
        elif str(easingCurveName) == "InExpo":          
            return QtCore.QEasingCurve.Type.InExpo
        elif str(easingCurveName) == "OutExpo":          
            return QtCore.QEasingCurve.Type.OutExpo
        elif str(easingCurveName) == "InOutExpo":          
            return QtCore.QEasingCurve.Type.InOutExpo
        elif str(easingCurveName) == "OutInExpo":          
            return QtCore.QEasingCurve.Type.OutInExpo
        elif str(easingCurveName) == "InCirc":          
            return QtCore.QEasingCurve.Type.InCirc
        elif str(easingCurveName) == "OutCirc":          
            return QtCore.QEasingCurve.Type.OutCirc
        elif str(easingCurveName) == "InOutCirc":          
            return QtCore.QEasingCurve.Type.InOutCirc
        elif str(easingCurveName) == "OutInCirc":          
            return QtCore.QEasingCurve.Type.OutInCirc
        elif str(easingCurveName) == "InElastic":          
            return QtCore.QEasingCurve.Type.InElastic
        elif str(easingCurveName) == "OutElastic":          
            return QtCore.QEasingCurve.Type.OutElastic
        elif str(easingCurveName) == "InOutElastic":        
            return QtCore.QEasingCurve.Type.InOutElastic
        elif str(easingCurveName) == "OutInElastic":        
            return QtCore.QEasingCurve.Type.OutInElastic
        elif str(easingCurveName) == "InBack":        
            return QtCore.QEasingCurve.Type.InBack
        elif str(easingCurveName) == "OutBack":        
            return QtCore.QEasingCurve.Type.OutBack
        elif str(easingCurveName) == "InOutBack":        
            return QtCore.QEasingCurve.Type.InOutBack
        elif str(easingCurveName) == "OutInBack":        
            return QtCore.QEasingCurve.Type.OutInBack
        elif str(easingCurveName) == "InBounce":        
            return QtCore.QEasingCurve.Type.InBounce
        elif str(easingCurveName) == "OutBounce":        
            return QtCore.QEasingCurve.Type.OutBounce
        elif str(easingCurveName) == "InOutBounce":        
            return QtCore.QEasingCurve.Type.InOutBounce
        elif str(easingCurveName) == "OutInBounce":        
            return QtCore.QEasingCurve.Type.OutInBounce
        else:
            raise Exception("Unknown value'" +easingCurveName+ "' for setEasingCurve() on ", animation)

def returnQtDirection(direction):
    if len(str(direction)) > 0:
        if str(direction) == "horizontal":
            return "Horizontal"
        elif str(direction) == "vertical":
            return "Vertical"
        else:
            raise Exception("Unknown direction name given ("+direction+"), please use Vertical or Horizontal direction")

    else:
        raise Exception("Empty direction name given, please use Vertical or Horizontal direction")

                            
