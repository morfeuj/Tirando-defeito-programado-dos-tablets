param([switch]$TestMode)
# Otimizador de Tablets Samsung / Android v2.0 - App Grafico Nativo Windows (WinForms)
# Roda nativamente em qualquer Windows 10/11 sem precisar instalar Python!

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

[System.Windows.Forms.Application]::EnableVisualStyles()

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -Path $ScriptDir
$AdbLocal = Join-Path $ScriptDir "platform-tools\adb.exe"
$script:SerialAtual = $null

# Cores do Tema Escuro
$BgDark       = [System.Drawing.Color]::FromArgb(18, 22, 31)
$BgCard       = [System.Drawing.Color]::FromArgb(28, 34, 48)
$BgInput      = [System.Drawing.Color]::FromArgb(38, 46, 64)
$AccentBlue   = [System.Drawing.Color]::FromArgb(56, 139, 253)
$AccentGreen  = [System.Drawing.Color]::FromArgb(46, 160, 67)
$AccentOrange = [System.Drawing.Color]::FromArgb(210, 153, 34)
$AccentRed    = [System.Drawing.Color]::FromArgb(248, 81, 73)
$TextLight    = [System.Drawing.Color]::FromArgb(230, 237, 243)
$TextMuted    = [System.Drawing.Color]::FromArgb(139, 148, 158)

$PacotesProtegidos = @(
    "android", "com.android.systemui", "com.android.settings",
    "com.android.vending", "com.google.android.gms",
    "com.sec.android.app.samsungapps", "com.android.chrome",
    "com.samsung.android.honeyboard", "com.sec.android.app.launcher",
    "com.openai.chatgpt", "com.google.android.youtube"
)

