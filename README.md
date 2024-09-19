# SUDFinder

This repository contains all the artifacts (including the dataset and the tool SUDFinder) in our study.

## Project Directory Structure

```
home
    |
    | --- Dataset:                      The bug list of 218 SUD bug reports
    | --- SUDFinder:                    The source code of SUDFinder
         |
         | --- main.py                  The main module of SUDFinder
         | --- executor.py              The execution module of SUDFinder
```

## Requirements

Android SDK: API level 34

python 3.8

We use some libraries (e.g., uiautomator2, androguard, cv2) provided by python, you can add them as prompted, for example:

```python
pips install uiautomator2
```
## Setting up

You can create an emulator before running SUDFinder. See this link for how to create avd using avdmanager. The following sample command will help you create an emulator, which will help you to start using SUDFinder quickly：

```
sdkmanager "system-images;android-34;google_apis;x86"
avdmanager create avd --force --name Android1 --package 'system-images;android-34;google_apis;x86' --abi google_apis/x86 --sdcard 512M --device "pixel_xl"
```

Next, you can start two identical emulators and assign their port numbers with the following commands:

```
emulator -avd Android1 -read-only -port 5554
emulator -avd Android1 -read-only -port 5556
```

Run
If you have downloaded our project and configured the environment, you only need to enter download_path/tool/SUDFinder to execute our sample app with the following command:

```
python3 start.py -app_path ./AmazeFileManager-3.7.1.apk -append_device emulator-5554 -append_device emulator-5556
```
