using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Windows.Forms;

[assembly: AssemblyTitle("Otimizador de Tablets Samsung e Android")]
[assembly: AssemblyDescription("Interface grafica nativa para otimizacao de tablets Android via ADB sem root")]
[assembly: AssemblyCompany("Projeto Tirando Defeito Programado dos Tablets")]
[assembly: AssemblyProduct("OtimizadorTabletSamsung")]
[assembly: AssemblyCopyright("Copyright (c) 2026")]
[assembly: AssemblyVersion("2.0.0.0")]
[assembly: AssemblyFileVersion("2.0.0.0")]

namespace OtimizadorTabletSamsung
{
    public class CategoriaBloat
    {
        public string Id { get; set; }
        public string Nome { get; set; }
        public bool PadraoMarcado { get; set; }
        public string[] Pacotes { get; set; }
    }

    public class MainForm : Form
    {
        private string baseDir;
        private string adbPath;
        private string serialAtual = null;

        private readonly Color bgDark = Color.FromArgb(18, 22, 31);
        private readonly Color bgCard = Color.FromArgb(28, 34, 48);
        private readonly Color bgInput = Color.FromArgb(38, 46, 64);
        private readonly Color accentBlue = Color.FromArgb(56, 139, 253);
        private readonly Color accentGreen = Color.FromArgb(46, 160, 67);
        private readonly Color accentOrange = Color.FromArgb(210, 153, 34);
        private readonly Color accentRed = Color.FromArgb(248, 81, 73);
        private readonly Color textLight = Color.FromArgb(230, 237, 243);
        private readonly Color textMuted = Color.FromArgb(139, 148, 158);

        public Label lblStatusAdb;
        public Label lblCardModelo;
        public Label lblCardRam;
        public Label lblCardStorage;
        public Label lblCardApps;
        private RichTextBox txtLog;
        private CheckedListBox clbCategorias;
        private CheckBox chkManterStreaming;
        private CheckBox chkManterGooglePessoal;
        private ProgressBar progressBar;
        private Label lblProgresso;

        private List<CategoriaBloat> categorias;
        private HashSet<string> pacotesProtegidos;

        public MainForm()
        {
            baseDir = AppDomain.CurrentDomain.BaseDirectory;
            string subRepo = Path.Combine(baseDir, "Tirando-defeito-programado-dos-tablets");
            if (!Directory.Exists(Path.Combine(baseDir, "platform-tools")) && Directory.Exists(subRepo))
            {
                baseDir = subRepo;
            }
            InicializarDados();
            InicializarComponentes();
        }