$Categorias = @(
    @{ Id="1";Marcado=$true; Nome="1. Bixby, Rotinas e Painéis Edge"; Pacotes=@("com.samsung.android.app.spage","com.samsung.android.app.settings.bixby","com.samsung.android.app.routines","com.samsung.android.app.appsedge","com.samsung.android.app.taskedge","com.samsung.android.app.cocktailbarservice","com.samsung.android.app.clipboardedge") },
    @{ Id="2";Marcado=$true; Nome="2. Nuvem, Conta e Diagnóstico Samsung"; Pacotes=@("com.samsung.android.scloud","com.samsung.android.mobileservice","com.samsung.android.scs","com.samsung.android.rubin.app","com.samsung.android.bbc.bbcagent","com.samsung.android.dqagent","com.sec.android.diagmonagent") },
    @{ Id="3";Marcado=$true; Nome="3. Transferência (Smart Switch) e Modo Crianças"; Pacotes=@("com.samsung.android.smartswitchassistant","com.sec.android.easyMover","com.sec.android.easyMover.Agent","com.samsung.android.kidsinstaller","com.samsung.android.app.parentalcare","com.samsung.android.forest") },
    @{ Id="4";Marcado=$true; Nome="4. Compartilhamento, Continuidade e Espelhamento"; Pacotes=@("com.samsung.android.app.sharelive","com.samsung.android.galaxycontinuity","com.samsung.android.mdx.kit","com.samsung.android.mdx.quickboard","com.samsung.android.smartmirroring","com.samsung.android.allshare.service.mediashare","com.samsung.android.beaconmanager","com.samsung.android.mapsagent","com.samsung.android.aware.service") },
    @{ Id="5";Marcado=$true; Nome="5. Clima, Vídeo, Foto, Stickers e Temas"; Pacotes=@("com.sec.android.daemonapp","com.sec.android.app.ve.vebgm","com.sec.android.autodoodle.service","com.sec.android.mimage.photoretouching","com.samsung.app.newtrim","com.sec.android.app.DataCreate","com.samsung.storyservice","com.samsung.android.stickercenter","com.samsung.android.themecenter","com.samsung.android.app.dressroom","com.samsung.android.dynamiclock","com.samsung.android.widget.pictureframe") },
    @{ Id="6";Marcado=$true; Nome="6. Telemetria Knox e Mensagens SMS"; Pacotes=@("com.samsung.android.messaging","com.samsung.android.knox.analytics.uploader","com.samsung.android.knox.app.networkfilter","com.samsung.android.knox.attestation") },
    @{ Id="7";Marcado=$true; Nome="7. Anúncios e Terceiros (OneDrive, Outlook, AppLovin, Hiya)"; Pacotes=@("com.applovin.array.apphub.samsung","com.hiya.star","com.microsoft.office.outlook","com.microsoft.skydrive") },
    @{ Id="8";Marcado=$true; Nome="8. Apps do Google Secundários (Drive, Maps, Meet, Google TV, Busca)"; Pacotes=@("com.google.android.apps.youtube.music","com.google.android.apps.photos","com.google.android.gm","com.google.android.apps.tachyon","com.google.android.videos","com.google.android.apps.messaging","com.google.android.apps.docs","com.google.android.apps.maps","com.google.android.googlequicksearchbox") },
    @{ Id="9";Marcado=$true; Nome="9. Vozes de Leitura (TTS) Estrangeiras"; Pacotes=@("com.samsung.SMT.lang_de_de_f00","com.samsung.SMT.lang_en_gb_f00","com.samsung.SMT.lang_en_us_l03","com.samsung.SMT.lang_es_es_f00","com.samsung.SMT.lang_es_mx_f00","com.samsung.SMT.lang_fr_fr_f00","com.samsung.SMT.lang_it_it_f00","com.samsung.SMT.lang_ru_ru_f00") },
    @{ Id="10";Marcado=$true; Nome="10. Limitadores de Jogos Samsung (GOS e Smart FPS)"; Pacotes=@("com.samsung.android.game.gos","com.sec.android.smartfpsadjuster","com.samsung.android.game.gamehome","com.samsung.android.game.gametools") },
    @{ Id="11";Marcado=$true; Nome="11. Extras Galaxy Tab A 10.1 SM-T510 (DailyBoard, ANT+, Pasta Segura)"; Pacotes=@("com.sec.android.app.kidshome","com.sec.android.usermanual","com.sec.android.widgetapp.webmanual","com.diotek.sec.lookup.dictionary","com.dsi.ant.plugins.antplus","com.dsi.ant.sample.acquirechannels","com.dsi.ant.server","com.dsi.ant.service.socket","com.samsung.android.homemode","com.samsung.android.livestickers","com.samsung.android.icecone","com.samsung.android.app.watchmanagerstub","com.samsung.android.app.simplesharing","com.samsung.android.privateshare","com.samsung.android.allshare.service.fileshare","com.samsung.android.easysetup","com.samsung.android.service.stplatform","com.samsung.android.mcfds","com.samsung.android.mcfserver","com.samsung.knox.securefolder","com.samsung.android.knox.containeragent","com.samsung.android.knox.containercore","com.samsung.android.knox.pushmanager","com.sec.enterprise.knox.attestation","com.sec.enterprise.knox.cloudmdm.smdms","com.sec.spp.push","com.samsung.android.aremoji","com.sec.android.mimage.avatarstickers","com.samsung.android.FastSwitch","com.samsung.android.app.galaxyfinder") },
    @{ Id="12";Marcado=$false; Nome="12. Apps de Streaming (Netflix, Disney+, Spotify, Prime Video, YT Kids)"; Pacotes=@("com.netflix.mediaclient","com.netflix.partner.activation","com.spotify.music","com.disney.disneyplus","com.amazon.avod.thirdpartyclient","com.google.android.apps.youtube.kids") }
)

# Janela Principal
$Form = New-Object System.Windows.Forms.Form
$Form.Text = "Otimizador de Tablets Samsung / Android v2.0 (App Nativo Windows - Sem Python)"
$Form.Size = New-Object System.Drawing.Size(1050, 750)
$Form.StartPosition = "CenterScreen"
$Form.BackColor = $BgDark
$Form.ForeColor = $TextLight
$Form.Font = New-Object System.Drawing.Font("Segoe UI", 9.5)

# Cabecalho
$PnlHeader = New-Object System.Windows.Forms.Panel
$PnlHeader.Dock = "Top"
$PnlHeader.Height = 64
$PnlHeader.BackColor = $BgCard

$LblTitulo = New-Object System.Windows.Forms.Label
$LblTitulo.Text = "OTIMIZADOR DE TABLETS SAMSUNG E CONSOLE RETRO"
$LblTitulo.Font = New-Object System.Drawing.Font("Segoe UI", 13, [System.Drawing.FontStyle]::Bold)
$LblTitulo.ForeColor = $AccentBlue
$LblTitulo.AutoSize = $true
$LblTitulo.Location = New-Object System.Drawing.Point(16, 10)

