@if (@This==@IsBatch) @then
wscript //E:JScript "%~dpnx0" %1
exit /b
@end
var se = decodeURI(WScript.arguments(0).split("db-open:")[1]);
WScript.CreateObject("WScript.Shell").Run("cmd /C " + "C:\\Users\\robse\\Documents\\Extremist-Application\\DB_Browser\\DB_Browser.exe" + " " + se,0);
WScript.Quit(0);
