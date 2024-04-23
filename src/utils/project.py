# Project Manager for Mi Create
# tostr 2024

# Responsible for saving and loading project formats
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
from lxml import etree

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
            "32":"DigitalNumbers"
        }
        self.watchFileTemplate = {
            "FaceProject": {
                "@DeviceType": "",
                "Screen": {
                    "@Title": "",
                    "@Bitmap": "",
                    "Widget": ""
                }
            }
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
        pass

    def create(self, path, device, name):
        try:
            template = WatchData().watchFileTemplate
            template["FaceProject"]["@DeviceType"] = str(device)
            folder = os.path.join(path, name)
            os.makedirs(os.path.join(folder, "images"))
            os.makedirs(os.path.join(folder, "output"))
            with open(os.path.join(folder, f"{name}.fprj"), "x", encoding="utf8") as fprj:
                rawXml = xmltodict.unparse(template)
                dom = minidom.parseString(rawXml)
                prettyXml = dom.toprettyxml()
                fprj.write(prettyXml)
            return True, os.path.join(folder, f"{name}.fprj")
        except Exception as e:
            return False, str(e), traceback.format_exc()
        
    def formatToKeys(self, widgetList):
        # Format list to dict for fast access
        # Uses the @Name property for the key
        widgetDict = {}
        if widgetList == None:
            return widgetDict
        for widget in widgetList:
            if widgetDict.get(widget["@Name"]):
                return False, "Duplicate widget name!", f"Cannot format {widget['@Name']} because there already is another widget named the same"
            widgetDict[widget["@Name"]] = widget
        return widgetDict
    
    def formatToList(self, widgets):
        # Format dict to list
        widgetList = []
        for widget in widgets:
            widgetList.append(widgets[widget])
        return widgetList

    def load(self, path):
        xml_path = os.path.join(path)

        try:
            with open(xml_path, 'r', encoding="utf8") as project:
                xmlsource = project.read()
                parse = xmltodict.parse(xmlsource)
                print(parse)
                if parse.get("FaceProject"):
                    imagesDir = os.path.join(os.path.dirname(path), "images")
                    if not parse["FaceProject"]["Screen"].get("Widget"):
                        parse["FaceProject"]["Screen"]["Widget"] = []
                    if type(parse["FaceProject"]["Screen"]["Widget"]) == dict:
                        parse["FaceProject"]["Screen"]["Widget"] = [parse["FaceProject"]["Screen"]["Widget"]]

                    parse["FaceProject"]["Screen"]["Widget"] = self.formatToKeys(parse["FaceProject"]["Screen"]["Widget"])

                    print(parse["FaceProject"]["Screen"]["Widget"], parse)

                    return True, parse, imagesDir
                else:
                    return False, "Not a FaceProject!", ""
        except Exception as e:
            return False, str(e), traceback.format_exc()

    def unparse(self, data):
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
    def __init__(self, folder):
        # TODO
        # Get manifest.xml parsed properly and resources
        # Use lxml instead of xmltodict

        # NOTE
        # There are 2 important files
        # - description.xml located at top level
        # - manifest.xml located at /resources
        # description.xml contains, well, descriptions about the watchface
        # manifest.xml contains a list of resources and widgets in the watchface
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
            <Theme type="normal" name="theme1" bg="" isPhotoAlbumWatchface="false" preview="">
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
        description = etree.parse(joinPath(folder, "description.xml"))
        manifest = etree.parse(joinPath(self.resourceFolder, "manifest.xml"))

        # process manifest elements
        self.description = description.getroot()
        self.manifest = manifest.getroot()
        
    def getAllWidgets(self):
        pass

    def getWidget(self, name):
        pass

    def save(self, folder):
        pass