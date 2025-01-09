import os
import shutil

main_window = None
plugin_loader = None

class PluginAPI:
    def __init__(self):
        self.main_window = main_window
        self.plugin_loader = plugin_loader

    def init_globals(self, window, loader):
        global main_window
        global plugin_loader
        main_window = window
        plugin_loader = loader

    def get_api_version(self):
        return "1.0"

    def get_main_window(self):
        return self.main_window
    
    def get_installed_plugins(self):
        self.plugin_loader.listPlugins()

    def reload_plugins(self):
        self.plugin_loader.loadPlugins()
    
    def show_dialog(self, type, message):
        self.main_window.showDialog(type, message)

    def install_library(self, wheel):
        libs_folder = os.path.join(self.plugin_loader.folder, "libs")
        shutil.unpack_archive(wheel, libs_folder, "zip")

    def delete_library(self, library_name):
        libs_folder = os.path.join(self.plugin_loader.folder, "libs")
        shutil.rmtree(os.path.join(libs_folder, library_name))