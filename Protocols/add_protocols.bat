reg add HKEY_CLASSES_ROOT\db-open /t REG_SZ /d "URL:DB_Browser" /f
reg add HKEY_CLASSES_ROOT\db-open /v "URL Protocol" /t REG_SZ /d "" /f
reg add HKEY_CLASSES_ROOT\db-open\DefaultIcon /f
reg add HKEY_CLASSES_ROOT\db-open\DefaultIcon /t REG_SZ /d "db.bat,1" /f
reg add HKEY_CLASSES_ROOT\db-open\shell /f
reg add HKEY_CLASSES_ROOT\db-open\shell\open /f
reg add HKEY_CLASSES_ROOT\db-open\shell\open\command /t REG_SZ /d "\"C:\Users\robse\Documents\Extremist-Application\Protocols\db.bat\" \"%%1\"" /f

reg add HKEY_CLASSES_ROOT\xml-open /t REG_SZ /d "URL:Notepad" /f
reg add HKEY_CLASSES_ROOT\xml-open /v "URL Protocol" /t REG_SZ /d "" /f
reg add HKEY_CLASSES_ROOT\xml-open\DefaultIcon /f
reg add HKEY_CLASSES_ROOT\xml-open\DefaultIcon /t REG_SZ /d "xml.bat,1" /f
reg add HKEY_CLASSES_ROOT\xml-open\shell /f
reg add HKEY_CLASSES_ROOT\xml-open\shell\open /f
reg add HKEY_CLASSES_ROOT\xml-open\shell\open\command /t REG_SZ /d "\"C:\Users\robse\Documents\Extremist-Application\Protocols\xml.bat\" \"%%1\"" /f
