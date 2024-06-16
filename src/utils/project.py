# Watchface Projects
# ooflet <ooflet@proton.me>

# Projects are handled with abstractions in the form of classes

# XiaomiProject uses the official Xiaomi watchface format.
# FprjProject uses m0tral's XML format for use with m0tral's compiler.
# GMFProject uses GiveMeFive's JSON based format for use with GMF's compiler

# All project manipulation is done through functions
# There are designated IDs for each property, device type and data source.

# Processes like compilation are handled by Qt's QProcess class because it is discreet and robust. 
# If you are planning to port the code over to your own project, make sure you either:
# - install PyQt/PySide libraries if you are fine with the extra bloat
# - port to Python's subprocess

import os
import traceback
import logging
import json
import xmltodict
import xml
import xml.dom.minidom as minidom

from pathlib import Path
from pprint import pprint
from copy import deepcopy
from PyQt6.QtCore import QProcess
from PyQt6.QtWidgets import QMessageBox

supportedOneFileVersion = "1.0"
logging.basicConfig(level=logging.DEBUG)

class WatchData:
    def __init__(self):
        self.models = []
        self.modelID = {}
        self.modelSize = {}
        self.modelSourceList = {}
        self.modelSourceData = {}
        self.deviceId = [
            "xiaomi_color",
            "70mai_saphir",
            "xiaomi_color_sport",
            "xiaomi_color_2/s1/s2",
            "xiaomi_watch_s1_pro",
            "redmi/poco_watch",
            "xiaomi_band_7_pro",
            "redmi_watch_3",
            "redmi_band_pro",
            "xiaomi_band_8",
            "redmi_watch_2_lite",
            "xiaomi_band_8_pro",
            "redmi_watch_3_active",
            "xiaomi_watch_s3",
            "redmi_watch_4",
            "xiaomi_band_9"
        ]
        self.widgetId = [
            "widget"
            "widget_analog"
            "widget_arc"
            "widget_imagelist"
            "widget_num"
        ]
        self.propertyId = [
            "num_alignment",
            "widget_alpha",
            "widget_background_bitmap",
            "analog_bg_anchor_x",
            "analog_bg_anchor_y",
            "widget_bitmap",
            "widget_bitmaplist",
            "num_hide_zeros",
            "imagelist_default_index",
            "num_digits",
            "arc_end_angle",
            "arc_image",
            "widget_size_height",
            "analog_hour_image",
            "analog_hour_anchor_x",
            "analog_hour_anchor_y",
            "analog_hour_smooth_motion",
            "imagelist_source",
            "arc_thickness",
            "analog_minute_image",
            "analog_minute_anchor_x",
            "analog_minute_anchor_y",
            "analog_minute_smooth_motion",
            "widget_name",
            "arc_radius",
            "arc_max_value",
            "arc_max_value_source",
            "arc_min_value",
            "arc_min_step_value",
            "arc_step_value",
            "arc_source",
            "arc_pos_x",
            "arc_pos_y",
            "analog_second_image",
            "analog_second_anchor_x",
            "analog_second_anchor_y",
            "widget_type",
            "num_spacing",
            "arc_start_angle",
            "num_source",
            "widget_visiblity_source",
            "widget_size_width",
            "widget_pos_x",
            "widget_pos_y"
        ]
        self.sourceId = [
            'time_hour',
            'time_hour_low',
            'time_hour_high',
            'time_minute',
            'time_minute_low',
            'time_minute_high',
            'time_second',
            'time_second_low',
            'time_second_high',
            'time_centi_second',
            'time_centi_second_low',
            'time_centi_second_high',
            'date_year',
            'date_year_digit1',
            'date_year_digit2',
            'date_year_digit3',
            'date_year_digit4',
            'date_month',
            'date_month_low',
            'date_month_high',
            'date_day',
            'date_day_low',
            'date_day_high',
            'date_week',
            'date_lunar_year',
            'date_lunar_month',
            'date_lunar_day',
            'date_week_string_short_cn',
            'date_week_string_full_cn',
            'date_week_string_full_pascal_en',
            'date_week_string_full_upper_en',
            'date_week_string_full_lower_en',
            'date_week_string_short_pascal_en',
            'date_week_string_short_upper_en',
            'date_week_string_short_lower_en',
            'date_month_string_short_cn',
            'date_month_string_full_pascal_en',
            'date_month_string_full_upper_en',
            'date_month_string_full_lower_en',
            'date_month_string_short_pascal_en',
            'date_month_string_short_upper_en',
            'date_month_string_short_lower_en',
            'misc_is_am',
            'misc_is_pm',
            'misc_is24_h',
            'health_step_count',
            'health_step_count_digit1',
            'health_step_count_digit2',
            'health_step_count_digit3',
            'health_step_count_digit4',
            'health_step_count_digit5',
            'health_step_progress',
            'health_step_kilo_meter',
            'health_heart_rate',
            'health_heart_rate_zone',
            'health_heart_rate_min',
            'health_heart_rate_max',
            'health_calorie',
            'health_calorie_value',
            'health_calorie_progress',
            'health_stand_count',
            'health_stand_progress',
            'health_oxygen_spo2',
            'health_pressure_index',
            'health_blood_diastolic_pressure_mmhg',
            'health_blood_systolic_pressure_mmhg',
            'health_blood_diastolic_pressure_kpa',
            'health_blood_systolic_pressure_kpa',
            'health_blood_pressure_unit',
            'health_sleep_duration',
            'health_sleep_duration_minute',
            'health_sleep_score',
            'health_sleep_quality',
            'health_sleep_target_progress',
            'health_exercise_duration',
            'health_exercise_progress',
            'health_energy_consumed',
            'health_misc_recovery_time',
            'health_misc_run_power_index',
            'health_misc_today_vitality_value',
            'health_misc_seven_days_vitality_value',
            'weather_current_sun_rise_hour',
            'weather_current_sun_rise_minute',
            'weather_current_sun_set_hour',
            'weather_current_sun_set_minute',
            'weather_temperature_unit',
            'weather_current_temperature',
            'weather_current_temperature_fahrenheit',
            'weather_current_temperature_feel',
            'weather_current_humidity',
            'weather_current_weather',
            'weather_current_wind_direction',
            'weather_current_wind_angle',
            'weather_current_wind_speed',
            'weather_current_wind_level',
            'weather_current_air_quality_index',
            'weather_current_air_quality_level',
            'weather_current_chance_of_rain',
            'weather_current_pressure',
            'weather_current_visibility',
            'weather_current_uv_index',
            'weather_current_dress_index',
            'weather_today_temperature_max',
            'weather_today_temperature_min',
            'weather_today_temperature_max_fahrenheit',
            'weather_today_temperature_min_fahrenheit',
            'weather_tomorrow_temperature_max',
            'weather_tomorrow_temperature_min',
            'weather_tomorrow_temperature_max_fahrenheit',
            'weather_tomorrow_temperature_min_fahrenheit',
            'system_status_battery',
            'system_status_charge',
            'system_status_disturb',
            'system_status_bluetooth',
            'system_status_wifi',
            'system_status_screen_lock',
            'system_sensor_fusion_altitude',
            'app_alarm_hour',
            'app_alarm_minute'
        ]

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
    
