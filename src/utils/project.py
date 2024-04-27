# Project Classes
# tostr 2024

# ProjectV1 uses the old EasyFace fprj format
# ProjectV2 uses the official Xiaomi watchface format

import os
import subprocess
import traceback
import logging
import base64
import json
import xmltodict
import xml
import xml.dom.minidom as minidom

from pathlib import Path
from pprint import pprint
from copy import deepcopy
from PyQt6.QtCore import QProcess

supportedOneFileVersion = "1.0"
logging.basicConfig(level=logging.DEBUG)

class WatchData:
    def __init__(self):
        super().__init__()
    
        self.models = []
        self.modelID = {}
        self.modelSize = {}
        self.modelSourceList = {}
        self.modelSourceData = {}
        self.shapeId = {
            "27":"AnalogDisplay",
            "30":"Image",
            "31":"ImageList",
            "32":"DigitalNumber"
        }
        dataPath = os.path.join(os.getcwd(), "data", "DeviceInfo.db")

        with open(dataPath, "r") as file:
            deviceInfo = xmltodict.parse(file.read())
            for x in deviceInfo["DeviceList"]["DeviceInfo"]:
                self.models.append(x["@Name"])
                self.modelID[x["@Name"]] = x["@Type"]
                self.modelSize[x["@Type"]] = [int(x["@Width"]), int(x["@Height"]), int(x["@Radius"])]
                self.modelSourceData[x["@Type"]] = x["SourceDataList"]["SRC"]
                self.modelSourceList[x["@Type"]] = []
                for y in x["SourceDataList"]["SRC"]:
                    self.modelSourceList[x["@Type"]].append(y["@Name"])

    def getWatchModel(self, id):
        return self.watchID[id]

class ProjectV1:  
    def __init__(self):
        # TODO
        # Use proper object oriented design

        self.data = None
        self.widgets = None

        self.name = None
        self.directory = None
        self.dataPath = None
        self.imageDirectory = None

        self.watchFileBlank = {
            "FaceProject": {
                "@DeviceType": "",
                "Screen": {
                    "@Title": "",
                    "@Bitmap": "",
                    "Widget": ""
                }
            }
        }

    def fromBlank(self, path, device, name):
        try:
            template = self.watchFileBlank
            template["FaceProject"]["@DeviceType"] = str(device)
            folder = os.path.join(path, name)
            os.makedirs(os.path.join(folder, "images"))
            os.makedirs(os.path.join(folder, "output"))
            with open(os.path.join(folder, f"{name}.fprj"), "x", encoding="utf8") as fprj:
                rawXml = xmltodict.unparse(template)
                dom = minidom.parseString(rawXml)
                prettyXml = dom.toprettyxml()
                fprj.write(prettyXml)

            self.data = template
            self.widgets = template["FaceProject"]["Screen"].get("Widget")

            self.name = os.path.basename(path)
            self.directory = os.path.dirname(path)
            self.dataPath = os.path.join(folder, f"{name}.fprj")
            self.imageDirectory = os.path.join(folder, "images")

            return True, os.path.join(folder, f"{name}.fprj")
        except Exception as e:
            return False, str(e), traceback.format_exc()
        
    def fromExisting(self, path):
        projectDir = os.path.dirname(path)
        try:
            with open(path, 'r', encoding="utf8") as project:
                xmlsource = project.read()
                parse = xmltodict.parse(xmlsource)
                print(parse)
                if parse.get("FaceProject"):
                    imagesDir = os.path.join(projectDir, "images")
                    if not parse["FaceProject"]["Screen"].get("Widget"):
                        parse["FaceProject"]["Screen"]["Widget"] = []
                    if type(parse["FaceProject"]["Screen"]["Widget"]) == dict:
                        parse["FaceProject"]["Screen"]["Widget"] = [parse["FaceProject"]["Screen"]["Widget"]]

                    self.data = parse
                    self.widgets = parse["FaceProject"]["Screen"].get("Widget")
                    
                    self.name = os.path.basename(path)
                    self.directory = projectDir
                    self.dataPath = path
                    self.imageDirectory = imagesDir

                    return True, "Success"
                else:
                    return False, "Not a FaceProject!", ""
        except Exception as e:
            return False, str(e), traceback.format_exc()
        
    def getDeviceType(self):
        return self.data["FaceProject"]["@DeviceType"]
        
    def getAllWidgets(self, type=None, theme=None): # type and theme are for theme support sometime over the rainbow
        return self.widgets
    
    def getWidget(self, name):
        return [ self.widgets for widget in self.widgets if widget.get("@Name") == name ]
    
    def getProperty(self, name, property):
        widget = [ self.widgets for widget in self.widgets if widget.get("@Name") == name ]
        return widget[property]
    
    def getTitle(self):
        return self.data["FaceProject"]["Screen"]["@Title"]

    def setProperty(self, name, property, value):
        widget = [ self.widgets for widget in self.widgets if widget.get("@Name") == name ]
        widget[property] = value
        
    def setTitle(self, value):
        self.data["FaceProject"]["Screen"] = value

    def toString(self, data):
        raw = xmltodict.unparse(data)
        dom = xml.dom.minidom.parseString(raw)
        pretty_xml = dom.toprettyxml()

        return pretty_xml

    def save(self, path, data: dict):
        rawdata = deepcopy(data)
        print(rawdata)
        rawdata["FaceProject"]["Screen"]["Widget"] = self.formatToList(rawdata["FaceProject"]["Screen"]["Widget"])
        print(rawdata)

        raw = xmltodict.unparse(rawdata)
        dom = xml.dom.minidom.parseString(raw)
        pretty_xml = dom.toprettyxml()

        try:
            with open(path, "w", encoding="utf8") as file:
                file.write(pretty_xml)
            return True, "success"
            
        except Exception as e:
            return False, e        

    def compile(self, path, location, compilerLocation):
        logging.info("Compiling project "+path)
        process = QProcess()
        process.setProgram(compilerLocation)
        process.setArguments(["compile", path, location, str.split(os.path.basename(path), ".")[0]+".face", "0"])
        process.start()
        return process
    
    def decompile(self, path, location, compilerLocation):
        logging.info("Decompiling project "+path)
        process = QProcess()
        process.setWorkingDirectory(location)
        process.setProgram(compilerLocation)
        process.setArguments(path)
        process.start()
        return process
    
