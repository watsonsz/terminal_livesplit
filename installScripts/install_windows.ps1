Write-Host "== Seriphai Terminal Livesplit (Windows) installer =="

# Ensure Python Launcher exists
try {
    py --version | Out-Null
} catch {
    Write-Error "Python 'py' launcher not found. Install Python from python.org and re-run."
    exit 1
}

py -m venv venv
.\venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt

Write-Host ""
Write-Host "Done."
Write-Host "Run:"
Write-Host "  .\venv\Scripts\Activate.ps1"
Write-Host "  python .\terminal_livesplit.py"
Write-Host ""
Write-Host "NOTE: This app uses curses. Native Windows Python often can't run curses."
Write-Host "Recommended: run inside WSL for full TUI support."