$LblStatus = New-Object System.Windows.Forms.Label
$LblStatus.Text = "Pronto para conectar via ADB"
$LblStatus.Font = New-Object System.Drawing.Font("Segoe UI", 9.5, [System.Drawing.FontStyle]::Bold)
$LblStatus.ForeColor = $AccentOrange
$LblStatus.AutoSize = $true
$LblStatus.Location = New-Object System.Drawing.Point(16, 36)

$PnlHeader.Controls.Add($LblTitulo)
$PnlHeader.Controls.Add($LblStatus)

# Painel de Cartoes de Diagnostico
$PnlCards = New-Object System.Windows.Forms.Panel
$PnlCards.Dock = "Top"
$PnlCards.Height = 82
$PnlCards.Padding = New-Object System.Windows.Forms.Padding(12, 8, 12, 8)

$TblCards = New-Object System.Windows.Forms.TableLayoutPanel
$TblCards.Dock = "Fill"
$TblCards.ColumnCount = 4
$TblCards.RowCount = 1
for ($i = 0; $i -lt 4; $i++) {
    [void]$TblCards.ColumnStyles.Add((New-Object System.Windows.Forms.ColumnStyle([System.Windows.Forms.SizeType]::Percent, 25)))
}

function New-DiagCard($Col, $Titulo, $ValorInicial) {
    $Card = New-Object System.Windows.Forms.Panel
    $Card.Dock = "Fill"
    $Card.BackColor = $BgCard
    $Card.Margin = New-Object System.Windows.Forms.Padding(5)
    $Card.Padding = New-Object System.Windows.Forms.Padding(10, 6, 10, 6)

    $LTit = New-Object System.Windows.Forms.Label
    $LTit.Text = $Titulo
    $LTit.ForeColor = $TextMuted
    $LTit.Font = New-Object System.Drawing.Font("Segoe UI", 8, [System.Drawing.FontStyle]::Bold)
    $LTit.Dock = "Top"
    $LTit.Height = 18

    $LVal = New-Object System.Windows.Forms.Label
    $LVal.Text = $ValorInicial
    $LVal.ForeColor = $TextLight
    $LVal.Font = New-Object System.Drawing.Font("Segoe UI", 11, [System.Drawing.FontStyle]::Bold)
    $LVal.Dock = "Fill"

    $Card.Controls.Add($LVal)
    $Card.Controls.Add($LTit)
    $TblCards.Controls.Add($Card, $Col, 0)
    return $LVal
}

$LblCardModelo  = New-DiagCard 0 "APARELHO / ANDROID" "Clique em Analisar"
$LblCardRam     = New-DiagCard 1 "MEMÓRIA RAM LIVRE" "-- / -- MB"
$LblCardStorage = New-DiagCard 2 "ARMAZENAMENTO (/data)" "-- GB livres"
$LblCardApps    = New-DiagCard 3 "PACOTES ATIVOS" "-- ativos"
$PnlCards.Controls.Add($TblCards)

# Rodape com Progresso e Log
$PnlFooter = New-Object System.Windows.Forms.Panel
$PnlFooter.Dock = "Bottom"
$PnlFooter.Height = 200
$PnlFooter.Padding = New-Object System.Windows.Forms.Padding(12, 4, 12, 12)

$LblProg = New-Object System.Windows.Forms.Label
$LblProg.Text = "Aguardando comando..."
$LblProg.Dock = "Top"
$LblProg.Height = 20
$LblProg.ForeColor = $TextMuted

$ProgBar = New-Object System.Windows.Forms.ProgressBar
$ProgBar.Dock = "Top"
$ProgBar.Height = 10

$TxtLog = New-Object System.Windows.Forms.RichTextBox
$TxtLog.Dock = "Fill"
$TxtLog.BackColor = [System.Drawing.Color]::FromArgb(12, 15, 22)
$TxtLog.ForeColor = [System.Drawing.Color]::FromArgb(165, 214, 255)
$TxtLog.Font = New-Object System.Drawing.Font("Consolas", 9.5)
$TxtLog.ReadOnly = $true
$TxtLog.BorderStyle = "None"

$PnlFooter.Controls.Add($TxtLog)
$PnlFooter.Controls.Add($ProgBar)
$PnlFooter.Controls.Add($LblProg)

