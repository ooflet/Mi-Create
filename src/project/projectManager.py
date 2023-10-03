# Project Manager for Mi Create
# tostr 2023

# Responsible for saving and loading various project formats, such as .mprj & .fprj

import os
import subprocess
import traceback
import logging
import tempfile
import xmltodict
import xml.dom.minidom as minidom
import json
import base64
from pprint import pprint

loadedProject = None
supportedDialVersion = "1.0"
logging.basicConfig(level=logging.DEBUG)

class watchData:
    def __init__(self):
        super().__init__()
    
        self.models = [
            "Xiaomi Watch Color", "Xiaomi Watch Color Sport", "Xiaomi Watch Color 2/s1/s2", "Xiaomi Watch S1 Pro", "Redmi Watch 2", "Xiaomi Smart Band 7 Pro", "Redmi Watch 3", "Redmi Smart Band Pro", "Xiaomi Smart Band 8", "Redmi Watch 3 Active", "Xiaomi Smart Band 8 Pro"
        ]
        self.modelID = {
            "0":"Xiaomi Watch Color",
            "1":"Xiaomi Watch Color Sport",
            "3":"Xiaomi Watch Color 2/s1/s2",
            "4":"Xiaomi Watch S1 Pro",
            "5":"Redmi Watch 2",
            "6":"Xiaomi Smart Band 7 Pro",
            "7":"Redmi Watch 3",
            "8":"Redmi Smart Band Pro",
            "9":"Xiaomi Smart Band 8",
            "10":"Redmi Watch 3 Active",
            "11":"Xiaomi Smart Band 8 Pro"
        }
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

    def create(path, device):
        # Create a dialproject
        template = watchData().watchFileTemplate
        template["FaceProject"]["@DeviceType"] = str(device)

        file = {}

        try:
            with open(path, "w") as dataFile:
                file["version"] = "1.0"
                file["data"] = template
                file["imgdata"] = ""
                dataFile.write(json.dumps(file, indent=4))
                return True, path
        except Exception as e:
            return False, str(e), traceback.format_exc()

    def load(path):
        # Load data & images into a readable format for the program.
        try:
            with open(path) as dataFile:
                raw = str(dataFile.read())
                data = json.loads(raw)
                if str(data["version"]) <= supportedDialVersion:
                    rawXml = xmltodict.unparse(data["data"])
                    dom = minidom.parseString(rawXml)
                    prettyXml = dom.toprettyxml()
                    return True, data["imgdata"], data["data"], prettyXml
                else:
                    return False, ".mprj format version unsupported!", f"Project version {data['version']} > Supported version {supportedDialVersion}"
        except Exception as e:
            return False, str(e), traceback.format_exc()

    def save(path, data, imgdata):
        try:
            with open(path) as dataFile:
                try:
                    file = {}
                    with open(path, "w") as dataFile:
                        file["version"] = "1.0"
                        file["data"] = data
                        file["imgdata"] = imgdata
                        dataFile.write(json.dumps(file, indent=4))
                        return True, path
                except Exception as e:
                    return False, str(e), traceback.format_exc()
        except Exception as e:
            return False, str(e), traceback.format_exc()

    def compile(path, location, compilerLocation):
        try:
            logging.info(f"Building project {path}...")
            with tempfile.TemporaryDirectory() as folder:
                logging.info(f"Creating virtual environment at {folder}...")
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
                        logging.info(f'{compilerLocation} compile "{os.path.join(folder, name)}" "{location}" "{data["data"]["FaceProject"]["Screen"]["@Title"]+".face"}" 0')
                        result = subprocess.run(f'{compilerLocation} compile "{os.path.join(folder, name)}" "{location}" "{data["data"]["FaceProject"]["Screen"]["@Title"]+".face"}" 0', capture_output=True, text=True)
                        logging.info(result.stdout)
                        return result.stdout
                    else:
                        return f".mprj format version unsupported!\nProject version {data['version']} > Supported version {supportedDialVersion}"
        except Exception as e:
            return traceback.format_exc()
        
class fprjProject:
    def load(self, path):
        pass

    def save(self, path):
        pass

class resourcePackage:
    def unpack(path):
        pass

    def pack(data):
        pass