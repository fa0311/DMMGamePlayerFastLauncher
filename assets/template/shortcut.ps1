$WshShell = New-Object -ComObject WScript.Shell;
$ShortCut = $WshShell.CreateShortcut("{{SORCE}}");
$ShortCut.TargetPath = "{{TARGET}}";
$ShortCut.WorkingDirectory = "{{WORKING_DIRECTORY}}";
$ShortCut.IconLocation = "{{ICON_LOCATION}}";
$ShortCut.Arguments = "{{ARGUMENTS}}";
$ShortCut.WindowStyle = 1;
$ShortCut.Description = "Made by DMMGamePlayerFastLauncher";
$ShortCut.Save();