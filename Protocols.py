import os

db = os.path.abspath("./Protocols/db.bat")
xml = os.path.abspath("./Protocols/xml.bat")
db_brow = os.path.abspath("./DB_Browser/DB_Browser.exe").replace("\\","\\\\").replace(" ","^ ")

f = open("./Protocols/add_protocols.bat", "w")
f.write("reg add HKEY_CLASSES_ROOT\\db-open /t REG_SZ /d \"URL:DB_Browser\" /f\n")
f.write("reg add HKEY_CLASSES_ROOT\\db-open /v \"URL Protocol\" /t REG_SZ /d \"\" /f\n")
f.write("reg add HKEY_CLASSES_ROOT\\db-open\\DefaultIcon /f\n")
f.write("reg add HKEY_CLASSES_ROOT\\db-open\\DefaultIcon /t REG_SZ /d \"db.bat,1\" /f\n")
f.write("reg add HKEY_CLASSES_ROOT\\db-open\\shell /f\n")
f.write("reg add HKEY_CLASSES_ROOT\\db-open\\shell\\open /f\n")
f.write("reg add HKEY_CLASSES_ROOT\\db-open\\shell\\open\\command /t REG_SZ /d \"\\\"{}\\\" \\\"%%1\\\"\" /f\n\n".format(db))

f.write("reg add HKEY_CLASSES_ROOT\\xml-open /t REG_SZ /d \"URL:Notepad\" /f\n")
f.write("reg add HKEY_CLASSES_ROOT\\xml-open /v \"URL Protocol\" /t REG_SZ /d \"\" /f\n")
f.write("reg add HKEY_CLASSES_ROOT\\xml-open\\DefaultIcon /f\n")
f.write("reg add HKEY_CLASSES_ROOT\\xml-open\\DefaultIcon /t REG_SZ /d \"xml.bat,1\" /f\n")
f.write("reg add HKEY_CLASSES_ROOT\\xml-open\\shell /f\n")
f.write("reg add HKEY_CLASSES_ROOT\\xml-open\\shell\\open /f\n")
f.write("reg add HKEY_CLASSES_ROOT\\xml-open\\shell\\open\\command /t REG_SZ /d \"\\\"{}\\\" \\\"%%1\\\"\" /f\n".format(xml))
f.close()

f = open("./Protocols/db.bat", "w")
f.write("@if (@This==@IsBatch) @then\n")
f.write("wscript //E:JScript \"%~dpnx0\" %1\n")
f.write("exit /b\n")
f.write("@end\n")
f.write("var se = decodeURI(WScript.arguments(0).split(\"db-open:\")[1]);\n")
f.write("WScript.CreateObject(\"WScript.Shell\").Run(\"cmd /C \" + \"{}\" + \" \" + se,0);\n".format(db_brow))
f.write("WScript.Quit(0);\n")
f.close()