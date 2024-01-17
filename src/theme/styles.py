# QModernStyle


from PyQt6.QtGui import QPalette, QColor
from ._utils import resource_path

_STYLESHEET = resource_path('resources/style.qss')
""" str: Main stylesheet. """


def _apply_base_theme(app):

    app.setStyle('fusion')

    with open(_STYLESHEET) as stylesheet:
        app.setStyleSheet(stylesheet.read())


def dark(app):
    """ Apply Dark Theme to the Qt application instance.

        Args:
            app (QApplication): QApplication instance.
    """

    darkPalette = QPalette()

    # base
    darkPalette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    darkPalette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    darkPalette.setColor(QPalette.ColorRole.Light, QColor(255, 255, 255))
    darkPalette.setColor(QPalette.ColorRole.Midlight, QColor(90, 90, 90))
    darkPalette.setColor(QPalette.ColorRole.Dark, QColor(35, 35, 35))
    darkPalette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    darkPalette.setColor(QPalette.ColorRole.BrightText, QColor(255, 255, 255))
    darkPalette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    darkPalette.setColor(QPalette.ColorRole.Base, QColor(42, 42, 42))
    darkPalette.setColor(QPalette.ColorRole.Window, QColor(50, 50, 50))
    darkPalette.setColor(QPalette.ColorRole.Shadow, QColor(20, 20, 20))
    darkPalette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    darkPalette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    darkPalette.setColor(QPalette.ColorRole.Link, QColor(85, 170, 255))
    darkPalette.setColor(QPalette.ColorRole.AlternateBase, QColor(66, 66, 66))
    darkPalette.setColor(QPalette.ColorRole.ToolTipBase, QColor(53, 53, 53))
    darkPalette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
    darkPalette.setColor(QPalette.ColorRole.LinkVisited, QColor(80, 80, 80))

    # disabled
    darkPalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText,
                         QColor(127, 127, 127))
    darkPalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text,
                         QColor(127, 127, 127))
    darkPalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText,
                         QColor(127, 127, 127))
    darkPalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Highlight,
                         QColor(80, 80, 80))
    darkPalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.HighlightedText,
                         QColor(127, 127, 127))

    app.setPalette(darkPalette)
    
    _apply_base_theme(app)


def light(app):
    """ Apply Light Theme to the Qt application instance.

        Args:
            app (QApplication): QApplication instance.
    """

    lightPalette = QPalette()

    # base
    lightPalette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
    lightPalette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
    lightPalette.setColor(QPalette.ColorRole.Light, QColor(180, 180, 180))
    lightPalette.setColor(QPalette.ColorRole.Midlight, QColor(200, 200, 200))
    lightPalette.setColor(QPalette.ColorRole.Dark, QColor(225, 225, 225))
    lightPalette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
    lightPalette.setColor(QPalette.ColorRole.BrightText, QColor(0, 0, 0))
    lightPalette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
    lightPalette.setColor(QPalette.ColorRole.Base, QColor(237, 237, 237))
    lightPalette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
    lightPalette.setColor(QPalette.ColorRole.Shadow, QColor(20, 20, 20))
    lightPalette.setColor(QPalette.ColorRole.Highlight, QColor(76, 163, 224))
    lightPalette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
    lightPalette.setColor(QPalette.ColorRole.Link, QColor(0, 162, 232))
    lightPalette.setColor(QPalette.ColorRole.AlternateBase, QColor(225, 225, 225))
    lightPalette.setColor(QPalette.ColorRole.ToolTipBase, QColor(240, 240, 240))
    lightPalette.setColor(QPalette.ColorRole.ToolTipText, QColor(0, 0, 0))
    lightPalette.setColor(QPalette.ColorRole.LinkVisited, QColor(222, 222, 222))

    # disabled
    lightPalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText,
                         QColor(115, 115, 115))
    lightPalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text,
                         QColor(115, 115, 115))
    lightPalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText,
                         QColor(115, 115, 115))
    lightPalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Highlight,
                         QColor(190, 190, 190))
    lightPalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.HighlightedText,
                         QColor(115, 115, 115))

    app.setPalette(lightPalette)

    _apply_base_theme(app)