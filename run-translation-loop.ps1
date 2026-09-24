param([int]$MaxRounds=0,[int]$MaxConsecutiveFailures=3)
$ErrorActionPreference='Stop'
$root=(Get-Location).Path
$codex='C:\Users\pc\AppData\Roaming\npm\codex.cmd'
$py='C:\Users\pc\AppData\Local\Programs\Python\Python312\python.exe'
$log=Join-Path $root 'out\runner-logs'; New-Item -ItemType Directory -Force $log | Out-Null
$round=0; $fail=0
function Count-Stage([string]$stage) {
  $script = "import json,sys; p=json.load(open('out/state.json',encoding='utf-8'))['actionable']; stage=sys.argv[1]; bad=('BattleSpeechBubbleDlg','Skills_','Passives_','BattleKeywords_'); print(sum(1 for x in p if x.get('status') in ('todo','stale','outdated_official') and ((stage=='speech' and 'BattleSpeechBubbleDlg' in x.get('key','')) or (stage=='boss' and any(z in x.get('key','') for z in bad[1:])) or (stage=='floors' and not any(z in x.get('key','') for z in bad)))) )"
  [int](& $py -c $script $stage)
}
while ($true) {
  $round++; if($MaxRounds -gt 0 -and $round -gt $MaxRounds){break}
  $stage='speech'; if((Count-Stage 'speech') -eq 0){$stage='boss'}; if((Count-Stage $stage) -eq 0){$stage='floors'}
  if((Count-Stage $stage) -eq 0){break}
  $prompt="Work from disk state only. This is autonomous translation round $round. Current phase: $stage. Claim the next batch for agent b, actually translate every item, write batch_answers.json, run batch_merge.py, then verify state/progress. Do not merely report progress. Do not stop while the current batch remains unfinished. Respect TRANSLATION_GUIDE.md, FORMAT_TAGS.md, CHARACTER_VOICE.md, glossary files. If the phase has no todo, move to the next phase. Return a concise result only after committing the batch or documenting a real blocking error."
  $out=Join-Path $log ("round-{0:D4}.stdout.log" -f $round); $err=Join-Path $log ("round-{0:D4}.stderr.log" -f $round); $pf=Join-Path $log ("round-{0:D4}.prompt.txt" -f $round)
  Set-Content -LiteralPath $pf -Value $prompt -Encoding UTF8
  Get-Content -LiteralPath $pf -Raw | & $codex exec -C $root --approve-for-me --dangerously-bypass-hook-trust --json - 1>$out 2>$err; $code=$LASTEXITCODE
  if($code -ne 0){$fail++; if($fail -ge $MaxConsecutiveFailures){throw "Codex failed $fail consecutive rounds. See $out and $err"}; continue}
  $fail=0
}
Write-Output "runner stopped: rounds=$round speech=$(Count-Stage 'speech') boss=$(Count-Stage 'boss') floors=$(Count-Stage 'floors')"