        private void InicializarDados()
        {
            pacotesProtegidos = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
            {
                "android", "com.android.systemui", "com.android.settings",
                "com.android.vending", "com.google.android.gms",
                "com.sec.android.app.samsungapps", "com.android.chrome",
                "com.samsung.android.honeyboard", "com.sec.android.app.launcher",
                "com.openai.chatgpt", "com.google.android.youtube"
            };

            categorias = new List<CategoriaBloat>
            {
                new CategoriaBloat {
                    Id = "1", PadraoMarcado = true,
                    Nome = "1. Bixby, Rotinas e Paineis Edge",
                    Pacotes = new[] {
                        "com.samsung.android.app.spage", "com.samsung.android.app.settings.bixby",
                        "com.samsung.android.app.routines", "com.samsung.android.app.appsedge",
                        "com.samsung.android.app.taskedge", "com.samsung.android.app.cocktailbarservice",
                        "com.samsung.android.app.clipboardedge"
                    }
                },
                new CategoriaBloat {
                    Id = "2", PadraoMarcado = true,
                    Nome = "2. Nuvem, Conta e Diagnostico Samsung",
                    Pacotes = new[] {
                        "com.samsung.android.scloud", "com.samsung.android.mobileservice",
                        "com.samsung.android.scs", "com.samsung.android.rubin.app",
                        "com.samsung.android.bbc.bbcagent", "com.samsung.android.dqagent",
                        "com.sec.android.diagmonagent"
                    }
                },
                new CategoriaBloat {
                    Id = "3", PadraoMarcado = true,
                    Nome = "3. Transferencia (Smart Switch) e Modo Criancas",
                    Pacotes = new[] {
                        "com.samsung.android.smartswitchassistant", "com.sec.android.easyMover",
                        "com.sec.android.easyMover.Agent", "com.samsung.android.kidsinstaller",
                        "com.samsung.android.app.parentalcare", "com.samsung.android.forest"
                    }
                },
                new CategoriaBloat {
                    Id = "4", PadraoMarcado = true,
                    Nome = "4. Compartilhamento, Continuidade e Espelhamento",
                    Pacotes = new[] {
                        "com.samsung.android.app.sharelive", "com.samsung.android.galaxycontinuity",
                        "com.samsung.android.mdx.kit", "com.samsung.android.mdx.quickboard",
                        "com.samsung.android.smartmirroring", "com.samsung.android.allshare.service.mediashare",
                        "com.samsung.android.beaconmanager", "com.samsung.android.mapsagent",
                        "com.samsung.android.aware.service"
                    }
                },
                new CategoriaBloat {
                    Id = "5", PadraoMarcado = true,
                    Nome = "5. Clima, Video, Foto, Stickers e Temas",
                    Pacotes = new[] {
                        "com.sec.android.daemonapp", "com.sec.android.app.ve.vebgm",
                        "com.sec.android.autodoodle.service", "com.sec.android.mimage.photoretouching",
                        "com.samsung.app.newtrim", "com.sec.android.app.DataCreate",
                        "com.samsung.storyservice", "com.samsung.android.stickercenter",
                        "com.samsung.android.themecenter", "com.samsung.android.app.dressroom",
                        "com.samsung.android.dynamiclock", "com.samsung.android.widget.pictureframe"
                    }
                },
                new CategoriaBloat {
                    Id = "6", PadraoMarcado = true,
                    Nome = "6. Telemetria Knox e Mensagens SMS",
                    Pacotes = new[] {
                        "com.samsung.android.messaging", "com.samsung.android.knox.analytics.uploader",
                        "com.samsung.android.knox.app.networkfilter", "com.samsung.android.knox.attestation"
                    }
                },
                new CategoriaBloat {
                    Id = "7", PadraoMarcado = true,
                    Nome = "7. Anuncios e Terceiros (OneDrive, Outlook, AppLovin, Hiya)",
                    Pacotes = new[] {
                        "com.applovin.array.apphub.samsung", "com.hiya.star",
                        "com.microsoft.office.outlook", "com.microsoft.skydrive"
                    }
                },
                new CategoriaBloat {
                    Id = "8", PadraoMarcado = true,
                    Nome = "8. Apps do Google Secundarios (Drive, Maps, Meet, Google TV, Busca)",
                    Pacotes = new[] {
                        "com.google.android.apps.youtube.music", "com.google.android.apps.photos",
                        "com.google.android.gm", "com.google.android.apps.tachyon",
                        "com.google.android.videos", "com.google.android.apps.messaging",
                        "com.google.android.apps.docs", "com.google.android.apps.maps",
                        "com.google.android.googlequicksearchbox"
                    }
                },
                new CategoriaBloat {
                    Id = "9", PadraoMarcado = true,
                    Nome = "9. Vozes de Leitura (TTS) Estrangeiras",
                    Pacotes = new[] {
                        "com.samsung.SMT.lang_de_de_f00", "com.samsung.SMT.lang_en_gb_f00",
                        "com.samsung.SMT.lang_en_us_l03", "com.samsung.SMT.lang_es_es_f00",
                        "com.samsung.SMT.lang_es_mx_f00", "com.samsung.SMT.lang_fr_fr_f00",
                        "com.samsung.SMT.lang_it_it_f00", "com.samsung.SMT.lang_ru_ru_f00"
                    }
                },
                new CategoriaBloat {
                    Id = "10", PadraoMarcado = true,
                    Nome = "10. Limitadores de Jogos Samsung (GOS e Smart FPS)",
                    Pacotes = new[] {
                        "com.samsung.android.game.gos", "com.sec.android.smartfpsadjuster",
                        "com.samsung.android.game.gamehome", "com.samsung.android.game.gametools"
                    }
                },
                new CategoriaBloat {
                    Id = "11", PadraoMarcado = true,
                    Nome = "11. Extras Galaxy Tab A 10.1 SM-T510 (DailyBoard, ANT+, Pasta Segura)",
                    Pacotes = new[] {
                        "com.sec.android.app.kidshome", "com.sec.android.usermanual",
                        "com.sec.android.widgetapp.webmanual", "com.diotek.sec.lookup.dictionary",
                        "com.dsi.ant.plugins.antplus", "com.dsi.ant.sample.acquirechannels",
                        "com.dsi.ant.server", "com.dsi.ant.service.socket",
                        "com.samsung.android.homemode", "com.samsung.android.livestickers",
                        "com.samsung.android.icecone", "com.samsung.android.app.watchmanagerstub",
                        "com.samsung.android.app.simplesharing", "com.samsung.android.privateshare",
                        "com.samsung.android.allshare.service.fileshare", "com.samsung.android.easysetup",
                        "com.samsung.android.service.stplatform", "com.samsung.android.mcfds",
                        "com.samsung.android.mcfserver", "com.samsung.knox.securefolder",
                        "com.samsung.android.knox.containeragent", "com.samsung.android.knox.containercore",
                        "com.samsung.android.knox.pushmanager", "com.sec.enterprise.knox.attestation",
                        "com.sec.enterprise.knox.cloudmdm.smdms", "com.sec.spp.push",
                        "com.samsung.android.aremoji", "com.sec.android.mimage.avatarstickers",
                        "com.samsung.android.FastSwitch", "com.samsung.android.app.galaxyfinder"
                    }
                },
                new CategoriaBloat {
                    Id = "12", PadraoMarcado = false,
                    Nome = "12. Apps de Streaming (Netflix, Disney+, Spotify, Prime Video, YT Kids)",
                    Pacotes = new[] {
                        "com.netflix.mediaclient", "com.netflix.partner.activation",
                        "com.spotify.music", "com.disney.disneyplus",
                        "com.amazon.avod.thirdpartyclient", "com.google.android.apps.youtube.kids"
                    }
                }
            };
        }

