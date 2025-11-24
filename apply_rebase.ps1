# Apply rebase using the todo list
$ErrorActionPreference = "Stop"

# Set up environment for non-interactive rebase
$env:GIT_EDITOR = "true"
$env:GIT_SEQUENCE_EDITOR = "cat rebase_todo.txt"

# Create a wrapper script
$script = @"
#!/bin/sh
cat rebase_todo.txt
"@

$script | Out-File -FilePath "git_editor.sh" -Encoding utf8

# Try using git rebase with the todo file
Write-Host "Starting rebase..." -ForegroundColor Cyan

# Use git rebase with custom sequence editor
$env:GIT_SEQUENCE_EDITOR = "powershell -File apply_rebase_helper.ps1"

try {
    git rebase -i --root
} catch {
    Write-Host "Rebase may require manual intervention" -ForegroundColor Yellow
}