# ProjectV2 uses proper OOP instead of half assed static functions
class ProjectV2:
    def __init__(self):
        # TODO
        # Get manifest.xml parsed properly and resources

        # NOTE
        # There are 2 important files
        # - description.xml located at top level
        # - manifest.xml located at /resources

        self.descriptionBlank = """
        <?xml version="1.0" encoding="utf-8"?>
        <watch>
            <name></name>
            <deviceType></deviceType>
            <version>5.0</version>
            <pkgName></pkgName>
            <size></size>
            <author></author>
            <description></description>
            <romVersion>1</romVersion>
            <imageCompression>true</imageCompression>
            <watchFaceLanguages>false</watchFaceLanguages>
            <langData></langData>
            <_recolorEnable>false</_recolorEnable>
            <recolorTable>undefined</recolorTable>
            <nameCHT></nameCHT>
            <nameEN></nameEN>
        </watch>
        """

        self.manifestBlank = """
        <?xml version="1.0" encoding="utf-8"?>
        <Watchface width="" height="" editable="false" id="" _recolorEnable="" recolorTable="" compressMethod="" name="">
            <Resources>
            </Resources>
            <Theme type="normal" name="default" bg="" isPhotoAlbumWatchface="false" preview="">
            </Theme>
        </Watchface>
        """
        
        self.description = None
        self.manifest = None
        
    def fromBlank(self):
        pass
        
    def fromExisting(self, folder):
        def joinPath(path, file):
            # on the rare off chance that windows does not like forward slashes, just replace all forward slashes
            # with backslashes
            return path+"/"+file

        logging.info("Opening "+folder)

        # Get file locations

        # folders
        self.previewFolder = joinPath(folder, "preview")
        self.resourceFolder = joinPath(folder, "resources")

        logging.info("Parsing description.xml & manifest.xml")

        # xml source files
        with open(joinPath(folder, "description.xml"), "r", encoding="utf8") as descFile:
            self.description = xmltodict.parse(descFile.read())

        with open(joinPath(self.resourceFolder, "manifest.xml"), "r", encoding="utf8") as manifestFile:
            self.manifest = xmltodict.parse(manifestFile.read())["Watchface"]

    def getResource(self, name):
        return 
        
    def getAllWidgets(self, type, theme):
        pprint(self.manifest)
        return self.manifest["Theme"]

    def getWidget(self, theme, name):
        widgets = self.manifest["Theme"]["Layout"]
        return [ widgets for widget in widgets if widget.get(name) == theme ]

    def save(self, folder):
        pass