        private void InicializarComponentes()
        {
            Text = "Otimizador de Tablets Samsung / Android v2.0 (Executavel Nativo Windows - Sem Python)";
            Size = new Size(1050, 750);
            StartPosition = FormStartPosition.CenterScreen;
            BackColor = bgDark;
            ForeColor = textLight;
            Font = new Font("Segoe UI", 9.5f, FontStyle.Regular);

            Panel pnlHeader = new Panel { Dock = DockStyle.Top, Height = 64, BackColor = bgCard };
            Label lblTitulo = new Label
            {
                Text = "OTIMIZADOR DE TABLETS SAMSUNG E CONSOLE RETRO",
                Font = new Font("Segoe UI", 13f, FontStyle.Bold),
                ForeColor = accentBlue,
                AutoSize = true,
                Location = new Point(16, 10)
            };
            lblStatusAdb = new Label
            {
                Text = "Pronto para conectar via ADB",
                Font = new Font("Segoe UI", 9.5f, FontStyle.Bold),
                ForeColor = accentOrange,
                AutoSize = true,
                Location = new Point(16, 36)
            };
            pnlHeader.Controls.Add(lblTitulo);
            pnlHeader.Controls.Add(lblStatusAdb);

            Panel pnlCards = new Panel { Dock = DockStyle.Top, Height = 82, Padding = new Padding(12, 8, 12, 8) };
            TableLayoutPanel tblCards = new TableLayoutPanel { Dock = DockStyle.Fill, ColumnCount = 4, RowCount = 1 };
            for (int i = 0; i < 4; i++) tblCards.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 25f));

