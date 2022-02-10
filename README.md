# ASNAAT
Alternative Social Networking Applications Analysis Tool (ASNAAT)

## Setup

### Requirements:
>* Python 3.8+
>* Any Chromium Browser for best results. (Use to open report)<br/>
>**NOTE: Don't use Safari**

### Download:
>Go to the releases to download either the Windows or Mac versions.<br/>
>**NOTE: For Mac it is important to put the tool in your users folder "/Users/[Username]/ASNAAT-Mac/".**

### Virtual Environment:
>To setup this tool, it is advised to configure a virtual environment inside the tool directory. To do this, navigate into the tool's main folder and enter the following commands documented below. These commands will setup a virtual environment inside the directory which will allow you to install the dependencies for this tool:<br /><br />
>```$ python -m venv ./virtualenv```<br /><br />
>Use "**python3**" in command if multiple versions of python are installed.

### Activate/Deactivate Environment:

>Windows:<br />
>```$ .\virtualenv\Scripts\activate```<br />
>```$ deactivate                   ```<br /><br />

>Mac:<br />
```$ source ./virtualenv/bin/activate```<br />
```$ deactivate```<br /><br />


### Install Dependencies:
>```$ pip install -r requirements.txt```

## URL Scheme Setup
This adds two custom url scheme protocols (db-open:// and xml-open://). It allows the report to hyperlink SQLite and XML files to open with specific applications.

### Windows:
If your reinstalling, go to the remove section to delete the previous URL schemes.

>1. ```$ python Protocols.py```
>2. Go to **ASNAAT-Windows/Protocols/** folder.
>3. Right click **add_protocols.bat**.
>4. Click on **Run as administrator**.
>5. Press **Yes**, if it asks to allow app to make changes to your device.

To remove:
>1. Go to **ASNAAT-Windows/Protocols/** folder. 
>2. Right click **del_protocols.bat**.
>3. Click on **Run as Administrator**.
>4. Press **Yes**, if it asks to allow app to make changes to your device.<br />
>5. A terminal will pop up asking you to permanently delete both registry keys. Type **y** and press **Enter** for both.

### Mac:
>1. ```$ sh Protocols.sh```
>2. Go to **/Users/[username]/ASNAAT-Mac/Protocols/** folder.
>3. Drag **db_proto** and **xml_proto** to the Macs **Applications** folder.

To remove:
>1. Go to the Macs **Applications** folder.
>2. Delete **db_proto** and **xml_proto**.

## Command line arguments

Executing the tool is very simple and straight forward. 
The tool is setup to use default wordlists in order to provided a tailored report file documenting what we believe to be the most important data for an investigation. The image type that this tool is made for are TAR files. The following options are available:

```bash
Usage:   python ASNAAT.py [options] <inputfile>
Example: python ASNAAT.py -a Apple.tar
Options:
         -h, --help
         -a            apple image tar
         -b            android image tar
```

Upon execution of the tool with the necessary options, the tool will ask for a Case Number and name of Examiner to preserve the chain of custody. Additionally, there is a built in feature to hash the TAR files before and after execution of the tool to ensure that the data has not been tampered.

## Report & Artifact Generation
Once the tool is run, a customized report is generated for either Android or Apple. Currently it only supports documentation for the information we deemed important to convey. However, our tool extracts and separates the files defined in wordlists to a folder named after the case file and image source type (ex: 00001-Apple).
