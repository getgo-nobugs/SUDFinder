# SUDFinder

This repository contains all the artifacts (including the dataset and the tool SUDFinder) in our study.

## Project Directory Structure

```python
home
    |
    | --- Dataset:                      The bug list of 218 bug reports
    | --- SUDFinder:                    The source code of SUDFinder
         |
         | --- start.py:                The entry of RegDroid, which accepts the parameters
         | --- main.py                  The main module of SUDFinder
         | --- executor.py              The execution module of SUDFinder
```

Requirements

    Android SDK: API34
    python 3.8
    We use some libraries (e.g., uiautomator2, androguard, cv2) provided by python, you can add them as prompted, for example:

```python
pips install uiautomator2
```