function Write-GuiLog($Mensagem) {
    $Hora = (Get-Date).ToString("HH:mm:ss")
    $TxtLog.AppendText("[$Hora] $Mensagem`r`n")
    $TxtLog.SelectionStart = $TxtLog.Text.Length
    $TxtLog.ScrollToCaret()
    [System.Windows.Forms.Application]::DoEvents()
}

function Set-GuiProgress($Valor, $Max, $Texto) {
    $ProgBar.Maximum = if ($Max -gt 0) { $Max } else { 100 }
    $ProgBar.Value = [Math]::Min([Math]::Max(0, $Valor), $ProgBar.Maximum)
    $LblProg.Text = $Texto
    [System.Windows.Forms.Application]::DoEvents()
}

function Invoke-AdbCommand([string[]]$Argumentos) {
    if (-not (Test-Path $AdbLocal)) {
        Write-GuiLog "Baixando ADB oficial do Google (~15 MB)..."
        Set-GuiProgress 20 100 "Baixando platform-tools do Google..."
        $ZipFile = Join-Path $ScriptDir "platform-tools-latest-windows.zip"
        Invoke-WebRequest -Uri "https://dl.google.com/android/repository/platform-tools-latest-windows.zip" -OutFile $ZipFile
        Expand-Archive -Path $ZipFile -DestinationPath $ScriptDir -Force
        Remove-Item $ZipFile -Force -ErrorAction SilentlyContinue
        Write-GuiLog "[OK] ADB oficial instalado em: $AdbLocal"
    }
    $FinalArgs = @()
    if ($script:SerialAtual -and $Argumentos[0] -notin @("devices", "connect", "disconnect")) {
        $FinalArgs += "-s"
        $FinalArgs += $script:SerialAtual
    }
    $FinalArgs += $Argumentos
    $Saida = & $AdbLocal @FinalArgs 2>&1 | Out-String
    return $Saida.Trim()
}

function Test-TabletConnection {
    $Out = Invoke-AdbCommand @("devices")
    $Linhas = $Out -split "`r?`n"
    foreach ($L in $Linhas) {
        if ($L -match "^(\S+)\s+(unauthorized|authorizing)") {
            $LblStatus.Text = "Tablet detectado ($($Matches[1])) - Toque em 'Permitir' na tela do tablet!"
            $LblStatus.ForeColor = $AccentOrange
            Write-GuiLog "[!] Olhe a tela do tablet e toque em 'Permitir depuração USB'."
            return $false
        }
        if ($L -match "^(\S+)\s+device\b") {
            $script:SerialAtual = $Matches[1]
            return $true
        }
    }
    $LblStatus.Text = "Nenhum tablet conectado via ADB. Conecte o cabo USB e ative a Depuração USB."
    $LblStatus.ForeColor = $AccentRed
    Write-GuiLog "[!] Nenhum tablet encontrado em estado 'device'."
    return $false
}

function Invoke-TabletScan {
    Set-GuiProgress 20 100 "Verificando conexão com o tablet..."
    if (-not (Test-TabletConnection)) {
        Set-GuiProgress 0 100 "Tablet desconectado."
        return
    }
    Set-GuiProgress 50 100 "Coletando dados de hardware, RAM, armazenamento e pacotes..."
    $Modelo  = Invoke-AdbCommand @("shell", "getprop ro.product.model")
    $Device  = Invoke-AdbCommand @("shell", "getprop ro.product.device")
    $Android = Invoke-AdbCommand @("shell", "getprop ro.build.version.release")
    $MemInfo = Invoke-AdbCommand @("shell", "grep -E 'MemTotal|MemAvailable' /proc/meminfo")
    $DfData  = Invoke-AdbCommand @("shell", "df -h /data")
    $PkgsRaw = Invoke-AdbCommand @("shell", "pm list packages -e")

    $MemTotalMb = if ($MemInfo -match "MemTotal:\s+(\d+)") { [Math]::Round([double]$Matches[1] / 1024, 0) } else { 0 }
    $MemLivreMb = if ($MemInfo -match "MemAvailable:\s+(\d+)") { [Math]::Round([double]$Matches[1] / 1024, 0) } else { 0 }

    $ListaPkgs = ($PkgsRaw -split "`r?`n" | Where-Object { $_ -match "^package:" })
    $DfLinhas = ($DfData -split "`r?`n" | Where-Object { $_.Trim() -ne "" })
    $StorageTxt = "N/D"
    if ($DfLinhas.Count -ge 2) {
        $Cols = $DfLinhas[-1] -split "\s+"
        if ($Cols.Count -ge 5) { $StorageTxt = "$($Cols[3]) livres ($($Cols[4]) usado)" }
    }

    $LblStatus.Text = "CONECTADO - Serial: $($script:SerialAtual) | $Modelo ($Device)"
    $LblStatus.ForeColor = $AccentGreen
    $LblCardModelo.Text  = "$Modelo (Android $Android)"
    $LblCardRam.Text     = "$MemLivreMb / $MemTotalMb MB"
    $LblCardStorage.Text = $StorageTxt
    $LblCardApps.Text    = "$($ListaPkgs.Count) pacotes ativos"

    Write-GuiLog "Diagnóstico: $Modelo ($($script:SerialAtual)) | Android $Android | RAM Livre: $MemLivreMb MB | Armazenamento: $StorageTxt | Apps ativos: $($ListaPkgs.Count)"
    Set-GuiProgress 100 100 "Diagnóstico concluído."
}

