from PyQt6.QtCore import QCoreApplication
import gettext

_ = gettext.gettext

class Translator():
    @staticmethod
    def loadLanguage(language):
        translation = gettext.translation('window', localedir='locales', languages=[language])
        translation.install()
        global _
        _ = translation.gettext

    @staticmethod
    def translate(context, key):
        if not "Ctrl" in key:
            return _(key)
        else:
            return key

class QCoreApplication(Translator): # easily replace existing translate function
    def __init__(self):             # when using Qt Designer
        super().__init__()
