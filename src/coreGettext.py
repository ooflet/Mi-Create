from PySide6.QtCore import QCoreApplication
import gettext
import sys

# from coreGettext import QCoreApplication

"""
import sys
sys.path.append("..")
from coreGettext import QCoreApplication
"""

class QCoreApplication(QCoreApplication):
    @staticmethod
    def translate(context, key, disambiguation):
        with open("locales/window.pot", "a") as file:
            if not "Ctrl" in key:

                return key
            else:
                return key