# Painel Central Dividido
$PnlMain = New-Object System.Windows.Forms.Panel
$PnlMain.Dock = "Fill"
$PnlMain.Padding = New-Object System.Windows.Forms.Padding(12, 4, 12, 4)

$Split = New-Object System.Windows.Forms.SplitContainer
$Split.Dock = "Fill"
$Split.SplitterDistance = 580

# Esquerda: Checkboxes de Categorias
$LblCatTitle = New-Object System.Windows.Forms.Label
$LblCatTitle.Text = "Categorias de Bloatware para remover (Sem Root, 100% Reversível):"
$LblCatTitle.Dock = "Top"
$LblCatTitle.Height = 24
$LblCatTitle.Font = New-Object System.Drawing.Font("Segoe UI", 9.5, [System.Drawing.FontStyle]::Bold)

$ClbCategorias = New-Object System.Windows.Forms.CheckedListBox
$ClbCategorias.Dock = "Fill"
$ClbCategorias.BackColor = $BgCard
$ClbCategorias.ForeColor = $TextLight
$ClbCategorias.BorderStyle = "FixedSingle"
$ClbCategorias.CheckOnClick = $true
foreach ($C in $Categorias) {
    [void]$ClbCategorias.Items.Add($C.Nome, $C.Marcado)
}

$PnlProtecao = New-Object System.Windows.Forms.Panel
$PnlProtecao.Dock = "Bottom"
$PnlProtecao.Height = 56

$ChkStreaming = New-Object System.Windows.Forms.CheckBox
$ChkStreaming.Text = "Manter e proteger todos os apps de Streaming (Netflix, Disney+, Prime Video, Spotify, YouTube)"
$ChkStreaming.Checked = $true
$ChkStreaming.AutoSize = $true
$ChkStreaming.ForeColor = [System.Drawing.Color]::FromArgb(126, 231, 135)
$ChkStreaming.Location = New-Object System.Drawing.Point(4, 4)

$ChkGoogle = New-Object System.Windows.Forms.CheckBox
$ChkGoogle.Text = "Manter e proteger Gmail e Google Fotos"
$ChkGoogle.Checked = $true
$ChkGoogle.AutoSize = $true
$ChkGoogle.ForeColor = [System.Drawing.Color]::FromArgb(126, 231, 135)
$ChkGoogle.Location = New-Object System.Drawing.Point(4, 28)

$PnlProtecao.Controls.Add($ChkStreaming)
$PnlProtecao.Controls.Add($ChkGoogle)

$Split.Panel1.Controls.Add($ClbCategorias)
$Split.Panel1.Controls.Add($PnlProtecao)
$Split.Panel1.Controls.Add($LblCatTitle)

# Direita: Botoes de Acao
$FlowBtns = New-Object System.Windows.Forms.FlowLayoutPanel
$FlowBtns.Dock = "Fill"
$FlowBtns.FlowDirection = "TopDown"
$FlowBtns.WrapContents = $false
$FlowBtns.Padding = New-Object System.Windows.Forms.Padding(10, 0, 0, 0)
$FlowBtns.AutoScroll = $true

function New-ActionBtn($Texto, $Cor, $Altura = 38) {
    $B = New-Object System.Windows.Forms.Button
    $B.Text = $Texto
    $B.BackColor = $Cor
    $B.ForeColor = [System.Drawing.Color]::White
    $B.FlatStyle = "Flat"
    $B.FlatAppearance.BorderSize = 0
    $B.Font = New-Object System.Drawing.Font("Segoe UI", 9.5, [System.Drawing.FontStyle]::Bold)
    $B.Size = New-Object System.Drawing.Size(390, $Altura)
    $B.Margin = New-Object System.Windows.Forms.Padding(4)
    $B.Cursor = [System.Windows.Forms.Cursors]::Hand
    return $B
}

