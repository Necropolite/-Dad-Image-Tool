#include "generated.iss"

[Setup]
AppId={{E34DE10D-0D32-4D67-8D2A-2C6C5F103A6C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppName}
AppComments={#MyProductDescription}
DefaultDirName={localappdata}\Dad Image Tool
DefaultGroupName=Dad Image Tool
DisableDirPage=yes
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=..\installer-output
OutputBaseFilename=Dad-Image-Tool-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes
RestartApplications=no
AppMutex=Local\DadImageTool-WatchedFolder
UninstallDisplayIcon={app}\Dad Image Tool.exe
SetupLogging=yes
MinVersion=10.0

[Files]
Source: "..\dist\Dad Image Tool\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Dirs]
Name: "{code:GetDropFolder}"
Name: "{code:GetFinishedFolder}"
Name: "{code:GetArchiveFolder}"
Name: "{code:GetAttentionFolder}"

[Icons]
Name: "{autodesktop}\Dad Image Tool"; Filename: "{app}\Dad Image Tool.exe"; WorkingDir: "{app}"; Comment: "Dad Image Tool"
Name: "{autodesktop}\Drop Client Pictures Here"; Filename: "{code:GetDropFolder}"; Comment: "Drop client pictures here for conversion"
Name: "{autostartup}\Dad Image Tool"; Filename: "{app}\Dad Image Tool.exe"; WorkingDir: "{app}"; Comment: "Dad Image Tool"
Name: "{group}\Dad Image Tool"; Filename: "{app}\Dad Image Tool.exe"; WorkingDir: "{app}"
Name: "{group}\Uninstall Dad Image Tool"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\Dad Image Tool.exe"; Description: "Open Dad Image Tool now"; Flags: nowait postinstall skipifsilent

[Code]
procedure ReplaceEnvironmentToken(var Value: string; Token: string; Replacement: string);
begin
  if Replacement <> '' then
    StringChangeEx(Value, Token, Replacement, True);
end;

function GetPicturesFolder(Param: string): string;
var
  Value: string;
begin
  if RegQueryStringValue(
    HKCU,
    'Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders',
    'My Pictures',
    Value
  ) then
  begin
    ReplaceEnvironmentToken(Value, '%USERPROFILE%', ExpandConstant('{%USERPROFILE|}'));
    ReplaceEnvironmentToken(Value, '%OneDrive%', ExpandConstant('{%OneDrive|}'));
    ReplaceEnvironmentToken(Value, '%OneDriveConsumer%', ExpandConstant('{%OneDriveConsumer|}'));
    ReplaceEnvironmentToken(Value, '%OneDriveCommercial%', ExpandConstant('{%OneDriveCommercial|}'));
    Result := Value;
  end
  else
    Result := ExpandConstant('{userprofile}\Pictures');
end;

function GetDataRoot(Param: string): string;
begin
  Result := AddBackslash(GetPicturesFolder('')) + 'Dad Image Tool';
end;

function GetDropFolder(Param: string): string;
begin
  Result := AddBackslash(GetDataRoot('')) + 'Drop Client Pictures Here';
end;

function GetFinishedFolder(Param: string): string;
begin
  Result := AddBackslash(GetDataRoot('')) + 'Finished';
end;

function GetArchiveFolder(Param: string): string;
begin
  Result := AddBackslash(GetDataRoot('')) + 'Originals Archive';
end;

function GetAttentionFolder(Param: string): string;
begin
  Result := AddBackslash(GetDataRoot('')) + 'Needs Attention';
end;
