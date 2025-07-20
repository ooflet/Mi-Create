# Project Classes
# ooflet <ooflet@proton.me>

# Projects are handled with abstractions in the form of classes

# XiaomiProject uses the official Xiaomi watchface format.
# FprjProject uses m0tral's XML format for use with m0tral's compiler.
# GMFProject uses GiveMeFive's JSON based format for use with GMF's compiler

# All project manipulation is done through functions
# There are designated IDs for each property, device type and data source.
# IDs are in the WatchData class

import os
import mmap
import traceback
import logging
import json
import shutil
import xmltodict
import xml

from shutil import which
from typing import List, Optional
from pathlib import Path
from pprint import pprint
from copy import deepcopy
from PyQt6.QtCore import QProcess, QSettings
from PyQt6.QtWidgets import QMessageBox, QInputDialog

from utils.data import WatchData
from utils.binary import WatchfaceBinary
from translate import Translator

supportedOneFileVersion = "1.0"
logging.basicConfig(level=logging.DEBUG)

class ProjectTools:
    def __init__(self):
        pass

class FprjProject:  
    def __init__(self):
        self.watchData = WatchData()

        self.name = None
        self.currentTheme = "default"
        self.themes = {}

        self.deviceIds = {
            "0": "xiaomi_color",
            "1": "xiaomi_color_sport",
            "2": "70mai_saphir",
            "3": "xiaomi_color_2/s1/s2",
            "4": "xiaomi_watch_s1_pro",
            "5": "redmi/poco_watch",
            "6": "xiaomi_band_7_pro",
            "7": "redmi_watch_3",
            "8": "redmi_band_pro",
            "9": "xiaomi_band_8",
            "10": "redmi_watch_2_lite",
            "11": "xiaomi_band_8_pro",
            "12": "redmi_watch_3_active",
            "362": "xiaomi_watch_s3",
            "365": "redmi_watch_4",
            "366": "xiaomi_band_9",
            "367": "xiaomi_band_9_pro",
            "462": "xiaomi_watch_s4",
            "465": "redmi_watch_5",
            "466": "xiaomi_band_10",
            "3651": "redmi_watch_5_active",
            "3652": "redmi_watch_5_lite"
        }

        self.widgetIds = {
            "27": "widget_analog",
            "29": "widget_arc",
            "30": "widget",
            "31": "widget_imagelist",
            "32": "widget_num",
            "34": "widget_container",
            "42": "widget_arc" # progress arc plus, prefer using this
        }

        self.propertyIds = {
            "@Alignment": "num_alignment",
            "@Alpha": "widget_alpha",
            "@Background_ImageName": "widget_background_bitmap",
            "@BgImage_rotate_xc": "analog_bg_anchor_x",
            "@BgImage_rotate_yc": "analog_bg_anchor_y",
            "@Bitmap": "widget_bitmap",
            "@BitmapList": "widget_bitmaplist",
            "@Blanking": "num_toggle_zeros",
            "@Butt_cap_ending_style_En": "arc_flat_caps",
            "@DefaultIndex": "imagelist_default_index",
            "@Digits": "num_digits",
            "@EndAngle": "arc_end_angle",
            "@Foreground_ImageName": "arc_image",
            "@Height": "widget_size_height",
            "@HourHand_ImageName": "analog_hour_image",
            "@HourImage_rotate_xc": "analog_hour_anchor_x",
            "@HourImage_rotate_yc": "analog_hour_anchor_y",
            "@HourHandCorrection_En": "analog_hour_smooth_motion",
            "@Index_Src": "imagelist_source",
            "@Line_Width": "arc_thickness",
            "@MinuteHand_Image": "analog_minute_image",
            "@MinuteImage_rotate_xc": "analog_minute_anchor_x",
            "@MinuteImage_rotate_yc": "analog_minute_anchor_y",
            "@MinuteHandCorrection_En": "analog_minute_smooth_motion",
            "@Name": "widget_name",
            "@Radius": "arc_radius",
            "@Range_Max": "arc_max_value",
            "@Range_Max_Src": "arc_max_value_source",
            "@Range_Min": "arc_min_value",
            "@Range_MinStep": "arc_min_step_value",
            "@Range_Step": "arc_step_value",
            "@Range_Val_Src": "arc_source",
            "@Rotate_xc": "arc_pos_x",
            "@Rotate_yc": "arc_pos_y",
            "@SecondHand_Image": "analog_second_image",
            "@SecondImage_rotate_xc": "analog_second_anchor_x",
            "@SecondImage_rotate_yc": "analog_second_anchor_y",
            "@Shape": "widget_type",
            "@Spacing": "num_spacing",
            "@StartAngle": "arc_start_angle",
            "@Value_Src": "num_source",
            "@Visible_Src": "widget_visiblity_source",
            "@Width": "widget_size_width",
            "@X": "widget_pos_x",
            "@Y": "widget_pos_y",
            "WidgetType": "WidgetType"
        }

        self.defaultItems = {
            "widget_analog": {
                "@Shape":"27",
                "@Name":"",
                "@X":"",
                "@Y":"",
                "@Width":"100",
                "@Height":"100",
                "@Alpha":"255",
                "@Visible_Src":"0",
                "@HourHandCorrection_En":"0",
                "@MinuteHandCorrection_En":"0",
                "@Background_ImageName":"",
                "@BgImage_rotate_xc":"0", 
                "@BgImage_rotate_yc":"0",
                "@HourHand_ImageName":"",
                "@HourImage_rotate_xc":"0",
                "@HourImage_rotate_yc":"0",
                "@MinuteHand_Image":"",
                "@MinuteImage_rotate_xc":"0",
                "@MinuteImage_rotate_yc":"0",
                "@SecondHand_Image":"",
                "@SecondImage_rotate_xc":"0",
                "@SecondImage_rotate_yc":"0"
            },
            "widget": {
                "@Shape":"30",
                "@Name":"",
                "@Bitmap":"",
                "@X":"",
                "@Y":"",
                "@Width":"48",
                "@Height":"48",
                "@Alpha":"255",
                "@Visible_Src":"0"
            },
            "widget_imagelist": {
                "@Shape":"31",
                "@Name":"",
                "@BitmapList":"",
                "@X":"",
                "@Y":"",
                "@Width":"48",
                "@Height":"48",
                "@Alpha":"255",
                "@Alignment":"0",
                "@DefaultIndex":"0",
                "@Value_Src":"0",
                "@Spacing":"0",
                "@Blanking":"0",
                "@Visible_Src":"0"
            },
            "widget_num": {
                "@Shape":"32",
                "@Name":"",
                "@BitmapList":"",
                "@X":"",
                "@Y":"",
                "@Width":"48",
                "@Height":"48",
                "@Alpha":"255",
                "@Visible_Src":"0",
                "@Digits":"1",
                "@Alignment":"0",
                "@Value_Src":"0",
                "@Spacing":"0",
                "@Blanking":"0"
            },
            "widget_container": {
                "@Shape":"34",
                "@Name":"",
                "@X":"0",
                "@Y":"0",
                "@Width":"50",
                "@Height":"50",
                "@Alpha":"255",
                "@Visible_Src":"0"
            },
            "widget_arc": {
                "@Shape":"42",
                "@Name":"",
                "@X":"0",
                "@Y":"0",
                "@Width":"200",
                "@Height":"200",
                "@Alpha":"255",
                "@Visible_Src":"0",
                "@Rotate_xc":"100",
                "@Rotate_yc":"100",
                "@Radius":"75",
                "@Line_Width":"30",
                "@Butt_cap_ending_style_En":"0",
                "@StartAngle":"-120",
                "@EndAngle":"120",
                "@Range_Min":"0",
                "@Range_Max":"100",
                "@Range_MinStep":"0",
                "@Range_Step":"0",
                "@Background_ImageName":"",
                "@Foreground_ImageName":"",
                "@Range_Max_Src":"0",
                "@Range_Val_Src":"0"
            }
        }

        self.watchFileBlank = {
            "FaceProject": {
                "@DeviceType": "",
                "@Id": "",
                "Screen": {
                    "@Title": "",
                    "@Bitmap": "",
                    "Widget": []
                }
            }
        }

    def createBlank(self, path, device, name, theme="default") -> tuple[bool, str, Optional[str]]:
        """
        Creates a blank project in the specified path.

        :return: True and path of the .fprj project if successful, otherwise False, short error message and traceback.
        """
        print("path", path)
        
        try:
            template = deepcopy(self.watchFileBlank)
            aodTemplate = deepcopy(self.watchFileBlank)

            template["FaceProject"]["@DeviceType"] = list(self.deviceIds.keys())[list(self.deviceIds.values()).index(str(device))]
            aodTemplate["FaceProject"]["@DeviceType"] = list(self.deviceIds.keys())[list(self.deviceIds.values()).index(str(device))]

            folder = os.path.join(path, name)

            os.makedirs(os.path.join(folder, "images"))
            os.makedirs(os.path.join(folder, "output"))

            with open(os.path.join(folder, f"{name}.fprj"), "x", encoding="utf8") as fprj:
                xml_string = xmltodict.unparse(template, pretty=True)
                fprj.write(xml_string)

            self.name = f"{name}.fprj"

            self.themes[theme] = {
                "directory": os.path.dirname(path),
                "path": os.path.join(folder, f"{name}.fprj"),
                "data": template,
                "widgets": template["FaceProject"]["Screen"].get("Widget"),
                "imageFolder": os.path.join(folder, "images")
            }

            if theme != "aod":
                self.themes["aod"] = {
                    "directory": "",
                    "path": "",
                    "data": aodTemplate,
                    "widgets": aodTemplate["FaceProject"]["Screen"].get("Widget"),
                    "imageFolder": ""
                }

            return True, os.path.join(folder, f"{name}.fprj")
        except Exception as e:
            return False, str(e), traceback.format_exc()
        
    def createAod(self, ignoreAodCheck=False) -> None:
        """
        Creates an AOD project. Will only work when a project is loaded.

        The compiler handles AODs with a seperate project created in the current one.
        """

        if not ignoreAodCheck and self.themes["aod"]["widgets"] == []:
            return

        # Before proper creation of an AOD, the project creates a temporary AOD theme
        # Copy the data before applying the default template project
        data = deepcopy(self.themes["aod"]["data"])

        # Create blank project in AOD location
        self.createBlank(self.themes["default"]["directory"], self.deviceIds.get(str(self.themes[self.currentTheme]["data"]["FaceProject"]["@DeviceType"])), "AOD", "aod")
        
        # Restore data
        self.themes["aod"]["data"] = data
        self.themes["aod"]["widgets"] = self.themes["aod"]["data"]["FaceProject"]["Screen"]["Widget"]

    def processFprj(self, file) -> dict:
        """
        Process an Fprj project and parse it to a Python dict object.

        :return: dict if success, otherwise False.
        """
        source = file.read()
        parse = xmltodict.parse(source)
        if parse.get("FaceProject"):
            # set widget to a list
            if not parse["FaceProject"]["Screen"].get("Widget"):
                parse["FaceProject"]["Screen"]["Widget"] = []
            if type(parse["FaceProject"]["Screen"]["Widget"]) == dict:
                parse["FaceProject"]["Screen"]["Widget"] = [parse["FaceProject"]["Screen"]["Widget"]]

            # get rid of duplicate items
            seen = set()
            duplicatesRemoved = []
            
            for widget in parse["FaceProject"]["Screen"]["Widget"]:
                # convert shape
                if widget["@Shape"] == "29": # legacy circle progress
                    widget["@Shape"] = "42" # circle progress plus 

                name = widget.get("@Name")
                if name not in seen:
                    seen.add(name)
                    duplicatesRemoved.append(widget)

            parse["FaceProject"]["Screen"]["Widget"] = duplicatesRemoved
            return parse
        else:
            return False

    def load(self, path) -> tuple[bool, str, Optional[str]]:
        """
        Loads an Fprj file and adds it to the project's theme list

        The theme list contains the default (normal) theme and AOD.
        This will eventually also contain other color themes.

        :return: True and the success message, otherwise False, short error message and traceback.
        """

        projectDir = os.path.dirname(path)

        try:
            imagesDir = os.path.join(projectDir, "images")
            
            with open(path, "r", encoding="utf8", errors="replace") as file:
                parse = self.processFprj(file)

            if not parse:
                return False, "Invalid/corrupted fprj project!", "FaceProject root not found"

            self.name = os.path.basename(path)
            self.themes["default"] = {
                "directory": projectDir,
                "path": path,
                "data": parse,
                "widgets": parse["FaceProject"]["Screen"]["Widget"],
                "imageFolder": imagesDir
            }

            aodDir = os.path.join(projectDir, "AOD")

            if os.path.isdir(aodDir):
                for file in os.listdir(aodDir):
                    if file.endswith(".fprj"):
                        aodFile = file
                        break
                else:
                    return False, "no AOD project found!", ""
                    
                with open(os.path.join(aodDir, aodFile), "r", encoding="utf8") as file:
                    aodParse = self.processFprj(file)

                self.themes["aod"] = {
                    "directory": aodDir,
                    "path": os.path.join(aodDir, aodFile),
                    "data": aodParse,
                    "widgets": aodParse["FaceProject"]["Screen"]["Widget"],
                    "imageFolder": os.path.join(aodDir, "images")
                }
            else:
                template = self.watchFileBlank
                template["FaceProject"]["@DeviceType"] = str(self.themes["default"]["data"]["FaceProject"]["@DeviceType"])
                self.themes["aod"] = {
                    "directory": "",
                    "path": "",
                    "data": template,
                    "widgets": template["FaceProject"]["Screen"].get("Widget"),
                    "imageFolder": ""
                }
                
            return True, "Success"
        
        except Exception as e:
            return False, str(e), traceback.format_exc()
        
    def fromBinary(self, outputDir, path, decompilerPath):
        raise NotImplementedError

        logging.info("Decompiling project "+path)
        process = QProcess()
        process.setWorkingDirectory(outputDir)
        process.setProgram(decompilerPath)
        process.setArguments([path])
        process.start()
        process.waitForFinished()
        print(process.readAllStandardOutput())

    def getDirectory(self) -> str:
        """
        Returns a path to the containing folder/directory of the project.
        
        :return: The path to the directory as a string.
        """
        return self.themes[self.currentTheme]["directory"]
    
    def getImageFolder(self) -> str:
        """
        Returns a path to the folder where images are stored.
        
        :return: The path to the directory as a string.
        """
        return self.themes[self.currentTheme]["imageFolder"]
    
    def getPath(self, theme=None) -> str:
        """
        Returns a path to the fprj file.
        
        :return: The path to the file as a string.
        """
        if theme == None:
            return self.themes[self.currentTheme]["path"]
        else:
            return self.themes[theme]["path"]

    def getDeviceType(self) -> str:
        """
        Returns the device the project was made for out of:

        "xiaomi_color"
        "70mai_saphir"
        "xiaomi_color_sport"
        "xiaomi_color_2/s1/s2"
        "xiaomi_watch_s1_pro"
        "redmi/poco_watch"
        "xiaomi_band_7_pro"
        "redmi_watch_3"
        "redmi_band_pro"
        "xiaomi_band_8"
        "redmi_watch_2_lite"
        "xiaomi_band_8_pro"
        "redmi_watch_3_active"
        "xiaomi_watch_s3"
        "redmi_watch_4"
        "xiaomi_band_9"
        
        :return: The DeviceId.
        """
        return self.deviceIds.get(str(self.themes["default"]["data"]["FaceProject"]["@DeviceType"]))
        
    def getAllWidgets(self) -> list:
        """
        Returns a list of FprjWidgets
        
        :return: A list of FprjWidgets
        """
        widgetList = []

        for widget in self.themes[self.currentTheme]["widgets"]:
            widgetList.append(FprjWidget(self, widget))
        
        return widgetList

    def getWidget(self, name):
        """
        Returns an FprjWidget from the name of the widget
        
        :return: An FprjWidget
        """
        widget = list(filter(lambda widget: widget["@Name"] == name, self.themes[self.currentTheme]["widgets"]))
        
        if len(widget) == 0:
            return None
        else:
            return FprjWidget(self, widget[0])
        
    def createWidget(self, id, name, posX, posY, properties):
        widget = self.defaultItems[id].copy()
        widget["@Name"] = name
        
        if properties != None:
            for property, value in properties.items():
                property = [k for k, v in self.propertyIds.items() if v == property]
            
                if len(property) > 0:
                    property = property[0]
                    widget[property] = value

        if posX == "center":
            widget["@X"] = int(self.watchData.modelSize[self.getDeviceType()][0] / 2 - int(widget["@Width"]) / 2)
        else:
            widget["@X"] = posX

        if posY == "center":
            widget["@Y"] = int(self.watchData.modelSize[self.getDeviceType()][1] / 2 - int(widget["@Height"]) / 2)
        else:
            widget["@Y"] = posY

        self.themes[self.currentTheme]["widgets"].append(widget)
        
    def deleteWidget(self, widget):
        for index, item in enumerate(self.themes[self.currentTheme]["widgets"]):
            if item["@Name"] == widget.getProperty("widget_name"):
                self.themes[self.currentTheme]["widgets"].pop(index) 
        
    def restoreWidget(self, widget, index):
        self.themes[self.currentTheme]["widgets"].insert(index, widget.data)

    def appendWidget(self, widget):
        if isinstance(widget, GMFWidget):
            QMessageBox.information(None, "Project", "Cannot paste widgets from another project format. Use the export function to convert one format to another.")
            return
        
        self.themes[self.currentTheme]["widgets"].append(widget.data)

    def addResource(self, file):
        if self.currentTheme == "aod" and os.path.isdir(self.themes["aod"]["imageFolder"]) is not True:
            self.createAod(True)

        destFile = os.path.join(self.themes[self.currentTheme]["imageFolder"], os.path.basename(file))
        if os.path.isfile(destFile):
            result = QMessageBox.question(None, "Resource Importer", f"A resource named '{os.path.basename(destFile)}' already exists. Overwrite?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if result == QMessageBox.StandardButton.Yes:
                os.remove(destFile)
            else:
                return
        shutil.copyfile(file, destFile)

    def addResources(self, files):
        if self.currentTheme == "aod" and os.path.isdir(self.themes["aod"]["imageFolder"]) is not True:
            self.createAod(True)

        for file in files:
            self.addResource(file)

    def removeResource(self, file):
        destFile = os.path.join(self.themes[self.currentTheme]["imageFolder"], os.path.basename(file))
        if os.path.isfile(destFile) is not True:
            QMessageBox.information(None, "Resource Importer", f"File {destFile} does not exist!")
        else:
            os.remove(destFile)

    def setTheme(self, theme):
        self.currentTheme = theme

    def setWidgetLayer(self, widget, layerIndex):        
        self.themes[self.currentTheme]["widgets"].pop(self.themes[self.currentTheme]["widgets"].index(widget.data))
        if layerIndex == "top":
            self.themes[self.currentTheme]["widgets"].append(widget.data)
        else:
            self.themes[self.currentTheme]["widgets"].insert(layerIndex, widget.data)
    
    def getId(self):
        return self.themes["default"]["data"]["FaceProject"].get("@Id") or "167210065"
    
    def getTitle(self):
        return self.themes["default"]["data"]["FaceProject"]["Screen"]["@Title"]
    
    def getThumbnail(self):
        return self.themes["default"]["data"]["FaceProject"]["Screen"]["@Bitmap"]

    def setWidgetPos(self, name, posX, posY):
        widget = list(filter(lambda widget: widget["@Name"] == name, self.themes[self.currentTheme]["widgets"]))

        if len(widget) == 0:
            return "Widget does not exist!"
        else:
            widget[0]["@X"] = posX
            widget[0]["@Y"] = posY
        
    def setDevice(self, value):
        for theme in self.themes.values():
            theme["data"]["FaceProject"]["@DeviceType"] = list(self.deviceIds.keys())[list(self.deviceIds.values()).index(value)]
    
    def setId(self, value):
        self.themes[self.currentTheme]["data"]["FaceProject"]["@Id"] = value

    def setTitle(self, value):
        self.themes[self.currentTheme]["data"]["FaceProject"]["Screen"]["@Title"] = value

    def setThumbnail(self, value):
        self.themes[self.currentTheme]["data"]["FaceProject"]["Screen"]["@Bitmap"] = value

    def toString(self):
        raw = xmltodict.unparse(self.themes[self.currentTheme]["data"])
        dom = xml.dom.minidom.parseString(raw)
        xml_string = dom.toprettyxml()
        return xml_string

    def save(self):
        try:
            if self.themes["aod"]["widgets"] != [] :
                self.createAod()
                pprint(self.themes)
                raw = xmltodict.unparse(self.themes["aod"]["data"])
                dom = xml.dom.minidom.parseString(raw)
                aod_xml_string = dom.toprettyxml()
                with open(self.themes["aod"]["path"], "w", encoding="utf8") as file:
                    file.write(aod_xml_string)

            for theme in self.themes:
                if os.path.isfile(self.themes[theme]["path"]):
                    raw = xmltodict.unparse(self.themes[theme]["data"])
                    dom = xml.dom.minidom.parseString(raw)
                    xml_string = dom.toprettyxml()
                    with open(self.themes[theme]["path"], "w", encoding="utf8") as file:
                        file.write(xml_string)
                
            return True, "success", self.themes["default"]["path"]
            
        except Exception as e:
            return False, e, traceback.format_exc()

    def compile(self, platform, path, location, compilerLocation, id=None):
        logging.info("Compiling project "+path)
        process = QProcess()

        if not os.path.isdir(os.path.join(self.themes["default"]["directory"], "output")):
            os.makedirs(os.path.join(self.themes["default"]["directory"], "output"))

        if platform == "Windows":
            process.setProgram(compilerLocation)
            process.setArguments(["-b", path.replace("/", "\\"), location.replace("/", "\\"), self.getTitle()+".face", "1461256429"])
        elif platform == "Linux":
            process.setProgram(which("wine"))
            process.setArguments([compilerLocation, "-b", path.replace("/", "\\"), location.replace("/", "\\"), self.getTitle()+".face", "1461256429"])
        else:
            return False, "Platform not implemented"

        print(process.arguments())

        process.start()
        return process, "Success"
    
class FprjWidget:
    def __init__(self, project, data):
        self.project: FprjProject = project
        self.data = data
        self.previewData = project.watchData.previewData
    
    def removeAssociation(self):
        # by default, the data that is passed through in the data argument is linked to the source data list/dict
        # removing association means that the data is instead independent as a seperate list
        # so modifications to the widget wont get applied over to the original data list
        self.data = deepcopy(self.data)

    def getSourceName(self):
        if self.data.get("@Shape") == "31":
            dataSource = self.getProperty("imagelist_source")
        elif self.data.get("@Shape") == "32":
            dataSource = self.getProperty("num_source")
        else:
            return
        
        if dataSource == None:
            return

        modelSources = self.project.watchData.modelSourceData[self.project.getDeviceType()]
        try:
            dataSourceName = [source["string"] for source in modelSources if int(source["id_fprj"]) == int(dataSource)]
        except ValueError:
            print(f"ValueError:{dataSource} is not a Integer")
            dataSourceName = ['None']

        if dataSourceName == []:
            return

        return dataSourceName[0]
    
    def getPreviewNumber(self):
        return self.previewData.get(self.getSourceName())
    
    def getProperty(self, property):
        property = [k for k, v in self.project.propertyIds.items() if v == property]
        
        if len(property) > 0:
            property = property[0]
        else:
            return

        if property == "WidgetType":
            return

        if property == "@Shape":
            return self.project.widgetIds.get(self.data.get(property))
        elif property == "@BitmapList":
            bitmapString = self.data[property]

            if bitmapString == "":
                return []

            bitmapList = bitmapString.split("|")

            if self.data.get("@Shape") == "31": # only split colons if its from an imagelist
                for index, item in enumerate(bitmapList):
                    split = item.split(":")
                    if len(split) > 1:
                        split[0] = split[0].strip("()")
                        bitmapList[index] = split

            return bitmapList
        elif property == "@Alignment":
            alignment = ["Left", "Center", "Right"]
            return alignment[int(self.data.get(property))]
        else:
            return self.data.get(property)

    def setProperty(self, property, value):
        print(property)
        property = [k for k, v in self.project.propertyIds.items() if v == property][0]
        if property == "@BitmapList":
            for index, item in enumerate(value):
                if isinstance(item, list): # contains index info
                    item[0] = f"({item[0]})" # add brackets
                    value[index] = ":".join(item)
            value = "|".join(value)
        elif property == "@Alignment":
            alignment = ["Left", "Center", "Right"]
            value = alignment.index(value)
        self.data[property] = value
    
class XiaomiProject:
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
            <Theme type="default" name="default" bg="" isPhotoAlbumWatchface="false" preview="">
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

class GMFProject:
    def __init__(self):
        self.currentTheme = "default"
        self.themes = {}
        self.widgets = None
        self.widgetsAOD = None
        self.watchData = WatchData()

        self.name = None
        self.directory = None
        self.dataPath = None
        self.imageFolder = None

        self.widgetIds = {
            "element": "widget",
            "widge_imagelist": "widget_imagelist",
            "widge_dignum": "widget_num",
            "widge_pointer": "widget_pointer"
        }

        self.propertyIds = {
            "align": "num_alignment",
            "dataSrc": "widget_source",
            "image": "widget_bitmap",
            "imageList": "widget_bitmaplist",
            "maxValue": "pointer_max_value",
            "allAngle": "pointer_max_angle",
            "imageRotateX": "pointer_anchor_x",
            "imageRotateY": "pointer_anchor_y",
            "id": "widget_name",
            "showCount": "num_digits",
            "showZero": "num_toggle_zeros",
            "spacing": "num_spacing",
            "type": "widget_type",
            "width": "widget_size_width", # temporary
            "height": "widget_size_height", # temporary
            "alpha": "widget_alpha", # temporary
            "defaultIndex": "imagelist_default_index", # temporary
            "x": "widget_pos_x",
            "y": "widget_pos_y"
        }

        self.defaultItems = {
            "widget_pointer": {
                "type": "widge_pointer",
                "x": 0,
                "y": 0,
                "dataSrc": "0",
                "image": "image_0001",
                "maxValue": 0,
                "allAngle": 0,
                "imageRotateX": 0,
                "imageRotateY": 0
            },
            "widget": {
                "type": "element",
                "x": 0,
                "y": 0,
                "image": ""
            },
            "widget_imagelist": {
                "type": "widge_imagelist",
                "x": 0,
                "y": 0,
                "dataSrc": "0",
                "imageList": [],
                "imageIndexList": []
            },
            "widget_num": {
                "type": "widge_dignum",
                "x": 0,
                "y": 0,
                "showCount": 1,
                "align": 1,
                "spacing": 0,
                "showZero": False,
                "dataSrc": "0",
                "imageList": []
            }
        }

    def setNameToWidgetList(self, widgetList):
        # applies a Universally Unique identifier for widgets
        # GMF projects dont use names for widgets
        nameList = []

        for widget in widgetList:
            widget["id"] = f"{widget['type']}-{str(nameList.count(widget['type']))}"
            nameList.append(widget["type"])

    def load(self, location):
        projectDir = os.path.dirname(location)
        try:
            with open(location, "r", encoding="utf8") as project:
                projectJson = dict(json.load(project))
                imagesDir = os.path.join(projectDir, "images")
                aodImagesDir = os.path.join(projectDir, "images_aod")
                if projectJson.get("elementsNormal") != None:
                    if not projectJson.get("deviceType"):
                        item, accepted = QInputDialog().getItem(None, "GMFProject", Translator.translate("Project", "Select the device the watchface was made for:"), self.watchData.deviceId, 0, False)
                        if item in self.watchData.deviceId and accepted:
                            projectJson["deviceType"] = item

                    self.setNameToWidgetList(projectJson["elementsNormal"])
                    self.setNameToWidgetList(projectJson["elementsAod"])

                    self.name = os.path.basename(location)

                    self.themes["default"] = {
                        "directory": projectDir,
                        "path": location,
                        "data": projectJson,
                        "widgets": projectJson["elementsNormal"],
                        "imageFolder": imagesDir
                    }

                    self.themes["aod"] = {
                        "directory": projectDir,
                        "path": location,
                        "data": projectJson,
                        "widgets": projectJson["elementsAod"],
                        "imageFolder": aodImagesDir
                    }

                    return True, "Success"
                else:
                    return False, "Invalid/corrupted GMF project!", "elementsNormal not found"

        except Exception as e:
            return False, str(e), traceback.format_exc()
        
    def save(self):
        json_string = json.dumps(self.themes["default"]["data"], indent=4, ensure_ascii=False)
        
        try:
            with open(self.themes["default"]["path"], "w", encoding="utf8") as file:
                file.write(json_string)
            
            return True, "success", ""
            
        except Exception as e:
            return False, e, traceback.format_exc()
        
    def toString(self):
        json_string = json.dumps(self.themes[self.currentTheme]["data"], indent=4)
        return json_string

    def compile(self, platform, path, location, compilerLocation, id=None):
        return False, "Compiler not implemented"


    def getDirectory(self) -> str:
        """
        Returns a path to the containing folder/directory of the project.
        
        :return: The path to the directory as a string.
        """
        return self.themes[self.currentTheme]["directory"]
    
    def getImageFolder(self) -> str:
        """
        Returns a path to the folder where images are stored.
        
        :return: The path to the directory as a string.
        """
        return self.themes[self.currentTheme]["imageFolder"]
    
    def getPath(self, theme=None) -> str:
        """
        Returns a path to the json file.
        
        :return: The path to the file as a string.
        """
        if theme == None:
            return self.themes[self.currentTheme]["path"]
        else:
            return self.themes[theme]["path"]

    def getDeviceType(self) -> str:
        """
        Returns the device the project was made for out of:

        "xiaomi_color"
        "70mai_saphir"
        "xiaomi_color_sport"
        "xiaomi_color_2/s1/s2"
        "xiaomi_watch_s1_pro"
        "redmi/poco_watch"
        "xiaomi_band_7_pro"
        "redmi_watch_3"
        "redmi_band_pro"
        "xiaomi_band_8"
        "redmi_watch_2_lite"
        "xiaomi_band_8_pro"
        "redmi_watch_3_active"
        "xiaomi_watch_s3"
        "redmi_watch_4"
        "xiaomi_band_9"
        
        :return: The DeviceId.
        """
        return self.themes[self.currentTheme]["data"]["deviceType"]
        
    def getWidget(self, name):
        widget = list(filter(lambda widget: widget["id"] == name, self.themes[self.currentTheme]["widgets"]))
        if len(widget) == 0:
            return None
        else:
            return GMFWidget(self, widget[0])

    def getAllWidgets(self, type=None, theme=None):
        widgetList = []
        for widget in self.themes[self.currentTheme]["widgets"]:
            widgetList.append(GMFWidget(self, widget))
        return widgetList

    def createWidget(self, id, name, posX, posY, properties):
        widget = self.defaultItems[id].copy()
        widget["id"] = name
        
        if properties != None:
            for property, value in properties.items():
                property = [k for k, v in self.propertyIds.items() if v == property]
            
                if len(property) > 0:
                    property = property[0]
                    widget[property] = value

        if posX == "center":
            widget["x"] = int(self.watchData.modelSize[self.getDeviceType()][0] / 2 - 40 / 2)
        else:
            widget["x"] = posX

        if posY == "center":
            widget["y"] = int(self.watchData.modelSize[self.getDeviceType()][1] / 2 - 40 / 2)
        else:
            widget["y"] = posY

        self.themes[self.currentTheme]["widgets"].append(widget)
    
    def deleteWidget(self, widget):
        for index, item in enumerate(self.themes[self.currentTheme]["widgets"]):
            if item["id"] == widget.getProperty("widget_name"):
                self.themes[self.currentTheme]["widgets"].pop(index) 

    def restoreWidget(self, widget, index):
        self.themes[self.currentTheme]["widgets"].insert(index, widget.data)

    def appendWidget(self, widget):
        if isinstance(widget, FprjWidget):
            QMessageBox.information(None, "Project", "Cannot paste widgets from another project format. Use the export function to convert one format to another.")
            return
        
        self.themes[self.currentTheme]["widgets"].append(widget.data)

    def setWidgetLayer(self, widget, layerIndex):        
        self.themes[self.currentTheme]["widgets"].pop(self.themes[self.currentTheme]["widgets"].index(widget.data))
        if layerIndex == "top":
            self.themes[self.currentTheme]["widgets"].append(widget.data)
        else:
            self.themes[self.currentTheme]["widgets"].insert(layerIndex, widget.data)

    def setWidgetPos(self, name, posX, posY):
        widget = list(filter(lambda widget: widget["id"] == name, self.themes[self.currentTheme]["widgets"]))

        if len(widget) == 0:
            return "Widget does not exist!"
        else:
            widget[0]["x"] = posX
            widget[0]["y"] = posY

    def addResource(self, files):
        for file in files:
            destFile = os.path.join(self.themes[self.currentTheme]["imageFolder"], os.path.basename(file))
            if os.path.isfile(destFile):
                result = QMessageBox.question(None, "Resource Importer", f"Overwrite {destFile}?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if result == QMessageBox.StandardButton.Yes:
                    os.remove(destFile)
                else:
                    return
            shutil.copyfile(file, destFile)
    
    def getId(self):
        return self.themes[self.currentTheme]["data"].get("@Id") or "167210065"

    def getTitle(self):
        return self.themes[self.currentTheme]["data"]["name"]
    
    def getThumbnail(self):
        return self.themes[self.currentTheme]["data"]["previewImg"]

    def setDevice(self, value):
        self.themes[self.currentTheme]["data"]["deviceType"] = value

    def setId(self, value):
        self.themes[self.currentTheme]["data"]["id"]

    def setTitle(self, value):
        self.themes[self.currentTheme]["data"]["name"] = value

    def setThumbnail(self, value):
        self.themes[self.currentTheme]["data"]["previewImg"] = value

    def setId(self, value):
        self.themes[self.currentTheme]["data"]["id"] = value
    
    def setTheme(self, theme):
        self.currentTheme = theme

class GMFWidget:
    def __init__(self, project, data):
        self.project = project
        self.data = data
        self.previewData = project.watchData.previewData
    
    def removeAssociation(self):
        # by default, the data that is passed through in the data argument is linked to the source data list/dict
        # removing association means that the data is instead independent as a seperate list
        # so modifications to the widget wont get applied over to the original data list
        self.data = deepcopy(self.themes[self.currentTheme]["data"])

    def getProperty(self, property):
        property = [k for k, v in self.project.propertyIds.items() if v == property]
        
        if len(property) > 0:
            property = property[0]
        else:
            return

        if property == "WidgetType":
            return

        if property == "type":
            return self.project.widgetIds.get(self.data.get(property))
        
        elif property == "width":
            return "50"

        elif property == "height":
            return "50"
        
        elif property == "alpha":
            return "255"

        elif property == "defaultIndex":
            return "0"
        
        elif property == "align":
            alignment = ["Right", "Left", "Center"]
            return alignment[int(self.data.get(property))]
        
        elif property == "showZero":
            if self.data.get("showZero") == False:
                return "1"
            else:
                return "0"

        elif property == "imageList":
            bitmapList = self.data[property]
            bitmapListCopy = deepcopy(self.data[property])

            if self.data["type"] == "widge_imagelist":
                if self.data.get("imageIndexList"):   
                    for index, item in enumerate(bitmapList):
                        merge = [self.data["imageIndexList"][index], item]
                        bitmapListCopy[index] = merge
                else:
                    for index, item in enumerate(bitmapList):
                        bitmapListCopy[index] = [index, item]
            
            return bitmapListCopy
        else:
            return self.data.get(property)

    def setProperty(self, property, value):
        property = [k for k, v in self.project.propertyIds.items() if v == property][0]
        print(property, value)

        if property == "imageList":
            if self.data["type"] == "widge_imagelist":
                useImageIndexList = False
                imageList = []
                imageIndexList = []
                
                for index, image in enumerate(value):
                    if index != int(image[0]):
                        useImageIndexList = True

                    imageList.append(image[1])

                # If useImageIndexList flagged, make imageIndexList
                # This must be done so that all images have an entry in imageIndexList
                # otherwise if the first index uses something like "0" then it skips it
                # (we dont want that)
                if useImageIndexList:
                    for imageIndex, image in value:
                        imageIndexList.append(int(imageIndex))
                    self.data["imageIndexList"] = imageIndexList # we set the property here now
                else:
                    if self.data.get("imageIndexList"):
                        self.data.pop("imageIndexList")

                value = imageList
                

        elif property == "showZero":
            if value == "0":
                value = True
            elif value == "1":
                value = False

        elif property == "align":
            alignment = ["Right", "Left", "Center"]
            value = alignment.index(value)

        self.data[property] = value

    def getPreviewNumber(self):
        return self.previewData.get(self.getSourceName())

    def getSourceName(self):
        dataSource = self.getProperty("widget_source")
        
        if dataSource == None:
            return

        modelSources = self.project.watchData.modelSourceData[self.project.getDeviceType()]
        dataSourceName = None

        for source in modelSources:
            if source["id_gmf"] == "":
                if source["id_fprj"] == dataSource:
                    dataSourceName = source["string"]
                    break
            else:
                if source["id_gmf"] == dataSource:
                    dataSourceName = source["string"]
                    break

        return dataSourceName

    
