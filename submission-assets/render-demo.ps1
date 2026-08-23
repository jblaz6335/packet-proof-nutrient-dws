param([switch]$SkipNarration)
$ErrorActionPreference = 'Stop'
$assetDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectDir = Split-Path -Parent $assetDir
$chrome = 'C:\Program Files\Google\Chrome\Application\chrome.exe'
$pdfToPpm = 'C:\Users\jblaz\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdftoppm.exe'
$ffmpeg = 'ffmpeg'

Set-Location $projectDir
& $pdfToPpm -png -f 1 -singlefile -r 95 'output/pdf/commercial-invoice.pdf' "$assetDir/commercial-invoice"
& $pdfToPpm -png -f 1 -singlefile -r 95 'output/pdf/packing-list.pdf' "$assetDir/packing-list"
& $pdfToPpm -png -f 1 -singlefile -r 95 'output/pdf/origin-certificate.pdf' "$assetDir/origin-certificate"

for ($i = 1; $i -le 6; $i++) {
  $url = 'file:///' + ($assetDir -replace '\\','/') + "/demo-video.html?slide=$i"
  $screen = Join-Path $assetDir "slide-$i.png"
  $profile = Join-Path $assetDir "chrome-$i"
  & $chrome '--headless' '--disable-gpu' '--hide-scrollbars' '--no-first-run' "--user-data-dir=$profile" '--window-size=1920,1080' "--screenshot=$screen" $url
  $limit = (Get-Date).AddSeconds(20)
  while (-not (Test-Path -LiteralPath $screen)) {
    if ((Get-Date) -gt $limit) { throw "Screenshot $i did not render" }
    Start-Sleep -Milliseconds 250
  }
}

if (-not $SkipNarration) {
  & (Join-Path $projectDir '.tts-venv\Scripts\python.exe') (Join-Path $assetDir 'render-kokoro.py')
}

$segments = @()
for ($i = 1; $i -le 6; $i++) {
  $segment = Join-Path $assetDir "segment-$i.mp4"
  $duration = (& ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 (Join-Path $assetDir "slide-$i.wav")).Trim()
  & $ffmpeg -y -loop 1 -framerate 1 -i (Join-Path $assetDir "slide-$i.png") -i (Join-Path $assetDir "slide-$i.wav") -t $duration -c:v libx264 -preset ultrafast -tune stillimage -r 1 -c:a aac -b:a 160k -af 'loudnorm=I=-16:TP=-1.5:LRA=11' -pix_fmt yuv420p -vf 'scale=1920:1080' $segment
  $segments += $segment
}
$list = Join-Path $assetDir 'segments.txt'
[System.IO.File]::WriteAllLines($list, ($segments | ForEach-Object { "file '$($_.Replace("'", "''"))'" }))
& $ffmpeg -y -f concat -safe 0 -i $list -c copy (Join-Path $assetDir 'packet-proof-demo.mp4')
& ffprobe -v error -show_entries format=duration,size -show_entries stream=codec_name,width,height,sample_rate -of json (Join-Path $assetDir 'packet-proof-demo.mp4')
