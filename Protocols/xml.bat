@if (@This==@IsBatch) @then
wscript //E:JScript "%~dpnx0" %1
exit /b
@end
var se = decodeURI(WScript.arguments(0).split("xml-open:")[1]);
WScript.CreateObject("WScript.Shell").Run("cmd /C notepad.exe " + se,0);
WScript.Quit(0);