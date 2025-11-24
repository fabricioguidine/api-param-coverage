# Script to squash commits based on time intervals
# Groups commits within random time intervals (5-30 minutes) and squashes them

$commits = git log --format="%H|%ct|%s" --reverse
$commitList = @()

# Parse commits
foreach ($line in $commits) {
    if ($line -match '^([^|]+)\|(\d+)\|(.+)$') {
        $commitList += [PSCustomObject]@{
            Hash = $matches[1]
            Timestamp = [int]$matches[2]
            Message = $matches[3]
        }
    }
}

Write-Host "Total commits: $($commitList.Count)"

# Random interval in seconds (5, 10, 15, 20, 25, or 30 minutes)
$intervals = @(300, 600, 900, 1200, 1500, 1800)  # 5, 10, 15, 20, 25, 30 minutes
$randomInterval = Get-Random -InputObject $intervals
$intervalMinutes = $randomInterval / 60

Write-Host "Using time interval: $intervalMinutes minutes ($randomInterval seconds)"

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

# Show grouping
$groupNum = 1
foreach ($group in $groups) {
    Write-Host "Group $groupNum : $($group.Count) commits"
    foreach ($commit in $group) {
        $date = [DateTimeOffset]::FromUnixTimeSeconds($commit.Timestamp).ToString("yyyy-MM-dd HH:mm:ss")
        Write-Host "  - $($commit.Hash.Substring(0,7)) $date : $($commit.Message)"
    }
    Write-Host ""
    $groupNum++
}

# Normalize commit messages
function Normalize-CommitMessage {
    param([string]$message)
    
    $message = $message.Trim()
    
    # Convert to lowercase
    $message = $message.ToLower()
    
    # Check if already has prefix
    if ($message -match '^(fix|feat|chore|docs|refactor|style|test|perf|ci|build|revert):\s') {
        return $message
    }
    
    # Add appropriate prefix based on message content
    $lowerMsg = $message.ToLower()
    
    if ($lowerMsg -match '^(fix|fixed|fixing|bug|error|issue)') {
        return "fix: $message"
    } elseif ($lowerMsg -match '^(add|added|create|created|new|implement)') {
        return "feat: $message"
    } elseif ($lowerMsg -match '^(update|updated|change|changed|modify|modified|refactor|refactored)') {
        return "refactor: $message"
    } elseif ($lowerMsg -match '^(remove|removed|delete|deleted|clean|cleanup)') {
        return "chore: $message"
    } elseif ($lowerMsg -match '^(doc|docs|documentation|readme)') {
        return "docs: $message"
    } elseif ($lowerMsg -match '^(test|tests|testing)') {
        return "test: $message"
    } else {
        return "chore: $message"
    }
}

# Create rebase script
$rebaseScript = @()
$rebaseScript += "#!/bin/sh"
$rebaseScript += "# Interactive rebase script"
$rebaseScript += ""

$currentIndex = 0
foreach ($group in $groups) {
    if ($group.Count -eq 1) {
        # Single commit - pick
        $rebaseScript += "pick $($group[0].Hash) $($group[0].Message)"
    } else {
        # Multiple commits - pick first, squash rest
        $firstCommit = $group[0]
        $normalizedMsg = Normalize-CommitMessage -message $firstCommit.Message
        
        $rebaseScript += "pick $($firstCommit.Hash) $normalizedMsg"
        
        for ($i = 1; $i -lt $group.Count; $i++) {
            $commit = $group[$i]
            $normalizedMsg = Normalize-CommitMessage -message $commit.Message
            $rebaseScript += "squash $($commit.Hash) $normalizedMsg"
        }
    }
    $currentIndex++
}

# Save rebase script
$rebaseScript | Out-File -FilePath "rebase_script.txt" -Encoding utf8

Write-Host "Rebase script created: rebase_script.txt"
Write-Host "Review the script and then run: git rebase -i --root"
Write-Host "Or use the script with: git rebase -i --root < rebase_script.txt"

