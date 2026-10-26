# Downloads the old WordPress images into assets/img/ (run once from the repo root in PowerShell):
#   powershell -ExecutionPolicy Bypass -File _import\get_images.ps1
$root = Split-Path $PSScriptRoot -Parent
Get-Content "$PSScriptRoot\images.txt" | ForEach-Object {
  $url, $rel = $_ -split "`t"
  if (-not $url) { return }
  $dest = Join-Path $root $rel
  New-Item -ItemType Directory -Force -Path (Split-Path $dest) | Out-Null
  if (-not (Test-Path $dest)) { Invoke-WebRequest $url -OutFile $dest; Write-Host "got $rel" }
}
