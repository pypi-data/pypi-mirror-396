# 首先判断 当前用户家目录下是否存在 Gist 目录 如果不存在则创建
$gistDir = Join-Path $env:USERPROFILE "Gist"
if (-not (Test-Path $gistDir)) {
    New-Item -ItemType Directory -Path $gistDir -Force | Out-Null
}

# 然后 在Gist 目录下创建 uv-tools.txt 文件 并获取文件的绝对路径
$uvToolsFile = Join-Path $gistDir "uv-tools.txt"

# 然后通过 uv tool list > uv-tools.txt文件路径  的方式把uv tool list 输出重定向到文件内
uv tool list > $uvToolsFile

# 然后通过  gh gist edit 06c21446ab716d2ed8927cca8914cc5e  uv-tools.txt文件路径的方式 更新 gist 
gh gist edit 06c21446ab716d2ed8927cca8914cc5e $uvToolsFile
