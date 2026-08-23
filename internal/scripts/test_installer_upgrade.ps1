param(
    [Parameter(Mandatory = $true)]
    [string]$CandidateInstaller,

    [string]$Repository = $env:GITHUB_REPOSITORY
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

if (-not $Repository) {
    throw "Repository must be supplied or GITHUB_REPOSITORY must be set."
}

$candidate = (Resolve-Path $CandidateInstaller).Path
$previousDir = Join-Path $env:RUNNER_TEMP "dad-image-tool-previous-release"
Remove-Item $previousDir -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $previousDir -Force | Out-Null

function Invoke-Setup {
    param([Parameter(Mandatory = $true)][string]$Path)

    $process = Start-Process -FilePath $Path -ArgumentList "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/CLOSEAPPLICATIONS" -Wait -PassThru
    if ($process.ExitCode -ne 0) {
        throw "Setup failed with exit code $($process.ExitCode): $Path"
    }
}

function Assert-PathExists {
    param([Parameter(Mandatory = $true)][string]$Path, [Parameter(Mandatory = $true)][string]$Message)
    if (-not (Test-Path $Path)) { throw $Message }
}

function Assert-PathMissing {
    param([Parameter(Mandatory = $true)][string]$Path, [Parameter(Mandatory = $true)][string]$Message)
    if (Test-Path $Path) { throw $Message }
}

# The latest published release is the real predecessor of a pre-release candidate.
# Using GitHub rather than a second copy of the candidate makes this an actual
# upgrade test instead of a repair-install test.
$releaseJson = gh api "repos/$Repository/releases/latest"
if ($LASTEXITCODE -ne 0) {
    throw "Could not query the latest published Dad Image Tool release."
}
$previousRelease = $releaseJson | ConvertFrom-Json
$previousTag = [string]$previousRelease.tag_name
if (-not $previousTag) {
    throw "Latest published release did not contain a tag name."
}

Write-Host "Testing upgrade from published release $previousTag"
gh release download $previousTag --repo $Repository --pattern "Dad-Image-Tool-Setup.exe" --dir $previousDir --clobber
if ($LASTEXITCODE -ne 0) {
    throw "Could not download the previous published installer for $previousTag."
}
$previousInstaller = Join-Path $previousDir "Dad-Image-Tool-Setup.exe"
Assert-PathExists $previousInstaller "Previous published installer was not downloaded."

Invoke-Setup $previousInstaller

$installedRoot = Join-Path $env:LOCALAPPDATA "Dad Image Tool"
$installedExe = Join-Path $installedRoot "Dad Image Tool.exe"
Assert-PathExists $installedExe "Previous Dad Image Tool release did not install correctly."

$picturesRoot = [Environment]::GetFolderPath("MyPictures")
$dataRoot = Join-Path $picturesRoot "Dad Image Tool"
$finishedDir = Join-Path $dataRoot "Finished"
$historyFile = Join-Path $dataRoot "job-history.jsonl"
New-Item -ItemType Directory -Path $finishedDir -Force | Out-Null

$dataMarker = "ci-data-preservation-$([Guid]::NewGuid().ToString('N'))"
$historyMarker = "ci-history-preservation-$([Guid]::NewGuid().ToString('N'))"
$userData = Join-Path $finishedDir "upgrade-preservation.txt"
Set-Content -Path $userData -Value $dataMarker -Encoding utf8
Add-Content -Path $historyFile -Value ('{"ci_marker":"' + $historyMarker + '"}') -Encoding utf8

# Seed files that must disappear when the candidate replaces the old runtime.
$staleRuntime = Join-Path $installedRoot "_internal\obsolete-runtime.tmp"
New-Item -ItemType Directory -Path (Split-Path $staleRuntime) -Force | Out-Null
Set-Content -Path $staleRuntime -Value "obsolete runtime" -Encoding ascii
$staleUpdate = Join-Path $installedRoot "Dad Image Tool.exe.update"
$staleBackup = Join-Path $installedRoot "Dad Image Tool.exe.backup"
Set-Content -Path $staleUpdate -Value "obsolete update" -Encoding ascii
Set-Content -Path $staleBackup -Value "obsolete backup" -Encoding ascii

$oldLearningLab = Join-Path $installedRoot "_internal\learning_lab"
$oldLearningLabWasPresent = Test-Path $oldLearningLab

Invoke-Setup $candidate

Assert-PathMissing $staleRuntime "Upgrade left an obsolete runtime file behind."
Assert-PathMissing $staleUpdate "Upgrade left an obsolete updater file behind."
Assert-PathMissing $staleBackup "Upgrade left an obsolete backup file behind."
if ($oldLearningLabWasPresent) {
    Assert-PathMissing $oldLearningLab "Upgrade left the removed Learning Lab bundle behind."
}
Assert-PathExists $installedExe "Upgraded Dad Image Tool executable was not found."
Assert-PathExists $userData "Upgrade removed user data from Pictures."
if ((Get-Content $userData -Raw) -notmatch [regex]::Escape($dataMarker)) {
    throw "Upgrade changed preserved user data."
}
if (-not (Select-String -Path $historyFile -Pattern $historyMarker -SimpleMatch -Quiet)) {
    throw "Upgrade removed or replaced existing job history."
}

$upgradedProcess = Start-Process -FilePath $installedExe -ArgumentList "--self-test" -Wait -PassThru
if ($upgradedProcess.ExitCode -ne 0) {
    throw "Upgraded Dad Image Tool failed its startup self-test with exit code $($upgradedProcess.ExitCode)."
}

# A repair install of the same candidate must also preserve user data.
Invoke-Setup $candidate
Assert-PathExists $userData "Repair install removed user data from Pictures."
if (-not (Select-String -Path $historyFile -Pattern $historyMarker -SimpleMatch -Quiet)) {
    throw "Repair install removed or replaced existing job history."
}

# Verify uninstall removes the application while leaving the separate Pictures data tree.
$uninstaller = Get-ChildItem -Path $installedRoot -Filter "unins*.exe" | Select-Object -First 1
if (-not $uninstaller) {
    throw "Dad Image Tool uninstaller was not found after installation."
}
$uninstallProcess = Start-Process -FilePath $uninstaller.FullName -ArgumentList "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART" -Wait -PassThru
if ($uninstallProcess.ExitCode -ne 0) {
    throw "Dad Image Tool uninstall failed with exit code $($uninstallProcess.ExitCode)."
}

Assert-PathMissing $installedExe "Uninstall left the Dad Image Tool executable installed."
Assert-PathExists $userData "Uninstall removed user data from Pictures."
if (-not (Select-String -Path $historyFile -Pattern $historyMarker -SimpleMatch -Quiet)) {
    throw "Uninstall removed existing job history."
}

$desktopShortcut = Join-Path ([Environment]::GetFolderPath("Desktop")) "Dad Image Tool.lnk"
$startupShortcut = Join-Path ([Environment]::GetFolderPath("Startup")) "Dad Image Tool.lnk"
Assert-PathMissing $desktopShortcut "Uninstall left the Dad Image Tool desktop shortcut behind."
Assert-PathMissing $startupShortcut "Uninstall left the Dad Image Tool startup shortcut behind."

Write-Host "Previous-release upgrade, repair, data preservation, and uninstall validation passed."
