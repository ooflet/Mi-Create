<h2 align="center"> Mi Create </h2>
<p align="center"> Unofficial watchface and application creator for Xiaomi Wearables. Compatible with all Xiaomi wearables made ~2021 and above </p>

<p align="center">
    <img src="images/linux.png" alt="linux">
    <img src="images/windows.png" alt="linux">
</p>

![window](images/window.png)

## There are known issues with the FramelessMainWindow module on Linux. In the meantime, a branch with the FramelessMainWindow module disabled has been created at https://github.com/ooflet/Mi-Create/tree/linux

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
- Execute main.py

Executing from source however will not create log files, it will output logs to console.

### Redistribution

I do not mind the program being redistributed, however please link the Github repository somewhere whether it be the post or the description.

Compiling for different platforms must be done using Nuitka, there are some specific compiled checks special for Nutika in the program. Plus, Nutika gives an added performance benefit.

There is an automated Github Actions script made for compiling this program, however there are some odd nuances from compilation through the script. Once the artifacts are ironed out, I will add the build script over into this repo.

### Help
If you are looking for a tutorial on Mi Create, please view the documentation at https://ooflet.github.io/docs. If you have any further questions that are not covered by the documentation, feel free to ask on the [discussions](https://github.com/ooflet/Mi-Create/discussions) tab. Otherwise, if there is a bug or issue with Mi Create, submit an [issue](https://github.com/ooflet/Mi-Create/issues) report.

### Licensing:
Mi Create is licensed under the GPL-3 licence. [View what you can and can't do](https://gist.github.com/kn9ts/cbe95340d29fc1aaeaa5dd5c059d2e60)   
Please note that the compiler & decompiler is made by a third party and is **NOT** open source.