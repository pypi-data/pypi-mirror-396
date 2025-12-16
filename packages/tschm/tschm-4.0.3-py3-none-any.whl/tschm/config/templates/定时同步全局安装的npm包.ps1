



# 首先判断 当前用户家目录下是否存在 Gist 目录 如果不存在则创建
$gistDir = Join-Path $env:USERPROFILE "Gist"
if (-not (Test-Path $gistDir)) {
    New-Item -ItemType Directory -Path $gistDir -Force | Out-Null
}

$npmPackageFile = Join-Path $gistDir "npm-packages.txt"
$originalEncoding = [Console]::OutputEncoding
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
npm list -g --depth=0 | Out-File -FilePath $npmPackageFile -Encoding utf8
[Console]::OutputEncoding = $originalEncoding
gh gist edit 8c20a41ec67e0f15157cbe9659591dc2 $npmPackageFile
