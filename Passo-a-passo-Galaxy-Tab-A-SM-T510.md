# Galaxy Tab A 10.1 (SM-T510): Otimização, Automação em Python e Guia de Atualização

Nov 01, 2026 · Documentação Técnica de Execução

## Visão geral

Um **Samsung Galaxy Tab A 10.1 (2019) — `SM-T510` (`gta3xlwifi`)** com 2 GB de RAM, Android 11 e One UI Core 3.1 foi diagnosticado e otimizado sem root usando o novo utilitário interativo em Python ([`otimizador_tablet.py`](otimizador_tablet.py)).

Diferente do perfil dedicado exclusivamente a jogos do Tab A8, neste `SM-T510` a otimização foi feita para **uso multimídia e cotidiano**, **preservando todos os aplicativos de streaming** (Netflix, Disney+, Prime Video, Spotify, YouTube, YouTube Kids), além de **Gmail, Google Fotos, Chrome e ChatGPT**.

Mesmo mantendo todos esses apps, **67 pacotes de bloatware e serviços em segundo plano da Samsung foram removidos com 100% de sucesso**, os pacotes ativos caíram de **336 para 271**, e o espaço livre interno subiu de **4,0 GB para 5,2 GB (+1,2 GB recuperados)**.

| Item | Valor Medido no Aparelho |
| :--- | :--- |
| **Tablet** | Samsung Galaxy Tab A 10.1 (2019) Wi-Fi, `SM-T510` (`gta3xlwifi`) |
| **Serial ADB** | `RX2N7010CWF` |
| **Sistema** | Android 11 (SDK 30), One UI Core 3.1 |
| **Compilação** | `RP1A.200720.012.T510XXS5CVL1` (Binário 5 / Dezembro 2022) |
| **Kernel** | `4.4.177-22626479` |
| **Hardware** | Exynos 7904 (`universal7904`), ~1,9 GB de RAM (`1.942.000 kB`) |
| **Arquitetura do Sistema** | 32 bits (`armeabi-v7a`) rodando sobre Kernel 64 bits (`arm32_binder64` / `a64_bvN`) |

---

## 1. Resultados Medidos (Antes vs. Depois)

| Medida | Antes da Otimização | Depois da Otimização (Pós-Reboot) | Ganho / Impacto |
| :--- | :--- | :--- | :--- |
| **Apps ativos (`pm list packages -e`)** | **336** | **271** | **-65 pacotes ativos** (67 removidos do usuário 0) |
| **Espaço livre em `/data`** | **4,0 GB** (84% ocupado) | **5,2 GB** (79% ocupado) | **+1,2 GB livres** recuperados |
| **Animações da interface** | Ligadas (`1.0`) | **Desligadas (`0.0`)** | Transição instantânea de janelas |
| **Limitador de jogos Samsung (`GOS`)** | Ativo (`com.samsung.android.game.gos`) | **Removido** | Fim da limitação agressiva de CPU |
| **Pré-compilação ART** | Padrão | **`speed`** (UI/Sistema) + **`speed-profile`** (Apps de mídia) | Abertura mais rápida sem inflar o armazenamento |
| **Processos Samsung no Top 20 de RAM** | Diversos (Bixby, Rubin, SCloud, Knox, DailyBoard) | **Zero** (Apenas Sistema Base e Apps do Usuário) | Memória dedicada aos apps reais |

> [!TIP]
> **Por que usar `speed-profile` nos apps grandes do `SM-T510`?**  
> Durante a execução, testamos primeiro a compilação total (`-m speed`) em todos os apps grandes (YouTube, Chrome, Netflix, Disney+, Fotos, ChatGPT). Isso gerou arquivos `.odex` descomprimidos que consumiram **1,4 GB** de armazenamento (reduzindo o espaço livre de 5,3 GB para 3,9 GB). Ao mudar os aplicativos gigantes para `-m speed-profile` e manter `-m speed` apenas na interface do sistema (`launcher`, `systemui`, `settings`, `honeyboard`), recuperamos **5,2 GB livres** mantendo o ganho de velocidade!

---

## 2. Como Usar o Aplicativo Gráfico Nativo (`.exe`) ou o Menu em Python

Você pode escolher entre a **interface gráfica nativa do Windows** (que não exige Python instalado) ou o **menu de terminal em Python**:

### Opção A: Aplicativo Gráfico Nativo Windows (Recomendado para usuários finais)
Dê dois cliques em **[`OtimizadorTabletSamsung.exe`](OtimizadorTabletSamsung.exe)** (ou em **[`Otimizador_Tablet_App.bat`](Otimizador_Tablet_App.bat)**):
- Exibe o **Termo de Responsabilidade** ao abrir e antes de aplicar alterações.
- Mostra cartões em tempo real com **Aparelho/Android**, **RAM Livre**, **Armazenamento (`/data`)** e **Pacotes Ativos**.
- Permite marcar/desmarcar as 12 categorias de bloatware e proteger com 1 clique seus apps de **Streaming** e **Gmail/Fotos**.
- Exibe **avisos na tela (popups)** ao concluir cada etapa (1/3 Diagnóstico, 2/3 Remoção de Bloatware, 3/3 Otimização de Sistema).

