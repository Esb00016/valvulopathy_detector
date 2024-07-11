# List all files in the git repository with their sizes
$files = git rev-list --objects --all | % {
    $parts = $_ -split " "
    $size = git cat-file -s $parts[0]
    [PSCustomObject]@{
        Size = [int]$size
        SHA1 = $parts[0]
        Path = $parts[1]
    }
} | Sort-Object Size -Descending

# Print the 10 largest files
$files[0..9] | Format-Table -AutoSize
