# Project Manager for Mi Face Studio
# tostr 2023

# Responsible for saving and loading various formats, such as .dial & .fprj

import os
import tempfile
import xmltodict
import shutil
import zipfile

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
    
        self.watchID = {
            0:"XiaomiWatchColor",
            1:"XiaomiWatchColorSport",
            3:"XiaomiWatchColor2/s1/s2",
            4:"XiaomiWatchS1Pro",
            5:"RedmiWatch2",
            6:"XiaomiSmartBand7Pro",
            7:"RedmiWatch3",
            8:"RedmiSmartBandPro",
            9:"XiaomiSmartBand8"
        }
        self.watchFileTemplate = {
            "FaceProject": {
                "@DeviceType": 9,
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
    def create(path):
        tempdir = tempfile.mkdtemp()
        try:
            faceData = open(os.path.join(tempdir, "face.xml"), "w")
            print(xmltodict.unparse(watchData().watchFileTemplate))
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

    @staticmethod
    def load(path):
        if zipfile.is_zipfile(path):
            with zipfile.ZipFile(path, 'r') as zip:
                with tempfile.TemporaryDirectory() as tempdir:
                    zip.extractall(tempdir)
                    xml_path = os.path.join(tempdir, "face.xml")
                    try:
                        with open(xml_path, 'r') as xml:
                            parse = xmltodict.parse(xml.read())
                            if parse["FaceProject"]:
                                return True, tempdir, parse
                            else:
                                return False, "Invalid header! Check that the provided files are correct."
                    except Exception as e:
                        return False, str(e)
        else:
            return False, "Project format is invalid!"

    @staticmethod
    def pack(path, data):
        tempdir = tempfile.mkdtemp()
        try:
            faceData = open(os.path.join(tempdir, "face.xml"), "w")
            print(xmltodict.unparse(data))
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
