from PyQt6.QtCore import QCoreApplication
import gettext

windowTranslate = gettext.gettext
propertyTranslate = gettext.gettext

class Translator():
    @staticmethod
    def loadLanguage(language):
        windowTranslation = gettext.translation('window', localedir='locales', languages=[language])
        windowTranslation.install()
        global windowTranslate
        windowTranslate = windowTranslation.gettext

        propertyTranslation = gettext.translation('properties', localedir='locales', languages=[language])
        propertyTranslation.install()
        global propertyTranslate
        propertyTranslate = propertyTranslation.gettext

    @staticmethod
    def translate(context, key):
        if not "Ctrl" in key:
            if context == "property":
                return propertyTranslate(key)
            else:
                return windowTranslate(key)
        else:
            return key

class QCoreApplication(Translator): # easily replace existing translate function
    def __init__(self):             # when using Qt Designer
        super().__init__()
