# Theme Manager
# ooflet <ooflet@proton.me>

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
        logging.info("Initializing Themes")
        for file in os.listdir(themeDirectory):
            themeFolder = os.path.join(themeDirectory, file)
            if os.path.isdir(themeFolder):
                logging.debug("Themes directory found: "+themeFolder)
                config.read_file(open(os.path.join(themeFolder, "config.ini"), encoding="utf8"))
                self.themes[config.get('config', 'themeName')] = {
                    "themeName": config.get('config', 'themeName'), 
                    "directory": themeFolder,
                    "baseStyle": config.get('theme', 'baseStyle'), 
                    "colorSchemes": json.loads(config.get('theme', 'colorSchemes')),
                    "dataFolder": os.path.join(themeFolder, config.get('theme', 'dataFolder')),
                    "iconFolder": os.path.join(themeFolder, config.get('theme', 'iconFolder'))
                }
                for scheme in json.loads(config.get('theme', 'colorSchemes')):
                    self.themeNames.append(f"{config.get('config', 'themeName')} {scheme}")
                
    def loadTheme(self, app, themeName):
        themeName = themeName.split(" ")

        if not self.themes.get(themeName[0]):
            return False
        theme = self.themes[themeName[0]]

        dataFolder = os.path.join(theme["dataFolder"], themeName[1])

        with open(os.path.join(dataFolder, "colorScheme.json")) as file: 
            colorSchemeJson = json.loads(file.read())

        stylesheet = os.path.join(dataFolder, "style.qss")

        palette = QPalette()

        scheme = themeName[1]
        for colorGroup, colors in colorSchemeJson.items():
            for colorRole, color in colors.items():
                if colorGroup == "Disabled":
                    palette.setColor(QPalette.ColorGroup.Disabled, getattr(QPalette.ColorRole, colorRole), QColor(color[0], color[1], color[2]))
                else:
                    palette.setColor(getattr(QPalette.ColorRole, colorRole), QColor(color[0], color[1], color[2]))
        
        app.setPalette(palette)

        palette = QPalette()

        QIcon().setThemeSearchPaths([theme["iconFolder"]])
        QIcon().setThemeName(themeName[1])
                
        if theme["baseStyle"] != "none":
            app.setStyle(theme["baseStyle"])

        with open(stylesheet) as stylesheetFile:
            app.setStyleSheet(stylesheetFile.read())

        return True