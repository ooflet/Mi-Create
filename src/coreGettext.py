from PySide6.QtCore import QCoreApplication
import gettext
import sys

# from coreGettext import QCoreApplication

"""
import sys
sys.path.append("..")
from coreGettext import QCoreApplication
"""

_ = gettext.gettext

class QCoreApplication(QCoreApplication):
    @staticmethod
    def loadLanguage(language):
        translation = gettext.translation('window', localedir='locales', languages=[language])
        translation.install()
        global _
        _ = translation.gettext

    @staticmethod
    def translate(context, key, disambiguation):
        with open("locales/window.pot", "a") as file:
            if not "Ctrl" in key:
                return _(key)
            else:
                return key