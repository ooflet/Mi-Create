# Theme Management

import os

from PyQt6.QtGui import QPalette, QColor, QIcon
from PyQt6.QtWidgets import QMessageBox
import logging
import configparser
import json

themeDirectory = "themes"

class Theme:
    def __init__(self):
        self.themes = {}
        self.themeNames = []
        
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
                    for scheme in schemes:
                        if config.get('config', 'themeName') == "Default":
                            self.themeNames.append(scheme)
                        else:
                            self.themeNames.append(f"{config.get('config', 'themeName')} {scheme}")

    def loadTheme(self, app, themeName):
        themeName = themeName.split(" ")

        print(themeName)
        if len(themeName) < 2:
            if not self.themes.get("Default"):
                raise NameError("No default theme found!")
            elif not self.themes["Default"]["colorSchemes"].get(themeName[0]):
                return False
            theme = self.themes["Default"]
            scheme = themeName[0]
        else:
            if not self.themes.get(themeName[0]) or not self.themes[themeName[0]]["colorSchemes"].get(themeName[1]):
                return False
            theme = self.themes[themeName[0]]
            scheme = themeName[1]

        palette = QPalette()

        for colorGroup, colors in theme["colorSchemes"][scheme].items():
            for colorRole, color in colors.items():
                if colorGroup == "Disabled":
                    palette.setColor(QPalette.ColorGroup.Disabled, getattr(QPalette.ColorRole, colorRole), QColor(color[0], color[1], color[2]))
                else:
                    print(colorRole, color)
                    palette.setColor(getattr(QPalette.ColorRole, colorRole), QColor(color[0], color[1], color[2]))
        
        app.setPalette(palette)

        QIcon().setThemeSearchPaths([theme["iconFolder"]])
        QIcon().setThemeName(scheme)
                
        if theme["baseStyle"] != "none":
            print(theme["baseStyle"])
            app.setStyle(theme["baseStyle"])

        with open(theme["stylesheet"]) as stylesheet:
            app.setStyleSheet(stylesheet.read())

        return True