# Project Manager for Mi Face Studio
# tostr 2023

# Responsible for saving and loading various project formats, such as .dial & .fprj

"""
About the .dial format:
- The .dial format is an improved version of .fprj.
- The file itself is a zip archive, which means that you can rename it to .zip and extract its contents
- While .fprj support was made for it to be cross-compatible with EasyFace, .dial was made so that its 
  more convenient for creators and developers alike to use.
- Also, you can convert the dial project into an fprj project (which is how it gets compiled).
"""

import os
import tempfile
import xmltodict
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
    def create(path, device):
        # Make temporary directory to place data and zip them all up
        tempdir = tempfile.mkdtemp()
        try:
            faceData = open(os.path.join(tempdir, "face.xml"), "w")
            template = watchData().watchFileTemplate
            template["FaceProject"]["@DeviceType"] = str(device)
            faceData.write(xmltodict.unparse(template))
            faceData.close()
            os.mkdir(os.path.join(tempdir, "images"))
            if os.path.isfile(path):
                os.remove(path)
            try:
                output = shutil.make_archive(path, 'zip', tempdir)
                os.rename(output, path)
            except Exception as e:
                return False, str(e)
        finally:
            shutil.rmtree(tempdir)
            return True, path

    @staticmethod
    def load(path):
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
                                pprint(parse)
                                return True, imagesData, parse, xmlsource
                            else:
                                return False, "Not a FaceProject! Check that the provided files are correct."
                    except Exception as e:
                        return False, str(e)
        else:
            return False, "Project format is invalid!"

    @staticmethod
    def pack(path, data):
        # Pack data into a zip file
        tempdir = tempfile.mkdtemp()
        try:
            faceData = open(os.path.join(tempdir, "face.xml"), "w")
            #print(xmltodict.unparse(data))
            faceData.write(xmltodict.unparse(watchData().watchFileTemplate))
            faceData.close()
            os.mkdir(os.path.join(tempdir, "images"))
            try:
                output = shutil.make_archive(path, 'zip', tempdir)
                os.rename(output, path)
    
            except Exception as e:
                return False, str(e)
        finally:
            shutil.rmtree(tempdir)
            return True, path

class fprjProject:
    def load(self, path):
        pass

    def save(self, path):
        pass
