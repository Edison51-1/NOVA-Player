#define MyAppName "NOVA Player"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "NOVA Player Project"
#define MyAppExeName "NOVAPlayer.exe"

[Setup]
AppId={{E2D21A5C-1D4B-4DA4-9B28-4A3B10A7A3F2}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\NOVA Player
DefaultGroupName=NOVA Player
OutputDir=.
OutputBaseFilename=NOVAPlayer-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64

[Tasks]
Name: "desktopicon"; Description: "Créer un raccourci sur le Bureau"; GroupDescription: "Raccourcis :"; Flags: unchecked

[Files]
Source: "..\dist\NOVAPlayer\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\NOVA Player"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\NOVA Player"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Lancer NOVA Player"; Flags: postinstall nowait skipifsilent
