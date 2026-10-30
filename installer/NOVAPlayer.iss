#define AppName "NOVA Player"
#define AppVersion "1.0"

[Setup]
AppId={{B7D5F3A2-6C41-4E8B-9A57-2D0F1E6C9A10}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=NOVA Player
DefaultDirName={autopf}\NOVA Player
DefaultGroupName=NOVA Player
OutputDir=..\dist
OutputBaseFilename=NOVA-Player-Setup
SetupIconFile=..\assets\icon.ico
UninstallDisplayIcon={app}\NOVA-Player.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "Créer un raccourci sur le Bureau"; GroupDescription: "Raccourcis :"

[Files]
Source: "..\dist\NOVA-Player\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{group}\NOVA Player"; Filename: "{app}\NOVA-Player.exe"
Name: "{autodesktop}\NOVA Player"; Filename: "{app}\NOVA-Player.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\NOVA-Player.exe"; Description: "Lancer NOVA Player"; Flags: nowait postinstall skipifsilent
