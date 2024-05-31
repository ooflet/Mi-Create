# Theme Manager
# tostr 2024

import os

from PyQt6.QtGui import QPalette, QColor, QIcon, QPixmap, QPainter
from PyQt6.QtWidgets import QMessageBox, QProxyStyle
from PyQt6.QtCore import Qt
import logging
import configparser
import json

themeDirectory = "themes"

class Theme:
    def __init__(self):
        self.themes = {}
        self.themeNames = []
        self.currentWelcomePage = ""
        
        config = configparser.ConfigParser()
        logging.debug("Initializing Themes")
        for file in os.listdir(themeDirectory):
            themeFolder = os.path.join(themeDirectory, file)
            if os.path.isdir(themeFolder):
                logging.debug("Themes directory found: "+themeFolder)
                config.read_file(open(os.path.join(themeFolder, "config.ini"), encoding="utf8"))
                with open(os.path.join(themeFolder, "colorScheme.json")) as colorSchemes:
                    schemes = json.load(colorSchemes)
                    self.themes[config.get('config', 'themeName')] = {
                        "themeName": config.get('config', 'themeName'), 
                        "directory": themeFolder,
                        "baseStyle": config.get('theme', 'baseStyle'), 
                        "colorSchemes": schemes,
                        "stylesheet": os.path.join(themeFolder, config.get('theme', 'stylesheet')),
                        "iconFolder": os.path.join(themeFolder, config.get('theme', 'iconFolder'))
                    }
                    if schemes.get("Base"): # no different color schemes for theme
                        self.themeNames.append(config.get('config', 'themeName'))
                    else:
                        for scheme in schemes:
                            self.themeNames.append(f"{config.get('config', 'themeName')} {scheme}")
                                

    def loadTheme(self, app, themeName):
        themeName = themeName.split(" ")

        if not self.themes.get(themeName[0]):
            return False
        theme = self.themes[themeName[0]]

        palette = QPalette()

        if len(themeName) < 2:
            scheme = None
            for colorGroup, colors in theme["colorSchemes"].items():
                for colorRole, color in colors.items():
                    if colorGroup == "Disabled":
                        palette.setColor(QPalette.ColorGroup.Disabled, getattr(QPalette.ColorRole, colorRole), QColor(color[0], color[1], color[2]))
                    else:
                        palette.setColor(getattr(QPalette.ColorRole, colorRole), QColor(color[0], color[1], color[2]))
        else:
            scheme = themeName[1]
            for colorGroup, colors in theme["colorSchemes"][scheme].items():
                for colorRole, color in colors.items():
                    if colorGroup == "Disabled":
                        palette.setColor(QPalette.ColorGroup.Disabled, getattr(QPalette.ColorRole, colorRole), QColor(color[0], color[1], color[2]))
                    else:
                        palette.setColor(getattr(QPalette.ColorRole, colorRole), QColor(color[0], color[1], color[2]))
        
        app.setPalette(palette)

        palette = QPalette()

        QIcon().setThemeSearchPaths([theme["iconFolder"]])

        if scheme:
            QIcon().setThemeName(scheme)
        else:
            QIcon().setThemeName(themeName[0])
                
        if theme["baseStyle"] != "none":
            app.setStyle(theme["baseStyle"])

        with open(theme["stylesheet"]) as stylesheet:
            app.setStyleSheet(stylesheet.read())

        return True