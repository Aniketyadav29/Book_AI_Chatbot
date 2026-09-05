# ============================================================
#  run.ps1 — One-click launcher for The Enchanted Library
# ============================================================
#  Usage:  Right-click this file → "Run with PowerShell"
#          OR in a terminal:  .\run.ps1
# ============================================================

$envFile = Join-Path $PSScriptRoot ".env"

if (-Not (Test-Path $envFile)) {
    Write-Host ""
    Write-Host "❌ ERROR: .env file not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "➡  Steps to fix:" -ForegroundColor Yellow
    Write-Host "   1. Copy '.env.example'  →  rename it to  '.env'" -ForegroundColor Yellow
    Write-Host "   2. Open '.env' and paste your real API keys" -ForegroundColor Yellow
    Write-Host "   3. Run this script again" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Load .env variables into the current process
Write-Host "📖 Loading environment variables from .env ..." -ForegroundColor Cyan
Get-Content $envFile | ForEach-Object {
    $line = $_.Trim()
    if ($line -and -not $line.StartsWith("#")) {
        $parts = $line -split "=", 2
        if ($parts.Count -eq 2) {
            $key   = $parts[0].Trim()
            $value = $parts[1].Trim()
            [System.Environment]::SetEnvironmentVariable($key, $value, "Process")
            Write-Host "  ✔ Set $key" -ForegroundColor Green
        }
    }
}

# Validate that required keys are non-empty placeholders
$groq     = [System.Environment]::GetEnvironmentVariable("GROQ_API_KEY")
$pinecone = [System.Environment]::GetEnvironmentVariable("PINECONE_API_KEY")

if ($groq -eq "your_groq_api_key_here" -or [string]::IsNullOrWhiteSpace($groq)) {
    Write-Host ""
    Write-Host "❌ GROQ_API_KEY is not set in your .env file." -ForegroundColor Red
    Write-Host "   Get one free at: https://console.groq.com" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

if ($pinecone -eq "your_pinecone_api_key_here" -or [string]::IsNullOrWhiteSpace($pinecone)) {
    Write-Host "🟡 WARNING: PINECONE_API_KEY is not set. You can still upload manuscripts and use all local features, but Canonical Classics cloud archive will be disabled." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[*] Launching The Enchanted Library..." -ForegroundColor Magenta
Write-Host "   App will open in your browser automatically." -ForegroundColor Cyan
Write-Host "   Press Ctrl+C in this window to stop the server." -ForegroundColor Gray
Write-Host ""

# Set onnxruntime arena fix BEFORE launching Python (must be in shell env)
$env:ORT_DISABLE_ARENA_BASED_ALLOCATOR = "1"
$env:PYTHONIOENCODING = "utf-8"

python -m streamlit run "$PSScriptRoot\app.py"
