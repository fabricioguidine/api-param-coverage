# Git rebase sequence editor script
# This script is called by git during rebase -i to provide the todo list
param(
    [string]$TodoFile
)

# Read and write without BOM
$content = Get-Content "rebase_todo.txt" -Raw
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText($TodoFile, $content, $utf8NoBom)

