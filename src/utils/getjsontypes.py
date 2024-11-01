import json

file = "/home/justin/Documents/Watchfaces/ChineseWFExamples/8p_resource_66103622500364.bin/wfDef.json"

propertyList = []
wfDef = json.load(open(file))

for element in wfDef["elementsNormal"]:
    for property in element:
        propertyList.append(property)

print(propertyList)