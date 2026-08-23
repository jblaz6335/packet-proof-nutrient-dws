$ErrorActionPreference = 'Stop'
$assetDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectDir = Split-Path -Parent $assetDir
$chrome = 'C:\Program Files\Google\Chrome\Application\chrome.exe'
$pdfToPpm = 'C:\Users\jblaz\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdftoppm.exe'
$ffmpeg = 'ffmpeg'
$narration = @(
  "A shipment packet can look complete and still disagree on the facts that determine release. Packet Proof catches those discrepancies before they become an expensive downstream surprise. It is an auditable exception desk for trade-document packets, built for the Nutrient DWS challenge.",
  "The demonstration starts with three polished, fictional documents: a commercial invoice, a packing list, and a certificate of origin. The invoice states twenty-four AX four-ten units. The packing list states twenty-two. The certificate provides the origin evidence. A human reviewer should not have to hunt across pages to discover that disagreement.",
  "Nutrient DWS performs the core document operation. Packet Proof sends each PDF to the official build endpoint and requests JSON content with plain text, structured text, key-value pairs, and tables. The provider response is treated as evidence, not authority. Required fields, confidence values, document identity, and response shape are validated, and uncertainty fails closed.",
  "Packet Proof then reconciles the extracted fields deterministically. It checks packet identity, supplier, SKU, quantity, country of origin, invoice arithmetic, and extraction confidence. The reproducible replay processes all three documents and produces exactly one finding: the quantity mismatch. The status is human review required, and automatic release is false. The implementation has seventy-eight automated tests and ninety-eight point zero-nine percent branch-aware coverage.",
  "The exception desk ties the finding back to both source documents. It shows twenty-four units on the invoice and twenty-two on the packing list, records the page evidence, preserves a SHA two-fifty-six hash for every input, and creates a stable audit hash for the complete run. The result can be replayed from the same evidence instead of asking anyone to trust an opaque model answer.",
  "The boundary is the product. Packet Proof extracts and normalizes evidence, compares every required field, surfaces confidence and mismatches, and preserves the audit trail. It does not auto-release, sign, amend, transmit, or represent a customs decision. Nutrient DWS extracted structured JSON content from each source PDF; Packet Proof reconciled those extracted fields deterministically and reserved the release decision for a human."
)

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

$speechScript = Join-Path $assetDir 'speech-temp.ps1'
$speechLines = @(
  "Add-Type -AssemblyName System.Speech",
  "`$voice = [System.Speech.Synthesis.SpeechSynthesizer]::new()",
  "`$voice.Rate = -1"
)
for ($i = 0; $i -lt $narration.Count; $i++) {
  $safe = $narration[$i].Replace("'", "''")
  $wav = Join-Path $assetDir ("slide-{0}.wav" -f ($i + 1))
  $speechLines += "`$voice.SetOutputToWaveFile('$wav')"
  $speechLines += "`$voice.Speak('$safe')"
}
$speechLines += "`$voice.Dispose()"
[System.IO.File]::WriteAllLines($speechScript, $speechLines)
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $speechScript

$segments = @()
for ($i = 1; $i -le 6; $i++) {
  $segment = Join-Path $assetDir "segment-$i.mp4"
  $duration = (& ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 (Join-Path $assetDir "slide-$i.wav")).Trim()
  & $ffmpeg -y -loop 1 -framerate 1 -i (Join-Path $assetDir "slide-$i.png") -i (Join-Path $assetDir "slide-$i.wav") -t $duration -c:v libx264 -preset ultrafast -tune stillimage -r 1 -c:a aac -b:a 128k -pix_fmt yuv420p -vf 'scale=1920:1080' $segment
  $segments += $segment
}
$list = Join-Path $assetDir 'segments.txt'
[System.IO.File]::WriteAllLines($list, ($segments | ForEach-Object { "file '$($_.Replace("'", "''"))'" }))
& $ffmpeg -y -f concat -safe 0 -i $list -c copy (Join-Path $assetDir 'packet-proof-demo.mp4')
& ffprobe -v error -show_entries format=duration,size -show_entries stream=codec_name,width,height,sample_rate -of json (Join-Path $assetDir 'packet-proof-demo.mp4')