### Opção B: Menu de Terminal em Python
```powershell
# Pelo terminal ou dando dois cliques em iniciar_otimizador.bat:
python otimizador_tablet.py
```

O menu oferece 8 módulos automatizados:
1. **Conectar ao Tablet:** Baixa o ADB oficial do Google se não existir, detecta o tablet via USB e configura **ADB via Wi-Fi** automaticamente.
2. **Diagnóstico e Varredura Completa:** Gera o relatório [`varredura-tablet.txt`](varredura-tablet.txt).
3. **Remover Bloatware e Limitadores Samsung:** Remove por categoria (1 a 12) ou em lote, gerando [`antes.txt`](antes.txt), [`removidos.txt`](removidos.txt) e [`restaurar_apps.bat`](restaurar_apps.bat).
4. **Otimizações de Sistema:** Desliga animações, limpa caches (`pm trim-caches 999G`) e compila pacotes no runtime ART.
5. **Medir Ganho de Desempenho:** Compara RAM livre, pacotes ativos e o tempo médio (3x) de abertura das Configurações.
6. **Reverter Alterações:** Reinstala qualquer app removido com `cmd package install-existing`.
7. **Utilitários de Emulação:** Cria as pastas `/sdcard/ROMs/...`, ajusta o `retroarch.cfg` (tanto no RetroArch 32 bits `ra32` do `SM-T510` quanto no 64 bits `aarch64` do Tab A8) e gera arquivos `.cue` de PS1.
8. **Verificar / Iniciar Atualização do Android:** Analisa firmware, CSC, suporte a Project Treble e reinicia em Modo Download (Odin) ou Recovery.

---

## 3. Lista Completa dos 67 Pacotes Removidos no `SM-T510`

Todos os 67 pacotes abaixo estão registrados em [`removidos.txt`](removidos.txt) e podem ser restaurados a qualquer momento com [`restaurar_apps.bat`](restaurar_apps.bat):

| Categoria | Quantidade | Pacotes Removidos |
| :--- | :---: | :--- |
| **Bixby, Painéis Edge e Busca** | 5 | `com.samsung.android.app.settings.bixby`, `com.samsung.android.app.appsedge`, `com.samsung.android.app.cocktailbarservice`, `com.samsung.android.app.clipboardedge`, `com.samsung.android.app.galaxyfinder` |
| **Nuvem, Conta, Push e Telemetria Samsung** | 7 | `com.samsung.android.scloud`, `com.samsung.android.mobileservice`, `com.samsung.android.rubin.app`, `com.samsung.android.bbc.bbcagent`, `com.samsung.android.dqagent`, `com.sec.android.diagmonagent`, `com.sec.spp.push` |
| **Knox e Pasta Segura** | 8 | `com.samsung.android.knox.analytics.uploader`, `com.samsung.android.knox.attestation`, `com.samsung.knox.securefolder`, `com.samsung.android.knox.containeragent`, `com.samsung.android.knox.containercore`, `com.samsung.android.knox.pushmanager`, `com.sec.enterprise.knox.attestation`, `com.sec.enterprise.knox.cloudmdm.smdms` |
| **Compartilhamento, SmartThings e TV** | 16 | `com.samsung.android.app.sharelive`, `com.samsung.android.app.simplesharing`, `com.samsung.android.privateshare`, `com.samsung.android.mdx.kit`, `com.samsung.android.mdx.quickboard`, `com.samsung.android.smartmirroring`, `com.samsung.android.allshare.service.mediashare`, `com.samsung.android.allshare.service.fileshare`, `com.samsung.android.beaconmanager`, `com.samsung.android.mapsagent`, `com.samsung.android.aware.service`, `com.samsung.android.easysetup`, `com.samsung.android.service.stplatform`, `com.samsung.android.mcfds`, `com.samsung.android.mcfserver`, `com.samsung.android.app.watchmanagerstub` |
| **Temas, Stickers, Clima, Porta-Retrato e Edição** | 13 | `com.sec.android.daemonapp`, `com.sec.android.app.ve.vebgm`, `com.sec.android.mimage.photoretouching`, `com.samsung.app.newtrim`, `com.sec.android.app.DataCreate`, `com.samsung.storyservice`, `com.samsung.android.stickercenter`, `com.samsung.android.livestickers`, `com.samsung.android.icecone`, `com.samsung.android.themecenter`, `com.samsung.android.app.dressroom`, `com.samsung.android.dynamiclock`, `com.samsung.android.homemode` |
| **Transferência, Kids, Manuais e Sensores ANT+** | 10 | `com.samsung.android.smartswitchassistant`, `com.sec.android.easyMover.Agent`, `com.samsung.android.kidsinstaller`, `com.samsung.android.forest`, `com.sec.android.usermanual`, `com.diotek.sec.lookup.dictionary`, `com.dsi.ant.plugins.antplus`, `com.dsi.ant.sample.acquirechannels`, `com.dsi.ant.server`, `com.dsi.ant.service.socket` |
| **Limitador de Jogos e Terceiros** | 3 | `com.samsung.android.game.gos`, `com.hiya.star`, `com.microsoft.skydrive` |
| **Google Secundários (Não usados pelo usuário)** | 5 | `com.google.android.apps.tachyon` (Meet/Duo), `com.google.android.videos` (Google TV), `com.google.android.apps.docs` (Drive), `com.google.android.apps.maps` (Maps), `com.google.android.googlequicksearchbox` (App Google) |

