# ASNAAT
Alternative Social Networking Applications Analysis Tool (ASNAAT)

## Setup

### Requirements:
>* Python 3.8+
>* Any Chromium Browser for best results. (Use to open report)

### Download:
>Go to the releases to download either the Windows or Mac versions. 
>* For Mac it is important to put the tool in your users folder (/Users/[Username]/ASNAAT-Mac/).

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
>1. ```$ python Protocols.py```
>2. Run add_protocols.bat as Administrator<br />

If you'd like to remove the added url scheme protocols from the registry run del_protocols.bat as Administrator

### Mac:
>1. ```sh Protocols.sh```
>2. In the "Protocols" folder, drag db_proto and xml_proto to the Macs Applications folder.

If you'd like to remove the added url scheme protocols just delete the files.

## Command line arguments

Executing the tool is very simple and straight forward. 
The tool is setup to use default wordlists in order to provided a tailored report file documenting what we believe to be the most important data for an investigation. However, if you wish to use your own wordlist there is a option to do so. (NOTE: Using your own wordlist will only extract artifacts found. The report won't have a detailed analysis.) The image type that this tool is made for are TAR files. The following options are available:

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
Once the tool is run, a customized report is generated for either Android or Apple. Currently it only supports documentation for the information we deemed important to convey. However, our tool extracts and separates the files defined in the wordlists to a folder named after the case file and image source type (ex: 00001-Apple).
