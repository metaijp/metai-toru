# MetAI Toru - Windows setup (the Windows counterpart of build_app.sh).
# Creates .venv, installs requirements, builds assets\icon.ico and adds
# "MetAI Toru" shortcuts to the Start menu and the Desktop.
#
#   powershell -ExecutionPolicy Bypass -File install_windows.ps1 [-NoDesktop] [-NoShortcuts]

param(
    [switch]$NoDesktop,
    [switch]$NoShortcuts
)
$ErrorActionPreference = 'Stop'
$D = $PSScriptRoot
Set-Location $D

# Refresh PATH from the registry (tools installed with winget after this console was opened)
$env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' +
            [Environment]::GetEnvironmentVariable('Path', 'User') + ';' + $env:Path

# Virtual environment + dependencies
$py = Join-Path $D '.venv\Scripts\python.exe'
if (-not (Test-Path $py)) {
    if (Get-Command py -ErrorAction SilentlyContinue) { py -3 -m venv .venv }
    else { python -m venv .venv }
    if ($LASTEXITCODE -ne 0) { throw 'Could not create .venv (Python 3.10+ required).' }
}
& $py -m pip install -q -U -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'pip install failed.' }

# External tools
foreach ($t in @(@{n='ffmpeg'; id='Gyan.FFmpeg'}, @{n='node'; id='OpenJS.NodeJS.LTS'})) {
    if (-not (Get-Command $t.n -ErrorAction SilentlyContinue)) {
        Write-Warning ("{0} not found. Install it with:  winget install {1}" -f $t.n, $t.id)
    }
}

# assets\icon.ico from assets\icon.png
$ico = Join-Path $D 'assets\icon.ico'
& $py -c "import sys; from PIL import Image; Image.open(sys.argv[1]).save(sys.argv[2], sizes=[(s, s) for s in (16, 24, 32, 48, 64, 128, 256)])" `
    (Join-Path $D 'assets\icon.png') $ico

# Shortcuts (pythonw.exe = no console window)
if (-not $NoShortcuts) {
    $pyw = Join-Path $D '.venv\Scripts\pythonw.exe'
    $sh = New-Object -ComObject WScript.Shell
    $dirs = @([Environment]::GetFolderPath('Programs'))
    if (-not $NoDesktop) { $dirs += [Environment]::GetFolderPath('Desktop') }
    foreach ($dir in $dirs) {
        $lnk = $sh.CreateShortcut((Join-Path $dir 'MetAI Toru.lnk'))
        $lnk.TargetPath = $pyw
        $lnk.Arguments = '"' + (Join-Path $D 'gui.py') + '"'
        $lnk.WorkingDirectory = $D
        $lnk.IconLocation = "$ico,0"
        $lnk.Description = 'MetAI Toru - video & audio downloader (yt-dlp)'
        $lnk.Save()
        Write-Host ([char]0x2713 + ' ' + $lnk.FullName)
    }
}
Write-Host 'Done. Start MetAI Toru from the Start menu, or run run_windows.bat'
