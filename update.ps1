# update.ps1 — Drop new PDFs into raw_pdfs/AK/ or raw_pdfs/NK/ and run this.
# Usage: .\update.ps1 [-Person AK] [-Person NK] [-DryRun]

param(
    [ValidateSet("AK","RK","both")][string]$Person = "both",
    [switch]$DryRun
)

$persons = if ($Person -eq "both") { @("AK","RK") } else { @($Person) }
$dryFlag = if ($DryRun) { "--dry-run" } else { "" }

foreach ($p in $persons) {
    Write-Host "`n=== $p ===" -ForegroundColor Cyan

    Write-Host "Step 1: Rename..." -ForegroundColor Yellow
    if ($dryFlag) {
        python ingestion/rename.py --person $p --dry-run
    } else {
        python ingestion/rename.py --person $p
    }

    if (-not $DryRun) {
        Write-Host "Step 2: Extract..." -ForegroundColor Yellow
        python ingestion/extract.py --person $p

        Write-Host "Step 3: Load into DB..." -ForegroundColor Yellow
        python ingestion/load.py --person $p
    }
}

if (-not $DryRun) {
    Write-Host "`nDone! Starting dashboard..." -ForegroundColor Green
    # uvicorn backend.main:app --reload --port 8000
}
