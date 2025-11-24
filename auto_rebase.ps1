# Automated rebase script with time-based commit squashing
# This will rewrite git history - use with caution!

$ErrorActionPreference = "Stop"

Write-Host "Creating rebase script..." -ForegroundColor Cyan

# Get all commits in reverse chronological order (oldest first)
$commits = git log --format="%H|%ct|%s" --reverse
$commitList = @()

# Parse commits
foreach ($line in $commits) {
    if ($line -match '^([^|]+)\|(\d+)\|(.+)$') {
        $msg = $matches[3].Trim()
        # Skip malformed commit messages that contain rebase commands
        if ($msg -notmatch '^(pick|squash|fixup|drop)\s' -and $msg.Length -gt 0) {
            $commitList += [PSCustomObject]@{
                Hash = $matches[1]
                Timestamp = [int]$matches[2]
                Message = $msg
            }
        }
    }
}

Write-Host "Total valid commits: $($commitList.Count)"

# Random interval in seconds (5, 10, 15, 20, 25, or 30 minutes)
$intervals = @(300, 600, 900, 1200, 1500, 1800)  # 5, 10, 15, 20, 25, 30 minutes
$randomInterval = Get-Random -InputObject $intervals
$intervalMinutes = $randomInterval / 60

Write-Host "Using time interval: $intervalMinutes minutes ($randomInterval seconds)" -ForegroundColor Yellow
Write-Host ""

# Normalize commit messages
function Normalize-CommitMessage {
    param([string]$message)
    
    $message = $message.Trim()
    $message = $message.ToLower()
    
    # Remove any existing prefix if malformed
    $message = $message -replace '^[a-z]+:\s*', ''
    
    # Check if already has proper prefix
    if ($message -match '^(fix|feat|chore|docs|refactor|style|test|perf|ci|build|revert):\s') {
        return $message
    }
    
    # Add appropriate prefix based on message content
    $lowerMsg = $message.ToLower()
    
    if ($lowerMsg -match '^(fix|fixed|fixing|bug|error|issue|remove|removed|delete|deleted)') {
        return "fix: $message"
    } elseif ($lowerMsg -match '^(add|added|create|created|new|implement|feat)') {
        return "feat: $message"
    } elseif ($lowerMsg -match '^(update|updated|change|changed|modify|modified|refactor|refactored|reorganize|reorganized)') {
        return "refactor: $message"
    } elseif ($lowerMsg -match '^(doc|docs|documentation|readme|improve.*readme|update.*readme)') {
        return "docs: $message"
    } elseif ($lowerMsg -match '^(test|tests|testing)') {
        return "test: $message"
    } elseif ($lowerMsg -match '^(clean|cleanup|organize|reorganize|move|moved)') {
        return "chore: $message"
    } else {
        return "chore: $message"
    }
}

# Group commits by time intervals
$groups = @()
$currentGroup = @()
$lastTimestamp = $null

foreach ($commit in $commitList) {
    if ($null -eq $lastTimestamp) {
        $currentGroup = @($commit)
        $lastTimestamp = $commit.Timestamp
    } else {
        $timeDiff = $commit.Timestamp - $lastTimestamp
        
        if ($timeDiff -le $randomInterval) {
            $currentGroup += $commit
        } else {
            if ($currentGroup.Count -gt 0) {
                $groups += ,$currentGroup
            }
            $currentGroup = @($commit)
        }
        $lastTimestamp = $commit.Timestamp
    }
}

if ($currentGroup.Count -gt 0) {
    $groups += ,$currentGroup
}

Write-Host "Grouped into $($groups.Count) commit groups" -ForegroundColor Green
Write-Host ""

# Create rebase todo list
$rebaseTodo = @()

foreach ($group in $groups) {
    if ($group.Count -eq 1) {
        $normalizedMsg = Normalize-CommitMessage -message $group[0].Message
        $rebaseTodo += "pick $($group[0].Hash) $normalizedMsg"
    } else {
        $firstCommit = $group[0]
        $normalizedMsg = Normalize-CommitMessage -message $firstCommit.Message
        $rebaseTodo += "pick $($firstCommit.Hash) $normalizedMsg"
        
        for ($i = 1; $i -lt $group.Count; $i++) {
            $commit = $group[$i]
            $normalizedMsg = Normalize-CommitMessage -message $commit.Message
            $rebaseTodo += "squash $($commit.Hash) $normalizedMsg"
        }
    }
}

# Save rebase todo file without BOM
$content = $rebaseTodo -join "`n"
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText("rebase_todo.txt", $content, $utf8NoBom)

Write-Host "Rebase todo list created: rebase_todo.txt"
Write-Host "Total commits after squashing: $($groups.Count)" -ForegroundColor Green
Write-Host ""
Write-Host "Preview:"
$rebaseTodo | Select-Object -First 5 | ForEach-Object { Write-Host "  $_" }
Write-Host "  ..."
Write-Host ""

# Create a script to automate the rebase
$rebaseScript = @"
#!/bin/sh
# Auto-generated rebase script
exec < /dev/tty
git rebase -i --root <<'REBASE_EOF'
$($rebaseTodo -join "`n")
REBASE_EOF
"@

$rebaseScript | Out-File -FilePath "run_rebase.sh" -Encoding utf8

Write-Host "To execute the rebase, run:" -ForegroundColor Yellow
Write-Host "  git rebase -i --root < rebase_todo.txt" -ForegroundColor White
Write-Host ""
Write-Host "Or manually copy the content of rebase_todo.txt when prompted during:" -ForegroundColor Yellow
Write-Host "  git rebase -i --root" -ForegroundColor White