$BtnScan      = New-ActionBtn "1. Analisar / Diagnosticar Tablet Conectado" $AccentBlue 40
$BtnOtimizar  = New-ActionBtn "2. OTIMIZAR TUDO AGORA (Recomendado)" $AccentGreen 44
$BtnSoBloat   = New-ActionBtn "3. Remover Apenas Bloatware Marcado" $BgInput 36
$BtnSoSistema = New-ActionBtn "4. Desligar Animações + Limpar Cache + Compilar ART" $BgInput 36
$BtnBenchmark = New-ActionBtn "5. Medir Velocidade de Abertura (Benchmark 3x)" $BgInput 36
$BtnRestaurar = New-ActionBtn "6. Reverter / Reinstalar Apps Removidos" $AccentOrange 36
$BtnPastasRom = New-ActionBtn "7. Criar Pastas de Emuladores (/sdcard/ROMs)" $BgInput 36
$BtnCheckUpd  = New-ActionBtn "8. Verificar Atualização do Android / Abrir OTA" $BgInput 36
$BtnReboot    = New-ActionBtn "9. Reiniciar Tablet (Consolidar RAM)" $BgInput 36

function Invoke-BloatwareRemoval {
    if (-not (Test-TabletConnection)) { return }
    $PkgsRaw = Invoke-AdbCommand @("shell", "pm list packages -e")
    $Ativos = @{}
    foreach ($L in ($PkgsRaw -split "`r?`n")) {
        if ($L -match "^package:(.+)$") { $Ativos[$Matches[1].Trim()] = $true }
    }

    $ArqAntes = Join-Path $ScriptDir "antes.txt"
    if (-not (Test-Path $ArqAntes)) {
        ($Ativos.Keys | Sort-Object | ForEach-Object { "package:$_" }) | Set-Content -Path $ArqAntes -Encoding UTF8
        Write-GuiLog "[Backup] Lista original salva em antes.txt"
    }

    $Alvos = New-Object System.Collections.Generic.List[string]
    for ($i = 0; $i -lt $ClbCategorias.Items.Count; $i++) {
        if (-not $ClbCategorias.GetItemChecked($i)) { continue }
        $Cat = $Categorias[$i]
        if ($Cat.Id -eq "12" -and $ChkStreaming.Checked) { continue }
        foreach ($P in $Cat.Pacotes) {
            if ($PacotesProtegidos -contains $P) { continue }
            if ($ChkStreaming.Checked -and ($Categorias[11].Pacotes -contains $P)) { continue }
            if ($ChkGoogle.Checked -and ($P -in @("com.google.android.gm", "com.google.android.apps.photos"))) { continue }
            if ($Ativos.ContainsKey($P) -and -not $Alvos.Contains($P)) {
                $Alvos.Add($P)
            }
        }
    }

    if ($Alvos.Count -eq 0) {
        Write-GuiLog "[OK] Nenhum pacote de bloatware ativo nas categorias selecionadas (seu tablet já está limpo!)."
        return
    }

    Write-GuiLog "Removendo $($Alvos.Count) pacotes no usuário 0..."
    $Removidos = New-Object System.Collections.Generic.List[string]
    $Idx = 0
    foreach ($Pkg in $Alvos) {
        $Idx++
        Set-GuiProgress $Idx $Alvos.Count "Removendo ($Idx/$($Alvos.Count)): $Pkg"
        $Res = Invoke-AdbCommand @("shell", "pm uninstall --user 0 $Pkg")
        if ($Res -match "Success") {
            Write-GuiLog "  [OK] Removido: $Pkg"
            $Removidos.Add($Pkg)
        } else {
            $ResD = Invoke-AdbCommand @("shell", "pm disable-user --user 0 $Pkg")
            if ($ResD -match "disabled-user") {
                Write-GuiLog "  [OK] Desativado: $Pkg"
                $Removidos.Add($Pkg)
            } else {
                Write-GuiLog "  [Protegido]: $Pkg"
            }
        }
    }

    if ($Removidos.Count -gt 0) {
        $ArqRem = Join-Path $ScriptDir "removidos.txt"
        $Existentes = if (Test-Path $ArqRem) { Get-Content $ArqRem } else { @() }
        ($Existentes + $Removidos | Where-Object { $_.Trim() -ne "" } | Select-Object -Unique | Sort-Object) | Set-Content -Path $ArqRem -Encoding UTF8
    }
    Write-GuiLog "[Concluído] $($Removidos.Count) pacotes removidos/desativados!"
    Invoke-TabletScan
}

