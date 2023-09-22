# Project Manager for Mi Face Studio
# tostr 2023

# Responsible for saving and loading various project formats, such as .dial & .fprj

"""
About the .dial format:
- The .dial format is an improved version of .fprj.
- The file itself is encoded using json.
- Some parts of the code reference a V1 & V2 version of .dial, this is because it used
  to use a zip archive instead of a json file.
- Once program has been fully released, V1 will have been fully removed.
"""

import os
import traceback
import tempfile
import xmltodict
import xml.dom.minidom as minidom
import json
import shutil
import zipfile
import base64
from pprint import pprint

"""
Usage: 
- Import class by respective names
- Call load() function to unload files onto memory, with .dial projects they'll be extracted to a temp folder
- Call pack() on dialProjects or save() on fprjProjects to save the project. Without calling load this will not work

"""

loadedProject = None
supportedDialVersion = "1.0"

class watchData:
    def __init__(self):
        super().__init__()
    
        self.models = [
            "Xiaomi Watch Color", "Xiaomi Watch Color Sport", "Xiaomi Watch Color 2/s1/s2", "Xiaomi Watch S1 Pro", "Redmi Watch 2", "Xiaomi Smart Band 7 Pro", "Redmi Watch 3", "Redmi Smart Band Pro", "Xiaomi Smart Band 8", "Redmi Watch 3 Active", "Xiaomi Smart Band 8 Pro"
        ]
        self.modelID = {
            0:"Xiaomi Watch Color",
            1:"Xiaomi Watch Color Sport",
            3:"Xiaomi Watch Color 2/s1/s2",
            4:"Xiaomi Watch S1 Pro",
            5:"Redmi Watch 2",
            6:"Xiaomi Smart Band 7 Pro",
            7:"Redmi Watch 3",
            8:"Redmi Smart Band Pro",
            9:"Xiaomi Smart Band 8",
            10:"Redmi Watch 3 Active",
            11:"Xiaomi Smart Band 8 Pro"
        }
        self.shapeId = {
            30:"Image",
            31:"ImageList",
            32:"DigitalNumbers"
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

class dialProject:
    @staticmethod
    def convertFromV0ToV1(path):
        # TODO: Convert function for use with .fprj
        # Converts beta dial projects to dial standard V1
        # Open a temp directory with zip file that will auto close once done
        if zipfile.is_zipfile(path):
            with zipfile.ZipFile(path, 'r') as zip:
                with tempfile.TemporaryDirectory() as tempdir:
                    zip.extractall(tempdir)
                    xml_path = os.path.join(tempdir, "face.xml")
                    try:
                        with open(xml_path, 'r') as xml:
                            # Parse XML, then encode images in /images dir to Base64
                            xmlsource = xml.read()
                            parse = xmltodict.parse(xmlsource)
                            if parse["FaceProject"]:
                                imagesDir = os.path.join(tempdir, "images")
                                imagesData = {}
                                for root, dirs, files in os.walk(imagesDir):
                                    for filename in files:
                                        file_path = os.path.join(root, filename)
                                        with open(file_path, 'rb') as img_file:
                                            imgData = img_file.read()
                                            img_base64 = base64.b64encode(imgData).decode('utf-8')
                                            imagesData[filename] = img_base64

                                # Write into dial V2 standard
                                file = {}

                                try:
                                    with open(path, "w") as dataFile:
                                        file["version"] = "1.0"
                                        file["data"] = parse
                                        file["imgdata"] = imagesData
                                        dataFile.write(json.dumps(file))
                                except Exception as e:
                                    return False, str(e), traceback.format_exc()

                                return True
                            else:
                                return False, "Not a FaceProject! Check that the provided files are correct.", "Invalid header (first tag was not FaceProject), check that face.xml is not corrupted"
                    except Exception as e:
                        return False, str(e), traceback.format_exc()
        else:
            return False, "Project format is invalid!", "Running is_zipfile() onto the path returned False."



    @staticmethod
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
                dataFile.write(json.dumps(file))
                return True, path
        except Exception as e:
            return False, str(e), traceback.format_exc()
        

    @staticmethod
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
                    return False, ".dial format version unsupported!", f"Project version {data['version']} > Supported version {supportedDialVersion}"
        except Exception as e:
            return False, str(e), traceback.format_exc()

    @staticmethod
    def save(path, data):
        # Pack data into a zip file
        pass
       
        
    @staticmethod
    def compile(path, data):
        pass

class fprjProject:
    def load(self, path):
        pass

    def save(self, path):
        pass
