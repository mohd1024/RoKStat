# RoKStat
This program reads the stats of top N players in the kingdom. It can be used with the PC version or with BlueStacks instance via ADB to take screenshots and parses them using the Tesseract OCR.

## Community
For comments, suggestions, and to stay informed about updates, please join our Discord community.

https://discord.gg/egZbTarX6q

## Dependencies

The following tools are required to run this program properly:

- Python.
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)

The following are additional dependencies, only required to use with BlueStacks:
- [Android SDK Platform Tools for Windows (ADB)](https://www.xda-developers.com/install-adb-windows-macos-linux/#adbsetupwindows).
- BlueStacks with ADB enabled.
- [Adb Clipboard](https://play.google.com/store/apps/details?id=ch.pete.adbclipboard): an android app that needs to be installed **inside the BlueStacks instance**.

## Installing Primary Dependencies (Required for use with both PC Version and Bluestack)
- Download and Install the latest Tesseract OCR engine from https://github.com/UB-Mannheim/tesseract/wiki. Follow the installation wizard and **make a note of the installation folder** (where you have **tesseract.exe** installed, the default folder is **C:\Program Files\Tesseract-OCR**).
- Add the installation folder of Tesseract to the **PATH** environment variable. If you have not done this before, you can follow this guide: https://www.computerhope.com/issues/ch000549.htm#windows10.
- Install the required python packages. This code requires, including pytesseract, Pillow, and pure-python-adb. They are available in the file **requirements.txt**. You can install them all at once using the following command:
  ```
  > pip install -r requirements.txt
  ```

## Usage with Graphical User Interface (GUI)

Once all dependencies are installed, run the following command in your terminal to start the GUI
```
> pythonw main-ui.py
```
The following sections provide more information on preparing your environment for a successful scanning.

## Usage with Command Line Interface (CLI)

Run the following command in your terminal:
```
> python main-cli.py [-h] -t TAG -n NUMBER -d DEVICE [-s SERIAL]

This program reads the stats of the top N players in the kindgom. It controls RoK PC Version or BlueStacks instance via ADB to take and parses them using the Tesseract OCR.

optional arguments:
  -h, --help            show this help message and exit
  -t TAG, --tag TAG     The name of the task (for example, KvK-Start, KvK-pass4). It will be used as the name of the output folder.
  -n NUMBER, --number NUMBER
                        How many profiles to read from the top of the list
  -d DEVICE, --device DEVICE
                        Device type: {pc, adb}
  -s SERIAL, --serial SERIAL
                        (Only with adb) Device serial in adb, such as 127.0.0.1:5555
```
The following sections provide more information on preparing your environment for a successful scanning.

## Setup and Run with PC Version (Windows)

No additional dependencies are required to run the script in Windows with RoK PC version. To run the code:
- The Rise of Kingdoms PC version must be running in **Fullscreen** mode before you start scanning.
  - You can select **Fullscreen** in the game Graphics Quality Settings.
  - The Graphics Quality itself must be set to **Very High**.
  - Your display resolution must be **1920x1080**.
  - The account used to scan should not be in the top 300 because you get a different view when you open your own **More Info** page.
  - Navigate to the **Individual Power Ranking** page.
  - **Recommended**: in RoK settings, disable **Kingdom Title Notification**. When this setting is enabled, it will display a notification when someone gets a title, which may interfere with the OCR.
  - **Recommended**: the account used to scan is better be in a low-activity alliance because if you're in an active alliance you get messages when someone launches or cancels a rally, which may interfere with the OCR.
- Keep the game running and start Windows Command Prompt (cmd.exe) to run the code.
  - While the game is running, you can press the Windows key (&#8862;), type "cmd", right click **Command Prompt** to start the game.
  - It is recommended to **Run as Administrator**. If your did not run as administrator, you will be prompted to do so. See the following image.

    ![Run as Administrator](doc-images/cmd-admin.png?raw=true "")


- In the command prompt, run the scanning program in the GUI or CLI mode.
  ```
  # To run in GUI mode
  > pythonw main-ui.py
  ```
  ```
  # To run in CLI mode and scan the top 350 profiles, run the following command. 
  # The option "-d pc" must be provided to use the PC version.
  # The images will be saved in the folder Output/Kvk-Start.
  > python main-cli.py -t "KvK-Start" -n 350 -d pc
  ```
  


## Setup and Run with BlueStacks

### Additional Dependencies

- Download and Install ADB from https://dl.google.com/android/repository/platform-tools-latest-windows.zip. This will download a ZIP file. Simply unzip/decompress the file on your machine and **make a note of the installation folder** (where you have **adb.exe**). 

  For more details on the installation, you can refer to the following page. https://www.xda-developers.com/install-adb-windows-macos-linux/#adbsetupwindows.
- Add the installation folder of ADB to the PATH environment variable. If you have not done this before, you can follow this guide: https://www.computerhope.com/issues/ch000549.htm#windows10.
- Run a BlueStacks instance with the following parameters:
  - Instance Resolution must be set to **1920x1080**.
  - Install the **Adb Clipboard** app on the BlueStacks, you can find it in the **Play** store.
  - Enable Android Debug Bridge (ADB) in the BlueStacks instance settings. See the picture below. Take a note of the ADB device name, which may be **127.0.0.1:5555** or **127.0.0.1:5585** by default. In BlueStacks 5, you will find these settings in the **Advanced** settings page.
  - The account used to scan should not be in the top 300 because you get a different view when you open your own **More Info** page.
  - **Recommended**: in RoK settings, disable **Kingdom Title Notification**. When this setting is enabled, it will display a notification when someone gets a title, which may interfere with the OCR.
  - **Recommended**: the account used to scan is better be in a low-activity alliance because if you're in an active alliance you get messages when someone launches or cancels a rally, which may interfere with the OCR.

    ![BlueStacks ADB Settings](doc-images/bssettings.png?raw=true "Title")

### Running the Script for use with BlueStacks

- Open RoK on the BlueStack instance.
- Navigate to the Individual Power ranking page. You must be at that page before running the code.

  ![Individual Power Ranking](doc-images/powerrank.png?raw=true "Title")

- In the command prompt, run the scanning program in the GUI or CLI mode.
  ```
  # To run in GUI mode
  > pythonw main-ui.py
  ```
  ```
  # To run in CLI mode and scan the top 350 profiles, run the following command. 
  # The option "-d adb" and "-s" must be provided to specify the BlueStacks device. 
  # The images will be saved in the folder Output/Kvk-Start.
  > python main-cli.py -t "KvK-Start" -n 350 -d adb -s "127.0.0.1:5555"
  ```

