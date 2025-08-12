#!/usr/bin/env pwsh
# Git Push retry script
# Usage: .\git-push-retry.ps1 [branch] [max-retries]

param(
    [string]$Branch = "",
    [int]$MaxRetries = 100,
    [int]$DelaySeconds = 5
)

$attempt = 1

Write-Host "Starting git push..." -ForegroundColor Green

while ($attempt -le $MaxRetries) {
    Write-Host "Attempt $attempt of $MaxRetries..." -ForegroundColor Yellow
    
    try {
        if ($Branch -eq "") {
            $result = git push 2>&1
        } else {
            $result = git push origin $Branch 2>&1
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Push successful!" -ForegroundColor Green
            exit 0
        } else {
            throw "Git push failed with exit code $LASTEXITCODE"
        }
    }
    catch {
        Write-Host "Attempt $attempt failed: $result" -ForegroundColor Red
        
        if ($attempt -eq $MaxRetries) {
            Write-Host "Max retries ($MaxRetries) reached. Push failed." -ForegroundColor Red
            exit 1
        }
        
        Write-Host "Waiting $DelaySeconds seconds before retry..." -ForegroundColor Cyan
        Start-Sleep -Seconds $DelaySeconds
        $attempt++
    }
}