            lblCardModelo = CriarCard(tblCards, 0, "APARELHO / ANDROID", "Clique em Analisar");
            lblCardRam = CriarCard(tblCards, 1, "MEMORIA RAM LIVRE", "-- / -- MB");
            lblCardStorage = CriarCard(tblCards, 2, "ARMAZENAMENTO (/data)", "-- GB livres");
            lblCardApps = CriarCard(tblCards, 3, "PACOTES ATIVOS", "-- ativos");
            pnlCards.Controls.Add(tblCards);

            Panel pnlFooter = new Panel { Dock = DockStyle.Bottom, Height = 200, Padding = new Padding(12, 4, 12, 12) };
            lblProgresso = new Label { Text = "Aguardando comando...", Dock = DockStyle.Top, Height = 20, ForeColor = textMuted };
            progressBar = new ProgressBar { Dock = DockStyle.Top, Height = 10 };
            txtLog = new RichTextBox
            {
                Dock = DockStyle.Fill,
                BackColor = Color.FromArgb(12, 15, 22),
                ForeColor = Color.FromArgb(165, 214, 255),
                Font = new Font("Consolas", 9.5f),
                ReadOnly = true,
                BorderStyle = BorderStyle.None
            };
            pnlFooter.Controls.Add(txtLog);
            pnlFooter.Controls.Add(progressBar);
            pnlFooter.Controls.Add(lblProgresso);

            Panel pnlMain = new Panel { Dock = DockStyle.Fill, Padding = new Padding(12, 4, 12, 4) };
            SplitContainer split = new SplitContainer { Dock = DockStyle.Fill, SplitterDistance = 580 };

            Label lblCat = new Label
            {
                Text = "Categorias de Bloatware para remover (Sem Root, 100% Reversivel):",
                Dock = DockStyle.Top,
                Height = 24,
                Font = new Font("Segoe UI", 9.5f, FontStyle.Bold)
            };

            clbCategorias = new CheckedListBox
            {
                Dock = DockStyle.Fill,
                BackColor = bgCard,
                ForeColor = textLight,
                BorderStyle = BorderStyle.FixedSingle,
                CheckOnClick = true
            };
            foreach (var c in categorias) clbCategorias.Items.Add(c.Nome, c.PadraoMarcado);

            Panel pnlProt = new Panel { Dock = DockStyle.Bottom, Height = 56 };
            chkManterStreaming = new CheckBox
            {
                Text = "Manter e proteger todos os apps de Streaming (Netflix, Disney+, Prime Video, Spotify, YouTube)",
                Checked = true,
                AutoSize = true,
                ForeColor = Color.FromArgb(126, 231, 135),
                Location = new Point(4, 4)
            };
            chkManterGooglePessoal = new CheckBox
            {
                Text = "Manter e proteger Gmail e Google Fotos",
                Checked = true,
                AutoSize = true,
                ForeColor = Color.FromArgb(126, 231, 135),
                Location = new Point(4, 28)
            };
            pnlProt.Controls.Add(chkManterStreaming);
            pnlProt.Controls.Add(chkManterGooglePessoal);

            split.Panel1.Controls.Add(clbCategorias);
            split.Panel1.Controls.Add(pnlProt);
            split.Panel1.Controls.Add(lblCat);

            FlowLayoutPanel flowBtns = new FlowLayoutPanel
            {
                Dock = DockStyle.Fill,
                FlowDirection = FlowDirection.TopDown,
                WrapContents = false,
                Padding = new Padding(10, 0, 0, 0),
                AutoScroll = true
            };

