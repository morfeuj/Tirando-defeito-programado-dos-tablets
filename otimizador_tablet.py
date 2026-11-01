#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Otimizador Interativo para Tablets Samsung / Android (via ADB, sem root)
Baseado no projeto: Tirando-defeito-programado-dos-tablets (Galaxy Tab A8 SM-X200)
"""

import os
import re
import sys
import time
import shutil
import zipfile
import subprocess
import urllib.request
from datetime import datetime
from pathlib import Path

# Garante saída UTF-8 no terminal do Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    os.system("")  # Ativa suporte a sequências ANSI no Windows 10/11

BASE_DIR = Path(__file__).resolve().parent
PLATFORM_TOOLS_DIR = BASE_DIR / "platform-tools"
ADB_URL_WINDOWS = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"

# Cores ANSI
class Cor:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    VERDE = "\033[92m"
    AMARELO = "\033[93m"
    VERMELHO = "\033[91m"
    CIANO = "\033[96m"
    AZUL = "\033[94m"
    CINZA = "\033[90m"


# Categorias de pacotes mapeadas a partir do guia do Galaxy Tab A8 (68 pacotes)
CATEGORIAS_PACOTES = {
    "1": {
        "nome": "Bixby, Rotinas e Painéis Edge",
        "aviso": "Remove assistente Bixby, Samsung Free (spage), Routines e painéis laterais Edge.",
        "pacotes": [
            "com.samsung.android.app.spage",
            "com.samsung.android.app.settings.bixby",
            "com.samsung.android.app.routines",
            "com.samsung.android.app.appsedge",
            "com.samsung.android.app.taskedge",
            "com.samsung.android.app.cocktailbarservice",
            "com.samsung.android.app.clipboardedge",
        ],
    },
    "2": {
        "nome": "Nuvem, Conta e Diagnóstico Samsung",
        "aviso": "Remove Samsung Cloud, Samsung Account, Customização (Rubin) e telemetria. Não remova se usar conta Samsung.",
        "pacotes": [
            "com.samsung.android.scloud",
            "com.samsung.android.mobileservice",
            "com.samsung.android.scs",
            "com.samsung.android.rubin.app",
            "com.samsung.android.bbc.bbcagent",
            "com.samsung.android.dqagent",
            "com.sec.android.diagmonagent",
        ],
    },
    "3": {
        "nome": "Transferência (Smart Switch) e Modo Crianças",
        "aviso": "Remove Smart Switch, instalador do Samsung Kids, Controle Parental e Bem-estar Digital.",
        "pacotes": [
            "com.samsung.android.smartswitchassistant",
            "com.sec.android.easyMover",
            "com.sec.android.easyMover.Agent",
            "com.samsung.android.kidsinstaller",
            "com.samsung.android.app.parentalcare",
            "com.samsung.android.forest",
        ],
    },
    "4": {
        "nome": "Compartilhamento, Continuidade e Espelhamento",
        "aviso": "Remove Quick Share, Smart View (espelhamento de tela), Galaxy Continuity e AllShare.",
        "pacotes": [
            "com.samsung.android.app.sharelive",
            "com.samsung.android.galaxycontinuity",
            "com.samsung.android.mdx.kit",
            "com.samsung.android.mdx.quickboard",
            "com.samsung.android.smartmirroring",
            "com.samsung.android.allshare.service.mediashare",
            "com.samsung.android.beaconmanager",
            "com.samsung.android.mapsagent",
            "com.samsung.android.aware.service",
        ],
    },
    "5": {
        "nome": "Clima, Vídeo, Foto, Stickers e Temas",
        "aviso": "Remove widgets de clima, editores secundários de foto/vídeo, Galaxy Themes e molduras.",
        "pacotes": [
            "com.sec.android.daemonapp",
            "com.sec.android.app.ve.vebgm",
            "com.sec.android.autodoodle.service",
            "com.sec.android.mimage.photoretouching",
            "com.samsung.app.newtrim",
            "com.sec.android.app.DataCreate",
            "com.samsung.storyservice",
            "com.samsung.android.stickercenter",
            "com.samsung.android.themecenter",
            "com.samsung.android.app.dressroom",
            "com.samsung.android.dynamiclock",
            "com.samsung.android.widget.pictureframe",
        ],
    },
    "6": {
        "nome": "Mensagens SMS e Telemetria Knox",
        "aviso": "ATENÇÃO: Se o seu tablet usa chip/SMS, NÃO remova com.samsung.android.messaging.",
        "pacotes": [
            "com.samsung.android.messaging",
            "com.samsung.android.knox.analytics.uploader",
            "com.samsung.android.knox.app.networkfilter",
            "com.samsung.android.knox.attestation",
        ],
    },
    "7": {
        "nome": "Anúncios e Apps de Terceiros (Microsoft / AppLovin / Hiya)",
        "aviso": "Remove AppHub (AppLovin), Hiya, Outlook e OneDrive.",
        "pacotes": [
            "com.applovin.array.apphub.samsung",
            "com.hiya.star",
            "com.microsoft.office.outlook",
            "com.microsoft.skydrive",
        ],
    },
    "8": {
        "nome": "Apps do Google (Para tablets sem uso de suíte Google)",
        "aviso": "ATENÇÃO: Remove Gmail, Fotos, Maps, Drive/Docs, YouTube Music, Meet e app Google. Mantém Play Store e Play Services.",
        "pacotes": [
            "com.google.android.apps.youtube.music",
            "com.google.android.apps.photos",
            "com.google.android.gm",
            "com.google.android.apps.tachyon",
            "com.google.android.videos",
            "com.google.android.apps.messaging",
            "com.google.android.apps.docs",
            "com.google.android.apps.maps",
            "com.google.android.googlequicksearchbox",
        ],
    },
    "9": {
        "nome": "Vozes de Leitura (TTS) em Idiomas Estrangeiros",
        "aviso": "Remove pacotes de voz Samsung TTS em alemão, inglês, espanhol, francês, italiano e russo.",
        "pacotes": [
            "com.samsung.SMT.lang_de_de_f00",
            "com.samsung.SMT.lang_en_gb_f00",
            "com.samsung.SMT.lang_en_us_l03",
            "com.samsung.SMT.lang_es_es_f00",
            "com.samsung.SMT.lang_es_mx_f00",
            "com.samsung.SMT.lang_fr_fr_f00",
            "com.samsung.SMT.lang_it_it_f00",
            "com.samsung.SMT.lang_ru_ru_f00",
        ],
    },
    "10": {
        "nome": "Limitadores e Hub de Jogos Samsung (GOS, Game Launcher, Game Tools)",
        "aviso": "Libera o desempenho máximo em jogos/emuladores (inclui pacotes do Tab A8 e do SM-T510).",
        "pacotes": [
            "com.samsung.android.game.gos",
            "com.sec.android.smartfpsadjuster",
            "com.samsung.android.game.gamehome",
            "com.samsung.android.game.gametools",
        ],
    },
    "11": {
        "nome": "Extras do Galaxy Tab A 10.1 SM-T510 (One UI Core 3.1 / Android 11)",
        "aviso": "Pacotes extras detectados no SM-T510: Daily Board, ANT+, Galaxy Wearable, Pasta Segura, SmartThings, Dicionário, Manuais e stickers.",
        "pacotes": [
            "com.sec.android.app.kidshome",
            "com.sec.android.usermanual",
            "com.sec.android.widgetapp.webmanual",
            "com.diotek.sec.lookup.dictionary",
            "com.dsi.ant.plugins.antplus",
            "com.dsi.ant.sample.acquirechannels",
            "com.dsi.ant.server",
            "com.dsi.ant.service.socket",
            "com.samsung.android.homemode",
            "com.samsung.android.livestickers",
            "com.samsung.android.icecone",
            "com.samsung.android.app.watchmanagerstub",
            "com.samsung.android.app.simplesharing",
            "com.samsung.android.privateshare",
            "com.samsung.android.allshare.service.fileshare",
            "com.samsung.android.easysetup",
            "com.samsung.android.service.stplatform",
            "com.samsung.android.mcfds",
            "com.samsung.android.mcfserver",
            "com.samsung.knox.securefolder",
            "com.samsung.android.knox.containeragent",
            "com.samsung.android.knox.containercore",
            "com.samsung.android.knox.pushmanager",
            "com.sec.enterprise.knox.attestation",
            "com.sec.enterprise.knox.cloudmdm.smdms",
            "com.sec.spp.push",
            "com.samsung.android.aremoji",
            "com.sec.android.mimage.avatarstickers",
            "com.samsung.android.FastSwitch",
            "com.samsung.android.app.galaxyfinder",
        ],
    },
    "12": {
        "nome": "Apps de Streaming / Vídeo Pré-instalados (Netflix, Spotify, Disney+, Prime, YT Kids)",
        "aviso": "Remova apenas os que você NÃO assiste/usa neste tablet.",
        "pacotes": [
            "com.netflix.mediaclient",
            "com.netflix.partner.activation",
            "com.spotify.music",
            "com.disney.disneyplus",
            "com.amazon.avod.thirdpartyclient",
            "com.google.android.apps.youtube.kids",
        ],
    },
}

# Pacotes críticos que nunca devem ser removidos
PACOTES_PROTEGIDOS = {
    "android",
    "com.android.systemui",
    "com.android.settings",
    "com.android.vending",              # Google Play Store
    "com.google.android.gms",           # Google Play Services
    "com.sec.android.app.samsungapps",  # Galaxy Store
    "com.android.chrome",               # Único navegador padrão
    "com.samsung.android.honeyboard",   # Teclado Samsung
    "com.sec.android.app.launcher",     # Tela inicial One UI Home
}


class GerenciadorADB:
    def __init__(self):
        self.adb_path = self._localizar_adb()
        self.serial = None
        self.ultima_medicao = None

    def _localizar_adb(self) -> str | None:
        adb_sistema = shutil.which("adb")
        if adb_sistema:
            return adb_sistema
        adb_local = PLATFORM_TOOLS_DIR / ("adb.exe" if os.name == "nt" else "adb")
        if adb_local.exists():
            return str(adb_local)
        return None

    def garantir_adb(self) -> bool:
        self.adb_path = self._localizar_adb()
        if self.adb_path:
            return True

        print(f"\n{Cor.AMARELO}[!] O ADB não foi encontrado no sistema nem na pasta local.{Cor.RESET}")
        resp = input("Deseja baixar e extrair o ADB oficial do Google agora (~15 MB)? [S/n]: ").strip().lower()
        if resp not in ("", "s", "sim", "y", "yes"):
            return False

        zip_path = BASE_DIR / "platform-tools-latest-windows.zip"
        try:
            print(f"{Cor.CIANO}Baixando {ADB_URL_WINDOWS}...{Cor.RESET}")
            urllib.request.urlretrieve(ADB_URL_WINDOWS, zip_path)
            print(f"{Cor.CIANO}Extraindo para {BASE_DIR}...{Cor.RESET}")
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(BASE_DIR)
            zip_path.unlink(missing_ok=True)
            self.adb_path = self._localizar_adb()
            if self.adb_path:
                print(f"{Cor.VERDE}[OK] ADB instalado em: {self.adb_path}{Cor.RESET}")
                return True
        except Exception as e:
            print(f"{Cor.VERMELHO}[ERRO] Falha ao baixar/extrair o ADB: {e}{Cor.RESET}")
        return False

    def executar(self, args: list[str], timeout: int = 120) -> tuple[int, str, str]:
        if not self.adb_path and not self.garantir_adb():
            return 1, "", "ADB não disponível."

        cmd = [self.adb_path]
        if self.serial and args[:1] != ["devices"] and args[:1] != ["connect"] and args[:1] != ["disconnect"]:
            cmd.extend(["-s", self.serial])
        cmd.extend(args)

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
            )
            return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
        except subprocess.TimeoutExpired:
            return 124, "", f"Comando excedeu o tempo limite ({timeout}s)."
        except Exception as e:
            return 1, "", str(e)

    def shell(self, comando: str, timeout: int = 120) -> tuple[int, str, str]:
        return self.executar(["shell", comando], timeout=timeout)

    def listar_dispositivos(self) -> list[tuple[str, str, str]]:
        code, out, _ = self.executar(["devices", "-l"])
        if code != 0:
            return []
        dispositivos = []
        for linha in out.splitlines()[1:]:
            linha = linha.strip()
            if not linha:
                continue
            partes = linha.split()
            if len(partes) >= 2:
                serial = partes[0]
                estado = partes[1]
                detalhes = " ".join(partes[2:])
                dispositivos.append((serial, estado, detalhes))
        return dispositivos

    def verificar_conexao(self, silencioso: bool = False) -> bool:
        if not self.garantir_adb():
            return False

        dispositivos = self.listar_dispositivos()
        prontos = [d for d in dispositivos if d[1] == "device"]
        nao_autorizados = [d for d in dispositivos if d[1] == "unauthorized"]

        if nao_autorizados and not prontos:
            if not silencioso:
                print(f"\n{Cor.AMARELO}[!] Tablet detectado ({nao_autorizados[0][0]}), mas NÃO AUTORIZADO.{Cor.RESET}")
                print("    Olhe a tela do tablet, marque 'Sempre permitir deste computador' e toque em 'Permitir'.")
            return False

        if not prontos:
            if not silencioso:
                print(f"\n{Cor.VERMELHO}[!] Nenhum tablet conectado em estado 'device'.{Cor.RESET}")
                print("    Dicas para Samsung Galaxy Tab A8:")
                print("    1. Ative Opções do Desenvolvedor > Depuração USB.")
                print("    2. Se não aparecer no Windows, ative: Configurações > Conexões > Roteador Wi-Fi e Ancoragem > Ancoragem USB.")
            return False

        if self.serial and any(d[0] == self.serial for d in prontos):
            return True

        if len(prontos) == 1:
            self.serial = prontos[0][0]
            return True

        print(f"\n{Cor.CIANO}Múltiplos aparelhos encontrados:{Cor.RESET}")
        for idx, (ser, est, det) in enumerate(prontos, 1):
            print(f"  [{idx}] {ser} ({det})")
        escolha = input("Escolha o número do aparelho: ").strip()
        if escolha.isdigit() and 1 <= int(escolha) <= len(prontos):
            self.serial = prontos[int(escolha) - 1][0]
            return True

        self.serial = prontos[0][0]
        return True


def cabecalho(adb: GerenciadorADB):
    os.system("cls" if os.name == "nt" else "clear")
    print(f"{Cor.CIANO}{Cor.BOLD}======================================================================{Cor.RESET}")
    print(f"{Cor.CIANO}{Cor.BOLD}   OTIMIZADOR DE TABLET SAMSUNG / ANDROID (SEM ROOT VIA ADB){Cor.RESET}")
    print(f"{Cor.AMARELO}   AVISO: Todas as alterações são de inteira responsabilidade de quem executa.{Cor.RESET}")
    print(f"{Cor.CIANO}{Cor.BOLD}======================================================================{Cor.RESET}")

    if adb.adb_path:
        dispositivos = adb.listar_dispositivos()
        prontos = [d for d in dispositivos if d[1] == "device"]
        if prontos:
            if not adb.serial or not any(d[0] == adb.serial for d in prontos):
                adb.serial = prontos[0][0]
            _, modelo, _ = adb.shell("getprop ro.product.model")
            _, android_ver, _ = adb.shell("getprop ro.build.version.release")
            print(f" Status ADB : {Cor.VERDE}CONECTADO{Cor.RESET} | Serial: {Cor.BOLD}{adb.serial}{Cor.RESET} | Modelo: {Cor.BOLD}{modelo or '?'}{Cor.RESET} (Android {android_ver or '?'})")
        elif dispositivos:
            print(f" Status ADB : {Cor.AMARELO}AGUARDANDO AUTORIZAÇÃO NA TELA DO TABLET ({dispositivos[0][0]}){Cor.RESET}")
        else:
            print(f" Status ADB : {Cor.VERMELHO}DESCONECTADO{Cor.RESET} (Use a opção 1 para conectar via USB ou Wi-Fi)")
    else:
        print(f" Status ADB : {Cor.AMARELO}ADB NÃO INSTALADO{Cor.RESET} (Será baixado automaticamente quando necessário)")
    print(f"{Cor.CIANO}----------------------------------------------------------------------{Cor.RESET}")


def pausar():
    input(f"\n{Cor.CINZA}Pressione ENTER para voltar ao menu...{Cor.RESET}")


def menu_conexao(adb: GerenciadorADB):
    cabecalho(adb)
    print(f"{Cor.BOLD}1. CONEXÃO ADB (USB E WI-FI){Cor.RESET}\n")
    print("  [1] Verificar conexão USB atual / Selecionar dispositivo")
    print("  [2] Ativar ADB sem fio (requer cabo USB conectado agora)")
    print("  [3] Conectar ao tablet por IP via Wi-Fi (sem cabo)")
    print("  [4] Desconectar sessões Wi-Fi do ADB")
    print("  [0] Voltar")

    op = input("\nEscolha uma opção: ").strip()
    if op == "1":
        if adb.verificar_conexao(silencioso=False):
            print(f"\n{Cor.VERDE}[OK] Dispositivo pronto: {adb.serial}{Cor.RESET}")
        pausar()
    elif op == "2":
        if not adb.verificar_conexao():
            pausar()
            return
        _, ip_out, _ = adb.shell("ip -f inet addr show wlan0")
        match = re.search(r"inet\s+(\d+\.\d+\.\d+\.\d+)", ip_out)
        ip_tablet = match.group(1) if match else ""
        print(f"\n{Cor.CIANO}Abrindo porta TCP 5555 no tablet...{Cor.RESET}")
        adb.executar(["tcpip", "5555"])
        time.sleep(2)
        if not ip_tablet:
            ip_tablet = input("Digite o IP do tablet (ex: 192.168.0.5): ").strip()
        else:
            print(f"IP detectado no Wi-Fi (wlan0): {Cor.BOLD}{ip_tablet}{Cor.RESET}")
        if ip_tablet:
            _, out, err = adb.executar(["connect", f"{ip_tablet}:5555"])
            print(f"{Cor.VERDE}{out or err}{Cor.RESET}")
            print("Agora você já pode desconectar o cabo USB!")
        pausar()
    elif op == "3":
        if not adb.garantir_adb():
            pausar()
            return
        ip_tablet = input("Digite o IP do tablet [padrão: 192.168.0.5]: ").strip() or "192.168.0.5"
        porta = input("Digite a porta [padrão: 5555]: ").strip() or "5555"
        _, out, err = adb.executar(["connect", f"{ip_tablet}:{porta}"])
        print(f"\n{Cor.CIANO}{out or err}{Cor.RESET}")
        adb.verificar_conexao(silencioso=True)
        pausar()
    elif op == "4":
        adb.executar(["disconnect"])
        adb.serial = None
        print(f"\n{Cor.AMARELO}Sessões ADB Wi-Fi desconectadas.{Cor.RESET}")
        pausar()


def realizar_varredura(adb: GerenciadorADB):
    cabecalho(adb)
    print(f"{Cor.BOLD}2. DIAGNÓSTICO E VARREDURA DO TABLET (SOMENTE LEITURA){Cor.RESET}\n")
    if not adb.verificar_conexao():
        pausar()
        return

    print(f"{Cor.CIANO}Coletando informações do sistema, memória, armazenamento e pacotes...{Cor.RESET}\n")

    props = [
        "ro.product.brand",
        "ro.product.manufacturer",
        "ro.product.model",
        "ro.product.device",
        "ro.build.version.release",
        "ro.build.version.sdk",
        "ro.build.display.id",
        "ro.product.cpu.abilist",
        "ro.board.platform",
        "ro.soc.manufacturer",
        "ro.soc.model",
    ]
    info_props = {}
    for p in props:
        _, val, _ = adb.shell(f"getprop {p}")
        info_props[p] = val

    _, meminfo, _ = adb.shell("grep -E 'MemTotal|MemAvailable|SwapTotal|SwapFree' /proc/meminfo")
    _, df_data, _ = adb.shell("df -h /data")
    _, bateria, _ = adb.shell("dumpsys battery")
    _, wm_size, _ = adb.shell("wm size")
    _, wm_density, _ = adb.shell("wm density")

    _, anim_win, _ = adb.shell("settings get global window_animation_scale")
    _, anim_trans, _ = adb.shell("settings get global transition_animation_scale")
    _, anim_dur, _ = adb.shell("settings get global animator_duration_scale")

    _, pkgs_ativos_raw, _ = adb.shell("pm list packages -e")
    _, pkgs_desativados_raw, _ = adb.shell("pm list packages -d")
    _, pkgs_terceiros_raw, _ = adb.shell("pm list packages -3")
    _, device_policy, _ = adb.shell("dumpsys device_policy")

    pkgs_ativos = [l.replace("package:", "").strip() for l in pkgs_ativos_raw.splitlines() if l.strip()]
    pkgs_desativados = [l.replace("package:", "").strip() for l in pkgs_desativados_raw.splitlines() if l.strip()]
    pkgs_terceiros = [l.replace("package:", "").strip() for l in pkgs_terceiros_raw.splitlines() if l.strip()]

    # Verifica quantos dos 68 pacotes de bloatware conhecidos ainda estão ativos
    todos_bloat = {p for cat in CATEGORIAS_PACOTES.values() for p in cat["pacotes"]}
    bloat_presentes = sorted(todos_bloat.intersection(pkgs_ativos))

    # Extrai MemTotal e MemAvailable em MB
    def extrair_mb(texto: str, chave: str) -> float:
        m = re.search(rf"{chave}:\s+(\d+)\s+kB", texto)
        return round(int(m.group(1)) / 1024, 1) if m else 0.0

    mem_total_mb = extrair_mb(meminfo, "MemTotal")
    mem_livre_mb = extrair_mb(meminfo, "MemAvailable")

    print(f"  {Cor.BOLD}Modelo:{Cor.RESET}           {info_props.get('ro.product.manufacturer')} {info_props.get('ro.product.model')} ({info_props.get('ro.product.device')})")
    print(f"  {Cor.BOLD}Android / Build:{Cor.RESET}  Android {info_props.get('ro.build.version.release')} (SDK {info_props.get('ro.build.version.sdk')}) - {info_props.get('ro.build.display.id')}")
    print(f"  {Cor.BOLD}Processador/SoC:{Cor.RESET}  {info_props.get('ro.soc.manufacturer')} {info_props.get('ro.soc.model')} ({info_props.get('ro.product.cpu.abilist')})")
    print(f"  {Cor.BOLD}Memória RAM:{Cor.RESET}      {Cor.VERDE}{mem_livre_mb} MB livres{Cor.RESET} de {mem_total_mb} MB totais")
    print(f"  {Cor.BOLD}Animações:{Cor.RESET}        Janela={anim_win} | Transição={anim_trans} | Animator={anim_dur}")
    print(f"  {Cor.BOLD}Apps Ativos:{Cor.RESET}      {len(pkgs_ativos)} ativos | {len(pkgs_desativados)} desativados | {len(pkgs_terceiros)} instalados pelo usuário")
    print(f"  {Cor.BOLD}Bloatware Tab A8:{Cor.RESET} {Cor.AMARELO}{len(bloat_presentes)} de {len(todos_bloat)} pacotes recomendados para remoção estão ativos{Cor.RESET}")

    print(f"\n  {Cor.BOLD}Armazenamento (/data):{Cor.RESET}")
    for linha in df_data.splitlines():
        print(f"    {linha}")

    if "Device Owner" in device_policy or "Profile Owner" in device_policy:
        print(f"\n  {Cor.VERMELHO}[ATENÇÃO] Device/Profile Owner detectado em dumpsys device_policy!{Cor.RESET}")
        print("  Este aparelho pode ser gerenciado por empresa ou escola.")

    # Salva relatório em varredura-tablet.txt
    arq_relatorio = BASE_DIR / "varredura-tablet.txt"
    with open(arq_relatorio, "w", encoding="utf-8") as f:
        f.write(f"=== VARREDURA DO TABLET ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ===\n\n")
        for k, v in info_props.items():
            f.write(f"{k}: {v}\n")
        f.write(f"\n--- MEMÓRIA ---\n{meminfo}\n")
        f.write(f"\n--- ARMAZENAMENTO ---\n{df_data}\n")
        f.write(f"\n--- TELA E ANIMAÇÕES ---\n{wm_size}\n{wm_density}\n")
        f.write(f"window_animation_scale={anim_win}\ntransition_animation_scale={anim_trans}\nanimator_duration_scale={anim_dur}\n")
        f.write(f"\n--- BATERIA ---\n{bateria}\n")
        f.write(f"\n--- BLOATWARE DETECTADO ({len(bloat_presentes)}) ---\n" + "\n".join(bloat_presentes) + "\n")
        f.write(f"\n--- PACOTES ATIVOS ({len(pkgs_ativos)}) ---\n" + "\n".join(sorted(pkgs_ativos)) + "\n")

    print(f"\n{Cor.VERDE}[OK] Relatório completo salvo em: {arq_relatorio}{Cor.RESET}")
    pausar()


def salvar_backup_antes(adb: GerenciadorADB, pkgs_ativos: list[str]):
    arq_antes = BASE_DIR / "antes.txt"
    if not arq_antes.exists():
        with open(arq_antes, "w", encoding="utf-8") as f:
            for p in sorted(pkgs_ativos):
                f.write(f"package:{p}\n")
        print(f"{Cor.VERDE}[Backup] Lista original salva em: {arq_antes.name}{Cor.RESET}")


def registrar_removidos(pacotes_removidos: list[str]):
    if not pacotes_removidos:
        return
    arq_rem = BASE_DIR / "removidos.txt"
    existentes = set()
    if arq_rem.exists():
        existentes = {
            l.strip()
            for l in arq_rem.read_text(encoding="utf-8").splitlines()
            if l.strip() and not l.strip().startswith("#")
        }
    atualizados = sorted(existentes.union(pacotes_removidos))
    with open(arq_rem, "w", encoding="utf-8") as f:
        for p in atualizados:
            f.write(f"{p}\n")

    # Também gera script .bat de restauração rápida
    arq_bat = BASE_DIR / "restaurar_apps.bat"
    with open(arq_bat, "w", encoding="utf-8") as f:
        f.write("@echo off\nchcp 65001 >nul\necho Restaurando pacotes removidos...\n")
        for p in atualizados:
            f.write(f"adb shell cmd package install-existing {p}\n")
        f.write("echo Concluido!\npause\n")


def menu_remover_bloatware(adb: GerenciadorADB):
    while True:
        cabecalho(adb)
        print(f"{Cor.BOLD}3. REMOVER BLOATWARE E SERVIÇOS EM SEGUNDO PLANO (SEM ROOT){Cor.RESET}\n")
        if not adb.verificar_conexao():
            pausar()
            return

        _, pkgs_ativos_raw, _ = adb.shell("pm list packages -e")
        pkgs_ativos = {l.replace("package:", "").strip() for l in pkgs_ativos_raw.splitlines() if l.strip()}

        print("Escolha a categoria que deseja analisar/remover:\n")
        for cid, dados in CATEGORIAS_PACOTES.items():
            ativos_cat = [p for p in dados["pacotes"] if p in pkgs_ativos]
            cor_qtd = Cor.AMARELO if ativos_cat else Cor.VERDE
            print(f"  [{cid:>2}] {dados['nome']} ({cor_qtd}{len(ativos_cat)}/{len(dados['pacotes'])} ativos{Cor.RESET})")

        todos_bloat = [p for d in CATEGORIAS_PACOTES.values() for p in d["pacotes"] if p in pkgs_ativos]
        print(f"\n  [T]  {Cor.BOLD}Selecionar TODAS as categorias recomendadas ({len(todos_bloat)} pacotes ativos){Cor.RESET}")
        print("  [M]  Digitar nome de um pacote manualmente")
        print("  [0]  Voltar ao menu principal")

        escolha = input("\nOpção (ou números separados por vírgula, ex: 1,2,10): ").strip().upper()
        if escolha == "0" or not escolha:
            return

        alvos = []
        if escolha == "T":
            usa_google = input("Você usa Conta Google (Gmail, Fotos, Maps, Drive) neste tablet? [s/N]: ").strip().lower()
            usa_chip = input("Você usa Chip SIM / SMS neste tablet? [s/N]: ").strip().lower()
            for cid, dados in CATEGORIAS_PACOTES.items():
                if cid == "8" and usa_google in ("s", "sim", "y", "yes"):
                    continue
                for p in dados["pacotes"]:
                    if p == "com.samsung.android.messaging" and usa_chip in ("s", "sim", "y", "yes"):
                        continue
                    if p in pkgs_ativos and p not in alvos:
                        alvos.append(p)
        elif escolha == "M":
            pkg_manual = input("Digite o nome exato do pacote (ex: com.samsung.android.app.spage): ").strip()
            if pkg_manual in PACOTES_PROTEGIDOS:
                print(f"{Cor.VERMELHO}[BLOQUEADO] {pkg_manual} é um pacote crítico protegido!{Cor.RESET}")
                pausar()
                continue
            if pkg_manual:
                alvos.append(pkg_manual)
        else:
            ids = [x.strip() for x in escolha.split(",")]
            for cid in ids:
                if cid in CATEGORIAS_PACOTES:
                    print(f"\n{Cor.AMARELO}Aviso ({CATEGORIAS_PACOTES[cid]['nome']}): {CATEGORIAS_PACOTES[cid]['aviso']}{Cor.RESET}")
                    for p in CATEGORIAS_PACOTES[cid]["pacotes"]:
                        if p in pkgs_ativos and p not in alvos:
                            alvos.append(p)

        if not alvos:
            print(f"\n{Cor.VERDE}Nenhum pacote ativo encontrado nas categorias selecionadas (já foram removidos!).{Cor.RESET}")
            pausar()
            continue

        print(f"\n{Cor.CIANO}Pacotes que serão removidos do usuário 0 ({len(alvos)}):{Cor.RESET}")
        for p in alvos:
            print(f"  - {p}")

        conf = input(f"\nConfirma a remoção destes {len(alvos)} pacotes? [s/N]: ").strip().lower()
        if conf not in ("s", "sim", "y", "yes"):
            print("Operação cancelada.")
            pausar()
            continue

        salvar_backup_antes(adb, list(pkgs_ativos))
        removidos_agora = []

        for idx, pkg in enumerate(alvos, 1):
            if pkg in PACOTES_PROTEGIDOS:
                continue
            _, out, err = adb.shell(f"pm uninstall --user 0 {pkg}")
            resultado = (out + " " + err).strip()
            if "Success" in resultado:
                print(f"  [{idx}/{len(alvos)}] {Cor.VERDE}Removido:{Cor.RESET} {pkg}")
                removidos_agora.append(pkg)
            else:
                # Tenta desativar caso uninstall --user 0 não seja permitido
                _, out_dis, err_dis = adb.shell(f"pm disable-user --user 0 {pkg}")
                res_dis = (out_dis + " " + err_dis).strip()
                if "disabled-user" in res_dis:
                    print(f"  [{idx}/{len(alvos)}] {Cor.AMARELO}Desativado:{Cor.RESET} {pkg}")
                    removidos_agora.append(pkg)
                else:
                    print(f"  [{idx}/{len(alvos)}] {Cor.VERMELHO}Protegido/Ignorado:{Cor.RESET} {pkg} ({resultado})")

        registrar_removidos(removidos_agora)
        print(f"\n{Cor.VERDE}[Concluído] {len(removidos_agora)} pacotes removidos/desativados com sucesso.{Cor.RESET}")
        print(f"Lista atualizada em 'removidos.txt' e script 'restaurar_apps.bat' gerado.")
        pausar()


def menu_otimizacoes_sistema(adb: GerenciadorADB):
    cabecalho(adb)
    print(f"{Cor.BOLD}4. OTIMIZAÇÕES DE SISTEMA (ANIMAÇÕES, CACHE E COMPILAÇÃO ART){Cor.RESET}\n")
    if not adb.verificar_conexao():
        pausar()
        return

    print("  [1] Desligar todas as animações da interface (escala = 0) [Instantâneo]")
    print("  [2] Limpar caches de todos os aplicativos (pm trim-caches 999G)")
    print("  [3] Pré-compilar todos os apps em modo 'speed' (Leva de 3 a 10 minutos)")
    print("  [4] Executar o PACOTE COMPLETO (Opções 1 + 2 + 3 + Reiniciar tablet)")
    print("  [0] Voltar")

    op = input("\nEscolha uma opção: ").strip()
    if op in ("1", "4"):
        print(f"\n{Cor.CIANO}Desativando animações da interface...{Cor.RESET}")
        adb.shell("settings put global window_animation_scale 0")
        adb.shell("settings put global transition_animation_scale 0")
        adb.shell("settings put global animator_duration_scale 0")
        print(f"{Cor.VERDE}[OK] Animações desligadas (escala 0).{Cor.RESET}")

    if op in ("2", "4"):
        print(f"\n{Cor.CIANO}Limpando caches (pm trim-caches 999G)...{Cor.RESET}")
        _, out, err = adb.shell("pm trim-caches 999G")
        print(f"{Cor.VERDE}[OK] Caches limpos. {out or err}{Cor.RESET}")

    if op in ("3", "4"):
        print(f"\n{Cor.AMARELO}Iniciando pré-compilação ART (cmd package compile -m speed -f -a)...{Cor.RESET}")
        print("Aguarde, isso pode levar vários minutos dependendo da quantidade de apps...")
        inicio = time.time()
        code, out, err = adb.shell("cmd package compile -m speed -f -a", timeout=900)
        duracao = int(time.time() - inicio)
        if code == 0:
            print(f"{Cor.VERDE}[OK] Pré-compilação concluída em {duracao}s! ({out}){Cor.RESET}")
        else:
            print(f"{Cor.VERMELHO}[Aviso] Código {code}: {out} {err}{Cor.RESET}")

    if op == "4":
        resp = input("\nDeseja reiniciar o tablet agora para consolidar os ganhos de RAM? [S/n]: ").strip().lower()
        if resp in ("", "s", "sim", "y", "yes"):
            adb.executar(["reboot"])
            print(f"{Cor.VERDE}Comando de reinicialização enviado!{Cor.RESET}")

    if op in ("1", "2", "3", "4"):
        pausar()


def menu_medir_ganho(adb: GerenciadorADB):
    cabecalho(adb)
    print(f"{Cor.BOLD}5. MEDIR GANHO DE DESEMPENHO (RAM E TEMPO DE ABERTURA){Cor.RESET}\n")
    if not adb.verificar_conexao():
        pausar()
        return

    print(f"{Cor.CIANO}Medindo RAM livre, pacotes ativos e tempo de abertura do app Configurações (3x)...{Cor.RESET}\n")
    _, meminfo, _ = adb.shell("grep MemAvailable /proc/meminfo")
    m = re.search(r"MemAvailable:\s+(\d+)\s+kB", meminfo)
    ram_mb = round(int(m.group(1)) / 1024, 1) if m else 0.0

    _, pkgs_raw, _ = adb.shell("pm list packages -e")
    qtd_pkgs = len([l for l in pkgs_raw.splitlines() if l.strip()])

    tempos = []
    for i in range(1, 4):
        adb.shell("am force-stop com.android.settings")
        time.sleep(1)
        _, out, _ = adb.shell("am start -W -n com.android.settings/.Settings")
        m_time = re.search(r"TotalTime:\s+(\d+)", out)
        if m_time:
            ms = int(m_time.group(1))
            tempos.append(ms)
            print(f"  Teste {i}/3 (Configurações): {ms} ms")
        time.sleep(1)

    media_ms = round(sum(tempos) / len(tempos), 1) if tempos else 0.0
    print(f"\n  {Cor.BOLD}Resultado Atual:{Cor.RESET}")
    print(f"  - RAM Disponível : {Cor.VERDE}{ram_mb} MB{Cor.RESET}")
    print(f"  - Apps Ativos    : {Cor.BOLD}{qtd_pkgs}{Cor.RESET}")
    print(f"  - Tempo Médio    : {Cor.CIANO}{media_ms} ms{Cor.RESET}")

    if adb.ultima_medicao:
        ant = adb.ultima_medicao
        diff_ram = round(ram_mb - ant["ram_mb"], 1)
        diff_pkgs = qtd_pkgs - ant["qtd_pkgs"]
        print(f"\n  {Cor.BOLD}Comparação com a medição anterior nesta sessão:{Cor.RESET}")
        print(f"  - Diferença de RAM  : {diff_ram:+} MB (Antes: {ant['ram_mb']} MB)")
        print(f"  - Diferença de Apps : {diff_pkgs:+} apps (Antes: {ant['qtd_pkgs']})")
        if media_ms > 0 and ant["media_ms"] > 0:
            ganho_vel = round(((ant["media_ms"] - media_ms) / media_ms) * 100, 1)
            print(f"  - Ganho de Abertura : {ganho_vel:+}% (Antes: {ant['media_ms']} ms -> Agora: {media_ms} ms)")

    salvar = input("\nDeseja guardar esta medição como referência 'Antes' para comparar depois? [S/n]: ").strip().lower()
    if salvar in ("", "s", "sim", "y", "yes"):
        adb.ultima_medicao = {"ram_mb": ram_mb, "qtd_pkgs": qtd_pkgs, "media_ms": media_ms}
        print(f"{Cor.VERDE}[OK] Medição salva como referência!{Cor.RESET}")
    pausar()


def menu_reverter(adb: GerenciadorADB):
    cabecalho(adb)
    print(f"{Cor.BOLD}6. REVERTER ALTERAÇÕES (RESTAURAR APPS E ANIMAÇÕES){Cor.RESET}\n")
    if not adb.verificar_conexao():
        pausar()
        return

    print("  [1] Reativar animações padrão do Android (escala = 1)")
    print("  [2] Reinstalar TODOS os pacotes listados em 'removidos.txt'")
    print("  [3] Reinstalar pacotes de uma categoria específica")
    print("  [4] Reinstalar um pacote específico pelo nome")
    print("  [0] Voltar")

    op = input("\nEscolha uma opção: ").strip()
    if op == "1":
        adb.shell("settings put global window_animation_scale 1")
        adb.shell("settings put global transition_animation_scale 1")
        adb.shell("settings put global animator_duration_scale 1")
        print(f"\n{Cor.VERDE}[OK] Animações restauradas para o valor padrão (1).{Cor.RESET}")
        pausar()
    elif op == "2":
        arq_rem = BASE_DIR / "removidos.txt"
        if not arq_rem.exists():
            print(f"\n{Cor.AMARELO}Arquivo 'removidos.txt' não encontrado. Use a opção 3 para restaurar por categoria.{Cor.RESET}")
            pausar()
            return
        pacotes = [l.strip() for l in arq_rem.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
        for idx, p in enumerate(pacotes, 1):
            adb.shell(f"pm enable {p}")
            _, out, _ = adb.shell(f"cmd package install-existing {p}")
            print(f"  [{idx}/{len(pacotes)}] {p}: {out}")
        print(f"\n{Cor.VERDE}[OK] Restauração concluída!{Cor.RESET}")
        pausar()
    elif op == "3":
        for cid, dados in CATEGORIAS_PACOTES.items():
            print(f"  [{cid:>2}] {dados['nome']}")
        cid = input("\nNúmero da categoria para restaurar: ").strip()
        if cid in CATEGORIAS_PACOTES:
            for p in CATEGORIAS_PACOTES[cid]["pacotes"]:
                adb.shell(f"pm enable {p}")
                _, out, _ = adb.shell(f"cmd package install-existing {p}")
                print(f"  - {p}: {out}")
        pausar()
    elif op == "4":
        pkg = input("Nome do pacote para reinstalar: ").strip()
        if pkg:
            adb.shell(f"pm enable {pkg}")
            _, out, err = adb.shell(f"cmd package install-existing {pkg}")
            print(f"\nResultado: {out or err}")
        pausar()


def menu_emuladores(adb: GerenciadorADB):
    cabecalho(adb)
    print(f"{Cor.BOLD}7. UTILITÁRIOS DE EMULAÇÃO (RETROARCH / PASTAS DE ROMS / PS1 .CUE){Cor.RESET}\n")
    if not adb.verificar_conexao():
        pausar()
        return

    print("  [1] Criar estrutura de pastas /sdcard/ROMs (psx, ps2, psp, snes, n64, gba, etc.)")
    print("  [2] Aplicar ajuste seguro no retroarch.cfg (Segurar Start = Menu, Esconder Overlay)")
    print("  [3] Gerar arquivo .cue automaticamente para um jogo .bin/.iso de PS1 no PC")
    print("  [4] Revogar permissão Bluetooth do BTPad no tablet (evitar que o tablet vire controle)")
    print("  [0] Voltar")

    op = input("\nEscolha uma opção: ").strip()
    if op == "1":
        pastas = [
            "_BIOS", "_BIOS/ps2", "psx", "ps2", "psp", "n64", "snes", "nes",
            "gba", "gb", "gbc", "nds", "megadrive", "mastersystem", "gamegear",
            "segacd", "pcengine", "dreamcast", "arcade", "atari2600", "neogeo"
        ]
        cmd_mkdir = "mkdir -p " + " ".join(f"/sdcard/ROMs/{p}" for p in pastas)
        adb.shell(cmd_mkdir)
        print(f"\n{Cor.VERDE}[OK] {len(pastas)} pastas criadas dentro de /sdcard/ROMs/ no tablet!{Cor.RESET}")
        pausar()
    elif op == "2":
        # Suporta RetroArch 64 bits (aarch64), 32 bits (ra32 - usado no SM-T510 oficial) e padrão
        candidatos = [
            ("com.retroarch.aarch64", "/sdcard/Android/data/com.retroarch.aarch64/files/retroarch.cfg"),
            ("com.retroarch.ra32", "/sdcard/Android/data/com.retroarch.ra32/files/retroarch.cfg"),
            ("com.retroarch", "/sdcard/Android/data/com.retroarch/files/retroarch.cfg"),
            ("com.retroarch", "/sdcard/RetroArch/retroarch.cfg"),
        ]
        pkg_encontrado = None
        cfg_path = None
        for pkg, caminho in candidatos:
            _, check, _ = adb.shell(f"ls {caminho}")
            if check and "No such file" not in check:
                pkg_encontrado = pkg
                cfg_path = caminho
                break

        if not cfg_path:
            print(f"\n{Cor.AMARELO}[!] Arquivo retroarch.cfg não encontrado. Abra o RetroArch pelo menos uma vez antes.{Cor.RESET}")
            pausar()
            return
        adb.shell(f"am force-stop {pkg_encontrado}")
        adb.shell(f"cp {cfg_path} {cfg_path}.bak")
        adb.shell(f"sed -i 's/^input_overlay_enable = .*/input_overlay_enable = \"false\"/' {cfg_path}")
        adb.shell(f"sed -i 's/^input_menu_toggle_gamepad_combo = .*/input_menu_toggle_gamepad_combo = \"7\"/' {cfg_path}")
        _, conf_out, _ = adb.shell(f"grep -E '^input_(overlay_enable|menu_toggle_gamepad_combo)' {cfg_path}")
        print(f"\n{Cor.VERDE}[OK] Configuração atualizada em {cfg_path}:{Cor.RESET}\n{conf_out}")
        pausar()
    elif op == "3":
        caminho_str = input("Digite o caminho completo do arquivo .bin ou .iso no PC: ").strip().strip('"')
        caminho = Path(caminho_str)
        if not caminho.exists() or not caminho.is_file():
            print(f"{Cor.VERMELHO}[Erro] Arquivo não encontrado: {caminho}{Cor.RESET}")
            pausar()
            return
        tam = caminho.stat().st_size
        divisivel = (tam % 2352 == 0)
        modo = "MODE2/2352" if divisivel else "MODE1/2048"
        cue_path = caminho.with_suffix(".cue")
        conteudo_cue = f'FILE "{caminho.name}" BINARY\n  TRACK 01 {modo}\n    INDEX 01 00:00:00\n'
        cue_path.write_text(conteudo_cue, encoding="utf-8")
        print(f"\n{Cor.VERDE}[OK] Arquivo gerado: {cue_path}{Cor.RESET} (Tamanho divisível por 2352: {'Sim' if divisivel else 'Não'})")
        enviar = input("Deseja enviar o jogo e o .cue para /sdcard/ROMs/psx/ agora? [s/N]: ").strip().lower()
        if enviar in ("s", "sim", "y", "yes"):
            print("Enviando imagem (pode demorar alguns segundos)...")
            adb.executar(["push", str(caminho), f"/sdcard/ROMs/psx/{caminho.name}"], timeout=600)
            adb.executar(["push", str(cue_path), f"/sdcard/ROMs/psx/{cue_path.name}"], timeout=60)
            print(f"{Cor.VERDE}[OK] Arquivos enviados para /sdcard/ROMs/psx/!{Cor.RESET}")
        pausar()
    elif op == "4":
        adb.shell("pm revoke com.cavaleiro.btpad android.permission.BLUETOOTH_CONNECT")
        adb.shell("pm revoke com.cavaleiro.btpad android.permission.BLUETOOTH_ADVERTISE")
        adb.shell("pm set-permission-flags com.cavaleiro.btpad android.permission.BLUETOOTH_CONNECT user-fixed")
        adb.shell("pm set-permission-flags com.cavaleiro.btpad android.permission.BLUETOOTH_ADVERTISE user-fixed")
        print(f"\n{Cor.VERDE}[OK] Permissões de Bluetooth do BTPad revogadas e travadas no tablet.{Cor.RESET}")
        pausar()


def menu_atualizacao_android(adb: GerenciadorADB):
    cabecalho(adb)
    print(f"{Cor.BOLD}8. ATUALIZAÇÃO DO ANDROID (OFICIAL OTA, ODIN E CUSTOM ROM / GSI){Cor.RESET}\n")
    if not adb.verificar_conexao():
        pausar()
        return

    _, modelo, _ = adb.shell("getprop ro.product.model")
    _, device, _ = adb.shell("getprop ro.product.device")
    _, android_ver, _ = adb.shell("getprop ro.build.version.release")
    _, sdk_ver, _ = adb.shell("getprop ro.build.version.sdk")
    _, patch_seg, _ = adb.shell("getprop ro.build.version.security_patch")
    _, build_id, _ = adb.shell("getprop ro.build.PDA")
    if not build_id:
        _, build_id, _ = adb.shell("getprop ro.build.display.id")
    _, csc, _ = adb.shell("getprop ro.boot.carrierid")
    if not csc:
        _, csc, _ = adb.shell("getprop ril.official_cscver")
    _, treble, _ = adb.shell("getprop ro.treble.enabled")
    _, dynamic_part, _ = adb.shell("getprop ro.boot.dynamic_partitions")
    _, cpu_abi, _ = adb.shell("getprop ro.product.cpu.abilist")
    _, binder_arch, _ = adb.shell("uname -m")

    print(f"  {Cor.BOLD}Aparelho detectado:{Cor.RESET} {modelo} ({device})")
    print(f"  {Cor.BOLD}Versão atual:{Cor.RESET}       Android {android_ver} (SDK {sdk_ver}) | Patch: {patch_seg}")
    print(f"  {Cor.BOLD}Firmware / CSC:{Cor.RESET}     {build_id} | Região/CSC: {csc or 'N/D'}")
    print(f"  {Cor.BOLD}Arquitetura / ABI:{Cor.RESET}  Userspace={cpu_abi} | Kernel={binder_arch}")
    print(f"  {Cor.BOLD}Project Treble:{Cor.RESET}     {'Suportado (GSI compatível)' if treble == 'true' else 'Não suportado'} | Partições Dinâmicas: {dynamic_part or 'false'}")

    if "SM-T510" in (modelo or "").upper() or "gta3xl" in (device or "").lower():
        print(f"\n  {Cor.AMARELO}[Guia Específico - Galaxy Tab A 10.1 (2019) SM-T510]:{Cor.RESET}")
        print("  - Último Android Oficial Samsung: Android 11 (One UI Core 3.1 - Binário B/U5).")
        print("  - Modo do Sistema Original: 32 bits em kernel 64 bits (arquitetura GSI: arm32_binder64 / a64_bvN).")
        print("  - Para ir ao Android 13 ou 14: Requer Desbloqueio de Bootloader + TWRP via Odin + LineageOS 20/21 (XDA: gta3xlwifi).")

    print(f"\n{Cor.CIANO}Opções de atualização:{Cor.RESET}")
    print("  [1] Abrir tela de Atualização de Software Oficial (OTA) no tablet")
    print("  [2] Reiniciar no Modo Download (Odin) para instalar firmware oficial (SamFw / Frija)")
    print("  [3] Reiniciar no Modo Recovery")
    print("  [0] Voltar")

    op = input("\nEscolha uma opção: ").strip()
    if op == "1":
        # Tenta abrir o atualizador da Samsung (FOTA) ou as configurações do sistema
        adb.shell("am start -a android.settings.SYSTEM_UPDATE_SETTINGS")
        print(f"\n{Cor.VERDE}[OK] Tela de atualização aberta no tablet.{Cor.RESET}")
        pausar()
    elif op == "2":
        conf = input(
            f"\n{Cor.AMARELO}ATENÇÃO:{Cor.RESET} O tablet vai reiniciar na tela azul do Modo Download (Odin).\n"
            "Para sair dele sem instalar nada, segure Volume Baixo + Power por 7 segundos.\n"
            "Deseja reiniciar em Modo Download agora? [s/N]: "
        ).strip().lower()
        if conf in ("s", "sim", "y", "yes"):
            adb.executar(["reboot", "download"])
            print(f"\n{Cor.VERDE}Reiniciando em Modo Download...{Cor.RESET}")
        pausar()
    elif op == "3":
        conf = input("Deseja reiniciar o tablet no Modo Recovery agora? [s/N]: ").strip().lower()
        if conf in ("s", "sim", "y", "yes"):
            adb.executar(["reboot", "recovery"])
            print(f"\n{Cor.VERDE}Reiniciando em Modo Recovery...{Cor.RESET}")
        pausar()


def main():
    adb = GerenciadorADB()
    while True:
        cabecalho(adb)
        print(f"{Cor.BOLD}MENU PRINCIPAL:{Cor.RESET}\n")
        print("  [1] Conectar ao Tablet (USB / ADB Wi-Fi / Baixar ADB)")
        print("  [2] Diagnóstico e Varredura Completa (RAM, Modelo, Bloatware, Armazenamento)")
        print("  [3] Remover Bloatware e Limitadores Samsung (Por Categoria ou Completo)")
        print("  [4] Otimizações de Sistema (Desligar Animações, Limpar Cache, Compilar ART)")
        print("  [5] Medir Ganho de Desempenho (Antes x Depois)")
        print("  [6] Reverter Alterações (Reinstalar Apps Removidos / Restaurar Animações)")
        print("  [7] Utilitários de Emulação (Pastas de ROMs, RetroArch, Gerador .cue PS1)")
        print("  [8] Verificar / Iniciar Atualização do Android (OTA, Modo Download/Odin, GSI)")
        print("  [0] Sair")

        opcao = input(f"\n{Cor.BOLD}Escolha uma opção [0-8]: {Cor.RESET}").strip()

        if opcao == "1":
            menu_conexao(adb)
        elif opcao == "2":
            realizar_varredura(adb)
        elif opcao == "3":
            menu_remover_bloatware(adb)
        elif opcao == "4":
            menu_otimizacoes_sistema(adb)
        elif opcao == "5":
            menu_medir_ganho(adb)
        elif opcao == "6":
            menu_reverter(adb)
        elif opcao == "7":
            menu_emuladores(adb)
        elif opcao == "8":
            menu_atualizacao_android(adb)
        elif opcao == "0":
            print(f"\n{Cor.VERDE}Encerrando o otimizador. Até mais!{Cor.RESET}")
            break
        else:
            print(f"\n{Cor.VERMELHO}Opção inválida!{Cor.RESET}")
            time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Cor.AMARELO}Interrompido pelo usuário.{Cor.RESET}")
        sys.exit(0)
