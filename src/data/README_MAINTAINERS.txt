------------------------------------------------------------------------------------------------
ABOUT TRANSLATIONS
------------------------------------------------------------------------------------------------

Translations are done to the 3 required translation files located at the locales folder:

- main.pot
- properties.pot
- window.pot

main.pot contains translation data for main.py. This mostly includes dialogs.
properties.pot contains translation data for properties and property categories.
window.pot contains translation data for "auto-compiled" windows/dialogs.

Translation can be done by using a program like Poedit

DeviceInfo.db is currently not possible to be translated

------------------------------------------------------------------------------------------------
ABOUT DeviceInfo.db
------------------------------------------------------------------------------------------------

DeviceInfo contains information about every compatible device. It is the same from EasyFace.

The program does not use every entry in DeviceInfo. It only uses:
- SRC ID
- DeviceInfo: Type, Name, Width, Height & Radius

Everything else gets ignored because it is either hardcoded or not used at all.

Mi Create can recognize hex strings in source ID and automatically convert it so it's cross
compatible with EasyFace projects.

------------------------------------------------------------------------------------------------
ABOUT properties.json
------------------------------------------------------------------------------------------------

If you would like to translate the properties, translate properties.pot. 
This will go in depth on the structure and layout of properties.json

The properties.json file contains a list of widget properties.

Each widget has it's own "root" named by its ID, and each root contains 2 keys:

- Shape
- properties

The Shape key identifies the name of the shape.

The properties key contains a dictionary containing all the properties.

Individual properties always start with an @, as they identify XML tags which are not present 
in json and Python dictionaries.

Each property contains an array with at most 5 values:

"properties": {
   "Property Category": {
      "@SourcePropertyName": [
         "Property Name",
         "Property Identifier",
         "Fallback Value",
         "Minimum Value"/["Combobox", "List", "Array"],
         "Maximum Value",
      ] 
   }
}

- "properties" is the properties key in a widget
- "Property Category" is a category containing a list of properties. 
- "@SourcePropertyName" is the property tag, which represents the property in XML.
- "Property Name" is the string which gets shown in the properties list.
- "Property Identifier" identifies which property type it is and what input field to display.
  
  The list of identifiers are:
  - disabled (disabled text input)
  - text
  - img
  - int 
  - bool
  - combobox
  - align (alignment values)
  - src (data source dropdown)
  - imglist (for displaying imagelist items)
  - numlist (for displaying Digital Number items)

  imglist is to be used at the end of a property list, because it clears itself and appends
  all image entries to the end of the properties list when refreshing (e.g when image number 
  increases) 

- "Fallback Value" is the value that is set when no value is given in the project file. This 
  value is optional and you can leave it empty.
- "Minimum Value" & "Maximum Value" both identify min and max range for int properties.
- ["Combobox", "List", "Array"] contins an array of a combobox items.

Both Property Category and Property Name get automatically translated to properties.mo

------------------------------------------------------------------------------------------------
ABOUT settings.json
------------------------------------------------------------------------------------------------

settings.json contains configuration values for the program. It uses the same system as
properties.json.

The actual settings are stored in Registry Computer\HKEY_CURRENT_USER\Software\Mi Create\Preferences.