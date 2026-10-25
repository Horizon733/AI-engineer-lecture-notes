# Activate the shared prompt-tools venv (PowerShell).
# Usage:  . .\activate.ps1
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
& "$here\.venv\Scripts\Activate.ps1"
Write-Host "prompt-tools venv active -> $here\.venv"