function Invoke-SystemOptimization {
    if (-not (Test-TabletConnection)) { return }
    Set-GuiProgress 25 100 "Desligando animações da interface..."
    Write-GuiLog "Desligando animações (escala = 0)..."
    [void](Invoke-AdbCommand @("shell", "settings put global window_animation_scale 0"))
    [void](Invoke-AdbCommand @("shell", "settings put global transition_animation_scale 0"))
    [void](Invoke-AdbCommand @("shell", "settings put global animator_duration_scale 0"))

    Set-GuiProgress 50 100 "Limpando caches (pm trim-caches 999G)..."
    Write-GuiLog "Limpando caches de aplicativos..."
    [void](Invoke-AdbCommand @("shell", "pm trim-caches 999G"))

    Set-GuiProgress 75 100 "Pré-compilando interface e apps principais (ART speed / speed-profile)..."
    Write-GuiLog "Pré-compilando interface em modo 'speed' e apps de mídia em 'speed-profile'..."
    foreach ($AppUi in @("com.sec.android.app.launcher", "com.android.systemui", "com.android.settings", "com.samsung.android.honeyboard")) {
        [void](Invoke-AdbCommand @("shell", "cmd package compile -m speed -f $AppUi"))
    }
    foreach ($AppMedia in @("com.google.android.youtube", "com.google.android.gm", "com.google.android.apps.photos", "com.netflix.mediaclient", "com.disney.disneyplus", "com.spotify.music", "com.android.chrome")) {
        [void](Invoke-AdbCommand @("shell", "cmd package compile -m speed-profile -f $AppMedia"))
    }
    [void](Invoke-AdbCommand @("shell", "pm trim-caches 999G"))
    Set-GuiProgress 100 100 "Otimização de sistema concluída!"
    Write-GuiLog "[OK] Animações desligadas, caches limpos e apps pré-compilados!"
    Invoke-TabletScan
}

$BtnScan.Add_Click({ Invoke-TabletScan })
$BtnSoBloat.Add_Click({ Invoke-BloatwareRemoval })
$BtnSoSistema.Add_Click({ Invoke-SystemOptimization })
$BtnOtimizar.Add_Click({
    Invoke-TabletScan
    Invoke-BloatwareRemoval
    Invoke-SystemOptimization
    [System.Windows.Forms.MessageBox]::Show("Otimização concluída com sucesso!`n`nClique em '9. Reiniciar Tablet' para consolidar a memória RAM livre.", "Otimização Concluída", "OK", "Information")
})

$BtnBenchmark.Add_Click({
    if (-not (Test-TabletConnection)) { return }
    Write-GuiLog "Medindo tempo de abertura do app Configurações (3x)..."
    $Tempos = @()
    for ($i = 1; $i -le 3; $i++) {
        Set-GuiProgress $i 3 "Teste de abertura $i/3..."
        [void](Invoke-AdbCommand @("shell", "am force-stop com.android.settings"))
        Start-Sleep -Milliseconds 700
        $Out = Invoke-AdbCommand @("shell", "am start -W -n com.android.settings/.Settings")
        if ($Out -match "TotalTime:\s+(\d+)") {
            $Ms = [int]$Matches[1]
            $Tempos += $Ms
            Write-GuiLog "  Teste $i/3: $Ms ms"
        }
    }
    if ($Tempos.Count -gt 0) {
        $Media = [Math]::Round(($Tempos | Measure-Object -Average).Average, 1)
        Write-GuiLog "[Benchmark] Tempo médio de abertura: $Media ms"
    }
    Invoke-TabletScan
})

