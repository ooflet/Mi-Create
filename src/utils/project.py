# Project Manager for Mi Create
# tostr 2023

# Responsible for saving and loading project formats
# Also contains code for fprjOneFile (originally mprj), an unused json based format
# May use fprjOneFile for easy distribution of watchface files? idk

import os
import subprocess
import traceback
import logging
import base64
import json
import xmltodict
import xml
import xml.dom.minidom as minidom

from copy import deepcopy
from PyQt6.QtCore import QProcess

supportedOneFileVersion = "1.0"
logging.basicConfig(level=logging.DEBUG)

class watchData:
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

class fprjProject:  
    def __init__(self):
        pass

    def create(self, path, device, name):
        try:
            template = watchData().watchFileTemplate
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
    
class fprjOneFile:
    def convert(path):
        # Converts .fprj to one file project
        xml_path = os.path.join(path)
        try:
            with open(xml_path, 'r') as xml:
                # Parse XML, then encode images in /images dir to Base64
                logging.info(f"Reading project {path}")
                xmlsource = xml.read()
                parse = xmltodict.parse(xmlsource)
                if parse["FaceProject"]:
                    imagesDir = os.path.join(os.path.dirname(path), "images")
                    imagesData = {}
                    for root, dirs, files in os.walk(imagesDir):
                        for filename in files:
                            file_path = os.path.join(root, filename)
                            with open(file_path, 'rb') as img_file:
                                logging.info(f"Encoding image {filename}")
                                imgData = img_file.read()
                                img_base64 = base64.b64encode(imgData).decode('utf-8')
                                imagesData[filename] = img_base64

                    # Write into file
                    file = {}

                    try:
                        with open(os.path.splitext(path)[0]+".ofprj", "w") as dataFile:
                            file["version"] = "1.0"
                            file["data"] = parse
                            file["imgdata"] = imagesData
                            logging.info(f"Writing data to {os.path.splitext(path)[0]+'.ofprj'}")
                            dataFile.write(json.dumps(file, indent=4))
                    except Exception as e:
                        return False, str(e), traceback.format_exc()

                    return True
                else:
                    return False, "Not a FaceProject! Check that the provided files are correct."
        except Exception as e:
            return False, str(e), traceback.format_exc()

    def unpack(path, folder):
        # Converts one file project to fprj
        try:
            logging.info(f"Opening project {path}")
            with open(path) as dataFile:
                raw = str(dataFile.read())
                data = json.loads(raw)
                if str(data["version"]) <= supportedOneFileVersion:
                    logging.info("Reading data")
                    rawXml = xmltodict.unparse(data["data"])
                    logging.info("Parsing to XML")
                    dom = minidom.parseString(rawXml)
                    prettyXml = dom.toprettyxml()
                    name = data["data"]["FaceProject"]["Screen"]["@Title"]+".fprj"
                    logging.info(f"Writing data to {name}")
                    with open(os.path.join(folder, name), "w") as fprjFile:
                        fprjFile.write(prettyXml)
                    imagesPath = os.path.join(folder, "images")
                    logging.info(f"Creating image directory at {imagesPath}")
                    os.mkdir(imagesPath)
                    for i, v in data["imgdata"].items():
                        logging.info(f"Decoding and writing image {i}")
                        with open(os.path.join(imagesPath, i), "wb") as image:
                            image.write(base64.b64decode(v))
                    logging.info("Creating output folder")
                    os.mkdir(os.path.join(folder, "output"))
                else:
                    return False, "fprjOneFile version unsupported!", f"Project version {data['version']} > Supported version {supportedOneFileVersion}"
        except Exception as e:
            return False, str(e), traceback.format_exc()
        
class NewFormat:
    def load(folder):
        # check all directories are there
        # unfortunately, no mac os support just yet

        # TODO
        # Get manifest.xml parsed properly
        # Use minidom instead of xmltodict

        logging.info("Opening "+folder)

        logging.info("Parsing ")