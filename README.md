# ![MiCreate48x48](https://raw.githubusercontent.com/ooflet/Mi-Create/main/src/resources/MiCreate48x48.png)
### Mi Create
Unofficial watchface and application creator for Xiaomi Wearables.

Compatible with all Xiaomi wearables made ~2021 and above (Devices manufactured by 70mai & Longcheer)

### Features:
- Intuitive and elegant user interface
- Modern control methods
- Powerful integrated text editor
- Language support

### Installation:
Download the latest installer from the [releases](https://github.com/ooflet/Mi-Create/releases) tab.

### Running source code
If there are no prebuilt packages for your OS, you may opt to run directly from source:
- Clone repo
- Install Python version >3.8 & install dependencies through pip: PyQt6, PyQt6-QScintilla, xmltodict, nuitka
- Execute main.py

Executing from source however will not create log files, it will output logs to console.

If you would like to build a package for your platform, use Nuitka as there are some Nuitka-specific checks (specifically the `__compiled__` global check in main.py:36).

### Help
If you are looking for a tutorial on Mi Create, please view the documentation at https://ooflet.github.io/docs. If you have any further questions that are not covered by the documentation, feel free to ask on the [discussions](https://github.com/ooflet/Mi-Create/discussions) tab. Otherwise, if there is a bug or issue with Mi Create, submit an [issue](https://github.com/ooflet/Mi-Create/issues) report.

### Licensing:
Mi Create is licensed under the GPL-3 licence. [View what you can and can't do](https://gist.github.com/kn9ts/cbe95340d29fc1aaeaa5dd5c059d2e60)   
Please note that the compiler & decompiler is made by a third party and is **NOT** open source.