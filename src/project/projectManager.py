# Project Manager for Mi Create
# tostr 2023

# Responsible for saving and loading various project formats, such as .mprj & .fprj

import sys
import os
import subprocess
import traceback
import logging
import base64
import json
import xmltodict
import xml.dom.minidom as minidom
from pprint import pprint

loadedProject = None
supportedDialVersion = "1.0"
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
                    "Widget": []
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

class mprjProject:
    def convertFromFprj(path):
        # Converts .fprj to .mprj
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

                    # Write into mprj
                    file = {}

                    try:
                        with open(os.path.splitext(path)[0]+".mprj", "w") as dataFile:
                            file["version"] = "1.0"
                            file["data"] = parse
                            file["imgdata"] = imagesData
                            logging.info(f"Writing data to {os.path.splitext(path)[0]+'.mprj'}")
                            dataFile.write(json.dumps(file, indent=4))
                    except Exception as e:
                        return False, str(e), traceback.format_exc()

                    return True
                else:
                    return False, "Not a FaceProject! Check that the provided files are correct.", "Invalid header (first tag was not FaceProject), check that face.xml is not corrupted"
        except Exception as e:
            return False, str(e), traceback.format_exc()

    def convertToFprj(path, folder):
        # Converts .mprj to .fprj
        try:
            logging.info(f"Opening project {path}")
            with open(path) as dataFile:
                raw = str(dataFile.read())
                data = json.loads(raw)
                if str(data["version"]) <= supportedDialVersion:
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
                    return False, ".mprj format version unsupported!", f"Project version {data['version']} > Supported version {supportedDialVersion}"
        except Exception as e:
            return False, str(e), traceback.format_exc()
        
class fprjProject:  
    def create(path, device, name):
        try:
            path = str.replace(path, "/", "\\")
            template = watchData().watchFileTemplate
            template["FaceProject"]["@DeviceType"] = str(device)
            folder = os.path.join(path, name)
            os.makedirs(os.path.join(folder, "images"))
            os.makedirs(os.path.join(folder, "output"))
            with open(os.path.join(folder, f"{name}.fprj"), "x") as fprj:
                rawXml = xmltodict.unparse(template)
                dom = minidom.parseString(rawXml)
                prettyXml = dom.toprettyxml()
                fprj.write(prettyXml)
            return True, os.path.join(folder, f"{name}.fprj")
        except Exception as e:
            return False, str(e), traceback.format_exc()

    def load(path):
        xml_path = os.path.join(path)
        try:
            with open(xml_path, 'r') as xml:
                # Parse XML, then encode images in /images dir to Base64
                xmlsource = xml.read()
                parse = xmltodict.parse(xmlsource)
                if parse["FaceProject"]:
                    imagesDir = os.path.join(os.path.dirname(path), "images")
                return True, parse, imagesDir, xmlsource
        except Exception as e:
            return False, str(e), traceback.format_exc()

    def save(path):
        pass

    def compile(path, location, compilerLocation):
        logging.info("Compiling project "+path)
        #path = str.replace(location, "/", "\\")
        #location = str.replace(location, "/", "\\")
        result = subprocess.run(f'{compilerLocation} compile "{path}" "{location}" "{str.split(os.path.basename(path), ".")[0]+".face"}" 0', capture_output=True, text=True)
        logging.info(result.stdout)
        return result.stdout

class resourcePackage:
    def unpack(path):
        pass

    def pack(data):
        pass