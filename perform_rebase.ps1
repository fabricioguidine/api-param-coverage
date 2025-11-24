# Script to perform interactive rebase with time-based commit squashing
# Groups commits within random time intervals and squashes them

$ErrorActionPreference = "Stop"

# Get all commits in reverse chronological order (oldest first)
$commits = git log --format="%H|%ct|%s" --reverse
$commitList = @()

# Parse commits
foreach ($line in $commits) {
    if ($line -match '^([^|]+)\|(\d+)\|(.+)$') {
        $commitList += [PSCustomObject]@{
            Hash = $matches[1]
            Timestamp = [int]$matches[2]
            Message = $matches[3].Trim()
        }
    }
}

Write-Host "Total commits: $($commitList.Count)"

# Random interval in seconds (5, 10, 15, 20, 25, or 30 minutes)
$intervals = @(300, 600, 900, 1200, 1500, 1800)  # 5, 10, 15, 20, 25, 30 minutes
$randomInterval = Get-Random -InputObject $intervals
$intervalMinutes = $randomInterval / 60

Write-Host "Using time interval: $intervalMinutes minutes ($randomInterval seconds)"
Write-Host ""

# Normalize commit messages
function Normalize-CommitMessage {
    param([string]$message)
    
    $message = $message.Trim()
    
    # Skip if message contains rebase commands (malformed)
    if ($message -match '^(pick|squash|fixup|drop)\s') {
        # Extract the actual message part
        $message = $message -replace '^(pick|squash|fixup|drop)\s+\w+\s+', ''
    }
    
    # Convert to lowercase
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
        # First commit
        $currentGroup = @($commit)
        $lastTimestamp = $commit.Timestamp
    } else {
        $timeDiff = $commit.Timestamp - $lastTimestamp
        
        if ($timeDiff -le $randomInterval) {
            # Within interval, add to current group
            $currentGroup += $commit
        } else {
            # New group
            if ($currentGroup.Count -gt 0) {
                $groups += ,$currentGroup
            }
            $currentGroup = @($commit)
        }
        $lastTimestamp = $commit.Timestamp
    }
}

# Add last group
if ($currentGroup.Count -gt 0) {
    $groups += ,$currentGroup
}

Write-Host "Grouped into $($groups.Count) commit groups"
Write-Host ""

# Create rebase todo list
$rebaseTodo = @()
$groupNum = 1

foreach ($group in $groups) {
    if ($group.Count -eq 1) {
        # Single commit - pick
        $normalizedMsg = Normalize-CommitMessage -message $group[0].Message
        $rebaseTodo += "pick $($group[0].Hash) $normalizedMsg"
        Write-Host "Group $groupNum : 1 commit - $normalizedMsg"
    } else {
        # Multiple commits - pick first, squash rest
        $firstCommit = $group[0]
        $normalizedMsg = Normalize-CommitMessage -message $firstCommit.Message
        
        $rebaseTodo += "pick $($firstCommit.Hash) $normalizedMsg"
        Write-Host "Group $groupNum : $($group.Count) commits - $normalizedMsg"
        
        for ($i = 1; $i -lt $group.Count; $i++) {
            $commit = $group[$i]
            $normalizedMsg = Normalize-CommitMessage -message $commit.Message
            $rebaseTodo += "squash $($commit.Hash) $normalizedMsg"
        }
    }
    $groupNum++
}

# Save rebase todo file
$rebaseTodo | Out-File -FilePath ".git/rebase-merge/git-rebase-todo" -Encoding utf8 -ErrorAction SilentlyContinue

# Alternative: create a script file
$scriptContent = $rebaseTodo -join "`n"
$scriptContent | Out-File -FilePath "rebase_todo.txt" -Encoding utf8

Write-Host ""
Write-Host "Rebase todo list created: rebase_todo.txt"
Write-Host "Total commits after squashing: $($groups.Count)"
Write-Host ""
Write-Host "To apply the rebase, you'll need to:"
Write-Host "1. Backup your current branch: git branch backup-before-rebase"
Write-Host "2. Start interactive rebase: git rebase -i --root"
Write-Host "3. Replace the todo list with the content from rebase_todo.txt"
Write-Host ""
Write-Host "Or use: git rebase -i --root < rebase_todo.txt (if supported)"

