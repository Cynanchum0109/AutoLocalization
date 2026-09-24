# Limbus Company 简体中文补丁 - 自动安装脚本
# 会自动找 Steam 里的 Limbus Company 安装目录，把本包里的 LLC_zh-CN 文件覆盖进游戏。

$ErrorActionPreference = 'Stop'
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SrcDir    = Join-Path $ScriptDir 'LLC_zh-CN'

function Write-Title($text) {
    Write-Host ""
    Write-Host "=============================================" -ForegroundColor Cyan
    Write-Host "  $text" -ForegroundColor Cyan
    Write-Host "=============================================" -ForegroundColor Cyan
}

Write-Title "Limbus Company 简体中文补丁 - 自动安装程序"

if (-not (Test-Path $SrcDir)) {
    Write-Host "[错误] 找不到补丁文件目录：$SrcDir" -ForegroundColor Red
    Write-Host "补丁文件可能损坏或本脚本被单独移动了，请重新解压整个安装包再运行。"
    Read-Host "按回车键退出"
    exit 1
}

# ---------- 1. 找游戏目录 ----------

function Find-LimbusDirs {
    $candidates = @()

    # 1a. Steam 主安装路径（注册表）
    $steamPaths = @()
    try {
        $regPath = Get-ItemProperty -Path 'HKCU:\Software\Valve\Steam' -Name 'SteamPath' -ErrorAction SilentlyContinue
        if ($regPath.SteamPath) { $steamPaths += $regPath.SteamPath.Replace('/', '\') }
    } catch {}
    try {
        $regPath2 = Get-ItemProperty -Path 'HKLM:\SOFTWARE\WOW6432Node\Valve\Steam' -Name 'InstallPath' -ErrorAction SilentlyContinue
        if ($regPath2.InstallPath) { $steamPaths += $regPath2.InstallPath }
    } catch {}
    $steamPaths = $steamPaths | Select-Object -Unique

    # 1b. 解析每个 Steam 主目录下的 libraryfolders.vdf，找出所有游戏库盘符
    $libraryRoots = @()
    foreach ($sp in $steamPaths) {
        $libraryRoots += $sp
        $vdf = Join-Path $sp 'steamapps\libraryfolders.vdf'
        if (Test-Path $vdf) {
            $lines = Get-Content $vdf -Encoding UTF8
            foreach ($line in $lines) {
                if ($line -match '"path"\s*"([^"]+)"') {
                    $p = $matches[1] -replace '\\\\', '\'
                    $libraryRoots += $p
                }
            }
        }
    }
    $libraryRoots = $libraryRoots | Select-Object -Unique

    foreach ($root in $libraryRoots) {
        $guess = Join-Path $root 'steamapps\common\Limbus Company'
        if (Test-Path (Join-Path $guess 'LimbusCompany_Data')) {
            $candidates += $guess
        }
    }

    return ($candidates | Select-Object -Unique)
}

$found = Find-LimbusDirs

$gameDir = $null
if ($found.Count -eq 1) {
    $gameDir = $found[0]
    Write-Host "自动找到游戏目录：$gameDir" -ForegroundColor Green
} elseif ($found.Count -gt 1) {
    Write-Host "找到多个 Limbus Company 安装目录，请选择："
    for ($i = 0; $i -lt $found.Count; $i++) {
        Write-Host "  [$($i+1)] $($found[$i])"
    }
    $sel = Read-Host "请输入序号"
    $idx = [int]$sel - 1
    if ($idx -ge 0 -and $idx -lt $found.Count) { $gameDir = $found[$idx] }
}

if (-not $gameDir) {
    Write-Host ""
    Write-Host "未能自动找到游戏目录。" -ForegroundColor Yellow
    Write-Host "请手动输入 Limbus Company 的安装路径"
    Write-Host "（例如 D:\Steam\steamapps\common\Limbus Company），"
    Write-Host "也可以直接把游戏文件夹拖到这个窗口里再按回车："
    $gameDir = (Read-Host ">").Trim('"').Trim()
}

if (-not (Test-Path (Join-Path $gameDir 'LimbusCompany_Data'))) {
    Write-Host "[错误] 找不到 `"$gameDir\LimbusCompany_Data`"，请确认路径正确。" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

$destDir = Join-Path $gameDir 'LimbusCompany_Data\Lang\LLC_zh-CN'
if (-not (Test-Path $destDir)) {
    Write-Host "[错误] 找不到游戏的中文语言目录：$destDir" -ForegroundColor Red
    Write-Host "游戏客户端里可能还没有切换过一次简体中文，请先在游戏设置里切换成中文后再安装本补丁。"
    Read-Host "按回车键退出"
    exit 1
}

Write-Host ""
Write-Host "游戏目录：$gameDir"
Write-Host "安装目标：$destDir"
Write-Host ""

# ---------- 2. 安装 ----------

$srcFiles = Get-ChildItem -Path $SrcDir -Recurse -File

Write-Host ""
Write-Host "正在安装中文翻译文件（共 $($srcFiles.Count) 个文件）..." -ForegroundColor Yellow

foreach ($f in $srcFiles) {
    $rel = $f.FullName.Substring($SrcDir.Length).TrimStart('\')
    $destFile = Join-Path $destDir $rel
    New-Item -ItemType Directory -Force -Path (Split-Path $destFile) | Out-Null
    Copy-Item -Path $f.FullName -Destination $destFile -Force
}

Write-Title "安装完成！"
Write-Host ""
Read-Host "按回车键关闭窗口"
