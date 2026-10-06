# Limbus Company 简体中文补丁 - 自动安装脚本
# 会自动找 Limbus Company 安装目录，把本包里的 LLC_zh-CN 文件覆盖进游戏。
# 所有路径操作都用 -LiteralPath：解压目录名里的 [ ] 会被 -Path 当成通配符。
# 拼路径用 [IO.Path]::Combine 不用 Join-Path：后者遇到已拔掉的盘符（Steam 记录的旧游戏库）会直接报错。

$ErrorActionPreference = 'Stop'
$ScriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$SrcDir    = [System.IO.Path]::Combine($ScriptDir, 'LLC_zh-CN')

function Write-Title($text) {
    Write-Host ""
    Write-Host "=============================================" -ForegroundColor Cyan
    Write-Host "  $text" -ForegroundColor Cyan
    Write-Host "=============================================" -ForegroundColor Cyan
}

function Exit-WithPause([int]$code) {
    Read-Host "按回车键退出"
    exit $code
}

# 任何没预料到的异常也要停住窗口，否则玩家只看到窗口一闪而过。
trap {
    Write-Host ""
    Write-Host "[错误] $($_.Exception.Message)" -ForegroundColor Red
    Exit-WithPause 1
}

Write-Title "Limbus Company 简体中文补丁 - 自动安装程序"

if (-not (Test-Path -LiteralPath $SrcDir -PathType Container)) {
    Write-Host "[错误] 找不到补丁文件目录：$SrcDir" -ForegroundColor Red
    Write-Host "补丁文件可能损坏或本脚本被单独移动了，请重新解压整个安装包再运行。"
    Exit-WithPause 1
}

# ---------- 1. 找游戏目录 ----------

