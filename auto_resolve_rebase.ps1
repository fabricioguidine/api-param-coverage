# Auto-resolve rebase conflicts and continue
$ErrorActionPreference = "Continue"

while ($true) {
    $status = git status --short 2>&1
    $conflicts = $status | Where-Object { $_ -match '^UU|^AA|^DD|^AU|^UA|^DU|^UD' }
    
    if ($conflicts.Count -eq 0) {
        Write-Host "No conflicts found. Continuing rebase..." -ForegroundColor Green
        $env:GIT_EDITOR = "powershell -File git_commit_editor.ps1"
        $result = git rebase --continue 2>&1
        Write-Host $result
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Rebase completed successfully!" -ForegroundColor Green
            break
        } elseif ($result -match "Successfully rebased") {
            Write-Host "Rebase completed successfully!" -ForegroundColor Green
            break
        } elseif ($result -match "no rebase in progress") {
            Write-Host "No rebase in progress." -ForegroundColor Yellow
            break
        }
    } else {
        Write-Host "Resolving conflicts..." -ForegroundColor Yellow
        Write-Host "Conflicts: $($conflicts.Count)"
        
        # Resolve modify/delete conflicts
        $deleteConflicts = $status | Where-Object { $_ -match '^\s*D\s+.*deleted in HEAD' }
        if ($deleteConflicts) {
            git rm $(($deleteConflicts -replace '^\s*D\s+', '')) 2>&1 | Out-Null
        }
        
        # Accept theirs for all conflicts
        git checkout --theirs . 2>&1 | Out-Null
        git add -A 2>&1 | Out-Null
        
        $env:GIT_EDITOR = "powershell -File git_commit_editor.ps1"
        $result = git rebase --continue 2>&1
        Write-Host $result | Select-Object -First 5
    }
    
    Start-Sleep -Seconds 1
}