### Pacotes Mantidos Intactos a Pedido do Usuário
- **Streaming:** `com.netflix.mediaclient`, `com.disney.disneyplus`, `com.amazon.avod.thirdpartyclient`, `com.spotify.music`, `com.google.android.youtube`, `com.google.android.apps.youtube.kids`.
- **Google e Uso Pessoal:** `com.google.android.gm` (Gmail), `com.google.android.apps.photos` (Google Fotos), `com.openai.chatgpt` (ChatGPT), `com.android.chrome` (Chrome), `com.android.vending` (Play Store), `com.google.android.gms` (Play Services).

---

## 4. Guia de Atualização de Versão do Android para o `SM-T510`

### 4.1. Situação Oficial da Samsung
- A compilação atual do aparelho (`RP1A.200720.012.T510XXS5CVL1`) **já é a última versão oficial lançada pela Samsung** (Android 11, One UI Core 3.1, Bootloader Binário 5).
- Não existe atualização oficial via OTA para Android 12, 13 ou 14 neste modelo.

### 4.2. Como Atualizar para o Android 13 ou 14 via Custom ROM (`LineageOS 20 / 21`)
Como o tablet já está no **Binário 5 (`XXS5CVL1`)**, ele já possui a base de bootloader e vendor exigida pelas ROMs customizadas mais recentes do `SM-T510` (`gta3xlwifi`) no XDA Developers (mantidas por *Magendanz* e *retiredtab*):

1. **Requisitos e Avisos:**
   - **Apaga todos os dados:** Faça backup de fotos e arquivos antes de começar.
   - **Knox `0x1`:** Desbloquear o bootloader altera o bit de garantia Knox permanentemente.
   - **Ganho de Memória:** Como o LineageOS não carrega a One UI da Samsung, o consumo de RAM cai drasticamente no modelo de 2 GB, rodando Android 13 ou 14 puro com mais folga que o Android 11 original.

2. **Passo 1 — Desbloquear o Bootloader:**
   - Conectado ao Wi-Fi, abra **Configurações > Opções do desenvolvedor** e ative **Desbloqueio de OEM (OEM Unlocking)**.
   - Desligue o tablet completamente.
   - Segure **Volume Cima + Volume Baixo** juntos e conecte o cabo USB ao computador.
   - Quando a tela azul aparecer, segure **Volume Cima** por alguns segundos até entrar na tela de confirmação de *Unlock Bootloader*, e aperte **Volume Cima** para confirmar (o tablet será formatado).
   - Assim que reiniciar no sistema original, conecte ao Wi-Fi novamente e verifique em *Opções do desenvolvedor* se o **Desbloqueio de OEM** aparece ativado e acinzentado.

3. **Passo 2 — Instalar o TWRP Recovery e LineageOS via Odin:**
   - Coloque o tablet em **Modo Download** (você pode usar a **opção `[8] -> [2]`** do [`otimizador_tablet.py`](otimizador_tablet.py)).
   - No computador, abra o **Odin3 v3.14.4**.
   - Se usar o pacote integrado `.tar.md5` do *Magendanz* (LineageOS + TWRP para `SM-T510` Binário 5), selecione-o no slot **`AP`** do Odin e clique em **Start**.
   - Se instalar o **TWRP (`twrp-3.7.x-gta3xlwifi.tar`)** separadamente no slot **`AP`**:
     1. Desmarque *Auto Reboot* no Odin e clique em **Start**.
     2. Segure **Volume Baixo + Power** por 7 segundos; assim que a tela apagar, mude imediatamente para **Volume Cima + Power** até abrir o TWRP.
     3. No TWRP, instale o `multidisabler-samsung-3.x.zip`, vá em **Wipe > Format Data**, digite `yes` e instale o `.zip` do **LineageOS 20 (Android 13)** ou **LineageOS 21 (Android 14)** para `gta3xlwifi`.

