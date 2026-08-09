Write-Output "Installing Python (requires winget; run as Administrator)..."
try {
    winget install --id Python.Python.3 -e --silent
} catch {
    Write-Warning "winget install failed. Please install Python manually from https://www.python.org/downloads/"
}

Write-Output "If installation succeeded, open a new terminal and run: python --version"