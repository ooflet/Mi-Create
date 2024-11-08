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
import traceback
import logging
import json
import shutil
import xmltodict

from pathlib import Path
from pprint import pprint
from copy import deepcopy
from PyQt6.QtCore import QProcess, QSettings
from PyQt6.QtWidgets import QMessageBox, QInputDialog

from utils.data import WatchData
from translate import Translator

supportedOneFileVersion = "1.0"
logging.basicConfig(level=logging.DEBUG)

class ProjectTools:
    def __init__(self):
        pass

class FprjProject:  
    def __init__(self):
        self.data = None
        self.widgets = None
        self.watchData = WatchData()

        self.name = None
        self.directory = None
        self.dataPath = None
        self.imageFolder = None

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
        }

        self.widgetIds = {
            "27": "widget_analog",
            "29": "widget_arc",
            "30": "widget",
            "31": "widget_imagelist",
            "32": "widget_num",
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
                "Screen": {
                    "@Title": "",
                    "@Bitmap": "",
                    "Widget": []
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
                xml_string = xmltodict.unparse(template, pretty=True)
                fprj.write(xml_string)

            self.data = template
            self.widgets = template["FaceProject"]["Screen"].get("Widget")

            self.name = f"{name}.fprj"
            self.directory = os.path.dirname(path)
            self.dataPath = os.path.join(folder, f"{name}.fprj")
            self.imageFolder = os.path.join(folder, "images")

            return True, os.path.join(folder, f"{name}.fprj")
        except Exception as e:
            return False, str(e), traceback.format_exc()
        
    def fromExisting(self, path):
        projectDir = os.path.dirname(path)
        try:
            with open(path, "r", encoding="utf8") as project:
                xmlsource = project.read()
                parse = xmltodict.parse(xmlsource)
                if parse.get("FaceProject"):
                    imagesDir = os.path.join(projectDir, "images")

                    # set widget to a list
                    if not parse["FaceProject"]["Screen"].get("Widget"):
                        parse["FaceProject"]["Screen"]["Widget"] = []
                    if type(parse["FaceProject"]["Screen"]["Widget"]) == dict:
                        parse["FaceProject"]["Screen"]["Widget"] = [parse["FaceProject"]["Screen"]["Widget"]]

                    # get rid of duplicate items
                    seen = set()
                    duplicatesRemoved = []
                    
                    for widget in parse["FaceProject"]["Screen"]["Widget"]:
                        name = widget.get("@Name")
                        if name not in seen:
                            seen.add(name)
                            duplicatesRemoved.append(widget)

                    parse["FaceProject"]["Screen"]["Widget"] = duplicatesRemoved

                    self.data = parse
                    self.widgets = parse["FaceProject"]["Screen"]["Widget"]

                    for widget in self.widgets:
                        if widget["@Shape"] == "29": # legacy circle progress
                            widget["@Shape"] = "42" # circle progress plus 
                    
                    self.name = os.path.basename(path)
                    self.directory = projectDir
                    self.dataPath = path
                    self.imageFolder = imagesDir

                    return True, "Success"
                else:
                    return False, "Invalid/corrupted fprj project!", "FaceProject root not found"
        except Exception as e:
            return False, str(e), traceback.format_exc()
        
    def fromBinary(self, outputDir, path, decompilerPath):
        logging.info("Decompiling project "+path)
        process = QProcess()
        process.setWorkingDirectory(outputDir)
        process.setProgram(decompilerPath)
        process.setArguments([path])
        process.start()
        process.waitForFinished()
        print(process.readAllStandardOutput())
        
    def getDeviceType(self):
        return self.deviceIds.get(str(self.data["FaceProject"]["@DeviceType"]))
        
    def getAllWidgets(self, type=None, theme=None): # type and theme are for theme support someday over the rainbow
        widgetList = []
        for widget in self.widgets:
            widgetList.append(FprjWidget(self, widget))
        return widgetList

    def getWidget(self, name):
        widget = list(filter(lambda widget: widget["@Name"] == name, self.widgets))
        if len(widget) == 0:
            return None
        else:
            return FprjWidget(self, widget[0])
        
    def createWidget(self, id, name, posX, posY):
        widget = self.defaultItems[id].copy()
        widget["@Name"] = name
        if posX == "center":
            widget["@X"] = int(self.watchData.modelSize[self.getDeviceType()][0] / 2 - int(widget["@Width"]) / 2)
        else:
            widget["@X"] = posX

        if posY == "center":
            widget["@Y"] = int(self.watchData.modelSize[self.getDeviceType()][1] / 2 - int(widget["@Height"]) / 2)
        else:
            widget["@Y"] = posY

        self.widgets.append(widget)
        
    def deleteWidget(self, widget):
        for index, item in enumerate(self.widgets):
            if item["@Name"] == widget.getProperty("widget_name"):
                self.widgets.pop(index) 

    def restoreWidget(self, widget, index):
        self.widgets.insert(index, widget.data)

    def appendWidget(self, widget):
        self.widgets.append(widget.data)

    def setWidgetLayer(self, widget, layerIndex):        
        self.widgets.pop(self.widgets.index(widget.data))
        if layerIndex == "top":
            self.widgets.append(widget.data)
        else:
            self.widgets.insert(layerIndex, widget.data)
    
    def getTitle(self):
        return self.data["FaceProject"]["Screen"]["@Title"]
    
    def getThumbnail(self):
        return self.data["FaceProject"]["Screen"]["@Bitmap"]

    def setWidgetPos(self, name, posX, posY):
        widget = list(filter(lambda widget: widget["@Name"] == name, self.widgets))
        if len(widget) == 0:
            return "Widget does not exist!"
        else:
            widget[0]["@X"] = posX
            widget[0]["@Y"] = posY
        
    def setTitle(self, value):
        self.data["FaceProject"]["Screen"]["@Title"] = value

    def setThumbnail(self, value):
        self.data["FaceProject"]["Screen"]["@Bitmap"] = value

    def toString(self):
        xml_string = xmltodict.unparse(self.data, pretty=True)
        return xml_string

    def save(self):
        xml_string = xmltodict.unparse(self.data, pretty=True)

        try:
            with open(self.dataPath, "w", encoding="utf8") as file:
                file.write(xml_string)
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
    
class FprjWidget:
    def __init__(self, project, data):
        self.project = project
        self.data = data
    
    def removeAssociation(self):
        # by default, the data that is passed through in the data argument is linked to the source data list/dict
        # removing association means that the data is instead independent as a seperate list
        # so modifications to the widget wont get applied over to the original data list
        self.data = deepcopy(self.data)

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
        else:
            return self.data.get(property)

    def setProperty(self, property, value):
        property = [k for k, v in self.project.propertyIds.items() if v == property][0]
        if property == "@BitmapList":
            for index, item in enumerate(value):
                if isinstance(item, list): # contains index info
                    item[0] = f"({item[0]})" # add brackets
                    value[index] = ":".join(item)
            value = "|".join(value)
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

class GMFProject:
    def __init__(self):
        self.data = None
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
            "dataSrc": "num_source",
            "image": "widget_bitmap",
            "imageList": "widget_bitmaplist",
            "maxValue": "pointer_max_value",
            "allAngle": "pointer_max_angle",
            "imageRotateX": "pointer_anchor_x",
            "imageRotateY": "pointer_anchor_y",
            "name": "widget_name",
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

    def setNameToWidgetList(self, widgetList):
        # applies a Universally Unique identifier for widgets
        # GMF projects dont use names for widgets
        nameList = []

        for widget in widgetList:
            widget["name"] = f"{widget['type']}-{str(nameList.count(widget['type']))}"
            nameList.append(widget["type"])

    def fromExisting(self, location):
        projectDir = os.path.dirname(location)
        try:
            with open(location, "r", encoding="utf8") as project:
                projectJson = dict(json.load(project))
                imagesDir = os.path.join(projectDir, "images")
                if projectJson.get("elementsNormal"):
                    if not projectJson.get("deviceType"):
                        item, accepted = QInputDialog().getItem(None, "GMFProject", Translator.translate("Project", "Select the device the watchface was made for:"), self.watchData.deviceId, 0, False)
                        if item in self.watchData.deviceId and accepted:
                            projectJson["deviceType"] = item

                    self.setNameToWidgetList(projectJson["elementsNormal"])
                    self.setNameToWidgetList(projectJson["elementsAod"])

                    self.name = os.path.basename(location)
                    self.directory = projectDir
                    self.dataPath = location
                    self.imageFolder = imagesDir

                    self.data = projectJson
                    self.widgets = projectJson["elementsNormal"]
                    self.widgetsAOD = projectJson["elementsAod"]

                    return True, "Success"
                else:
                    return False, "Invalid/corrupted GMF project!", "elementsNormal not found"

        except Exception as e:
            return False, str(e), traceback.format_exc()
        
    def getDeviceType(self):
        return self.data["deviceType"]
    
    def getWidget(self, name):
        widget = list(filter(lambda widget: widget["name"] == name, self.widgets))
        if len(widget) == 0:
            return None
        else:
            return GMFWidget(self, widget[0])

    def getAllWidgets(self, type=None, theme=None):
        widgetList = []
        for widget in self.widgets:
            widgetList.append(GMFWidget(self, widget))
        return widgetList
    
    def getTitle(self):
        return self.data["name"]
    
    def getThumbnail(self):
        return self.data["previewImg"]

class GMFWidget:
    def __init__(self, project, data):
        self.project = project
        self.data = data
    
    def removeAssociation(self):
        # by default, the data that is passed through in the data argument is linked to the source data list/dict
        # removing association means that the data is instead independent as a seperate list
        # so modifications to the widget wont get applied over to the original data list
        self.data = deepcopy(self.data)

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
        if property == "@BitmapList":
            for index, item in enumerate(value):
                if isinstance(item, list): # contains index info
                    item[0] = f"({item[0]})" # add brackets
                    value[index] = ":".join(item)
            value = "|".join(value)
        self.data[property] = value

    