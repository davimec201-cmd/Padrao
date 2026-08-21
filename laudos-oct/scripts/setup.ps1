# setup.ps1 — instala as dependencias da skill laudos-oct no Windows.
#
#   powershell -ExecutionPolicy Bypass -File setup.ps1
#
# Roda UMA vez, pelo operador, fora da sessao do agente. O agente nao roda isto:
# o guardiao bloqueia PowerShell de proposito.

$ErrorActionPreference = "Stop"
$SkillDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Write-Host "==> Skill em: $SkillDir"

$py = $null
foreach ($c in @("py", "python", "python3")) {
  if (Get-Command $c -ErrorAction SilentlyContinue) { $py = $c; break }
}
if (-not $py) {
  Write-Host "!! Python nao encontrado. Instale de https://python.org marcando 'Add to PATH'."
  exit 1
}
Write-Host "==> Python: $(& $py -V)"

Write-Host "==> Instalando dependencias..."
& $py -m pip install --user -r "$SkillDir\scripts\requirements-windows.txt"
if ($LASTEXITCODE -ne 0) {
  Write-Host "!! Falha ao instalar. Tente:  $py -m pip install --user pyautogui pillow reportlab"
  exit 1
}

$out = Join-Path $env:USERPROFILE "Laudos_OCT"
New-Item -ItemType Directory -Force -Path $out | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $env:USERPROFILE ".laudos_oct\assinaturas") | Out-Null
Write-Host "==> Pasta de saida: $out"

Write-Host ""
Write-Host "====================================================================="
Write-Host " LEIA ANTES DE USAR"
Write-Host "====================================================================="
Write-Host " 1) O Windows NAO pede permissao de Acessibilidade nem de Gravacao de"
Write-Host "    Tela, como o macOS pedia. Isso facilita a instalacao e PIORA a sua"
Write-Host "    posicao: aquele freio do sistema operacional nao existe aqui, e"
Write-Host "    tambem nao ha sandbox de kernel. O que sobra e o STOP, a lista"
Write-Host "    deny e o hook guardiao. Leia SEGURANCA.md secao 3."
Write-Host " 2) Instale o endurecimento (Passo 3b do INSTALACAO.md):"
Write-Host "      copy hardening\hooks\guardiao-laudos.py %USERPROFILE%\.claude\hooks\"
Write-Host "      copy hardening\settings-windows.json    %USERPROFILE%\.claude\settings.json"
Write-Host " 3) Se a tela usa escala diferente de 100%, NAO mude a escala nem troque"
Write-Host "    de monitor com a fila rodando: o clique passa a cair no elemento"
Write-Host "    vizinho e a guarda de retangulo nao pega isso."
Write-Host "====================================================================="
Write-Host ""

Write-Host "==> Rodando diagnostico..."
& $py "$SkillDir\scripts\hands.py" doctor
if ($LASTEXITCODE -ne 0) {
  Write-Host ""
  Write-Host "!! O diagnostico apontou pendencias acima. Resolva e rode de novo."
  exit 1
}
Write-Host ""
Write-Host "==> Tudo pronto. Abra o AnyDesk, deixe a janela visivel e peca ao Claude:"
Write-Host "    'lauda os OCTs da fila do AnyDesk'"