# 从给定路径往上找含 LimbusCompany_Data 的目录，找到返回游戏根目录，否则 $null。
# 这样玩家输入或拖入 LimbusCompany_Data、Lang、LLC_zh-CN 这些子目录也能认。
function Resolve-GameRoot([string]$path) {
    if ([string]::IsNullOrWhiteSpace($path)) { return $null }
    try { $dir = [System.IO.Path]::GetFullPath($path.Trim().Trim('"').Trim()) } catch { return $null }
    while ($dir) {
        if (Test-Path -LiteralPath ([System.IO.Path]::Combine($dir, 'LimbusCompany_Data')) -PathType Container) {
            return $dir.TrimEnd('\')
        }
        $parent = Split-Path -Parent $dir
        if ($parent -eq $dir) { break }
        $dir = $parent
    }
    return $null
}

function Get-SteamLibraries {
    $steamPaths = @()
    foreach ($key in @('HKCU:\Software\Valve\Steam',
                       'HKLM:\SOFTWARE\WOW6432Node\Valve\Steam',
                       'HKLM:\SOFTWARE\Valve\Steam')) {
        try { $props = Get-ItemProperty -LiteralPath $key -ErrorAction Stop } catch { continue }
        foreach ($name in @('SteamPath', 'InstallPath')) {
            $v = $props.$name
            if (-not [string]::IsNullOrWhiteSpace($v)) { $steamPaths += ($v -replace '/', '\') }
        }
    }

    # libraryfolders.vdf 列出玩家额外添加的游戏库，形如 "path"  "E:\\SteamLibrary"
    $libraries = @()
    foreach ($sp in ($steamPaths | Select-Object -Unique)) {
        $libraries += $sp
        $vdf = [System.IO.Path]::Combine($sp, 'steamapps\libraryfolders.vdf')
        if (-not (Test-Path -LiteralPath $vdf -PathType Leaf)) { continue }
        try { $text = Get-Content -LiteralPath $vdf -Raw -Encoding UTF8 -ErrorAction Stop } catch { continue }
        foreach ($m in [regex]::Matches($text, '"path"\s*"([^"]+)"')) {
            $libraries += ($m.Groups[1].Value -replace '\\\\', '\')
        }
    }
    return @($libraries | Select-Object -Unique)
}

function Find-LimbusDirs {
    $candidates = @()

    # 1a. 安装包本身放在游戏目录里（或其子目录里）时，直接用这个位置，最可靠
    $here = Resolve-GameRoot $ScriptDir
    if ($here) { $candidates += $here }

    # 1b. Steam 的各个游戏库
    foreach ($lib in Get-SteamLibraries) {
        $guess = [System.IO.Path]::Combine($lib, 'steamapps\common\Limbus Company')
        if (Test-Path -LiteralPath ([System.IO.Path]::Combine($guess, 'LimbusCompany_Data')) -PathType Container) {
            $candidates += $guess
        }
    }

    # 统一大小写和末尾斜杠后去重，避免同一目录因写法不同出现两次
    $seen = @{}
    $result = @()
    foreach ($c in $candidates) {
        $full = [System.IO.Path]::GetFullPath($c).TrimEnd('\')
        $k = $full.ToLowerInvariant()
        if (-not $seen.ContainsKey($k)) { $seen[$k] = $true; $result += $full }
    }
    return $result
}

# @() 必不可少：只找到一个结果时 PowerShell 会把数组拆成单个字符串，
# 之后 $found[0] 取到的就是路径的第一个字母。
$found = @(Find-LimbusDirs)

$gameDir = $null
if ($found.Count -eq 1) {
    $gameDir = $found[0]
    Write-Host "自动找到游戏目录：$gameDir" -ForegroundColor Green
} elseif ($found.Count -gt 1) {
    Write-Host "找到多个 Limbus Company 安装目录，请选择："
    for ($i = 0; $i -lt $found.Count; $i++) {
        Write-Host "  [$($i+1)] $($found[$i])"
    }
    $idx = 0
    if ([int]::TryParse((Read-Host "请输入序号"), [ref]$idx) -and $idx -ge 1 -and $idx -le $found.Count) {
        $gameDir = $found[$idx - 1]
    } else {
        Write-Host "序号无效，改为手动输入。" -ForegroundColor Yellow
    }
}

if (-not $gameDir) {
    Write-Host ""
    Write-Host "未能自动找到游戏目录。" -ForegroundColor Yellow
    Write-Host "可以在 Steam 里右键边狱巴士 -> 管理 -> 浏览本地文件，打开游戏文件夹，"
    Write-Host "然后把那个文件夹拖到这个窗口里再按回车（也可以手动输入路径，"
    Write-Host "例如 D:\Steam\steamapps\common\Limbus Company）。直接按回车退出。"
    while (-not $gameDir) {
        $inputPath = Read-Host ">"
        if ([string]::IsNullOrWhiteSpace($inputPath)) { exit 1 }
        $gameDir = Resolve-GameRoot $inputPath
        if (-not $gameDir) {
            Write-Host "这个位置里没有 LimbusCompany_Data 文件夹，不是游戏目录，请重新输入：" -ForegroundColor Red
        }
    }
}

$destDir = [System.IO.Path]::Combine($gameDir, 'LimbusCompany_Data\Lang\LLC_zh-CN')
if (-not (Test-Path -LiteralPath $destDir -PathType Container)) {
    Write-Host "[错误] 找不到游戏的中文语言目录：$destDir" -ForegroundColor Red
    Write-Host "请先安装零协会的汉化版本，再安装本补丁。"
    Exit-WithPause 1
}

Write-Host ""
Write-Host "游戏目录：$gameDir"
Write-Host "安装目标：$destDir"
Write-Host ""

# ---------- 2. 安装 ----------

$srcRoot  = (Get-Item -LiteralPath $SrcDir).FullName.TrimEnd('\')
$srcFiles = @(Get-ChildItem -LiteralPath $srcRoot -Recurse -File)

Write-Host "正在安装中文翻译文件（共 $($srcFiles.Count) 个文件）..." -ForegroundColor Yellow

foreach ($f in $srcFiles) {
    $rel = $f.FullName.Substring($srcRoot.Length).TrimStart('\')
    $destFile = [System.IO.Path]::Combine($destDir, $rel)
    $destParent = Split-Path -Parent $destFile
    if (-not (Test-Path -LiteralPath $destParent -PathType Container)) {
        New-Item -ItemType Directory -Force -Path $destParent | Out-Null
    }
    Copy-Item -LiteralPath $f.FullName -Destination $destFile -Force
}

Write-Title "安装完成！"
Write-Host ""
Read-Host "按回车键关闭窗口"
