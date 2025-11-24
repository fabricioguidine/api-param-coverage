# Git commit message editor for rebase
# Automatically uses the normalized message from the first commit in each group
param(
    [string]$MessageFile
)

# Extract the commit message from the first line of the rebase todo that matches
# For now, just use a simple message
$message = "chore: squash commits within time interval`n"
[System.IO.File]::WriteAllText($MessageFile, $message, [System.Text.UTF8Encoding]::new($false))