$BtnRestaurar.Add_Click({
    if (-not (Test-TabletConnection)) { return }
    $ArqRem = Join-Path $ScriptDir "removidos.txt"
    if (-not (Test-Path $ArqRem)) {
        [System.Windows.Forms.MessageBox]::Show("Arquivo removidos.txt não encontrado.", "Aviso", "OK", "Information")
        return
    }
    $Lista = Get-Content $ArqRem | Where-Object { $_.Trim() -ne "" -and -not $_.StartsWith("#") }
    $Resp = [System.Windows.Forms.MessageBox]::Show("Deseja reinstalar todos os $($Lista.Count) pacotes de removidos.txt e reativar as animações?", "Confirmar Restauração", "YesNo", "Question")
    if ($Resp -ne "Yes") { return }
    $Idx = 0
    foreach ($P in $Lista) {
        $Idx++
        Set-GuiProgress $Idx $Lista.Count "Restaurando ($Idx/$($Lista.Count)): $P"
        [void](Invoke-AdbCommand @("shell", "pm enable $P"))
        $Res = Invoke-AdbCommand @("shell", "cmd package install-existing $P")
        Write-GuiLog "  Restaurado: $P -> $Res"
    }
    [void](Invoke-AdbCommand @("shell", "settings put global window_animation_scale 1"))
    [void](Invoke-AdbCommand @("shell", "settings put global transition_animation_scale 1"))
    [void](Invoke-AdbCommand @("shell", "settings put global animator_duration_scale 1"))
    Write-GuiLog "[OK] Todos os pacotes e animações foram restaurados!"
    Invoke-TabletScan
})

$BtnPastasRom.Add_Click({
    if (-not (Test-TabletConnection)) { return }
    [void](Invoke-AdbCommand @("shell", "mkdir -p /sdcard/ROMs/_BIOS /sdcard/ROMs/_BIOS/ps2 /sdcard/ROMs/psx /sdcard/ROMs/ps2 /sdcard/ROMs/psp /sdcard/ROMs/n64 /sdcard/ROMs/snes /sdcard/ROMs/nes /sdcard/ROMs/gba /sdcard/ROMs/gb /sdcard/ROMs/gbc /sdcard/ROMs/nds /sdcard/ROMs/megadrive /sdcard/ROMs/mastersystem /sdcard/ROMs/gamegear /sdcard/ROMs/arcade"))
    Write-GuiLog "[OK] Pastas criadas em /sdcard/ROMs/ no tablet!"
})

$BtnCheckUpd.Add_Click({
    if (-not (Test-TabletConnection)) { return }
    $Build  = Invoke-AdbCommand @("shell", "getprop ro.build.display.id")
    $Patch  = Invoke-AdbCommand @("shell", "getprop ro.build.version.security_patch")
    $Treble = Invoke-AdbCommand @("shell", "getprop ro.treble.enabled")
    Write-GuiLog "Compilação Atual: $Build | Patch de Segurança: $Patch | Project Treble (GSI): $Treble"
    [void](Invoke-AdbCommand @("shell", "am start -a android.settings.SYSTEM_UPDATE_SETTINGS"))
    Write-GuiLog "[OK] Tela de Atualização de Software aberta no tablet."
})

$BtnReboot.Add_Click({
    if (-not (Test-TabletConnection)) { return }
    if ([System.Windows.Forms.MessageBox]::Show("Deseja reiniciar o tablet agora?", "Reiniciar", "YesNo", "Question") -eq "Yes") {
        [void](Invoke-AdbCommand @("reboot"))
        Write-GuiLog "Comando de reinicialização enviado!"
    }
})

$FlowBtns.Controls.AddRange(@($BtnScan, $BtnOtimizar, $BtnSoBloat, $BtnSoSistema, $BtnBenchmark, $BtnRestaurar, $BtnPastasRom, $BtnCheckUpd, $BtnReboot))
$Split.Panel2.Controls.Add($FlowBtns)
$PnlMain.Controls.Add($Split)

$Form.Controls.Add($PnlMain)
$Form.Controls.Add($PnlCards)
$Form.Controls.Add($PnlHeader)
$Form.Controls.Add($PnlFooter)

$Form.Add_Shown({
    Write-GuiLog "Aplicativo iniciado. Verificando tablet conectado..."
    Invoke-TabletScan
})

if ($TestMode) {
    Write-Host "[TESTE GUI OK] Janela construida com sucesso!"
    Invoke-TabletScan
    Write-Host "[TESTE SCAN OK] Status: $($LblStatus.Text) | Modelo: $($LblCardModelo.Text) | RAM: $($LblCardRam.Text) | Storage: $($LblCardStorage.Text) | Apps: $($LblCardApps.Text)"
} else {
    [void]$Form.ShowDialog()
}
