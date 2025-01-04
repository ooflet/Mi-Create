import os
import sys
import shutil
import traceback
import zipfile
from importlib import util
from configparser import ConfigParser
from PyQt6.QtCore import QSettings

libs_folder = "plugins/libs"

if os.path.exists(libs_folder) and libs_folder not in sys.path:
    sys.path.append(libs_folder)

from plugin_api import PluginAPI

class PluginLoader:
    def __init__(self, main_window, ):
        self.settings = QSettings("Mi Create", "Settings")
        self.folder = "plugins"
        self.plugins = {}
        self.main_window = main_window
        self.libs_folder = libs_folder

        PluginAPI().init_globals(main_window, self)

        self.disabledPluginsList = self.settings.value("disabledPlugins")

        if self.disabledPluginsList == None:
            self.disabledPluginsList = []

    def loadPlugins(self):
        self.plugins.clear()

        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

        for plugin_folder in os.listdir(self.folder):
            if plugin_folder != "libs" and os.path.isdir(os.path.join(self.folder, plugin_folder)):
                plugin_folder = os.path.join(self.folder, plugin_folder)

                config_path = os.path.join(plugin_folder, "config.ini")
                config = ConfigParser()
                config.read_file(open(os.path.join(config_path)))
                
                plugin_name = config.get("config", "name")
                plugin_path = os.path.join(plugin_folder, config.get("config", "script"))
                
                install_script_path = os.path.join(plugin_folder, "install.py")

                module = self.loadPlugin(plugin_name, plugin_path)
                
                if plugin_name not in self.disabledPluginsList:
                    if hasattr(module, "register"):
                        module.register()

                if config.get("config", "icon") == "none":
                    icon_path = "none"
                else:
                    icon_path = os.path.join(plugin_folder, config.get("config", "icon"))

                self.plugins[plugin_name] = {
                    "name": config.get("config", "name"),
                    "directory": plugin_folder,
                    "module": module,
                    "icon": icon_path,
                    "version": config.get("config", "version"),
                    "author": config.get("config", "author"),
                    "description": config.get("config", "description")
                }


    def loadPlugin(self, plugin_name, plugin_path):
        spec = util.spec_from_file_location(plugin_name, plugin_path)
        if spec and spec.loader:
            module = util.module_from_spec(spec)
            sys.modules[plugin_name] = module
            spec.loader.exec_module(module)
            if hasattr(module, "__init__"):
                plugin = module.Plugin()
            return plugin
        
    def installPlugin(self, plugin_path):
        config_file = zipfile.Path(plugin_path, at='config.ini')
        
        config = ConfigParser()
        config.read_file(config_file.open())
    
        plugin_name = config.get("config", "name")

        plugin_folder = os.path.join(self.folder, plugin_name)
        os.mkdir(plugin_folder)

        shutil.unpack_archive(plugin_path, plugin_folder, "zip")

        if os.path.isfile(os.path.join(plugin_folder, "install.py")):
            spec = util.spec_from_file_location("install", os.path.join(plugin_folder, "install.py"))
            
            if spec and spec.loader:
                module = util.module_from_spec(spec)
                spec.loader.exec_module(module)
                if hasattr(module, "__init__"):
                    module.install()
        
    def stopPlugins(self):
        for plugin in self.plugins.values():
            if hasattr(plugin["module"], "unregister"):
                plugin["module"].unregister()
            
    def listPlugins(self):
        return list(self.plugins.keys())
    
    def getPluginDisabled(self, plugin_name):
        if plugin_name in self.disabledPluginsList:
            return True
        else:
            return False

    def enablePlugin(self, plugin_name):
        if plugin_name in self.disabledPluginsList:
            self.disabledPluginsList.pop(self.disabledPluginsList.index(plugin_name))
            self.settings.setValue("disabledPlugins", self.disabledPluginsList)

            if hasattr(self.plugins[plugin_name]["module"], "register"):
                self.plugins[plugin_name]["module"].register()

    def disablePlugin(self, plugin_name):
        self.disabledPluginsList.append(plugin_name)
        self.settings.setValue("disabledPlugins", self.disabledPluginsList)
        
        if hasattr(self.plugins[plugin_name]["module"], "unregister"):
            self.plugins[plugin_name]["module"].unregister()
    
    def deletePlugin(self, plugin_name):
        try:
            if os.path.isfile(os.path.join(self.plugins[plugin_name]["directory"], "install.py")):
                spec = util.spec_from_file_location("install", os.path.join(self.plugins[plugin_name]["directory"], "install.py"))
            
                if spec and spec.loader:
                    module = util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    if hasattr(module, "__init__"):
                        module.uninstall()
                
            shutil.rmtree(self.plugins[plugin_name]["directory"])
            return True, "Success"
        except Exception as e:
            return False, traceback.format_exc()