class ProjectTools:
    def __init__(self):
        pass

class FprjProject:  
    def __init__(self):
        self.data = None
        self.widgets = None

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
            "@Blanking": "num_hide_zeros",
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
                "@Butt_cap_ending_style_En":"1",
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
                rawXml = xmltodict.unparse(template)
                dom = minidom.parseString(rawXml)
                prettyXml = dom.toprettyxml()
                fprj.write(prettyXml)

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
                    if not parse["FaceProject"]["Screen"].get("Widget"):
                        parse["FaceProject"]["Screen"]["Widget"] = []
                    if type(parse["FaceProject"]["Screen"]["Widget"]) == dict:
                        parse["FaceProject"]["Screen"]["Widget"] = [parse["FaceProject"]["Screen"]["Widget"]]

                    # get rid of duplicate items
                    seen = set()
                    duplicatesRemoved = []
                    for widget in parse["FaceProject"]["Screen"]["Widget"]:
                        t = tuple(widget.items())
                        if t not in seen:
                            seen.add(t)
                            duplicatesRemoved.append(widget)

                    parse["FaceProject"]["Screen"]["Widget"] = duplicatesRemoved

                    self.data = parse
                    self.widgets = parse["FaceProject"]["Screen"]["Widget"]

                    for widget in self.widgets:
                        if widget["@Shape"] == "29": # legacy circle progress
                            widget["@Shape"] == "42" # circle progress plus 
                    
                    self.name = os.path.basename(path)
                    self.directory = projectDir
                    self.dataPath = path
                    self.imageFolder = imagesDir

                    return True, "Success"
                else:
                    return False, "Invalid/corrupted fprj project!", ""
        except Exception as e:
            return False, str(e), traceback.format_exc()
        
    def getDeviceType(self):
        return self.data["FaceProject"]["@DeviceType"]
        
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
        widget["@X"] = posX
        widget["@Y"] = posY
        print(self.widgets)
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
        raw = xmltodict.unparse(self.data)
        dom = xml.dom.minidom.parseString(raw)
        pretty_xml = dom.toprettyxml()

        return pretty_xml

    def save(self):
        raw = xmltodict.unparse(self.data)
        dom = xml.dom.minidom.parseString(raw)
        pretty_xml = dom.toprettyxml()

        try:
            with open(self.dataPath, "w", encoding="utf8") as file:
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
        property = [k for k, v in self.project.propertyIds.items() if v == property][0]
        if property == "WidgetType":
            return

        if property == "@Shape":
            return self.project.widgetIds.get(self.data.get(property))
        elif property == "@BitmapList":
            bitmapString = self.data[property]
            bitmapList = bitmapString.split("|")
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
        pass