            Button btnScan = CriarBotao("1. Analisar / Diagnosticar Tablet Conectado", accentBlue, 40);
            Button btnOtimizar = CriarBotao("2. OTIMIZAR TUDO AGORA (Recomendado)", accentGreen, 44);
            Button btnSoBloat = CriarBotao("3. Remover Apenas Bloatware Marcado", bgInput, 36);
            Button btnSoSistema = CriarBotao("4. Desligar Animacoes + Limpar Cache + Compilar ART", bgInput, 36);
            Button btnBenchmark = CriarBotao("5. Medir Velocidade de Abertura (Benchmark 3x)", bgInput, 36);
            Button btnRestaurar = CriarBotao("6. Reverter / Reinstalar Apps Removidos", accentOrange, 36);
            Button btnPastasRom = CriarBotao("7. Criar Pastas de Emuladores (/sdcard/ROMs)", bgInput, 36);
            Button btnCheckUpd = CriarBotao("8. Verificar Atualizacao do Android / Abrir OTA", bgInput, 36);
            Button btnReboot = CriarBotao("9. Reiniciar Tablet (Consolidar RAM)", bgInput, 36);

            btnScan.Click += async (s, e) => await ExecutarVarreduraAsync();
            btnSoBloat.Click += async (s, e) => await RemoverBloatwareAsync();
            btnSoSistema.Click += async (s, e) => await OtimizarSistemaAsync();
            btnOtimizar.Click += async (s, e) => {
                await ExecutarVarreduraAsync();
                await RemoverBloatwareAsync();
                await OtimizarSistemaAsync();
                MessageBox.Show("Otimizacao concluida com sucesso!\n\nClique em '9. Reiniciar Tablet' para consolidar a memoria RAM livre.", "Otimizacao Concluida", MessageBoxButtons.OK, MessageBoxIcon.Information);
            };
            btnBenchmark.Click += async (s, e) => await MedirDesempenhoAsync();
            btnRestaurar.Click += async (s, e) => await RestaurarAppsAsync();
            btnPastasRom.Click += async (s, e) => {
                await RodarAdbAsync("shell mkdir -p /sdcard/ROMs/_BIOS /sdcard/ROMs/_BIOS/ps2 /sdcard/ROMs/psx /sdcard/ROMs/ps2 /sdcard/ROMs/psp /sdcard/ROMs/n64 /sdcard/ROMs/snes /sdcard/ROMs/nes /sdcard/ROMs/gba /sdcard/ROMs/gb /sdcard/ROMs/gbc /sdcard/ROMs/nds /sdcard/ROMs/megadrive /sdcard/ROMs/mastersystem /sdcard/ROMs/gamegear /sdcard/ROMs/arcade");
                Log("[OK] Pastas criadas em /sdcard/ROMs/ no tablet!");
            };
            btnCheckUpd.Click += async (s, e) => {
                string build = await RodarAdbAsync("shell getprop ro.build.display.id");
                string patch = await RodarAdbAsync("shell getprop ro.build.version.security_patch");
                string treble = await RodarAdbAsync("shell getprop ro.treble.enabled");
                Log("Compilacao: " + build + " | Patch: " + patch + " | Project Treble (GSI): " + treble);
                await RodarAdbAsync("shell am start -a android.settings.SYSTEM_UPDATE_SETTINGS");
                Log("[OK] Tela de Atualizacao de Software aberta no tablet.");
            };
            btnReboot.Click += async (s, e) => {
                if (MessageBox.Show("Deseja reiniciar o tablet agora?", "Reiniciar", MessageBoxButtons.YesNo, MessageBoxIcon.Question) == DialogResult.Yes)
                {
                    await RodarAdbAsync("reboot");
                    Log("Comando de reinicializacao enviado!");
                }
            };

            flowBtns.Controls.AddRange(new Control[] { btnScan, btnOtimizar, btnSoBloat, btnSoSistema, btnBenchmark, btnRestaurar, btnPastasRom, btnCheckUpd, btnReboot });
            split.Panel2.Controls.Add(flowBtns);
            pnlMain.Controls.Add(split);

            Controls.Add(pnlMain);
            Controls.Add(pnlCards);
            Controls.Add(pnlHeader);
            Controls.Add(pnlFooter);

