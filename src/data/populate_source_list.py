import xmltodict
import json

xml = []

fprjDeviceIds = {
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

source_list = {}
size_list = {}

with open("DeviceInfo.db", "r") as device_info:
    xml = xmltodict.parse(device_info.read())    

for device in xml["DeviceList"]["DeviceInfo"]:
    device_size_listing = {
        "width": int(device["@Width"]),
        "height": int(device["@Height"]),
        "radius": int(device["@Radius"]),
        "preview": {
            "width": 0,
            "height": 0,
            "radius": 0
        }
    }
    size_list[fprjDeviceIds[device["@Type"]]] = device_size_listing

    source_list[fprjDeviceIds[device["@Type"]]] = []
    for source in device["SourceDataList"]["SRC"]:
        source_listing = {
            "string": source["@Name"],
            "id_fprj": source["@ID"],
            "id_gmf": "",
            "tip": source["@Tip"]
        }
        source_list[fprjDeviceIds[device["@Type"]]].append(source_listing)

with open("sources.json", "w") as source_list_file:
    source_list_file.write(json.dumps(source_list, indent=4))

with open("devices.json", "w") as watch_sizes_file:
    watch_sizes_file.write(json.dumps(size_list, indent=4))
