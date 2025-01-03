# Plugin Toolkit
# Create and package plugins 

import os
import shutil
import argparse
import configparser

config_template = """[config]
name = {name}
script = plugin.py
icon = none
version = 1.0
author = {author}
description = Description

[plugin_api]
api_version = 1.0
supported_platforms = ["Windows", "Linux", "Darwin"]
"""

script_template = """# PluginAPI communicates between the plugin and Mi Create
# It is located in the libs folder in your plugins folder
# This allows you to patch the API on runtime
# However this is not recommended
from plugin_api import PluginAPI

class Plugin:
    def __init__(self):
        # Init function gets called upon plugin load immediately
        # It does not take into account whether or not the plugin is disabled
        self.api = PluginAPI()
        self.api.show_dialog("info", "Plugin has been initialized!")

    def register(self):
        # Function is called upon plugin initialization
        # This function is only called when the plugin is not disabled
        self.api.show_dialog("info", f"Hello World! We are running on PluginAPI version {self.api.get_api_version()}")

    def unregister(self):
        # Function called upon disabling a plugin
        # This function only calls when the user disables the plugin
        self.api.show_dialog("info", "Plugin has been disabled!")
"""

def create_plugin(path, name, author):
    print(f"Creating plugin at: {path} with name: {name}")
    folder_path = os.path.join(path, name)
    os.mkdir(os.path.join(path, name))
    with open(os.path.join(folder_path, "config.ini"), "w+") as config:
        config.write(config_template.format(name=name, author=author))
    with open(os.path.join(folder_path, "plugin.py"), 'w+') as script:
        script.write(script_template)

def package_plugin(path, output):
    print(f"Packaging plugin at: {path} to: {output}")
    config = configparser.ConfigParser()
    config.read_file(open(os.path.join(path, "config.ini")))
    name = config.get("config", "name")
    os.chdir(output)
    shutil.make_archive(os.path.join(output, name), "zip", path)
    os.rename(os.path.join(output, f"{name}.zip"), f"{name}.plg")

def main():
    parser = argparse.ArgumentParser(description="Plugin toolkit")
    
    # Define subcommands
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Create subcommand
    create_parser = subparsers.add_parser("create", help="create a plugin scaffold")
    create_parser.add_argument("path", type=str, help="path to the directory to create")
    create_parser.add_argument("name", type=str, help="name of the plugin")
    create_parser.add_argument("author", type=str, help="author of the plugin")
    
    # Package subcommand
    package_parser = subparsers.add_parser("package", help="package a plugin")
    package_parser.add_argument("path", type=str, help="path to the plugin to package")
    package_parser.add_argument("output", type=str, help="path to where the packaged plugin will output")
    
    args = parser.parse_args()

    # Execute based on the command
    if args.command == "create":
        create_plugin(args.path, args.name, args.author)
    elif args.command == "package":
        package_plugin(args.path, args.output)

if __name__ == "__main__":
    main()