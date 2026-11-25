; DroidKit — Inno Setup script (Windows installer)
; Build (after PyInstaller folder build):
;   iscc /DMyAppVersion=0.1.0 /DMyAppExeDir=..\dist\DroidKit installer\droidkit.iss
; Defaults below work when run from repo root via scripts\build_windows.ps1

#ifndef MyAppVersion
  #define MyAppVersion "0.0.0"
#endif
#ifndef MyAppExeDir
  #define MyAppExeDir "..\dist\DroidKit"
#endif

[Setup]
AppId={{8F3C2A19-5D4E-4B7A-9C11-D4A11B0E0001}
AppName=DroidKit
AppVersion={#MyAppVersion}
AppPublisher=DroidKit
DefaultDirName={autopf}\DroidKit
DefaultGroupName=DroidKit
DisableProgramGroupPage=yes
OutputDir=..\dist
OutputBaseFilename=DroidKit-Setup-{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\DroidKit.exe
PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "{#MyAppExeDir}\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{group}\DroidKit"; Filename: "{app}\DroidKit.exe"
Name: "{autodesktop}\DroidKit"; Filename: "{app}\DroidKit.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\DroidKit.exe"; Description: "{cm:LaunchProgram,DroidKit}"; Flags: nowait postinstall skipifsilent
