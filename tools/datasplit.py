import os
from pprint import pprint
os.chdir(os.path.dirname(os.path.realpath(__file__)))

def camel_to_snake(camel_case_string):
   snake_case_string = ""
   for i, c in enumerate(camel_case_string):
      if i == 0:
         snake_case_string += c.lower()
      elif c.isupper():
         snake_case_string += "_" + c.lower()
      else:
         snake_case_string += c

   return snake_case_string

with open("data.txt", "r") as f:
    rawDataList = f.read().splitlines()
    dataList = []
    for data in rawDataList:
        dataString = data.split(" ")
        dataList.append(camel_to_snake(dataString[1]))
    pprint(dataList)

