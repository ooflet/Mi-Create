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
- Install Python version >3.8 & install dependencies:
`pip install -r requirements.txt` or `python -m pip install -r requirements.txt`
- In the packages folder run `pip install PyQt6_Ads-4.4.1-cp38-abi3-win_amd64.whl` to install the [Qt Advanced Docking System for PyQt6](https://github.com/char101/Qt-Advanced-Docking-System/releases/tag/4.4.1). If you have any expertise in uploading wheels to PyPI, please contribute: <https://github.com/githubuser0xFFFF/Qt-Advanced-Docking-System/issues/556>
- Execute main.py

Executing from source however will not create log files, it will output logs to console.

### Redistribution

I do not mind the program being redistributed, however please link the Github repository somewhere whether it be the post or the description.

Compiling for different programs must be done using Nuitka, there are some specific compiled checks special for Nutika in the program. Plus, Nutika gives an added performance benefit.

If you want to redistrubute the program please do under your own risk. Any issues that arise from the redistribution of the program go towards the maintainer.

There is an automated Github Actions script made for compiling this program, however there are some odd nuances from compilation through the script. Once the artifacts are ironed out, I will add the build script over into this repo.

### Help
If you are looking for a tutorial on Mi Create, please view the documentation at https://ooflet.github.io/docs. If you have any further questions that are not covered by the documentation, feel free to ask on the [discussions](https://github.com/ooflet/Mi-Create/discussions) tab. Otherwise, if there is a bug or issue with Mi Create, submit an [issue](https://github.com/ooflet/Mi-Create/issues) report.

### Licensing:
Mi Create is licensed under the GPL-3 licence. [View what you can and can't do](https://gist.github.com/kn9ts/cbe95340d29fc1aaeaa5dd5c059d2e60)   
Please note that the compiler & decompiler is made by a third party and is **NOT** open source.