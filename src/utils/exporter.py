# https://github.com/Pzqqt/Fprj_to_wfDef

import os
import re
import json
import shutil
import sys

from PyQt6.QtWidgets import QMessageBox

from bs4 import BeautifulSoup
from PIL import Image

import lxml

del lxml

def remove_path(path: str):
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.isfile(path):
        os.remove(path)

def mkdir(path: str):
    remove_path(path)
    os.makedirs(path)

class FprjConverter:
    def __init__(self, src_dir: str, dst_dir: str, device_type: str):
        self.src_dir = src_dir
        self.dst_dir = dst_dir
        self.device_type = device_type
        self.fprj_info = self.parse_fprj_dir(src_dir)

    @staticmethod
    def rm_subfix(file_name: str) -> str:
        return file_name.rsplit('.', 1)[0]

    @staticmethod
    def switch_alignment_value(val: int) -> int:
        # EasyFace: 0: left, 1: center, 2: right
        # WatchfacePackTool: 0: right, 1: left, 2: center
        if val == 0:
            return 1
        if val == 1:
            return 2
        if val == 2:
            return 0
        else:
            QMessageBox.critical(None, "fprjConverter", "switch_alignment_value: ValueError")

    @staticmethod
    def split_bitmap_list(bitmap: str) -> list:
        files = bitmap.split('|')
        if not re.match(r'\((\d+)\):(.+)', files[0]):
            return files
        files_group = []
        for file in files:
            if re_match := re.match(r'\((\d+)\):(.+)', file):
                files_group.append(
                    (int(re_match.group(1)), re_match.group(2))
                )
        return sorted(files_group)

    @classmethod
    def parse_fprj_dir(cls, fprj_dir: str) -> dict:
        fprj_info = {
            "conf_file": "",
            "images": [],
            "aod": None,
        }
        for filename in os.listdir(fprj_dir):
            file_path = os.path.join(fprj_dir, filename)
            if os.path.isfile(file_path) and filename.endswith(".fprj"):
                fprj_info["conf_file"] = os.path.join(fprj_dir, filename)
            elif os.path.isdir(file_path) and filename == "images":
                fprj_info["images"] = os.listdir(file_path)
            elif os.path.isdir(file_path) and filename == "AOD":
                fprj_info["aod"] = cls.parse_fprj_dir(file_path)
        return fprj_info

    def parse_fprj_conf_file(self):
        info_dic = {}

        fprj_conf_file = self.fprj_info["conf_file"]
        with open(fprj_conf_file, 'r', encoding='utf-8') as f:
            bs_obj = BeautifulSoup(f.read(), features="xml")
        info_dic["name"] = bs_obj.FaceProject.Screen["Title"]
        info_dic["id"] = bs_obj.FaceProject.get("Id", "167210065")
        info_dic["deviceType"] = self.device_type
        info_dic["previewImg"] = self.rm_subfix(bs_obj.FaceProject.Screen["Bitmap"])

        def _parse_elements(fprj_conf_file_, bs_obj_):
            elements = []
            append_images = {
                # `widget name`: `image file name`,
            }
            for widget in bs_obj_.select("FaceProject > Screen > Widget"):
                widget_info = {}

                widget_name = widget["Name"]
                element_type = ""
                if widget["Shape"] == "30":
                    element_type = "element"
                elif widget["Shape"] == "31":
                    element_type = "widge_imagelist"
                elif widget["Shape"] == "32":
                    element_type = "widge_dignum"
                elif widget["Shape"] == "27":
                    pointer_props = {
                        "Hour":   {"image": "HourHand_ImageName", "dataSrc": "0811", "maxValue": 24, "allAngle": 7200},
                        "Minute": {"image": "MinuteHand_Image",   "dataSrc": "1011", "maxValue": 60, "allAngle": 3600},
                        "Second": {"image": "SecondHand_Image",   "dataSrc": "1811", "maxValue": 60, "allAngle": 3600,  "interval": 16},
                    }
                    if bg_hand_image := widget.get("Background_ImageName"):
                        QMessageBox.warning(None, "fprjConverter", "Warning: Does not support rotatable background image: " + bg_hand_image)
                    for pointer in ("Hour", "Minute", "Second"):
                        if not (pointer_hand_image := widget.get(pointer_props[pointer]["image"])):
                            continue
                        pointer_hand_image_path = os.path.join(
                            os.path.dirname(fprj_conf_file_), "images", pointer_hand_image
                        )
                        with Image.open(pointer_hand_image_path) as img:
                            pointer_hand_image_width = img.width
                            pointer_hand_image_height = img.height

                        img_rx = int(widget.get(pointer + "Image_rotate_xc", 0))
                        img_ry = int(widget.get(pointer + "Image_rotate_yc", 0))
                        elements.append({
                            "type": "widge_pointer",
                            "x": int(widget.get("X", 0)) + int(widget.get("Height", 0)) // 2 - img_rx, 
                            "y": int(widget.get("Y", 0)) + int(widget.get("Width", 0)) // 2 - img_ry,
                            "dataSrc": pointer_props[pointer]["dataSrc"],
                            "image": self.rm_subfix(pointer_hand_image),
                            "maxValue": pointer_props[pointer]["maxValue"],
                            "allAngle": pointer_props[pointer]["allAngle"],
                            "imageRotateX": img_rx,
                            "imageRotateY": img_ry,
                            "pointerUnknow25" : 0,
                            "pointerUnknow26" : 0,
                        })
                        print(elements) 
                        if "1811" in elements[-1].values():
                           elements[-1].update({
                               "interval" : pointer_props[pointer]["interval"],
                           })

                    QMessageBox.warning(None, "fprjConverter", 
                    """Warning: EasyFace always assumes that the pointer is in the exact center of the screen.
                    You may need to adjust the pointer component's coordinates after this."""
                    )
                    continue
                if not element_type:
                    QMessageBox.warning(None, "fprjConverter", "Warning: Invalid Widget: '%s', element type: %s" % (widget_name, widget["Shape"]))
                    continue

                if re.match(r'.*?_angle\[\d+\]$', widget_name):
                    QMessageBox.warning(None, "fprjConverter", "Warning: The rotation angle of widget '%s' will be ignored." % widget_name)

                if re_match := re.match(r'.*?_ref\[(.*?)\]$', widget_name):
                    append_images[re_match.group(1)] = self.rm_subfix(widget.get("Bitmap", ""))
                    continue

                # Attrs
                widget_info["_orig_name"] = widget_name
                widget_info["type"] = element_type
                widget_info["x"] = int(widget["X"])
                widget_info["y"] = int(widget["Y"])
                if element_type == "widge_imagelist":
                    widget_info["dataSrc"] = widget["Index_Src"]
                    if widget["Index_Src"] in ("10911", "1000911"):
                        widget_info["dataSrc"] = "0A11"
                    elif widget["Index_Src"] in ("11911", "1001911"):
                        widget_info["dataSrc"] = "1A11"
                elif element_type == "widge_dignum":
                    widget_info["showCount"] = int(widget["Digits"])
                    widget_info["align"] = self.switch_alignment_value(int(widget["Alignment"]))
                    widget_info["showZero"] = not bool(int(widget["Blanking"]))
                    widget_info["dataSrc"] = widget["Value_Src"]
                    widget_info["spacing"] = int(widget["Spacing"])

                # Images
                if element_type == "element":
                    widget_info["image"] = self.rm_subfix(widget.get("Bitmap", ""))
                elif element_type == "widge_imagelist":
                    image_list = self.split_bitmap_list(widget.get("BitmapList"))
                    assert image_list and isinstance(image_list[0], tuple)
                    widget_info["imageList"] = [self.rm_subfix(f_[1]) for f_ in image_list]
                    widget_info["imageIndexList"] = [f_[0] for f_ in image_list]
                elif element_type == "widge_dignum":
                    image_list = self.split_bitmap_list(widget.get("BitmapList"))
                    assert image_list and isinstance(image_list[0], str)
                    widget_info["imageList"] = [self.rm_subfix(f_) for f_ in image_list]

                # Correct X coordinate
                if element_type == "widge_dignum":
                    if widget_info["align"] in (0, 2):
                        sample_file = widget_info["imageList"][0]
                        images_dir = os.path.join(os.path.dirname(fprj_conf_file_), "images")
                        for f__ in os.listdir(images_dir):
                            if f__.startswith(sample_file+'.'):
                                sample_file = f__
                                break
                        with Image.open(os.path.join(images_dir, sample_file)) as img:
                            width = img.width
                        len_ = widget_info["showCount"] * (width + widget_info["spacing"]) - widget_info["spacing"]
                        if widget_info["align"] == 0:
                            widget_info["x"] += len_
                        elif widget_info["align"] == 2:
                            widget_info["x"] += int(len_ / 2)
                        print("Info: Correct X coordinate for %s element." % widget_name)
                elements.append(widget_info)

            for widget_name, image in append_images.items():
                for element in elements:
                    if element["type"] == "widge_dignum" and element["_orig_name"] == widget_name:
                        element["image"] = image
                        break
            for element in elements:
                if element.get("_orig_name"):
                    del element["_orig_name"]
            return elements

        info_dic["elementsNormal"] = _parse_elements(fprj_conf_file, bs_obj)

        info_dic["elementsAod"] = []

        if self.fprj_info["aod"]:
            fprj_conf_file = self.fprj_info["aod"]["conf_file"]
            with open(fprj_conf_file, 'r', encoding='utf-8') as f:
                bs_aod_obj = BeautifulSoup(f.read(), features="xml")
            info_dic["elementsAod"] = _parse_elements(fprj_conf_file, bs_aod_obj)

        return info_dic

    def make(self):
        if not (self.fprj_info["conf_file"] and self.fprj_info["images"]):
            QMessageBox.critical(None, "fprjConverter", "Invalid project!")
            return False
        mkdir(self.dst_dir)
        shutil.copytree(os.path.join(self.src_dir, "images"), os.path.join(self.dst_dir, "images"))
        if os.path.isdir(os.path.join(self.src_dir, "AOD", "images")):
            shutil.copytree(os.path.join(self.src_dir, "AOD", "images"), os.path.join(self.dst_dir, "images_aod"))
        else:
            mkdir(os.path.join(self.dst_dir, "images_aod"))
        with open(os.path.join(self.dst_dir, "wfDef.json"), 'w', encoding='utf-8') as f:
            json.dump(self.parse_fprj_conf_file(), f, indent=4, ensure_ascii=False)
        return True