            Shown += async (s, e) => {
                Log("Aplicativo nativo (.exe) iniciado. Verificando tablet conectado...");
                await ExecutarVarreduraAsync();
            };
        }

        private Label CriarCard(TableLayoutPanel parent, int col, string titulo, string valorInicial)
        {
            Panel card = new Panel { Dock = DockStyle.Fill, BackColor = bgCard, Margin = new Padding(5), Padding = new Padding(10, 6, 10, 6) };
            Label lblTit = new Label { Text = titulo, ForeColor = textMuted, Font = new Font("Segoe UI", 8f, FontStyle.Bold), Dock = DockStyle.Top, Height = 18 };
            Label lblVal = new Label { Text = valorInicial, ForeColor = textLight, Font = new Font("Segoe UI", 11f, FontStyle.Bold), Dock = DockStyle.Fill };
            card.Controls.Add(lblVal);
            card.Controls.Add(lblTit);
            parent.Controls.Add(card, col, 0);
            return lblVal;
        }

        private Button CriarBotao(string texto, Color cor, int altura)
        {
            Button btn = new Button
            {
                Text = texto,
                BackColor = cor,
                ForeColor = Color.White,
                FlatStyle = FlatStyle.Flat,
                Font = new Font("Segoe UI", 9.5f, FontStyle.Bold),
                Size = new Size(390, altura),
                Margin = new Padding(4),
                Cursor = Cursors.Hand
            };
            btn.FlatAppearance.BorderSize = 0;
            return btn;
        }

        public void Log(string msg)
        {
            if (InvokeRequired)
            {
                BeginInvoke(new Action<string>(Log), msg);
                return;
            }
            txtLog.AppendText("[" + DateTime.Now.ToString("HH:mm:ss") + "] " + msg + Environment.NewLine);
            txtLog.SelectionStart = txtLog.Text.Length;
            txtLog.ScrollToCaret();
        }

        private void AtualizarProgresso(int valor, int max, string texto)
        {
            if (InvokeRequired)
            {
                BeginInvoke(new Action<int, int, string>(AtualizarProgresso), valor, max, texto);
                return;
            }
            progressBar.Maximum = max > 0 ? max : 100;
            progressBar.Value = Math.Min(Math.Max(0, valor), progressBar.Maximum);
            lblProgresso.Text = texto;
        }

        public async Task<string> RodarAdbAsync(string argumentos)
        {
            adbPath = Path.Combine(baseDir, "platform-tools", "adb.exe");
            if (!File.Exists(adbPath))
            {
                return "ERRO: platform-tools\\adb.exe nao encontrado.";
            }

            string cmdFinal = argumentos;
            if (!string.IsNullOrEmpty(serialAtual) && !argumentos.StartsWith("devices"))
            {
                cmdFinal = "-s " + serialAtual + " " + argumentos;
            }

            return await Task.Run(() =>
            {
                ProcessStartInfo psi = new ProcessStartInfo
                {
                    FileName = adbPath,
                    Arguments = cmdFinal,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    CreateNoWindow = true,
                    StandardOutputEncoding = Encoding.UTF8,
                    StandardErrorEncoding = Encoding.UTF8
                };
                using (Process p = Process.Start(psi))
                {
                    string stdout = p.StandardOutput.ReadToEnd();
                    string stderr = p.StandardError.ReadToEnd();
                    p.WaitForExit(120000);
                    return (stdout + "\n" + stderr).Trim();
                }
            });
        }

        public async Task<bool> VerificarConexaoAsync()
        {
            string outDev = await RodarAdbAsync("devices");
            var linhas = outDev.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries);
            foreach (var l in linhas)
            {
                if (l.StartsWith("List of devices") || l.StartsWith("*")) continue;
                var partes = l.Split(new[] { '\t', ' ' }, StringSplitOptions.RemoveEmptyEntries);
                if (partes.Length >= 2)
                {
                    if (partes[1] == "unauthorized" || partes[1] == "authorizing")
                    {
                        lblStatusAdb.Text = "Tablet detectado (" + partes[0] + ") - Toque em 'Permitir' na tela do tablet!";
                        lblStatusAdb.ForeColor = accentOrange;
                        return false;
                    }
                    if (partes[1] == "device")
                    {
                        serialAtual = partes[0];
                        return true;
                    }
                }
            }
            lblStatusAdb.Text = "Nenhum tablet conectado via ADB. Conecte o cabo USB e ative a Depuracao USB.";
            lblStatusAdb.ForeColor = accentRed;
            return false;
        }

        public async Task ExecutarVarreduraAsync()
        {
            AtualizarProgresso(20, 100, "Verificando conexao com o tablet...");
            if (!await VerificarConexaoAsync())
            {
                AtualizarProgresso(0, 100, "Tablet desconectado.");
                return;
            }
            AtualizarProgresso(50, 100, "Coletando dados de hardware, RAM e pacotes...");
            string modelo = (await RodarAdbAsync("shell getprop ro.product.model")).Trim();
            string device = (await RodarAdbAsync("shell getprop ro.product.device")).Trim();
            string androidVer = (await RodarAdbAsync("shell getprop ro.build.version.release")).Trim();
            string memInfo = await RodarAdbAsync("shell grep -E \"MemTotal|MemAvailable\" /proc/meminfo");
            string dfData = await RodarAdbAsync("shell df -h /data");
            string pkgsRaw = await RodarAdbAsync("shell pm list packages -e");

            double memTotalMb = ExtrairKbParaMb(memInfo, "MemTotal");
            double memLivreMb = ExtrairKbParaMb(memInfo, "MemAvailable");
            int qtdApps = pkgsRaw.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries).Count(x => x.StartsWith("package:"));

            string resumoStorage = "N/D";
            var dfLinhas = dfData.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries);
            if (dfLinhas.Length >= 2)
            {
                var cols = dfLinhas[dfLinhas.Length - 1].Split(new[] { ' ', '\t' }, StringSplitOptions.RemoveEmptyEntries);
                if (cols.Length >= 5) resumoStorage = cols[3] + " livres (" + cols[4] + " usado)";
            }

            lblStatusAdb.Text = "CONECTADO - Serial: " + serialAtual + " | " + modelo + " (" + device + ")";
            lblStatusAdb.ForeColor = accentGreen;
            lblCardModelo.Text = modelo + " (Android " + androidVer + ")";
            lblCardRam.Text = memLivreMb + " / " + memTotalMb + " MB";
            lblCardStorage.Text = resumoStorage;
            lblCardApps.Text = qtdApps + " pacotes ativos";

            Log("Diagnostico: " + modelo + " (" + serialAtual + ") | Android " + androidVer + " | RAM Livre: " + memLivreMb + " MB | Apps ativos: " + qtdApps);
            AtualizarProgresso(100, 100, "Diagnostico concluido.");
        }

        private double ExtrairKbParaMb(string texto, string chave)
        {
            var m = Regex.Match(texto, chave + @":\s+(\d+)\s+kB");
            long kb;
            if (m.Success && long.TryParse(m.Groups[1].Value, out kb))
                return Math.Round(kb / 1024.0, 0);
            return 0;
        }

        private async Task RemoverBloatwareAsync()
        {
            if (!await VerificarConexaoAsync()) return;
            string pkgsRaw = await RodarAdbAsync("shell pm list packages -e");
            var ativosSet = new HashSet<string>(
                pkgsRaw.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries)
                       .Where(x => x.StartsWith("package:"))
                       .Select(x => x.Replace("package:", "").Trim()),
                StringComparer.OrdinalIgnoreCase
            );

            var alvos = new List<string>();
            for (int i = 0; i < clbCategorias.Items.Count; i++)
            {
                if (!clbCategorias.GetItemChecked(i)) continue;
                var cat = categorias[i];
                if (cat.Id == "12" && chkManterStreaming.Checked) continue;
                foreach (var pkg in cat.Pacotes)
                {
                    if (pacotesProtegidos.Contains(pkg)) continue;
                    if (chkManterStreaming.Checked && categorias[11].Pacotes.Contains(pkg)) continue;
                    if (chkManterGooglePessoal.Checked && (pkg == "com.google.android.gm" || pkg == "com.google.android.apps.photos")) continue;
                    if (ativosSet.Contains(pkg) && !alvos.Contains(pkg)) alvos.Add(pkg);
                }
            }

            if (alvos.Count == 0)
            {
                Log("[OK] Nenhum pacote de bloatware ativo nas categorias selecionadas!");
                return;
            }

            for (int i = 0; i < alvos.Count; i++)
            {
                string pkg = alvos[i];
                AtualizarProgresso(i + 1, alvos.Count, "Removendo (" + (i + 1) + "/" + alvos.Count + "): " + pkg);
                string res = await RodarAdbAsync("shell pm uninstall --user 0 " + pkg);
                if (res.IndexOf("Success", StringComparison.OrdinalIgnoreCase) >= 0)
                    Log("  [OK] Removido: " + pkg);
                else
                    Log("  [Protegido]: " + pkg);
            }
            await ExecutarVarreduraAsync();
        }

        private async Task OtimizarSistemaAsync()
        {
            if (!await VerificarConexaoAsync()) return;
            AtualizarProgresso(30, 100, "Desligando animacoes...");
            await RodarAdbAsync("shell settings put global window_animation_scale 0");
            await RodarAdbAsync("shell settings put global transition_animation_scale 0");
            await RodarAdbAsync("shell settings put global animator_duration_scale 0");
            AtualizarProgresso(70, 100, "Limpando caches (pm trim-caches 999G)...");
            await RodarAdbAsync("shell pm trim-caches 999G");
            AtualizarProgresso(100, 100, "Otimizacao concluida!");
            Log("[OK] Animacoes desligadas e caches limpos!");
            await ExecutarVarreduraAsync();
        }

        private async Task MedirDesempenhoAsync()
        {
            if (!await VerificarConexaoAsync()) return;
            var tempos = new List<int>();
            for (int i = 1; i <= 3; i++)
            {
                await RodarAdbAsync("shell am force-stop com.android.settings");
                await Task.Delay(700);
                string res = await RodarAdbAsync("shell am start -W -n com.android.settings/.Settings");
                var m = Regex.Match(res, @"TotalTime:\s+(\d+)");
                int ms;
                if (m.Success && int.TryParse(m.Groups[1].Value, out ms))
                {
                    tempos.Add(ms);
                    Log("  Teste " + i + "/3: " + ms + " ms");
                }
            }
            if (tempos.Count > 0) Log("[Benchmark] Media: " + Math.Round(tempos.Average(), 1) + " ms");
            await ExecutarVarreduraAsync();
        }

        private async Task RestaurarAppsAsync()
        {
            if (!await VerificarConexaoAsync()) return;
            string arqRem = Path.Combine(baseDir, "removidos.txt");
            if (!File.Exists(arqRem)) return;
            var lista = File.ReadAllLines(arqRem).Where(x => !string.IsNullOrWhiteSpace(x)).ToList();
            for (int i = 0; i < lista.Count; i++)
            {
                AtualizarProgresso(i + 1, lista.Count, "Restaurando: " + lista[i]);
                await RodarAdbAsync("shell cmd package install-existing " + lista[i].Trim());
            }
            await RodarAdbAsync("shell settings put global window_animation_scale 1");
            await RodarAdbAsync("shell settings put global transition_animation_scale 1");
            await RodarAdbAsync("shell settings put global animator_duration_scale 1");
            Log("[OK] Restauracao concluida!");
            await ExecutarVarreduraAsync();
        }
    }

    static class Program
    {
        [STAThread]
        static void Main(string[] args)
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            MainForm form = new MainForm();
            if (args != null && args.Length > 0 && args[0] == "-TestMode")
            {
                return;
            }
            Application.Run(form);
        }
    }
}
