#!/usr/bin/env python3
"""MetAI Toru — descargador de vídeo/audio con interfaz gráfica (yt-dlp)."""
import json
import math
import re
import os
import shutil
import subprocess
import threading
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox, filedialog

import yt_dlp
from PIL import Image, ImageDraw, ImageFilter, ImageTk
from yt_dlp.utils import DownloadError

# ---------- datos ----------
PLATFORMS = {
    "YouTube": r"(youtube\.com|youtu\.be)",
    "X / Twitter": r"(twitter\.com|x\.com|t\.co)",
    "Facebook": r"(facebook\.com|fb\.watch|fb\.com)",
    "Instagram": r"instagram\.com",
    "TikTok": r"tiktok\.com",
}
NEEDS_LOGIN = {"Facebook", "Instagram"}

RESOLUTIONS = ["Mejor disponible", "2160p (4K)", "1440p", "1080p", "720p", "480p", "360p", "240p"]
VIDEO_FORMATS = ["mp4", "mkv", "webm"]
AUDIO_FORMATS = ["mp3", "m4a", "opus", "flac", "wav"]
AUDIO_QUALITY = ["Mejor", "320 kbps", "256 kbps", "192 kbps", "128 kbps", "96 kbps"]
BROWSERS = ["Ninguno", "chrome", "safari", "firefox", "brave", "edge"]

# ---------- estilo MetAI (azul → violeta) ----------
BLUE, VIOLET = "#3B82F6", "#8B5CF6"
DEEP = "#4C1D95"
BG = "#F5F3FF"
CARD = "#FFFFFF"
BORDER = "#DDD6FE"
MUTED = "#7C6FA8"
OK, ERR, WARN = "#059669", "#DC2626", "#B45309"
FONT = "Helvetica Neue"


def detect_platform(url):
    for name, pat in PLATFORMS.items():
        if re.search(pat, url, re.I):
            return name
    return None


def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def lerp_color(a, b, t):
    ra, rb = hex2rgb(a), hex2rgb(b)
    return "#%02x%02x%02x" % tuple(int(ra[i] + (rb[i] - ra[i]) * t) for i in range(3))


def round_rect(c, x1, y1, x2, y2, r, **kw):
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
           x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return c.create_polygon(pts, smooth=True, **kw)


def gradient_rounded(c, w, h, r, c1, c2, x0=0, y0=0, tag="grad"):
    """Degradado horizontal recortado a rectángulo redondeado."""
    for x in range(w):
        if x < r:
            dy = r - math.sqrt(max(r * r - (r - x - 0.5) ** 2, 0))
        elif x > w - r:
            dy = r - math.sqrt(max(r * r - (x - (w - r) + 0.5) ** 2, 0))
        else:
            dy = 0
        c.create_line(x0 + x, y0 + dy, x0 + x, y0 + h - dy, fill=lerp_color(c1, c2, x / max(w - 1, 1)), tags=tag)


class Pill(tk.Canvas):
    """Botón tipo píldora seleccionable (radio)."""

    def __init__(self, master, text, value, variable, command=None, bg=CARD, pad_x=16, h=34):
        f = (FONT, 12, "bold")
        w = tk.Label(font=f, text=text).winfo_reqwidth() + pad_x * 2
        super().__init__(master, width=w, height=h, bg=bg, highlightthickness=0, cursor="pointinghand")
        self.text, self.value, self.var, self.cmd = text, value, variable, command
        self.w, self.h, self.f, self.hover = w, h, f, False
        self.bind("<Button-1>", self._click)
        self.bind("<Enter>", lambda e: self._set_hover(True))
        self.bind("<Leave>", lambda e: self._set_hover(False))
        self._tid = variable.trace_add("write", lambda *_: self.draw())
        self.bind("<Destroy>", lambda e: e.widget is self and variable.trace_remove("write", self._tid))
        self.draw()

    def _set_hover(self, v):
        self.hover = v
        self.draw()

    def _click(self, _):
        self.var.set(self.value)
        if self.cmd:
            self.cmd()

    def draw(self):
        self.delete("all")
        sel = self.var.get() == self.value
        if sel:
            gradient_rounded(self, self.w - 2, self.h - 2, (self.h - 2) // 2, BLUE, VIOLET, 1, 1)
            self.create_text(self.w / 2, self.h / 2, text=self.text, fill="white", font=self.f)
        else:
            round_rect(self, 1, 1, self.w - 1, self.h - 1, self.h // 2,
                       fill="#EEE9FF" if self.hover else CARD, outline=VIOLET if self.hover else BORDER, width=1.5)
            self.create_text(self.w / 2, self.h / 2, text=self.text, fill=DEEP, font=self.f)


class BigButton(tk.Canvas):
    def __init__(self, master, text, command, w=300, h=48, bg=BG, primary=True):
        super().__init__(master, width=w, height=h, bg=bg, highlightthickness=0, cursor="pointinghand")
        self.text, self.cmd, self.w, self.h, self.primary = text, command, w, h, primary
        self.enabled, self.hover = True, False
        self.bind("<Button-1>", lambda e: self.enabled and self.cmd())
        self.bind("<Enter>", lambda e: self._hv(True))
        self.bind("<Leave>", lambda e: self._hv(False))
        self.draw()

    def _hv(self, v):
        self.hover = v
        self.draw()

    def set_enabled(self, v):
        self.enabled = v
        self.draw()

    def set_text(self, t):
        self.text = t
        self.draw()

    def draw(self):
        self.delete("all")
        r = self.h // 2
        if self.primary:
            if self.enabled:
                a, b = (BLUE, VIOLET) if not self.hover else ("#2563EB", "#7C3AED")
            else:
                a, b = "#C4C0DC", "#C4C0DC"
            gradient_rounded(self, self.w, self.h, r, a, b)
            self.create_text(self.w / 2, self.h / 2, text=self.text, fill="white", font=(FONT, 15, "bold"))
        else:
            round_rect(self, 1, 1, self.w - 1, self.h - 1, r, fill="#EEE9FF" if self.hover else CARD, outline=BORDER, width=1.5)
            self.create_text(self.w / 2, self.h / 2, text=self.text, fill=DEEP, font=(FONT, 13, "bold"))


class Progress(tk.Canvas):
    def __init__(self, master, w=520, h=10, bg=BG):
        super().__init__(master, width=w, height=h, bg=bg, highlightthickness=0)
        self.w, self.h, self.value = w, h, 0
        self.draw()

    def set(self, v):
        self.value = max(0, min(100, v))
        self.draw()

    def draw(self):
        self.delete("all")
        r = self.h // 2
        round_rect(self, 0, 0, self.w, self.h, r, fill="#E4DEFF", outline="")
        fw = int(self.w * self.value / 100)
        if fw > self.h:
            gradient_rounded(self, fw, self.h, r, BLUE, VIOLET)


LANGS = {
    "en": "English", "ja": "日本語", "es": "Español", "fr": "Français",
    "de": "Deutsch", "pt": "Português", "zh": "中文", "ko": "한국어",
}
DEFAULT_LANG = "en"
CONFIG = Path("~/.metai_toru.json").expanduser()

T = {
    "subtitle": {
        "en": "Download video & audio  ·  取る  ✦", "ja": "動画と音声をダウンロード  ·  取る  ✦",
        "es": "Descarga vídeo y audio  ·  取る  ✦", "fr": "Télécharge vidéo et audio  ·  取る  ✦",
        "de": "Video & Audio herunterladen  ·  取る  ✦", "pt": "Baixe vídeo e áudio  ·  取る  ✦",
        "zh": "下载视频和音频  ·  取る  ✦", "ko": "영상 및 오디오 다운로드  ·  取る  ✦"},
    "from": {"en": "Where from?", "ja": "どこから?", "es": "¿De dónde?", "fr": "D'où ?",
             "de": "Woher?", "pt": "De onde?", "zh": "来源平台?", "ko": "어디서?"},
    "link": {"en": "Link", "ja": "リンク", "es": "Enlace", "fr": "Lien", "de": "Link",
             "pt": "Link", "zh": "链接", "ko": "링크"},
    "paste": {"en": "Paste", "ja": "貼り付け", "es": "Pegar", "fr": "Coller", "de": "Einfügen",
              "pt": "Colar", "zh": "粘贴", "ko": "붙여넣기"},
    "video": {"en": "🎬  Video", "ja": "🎬  動画", "es": "🎬  Vídeo", "fr": "🎬  Vidéo",
              "de": "🎬  Video", "pt": "🎬  Vídeo", "zh": "🎬  视频", "ko": "🎬  영상"},
    "audio": {"en": "🎵  Audio only", "ja": "🎵  音声のみ", "es": "🎵  Solo audio", "fr": "🎵  Audio seul",
              "de": "🎵  Nur Audio", "pt": "🎵  Só áudio", "zh": "🎵  仅音频", "ko": "🎵  오디오만"},
    "vtitle": {"en": "VIDEO", "ja": "動画", "es": "VÍDEO", "fr": "VIDÉO", "de": "VIDEO",
               "pt": "VÍDEO", "zh": "视频", "ko": "영상"},
    "atitle": {"en": "AUDIO", "ja": "音声", "es": "AUDIO", "fr": "AUDIO", "de": "AUDIO",
               "pt": "ÁUDIO", "zh": "音频", "ko": "오디오"},
    "resolution": {"en": "Resolution", "ja": "解像度", "es": "Resolución", "fr": "Résolution",
                   "de": "Auflösung", "pt": "Resolução", "zh": "分辨率", "ko": "해상도"},
    "format": {"en": "Format", "ja": "形式", "es": "Formato", "fr": "Format", "de": "Format",
               "pt": "Formato", "zh": "格式", "ko": "형식"},
    "quality": {"en": "Quality", "ja": "音質", "es": "Calidad", "fr": "Qualité", "de": "Qualität",
                "pt": "Qualidade", "zh": "音质", "ko": "음질"},
    "saveto": {"en": "Save to", "ja": "保存先", "es": "Guardar en", "fr": "Enregistrer dans",
               "de": "Speichern in", "pt": "Salvar em", "zh": "保存到", "ko": "저장 위치"},
    "change": {"en": "Change", "ja": "変更", "es": "Cambiar", "fr": "Changer", "de": "Ändern",
               "pt": "Alterar", "zh": "更改", "ko": "변경"},
    "cookies": {"en": "Cookies from", "ja": "Cookie の取得元", "es": "Cookies de", "fr": "Cookies de",
                "de": "Cookies aus", "pt": "Cookies de", "zh": "Cookie 来源", "ko": "쿠키 가져올 곳"},
    "cookies_hint": {
        "en": "  only if login is required or it's private", "ja": "  ログインが必要・非公開の場合のみ",
        "es": "  solo si pide login o es privado", "fr": "  seulement si connexion requise ou privé",
        "de": "  nur bei Login-Pflicht oder privaten Inhalten", "pt": "  só se exigir login ou for privado",
        "zh": "  仅在需要登录或为私密内容时使用", "ko": "  로그인이 필요하거나 비공개일 때만"},
    "login_hint": {
        "en": "  ← this platform often requires login: pick your browser",
        "ja": "  ← このサイトはログインが必要なことが多い:ブラウザを選択",
        "es": "  ← esta plataforma suele pedir login: elige tu navegador",
        "fr": "  ← cette plateforme exige souvent une connexion : choisis ton navigateur",
        "de": "  ← diese Plattform verlangt oft Login: Browser wählen",
        "pt": "  ← esta plataforma costuma exigir login: escolha o navegador",
        "zh": "  ← 该平台通常需要登录:请选择浏览器",
        "ko": "  ← 이 플랫폼은 로그인이 필요한 경우가 많습니다: 브라우저 선택"},
    "download": {"en": "⬇  Download", "ja": "⬇  ダウンロード", "es": "⬇  Descargar", "fr": "⬇  Télécharger",
                 "de": "⬇  Herunterladen", "pt": "⬇  Baixar", "zh": "⬇  下载", "ko": "⬇  다운로드"},
    "openfolder": {"en": "Open folder", "ja": "フォルダを開く", "es": "Abrir carpeta", "fr": "Ouvrir le dossier",
                   "de": "Ordner öffnen", "pt": "Abrir pasta", "zh": "打开文件夹", "ko": "폴더 열기"},
    "ready": {"en": "Ready ✦", "ja": "準備完了 ✦", "es": "Listo ✦", "fr": "Prêt ✦", "de": "Bereit ✦",
              "pt": "Pronto ✦", "zh": "就绪 ✦", "ko": "준비 완료 ✦"},
    "best": {"en": "Best available", "ja": "最高画質", "es": "Mejor disponible", "fr": "Meilleure dispo",
             "de": "Beste verfügbar", "pt": "Melhor disponível", "zh": "最佳可用", "ko": "최고 화질"},
    "bestq": {"en": "Best", "ja": "最高", "es": "Mejor", "fr": "Meilleure", "de": "Beste",
              "pt": "Melhor", "zh": "最佳", "ko": "최고"},
    "none": {"en": "None", "ja": "なし", "es": "Ninguno", "fr": "Aucun", "de": "Keine",
             "pt": "Nenhum", "zh": "无", "ko": "없음"},
    "starting": {"en": "Starting…", "ja": "開始中…", "es": "Iniciando…", "fr": "Démarrage…",
                 "de": "Wird gestartet…", "pt": "Iniciando…", "zh": "正在开始…", "ko": "시작 중…"},
    "downloading": {"en": "Downloading…", "ja": "ダウンロード中…", "es": "Descargando…", "fr": "Téléchargement…",
                    "de": "Lädt herunter…", "pt": "Baixando…", "zh": "下载中…", "ko": "다운로드 중…"},
    "processing": {"en": "Processing with ffmpeg…", "ja": "ffmpeg で処理中…", "es": "Procesando con ffmpeg…",
                   "fr": "Traitement avec ffmpeg…", "de": "Verarbeitung mit ffmpeg…",
                   "pt": "Processando com ffmpeg…", "zh": "正在用 ffmpeg 处理…", "ko": "ffmpeg 처리 중…"},
    "done": {"en": "✓ Download complete", "ja": "✓ ダウンロード完了", "es": "✓ Descarga completada",
             "fr": "✓ Téléchargement terminé", "de": "✓ Download abgeschlossen", "pt": "✓ Download concluído",
             "zh": "✓ 下载完成", "ko": "✓ 다운로드 완료"},
    "error": {"en": "✗ Error", "ja": "✗ エラー", "es": "✗ Error", "fr": "✗ Erreur", "de": "✗ Fehler",
              "pt": "✗ Erro", "zh": "✗ 错误", "ko": "✗ 오류"},
    "drm": {"en": "DRM-protected content: it can't be downloaded.",
            "ja": "DRM で保護されたコンテンツはダウンロードできません。",
            "es": "Contenido protegido con DRM: no se puede descargar.",
            "fr": "Contenu protégé par DRM : téléchargement impossible.",
            "de": "DRM-geschützter Inhalt: Download nicht möglich.",
            "pt": "Conteúdo protegido por DRM: não é possível baixar.",
            "zh": "受 DRM 保护的内容无法下载。", "ko": "DRM으로 보호된 콘텐츠는 다운로드할 수 없습니다."},
    "invalid_url": {"en": "Paste a valid URL (starting with http).",
                    "ja": "有効な URL(http で始まる)を貼り付けてください。",
                    "es": "Pega una URL válida (empieza por http).",
                    "fr": "Colle une URL valide (commençant par http).",
                    "de": "Füge eine gültige URL ein (beginnt mit http).",
                    "pt": "Cole uma URL válida (começa com http).",
                    "zh": "请粘贴有效的链接(以 http 开头)。", "ko": "유효한 URL(http로 시작)을 붙여넣으세요."},
    "mismatch": {"en": "You picked {sel} but the URL looks like {det}. Continue?",
                 "ja": "{sel} を選択しましたが、URL は {det} のようです。続行しますか?",
                 "es": "Has elegido {sel} pero la URL parece de {det}. ¿Continuar?",
                 "fr": "Tu as choisi {sel} mais l'URL semble être {det}. Continuer ?",
                 "de": "Du hast {sel} gewählt, die URL sieht aber nach {det} aus. Fortfahren?",
                 "pt": "Você escolheu {sel}, mas a URL parece ser de {det}. Continuar?",
                 "zh": "你选择了 {sel},但链接看起来是 {det}。继续吗?",
                 "ko": "{sel}을(를) 선택했지만 URL은 {det}처럼 보입니다. 계속할까요?"},
}

T["other"] = {"en": "Other", "ja": "その他", "es": "Otros", "fr": "Autres", "de": "Andere",
              "pt": "Outros", "zh": "其他", "ko": "기타"}
T["disclaimer"] = {
    "en": "The company is not responsible for how users use this application. Please respect copyright and each website's terms of use.",
    "ja": "本アプリの利用方法について、当社は責任を負いません。著作権と各サイトの利用規約をお守りください。",
    "es": "La empresa no se hace responsable del uso que los usuarios den a esta aplicación. Respeta los derechos de autor y las condiciones de cada web.",
    "fr": "L'entreprise n'est pas responsable de l'usage que les utilisateurs font de cette application. Respectez le droit d'auteur et les conditions de chaque site.",
    "de": "Das Unternehmen übernimmt keine Verantwortung für die Nutzung dieser Anwendung durch die Nutzer. Bitte beachte das Urheberrecht und die Nutzungsbedingungen jeder Website.",
    "pt": "A empresa não se responsabiliza pelo uso que os usuários fazem deste aplicativo. Respeite os direitos autorais e os termos de cada site.",
    "zh": "对于用户如何使用本应用,本公司概不负责。请尊重版权及各网站的使用条款。",
    "ko": "회사는 사용자가 이 애플리케이션을 사용하는 방식에 대해 책임을 지지 않습니다. 저작권과 각 웹사이트의 이용약관을 준수해 주세요."}
T["bot"] = {
    "en": "YouTube wants to confirm you're not a bot. I've selected your browser in “Cookies from”: press Download again. (You must be signed in to YouTube in that browser.)",
    "ja": "YouTube が「ボットではないこと」の確認を求めています。「Cookie の取得元」にブラウザを設定しました。もう一度ダウンロードを押してください。(そのブラウザで YouTube にログインしている必要があります)",
    "es": "YouTube pide confirmar que no eres un robot. He seleccionado tu navegador en «Cookies de»: pulsa Descargar otra vez. (Debes tener la sesión de YouTube iniciada en ese navegador.)",
    "fr": "YouTube demande de confirmer que tu n'es pas un robot. J'ai sélectionné ton navigateur dans « Cookies de » : appuie à nouveau sur Télécharger. (Tu dois être connecté à YouTube dans ce navigateur.)",
    "de": "YouTube verlangt eine Bestätigung, dass du kein Bot bist. Ich habe deinen Browser unter „Cookies aus“ gewählt: Klicke erneut auf Herunterladen. (Du musst in diesem Browser bei YouTube angemeldet sein.)",
    "pt": "O YouTube pede para confirmar que você não é um robô. Selecionei seu navegador em “Cookies de”: clique em Baixar novamente. (Você precisa estar logado no YouTube nesse navegador.)",
    "zh": "YouTube 要求确认你不是机器人。已在“Cookie 来源”中选择你的浏览器,请再次点击下载。(需要在该浏览器中登录 YouTube)",
    "ko": "YouTube가 봇이 아닌지 확인을 요구합니다. '쿠키 가져올 곳'에 브라우저를 선택했습니다. 다운로드를 다시 눌러 주세요. (해당 브라우저에서 YouTube에 로그인되어 있어야 합니다)"}
OTHER = "other"

BROWSER_APPS = {
    "brave": "/Applications/Brave Browser.app", "chrome": "/Applications/Google Chrome.app",
    "firefox": "/Applications/Firefox.app", "edge": "/Applications/Microsoft Edge.app",
    "safari": "/Applications/Safari.app",
}

HEIGHTS = [None, 2160, 1440, 1080, 720, 480, 360, 240]
AUDIO_KBPS = [None, 320, 256, 192, 128, 96]


def load_lang():
    try:
        lang = json.loads(CONFIG.read_text()).get("lang", DEFAULT_LANG)
        return lang if lang in LANGS else DEFAULT_LANG
    except Exception:
        return DEFAULT_LANG


ASSETS = Path(__file__).resolve().parent / "assets"
ICON_PNG = ASSETS / "icon.png"
LOGO_PNG = ASSETS / "logo_header.png"
HEADER_H = 132


def make_header(w, h):
    """Cabecera: degradado diagonal azul profundo → violeta con destellos luminosos."""
    k = 2
    W, H = w * k, h * k
    c1, c2 = hex2rgb("#1E3A8A"), hex2rgb("#6D28D9")
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        for x in range(W):
            t = min(1.0, (x * 0.85 + y * 0.6) / (W * 0.85 + H * 0.6))
            px[x, y] = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = ImageDraw.Draw(glow)
    g.ellipse((W * 0.62, -H * 0.9, W * 1.1, H * 0.75), fill=(167, 139, 250, 150))
    g.ellipse((W * 0.40, H * 0.55, W * 0.62, H * 1.5), fill=(96, 165, 250, 120))
    g.ellipse((-W * 0.08, -H * 0.6, W * 0.16, H * 0.45), fill=(96, 165, 250, 90))
    glow = glow.filter(ImageFilter.GaussianBlur(28 * k))
    img = Image.alpha_composite(img.convert("RGBA"), glow)
    d = ImageDraw.Draw(img)
    for sx, sy, r, a in ((0.50, 0.22, 7, 200), (0.58, 0.80, 5, 150), (0.71, 0.55, 4, 120), (0.30, 0.86, 3, 110)):
        cx, cy, rr = W * sx, H * sy, r * k
        d.polygon([(cx, cy - rr), (cx + rr * .28, cy - rr * .28), (cx + rr, cy), (cx + rr * .28, cy + rr * .28),
                   (cx, cy + rr), (cx - rr * .28, cy + rr * .28), (cx - rr, cy), (cx - rr * .28, cy - rr * .28)],
                  fill=(255, 255, 255, a))
    return img.resize((w, h), Image.LANCZOS)


def find_ffmpeg():
    """Al abrir la app desde el Dock el PATH es mínimo: busca ffmpeg también en las rutas de Homebrew."""
    extra = ["/opt/homebrew/bin", "/opt/homebrew/opt/ffmpeg-full/bin", "/usr/local/bin", "/opt/local/bin"]
    return shutil.which("ffmpeg", path=os.pathsep.join([os.environ.get("PATH", "")] + extra))


os.environ["PATH"] = os.pathsep.join([os.environ.get("PATH", ""), "/opt/homebrew/bin", "/usr/local/bin"])


class App(tk.Tk):
    W = 580

    def __init__(self):
        super().__init__()
        self.configure(bg=BG)
        self.resizable(False, False)
        try:
            self._icon = tk.PhotoImage(file=str(ICON_PNG))
            self.iconphoto(True, self._icon)
        except tk.TclError:
            pass
        self.lang = load_lang()
        self.out_dir = tk.StringVar(value=str(Path("~/Downloads/videos").expanduser()))
        self.platform = tk.StringVar(value="")
        self.mode = tk.StringVar(value="video")
        self.url = tk.StringVar()
        # selecciones por índice (independientes del idioma)
        self.i_res, self.i_vfmt, self.i_aq, self.i_afmt, self.i_browser = 0, 0, 0, 0, 0
        self.busy = False
        self.status_key, self.status_color = "ready", MUTED
        self._style()
        self._build()
        self._paste_if_url()
        self.url.trace_add("write", lambda *_: self._on_url())

    def tr(self, key, **kw):
        s = T[key].get(self.lang) or T[key][DEFAULT_LANG]
        return s.format(**kw) if kw else s

    def _style(self):
        st = ttk.Style(self)
        st.theme_use("clam")
        st.configure("M.TCombobox", fieldbackground=CARD, background="#EEE9FF", foreground=DEEP,
                     bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER, arrowcolor=VIOLET,
                     selectbackground=CARD, selectforeground=DEEP, padding=6)
        st.map("M.TCombobox", fieldbackground=[("readonly", CARD)], bordercolor=[("focus", VIOLET)])
        self.option_add("*TCombobox*Listbox.background", CARD)
        self.option_add("*TCombobox*Listbox.foreground", DEEP)
        self.option_add("*TCombobox*Listbox.selectBackground", VIOLET)
        self.option_add("*TCombobox*Listbox.selectForeground", "white")

    # ---------- listas traducidas ----------
    def res_values(self):
        return [self.tr("best")] + [f"{h}p (4K)" if h == 2160 else f"{h}p" for h in HEIGHTS[1:]]

    def aq_values(self):
        return [self.tr("bestq")] + [f"{k} kbps" for k in AUDIO_KBPS[1:]]

    def browser_values(self):
        return [self.tr("none")] + BROWSERS[1:]

    # ---------- UI ----------
    def _label(self, parent, text, bg=CARD, fg=DEEP, size=12, bold=False):
        return tk.Label(parent, text=text, bg=bg, fg=fg, font=(FONT, size, "bold" if bold else "normal"))

    def _card(self, parent, title=None):
        outer = tk.Frame(parent, bg=BORDER)
        inner = tk.Frame(outer, bg=CARD, padx=14, pady=10)
        inner.pack(padx=1, pady=1, fill="x")
        if title:
            self._label(inner, title, size=11, fg=MUTED, bold=True).pack(anchor="w", pady=(0, 6))
        grid = tk.Frame(inner, bg=CARD)
        grid.pack(anchor="w")
        return outer, grid

    def _combo(self, parent, values, index, attr, width):
        cb = ttk.Combobox(parent, values=values, state="readonly", width=width, style="M.TCombobox")
        cb.current(index)
        cb.bind("<<ComboboxSelected>>", lambda e: (setattr(self, attr, cb.current()), cb.selection_clear()))
        return cb

    def _rebuild(self):
        for w in self.winfo_children():
            w.destroy()
        self._build()
        self.update_idletasks()
        self.after(30, self._refresh)

    def _refresh(self):
        """macOS/Aqua a veces no repinta los ttk.Combobox recién creados."""
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"{w}x{h + 1}")
        self.update_idletasks()
        self.geometry(f"{w}x{h}")

    def _build(self):
        W, H = self.W, HEADER_H
        self.title("MetAI Toru")
        hd = tk.Canvas(self, width=W, height=H, highlightthickness=0, bg=BG)
        hd.pack()
        self._hdr_img = ImageTk.PhotoImage(make_header(W, H))
        hd.create_image(0, 0, image=self._hdr_img, anchor="nw")
        try:
            self._logo_img = tk.PhotoImage(file=str(LOGO_PNG))
            hd.create_image(22, H // 2, image=self._logo_img, anchor="w")
            tx = 132
        except tk.TclError:
            tx = 28
        hd.create_text(tx, 54, anchor="w", text="MetAI Toru", fill="white", font=(FONT, 32, "bold"))
        hd.create_text(tx + 2, 94, anchor="w", text=self.tr("subtitle"), fill="#DDD6FE", font=(FONT, 13))

        # Selector de idioma (píldora + menú propio)
        pw, ph, px0, py0 = 150, 34, W - 166, 16
        round_rect(hd, px0, py0, px0 + pw, py0 + ph, ph // 2, fill="#F5F3FF", outline="#C4B5FD", width=1.5, tags="lang")
        hd.create_text(px0 + pw / 2, py0 + ph / 2, text=f"🌐  {LANGS[self.lang]}  ▾", fill=DEEP,
                       font=(FONT, 12, "bold"), tags="lang")
        hd.tag_bind("lang", "<Button-1>", lambda e: self._lang_menu(hd, px0, py0 + ph + 6, pw))
        hd.tag_bind("lang", "<Enter>", lambda e: hd.config(cursor="pointinghand"))
        hd.tag_bind("lang", "<Leave>", lambda e: hd.config(cursor=""))

        body = tk.Frame(self, bg=BG, padx=28, pady=16)
        body.pack(fill="x")

        self._label(body, self.tr("from"), bg=BG, size=12, bold=True).pack(anchor="w")
        pf = tk.Frame(body, bg=BG)
        pf.pack(anchor="w", pady=(6, 12))
        for name in PLATFORMS:
            Pill(pf, name, name, self.platform, self._on_platform, bg=BG, pad_x=11).pack(side="left", padx=(0, 4))
        Pill(pf, self.tr("other"), OTHER, self.platform, self._on_platform, bg=BG, pad_x=11).pack(side="left")

        self._label(body, self.tr("link"), bg=BG, size=12, bold=True).pack(anchor="w")
        ur = tk.Frame(body, bg=BG)
        ur.pack(fill="x", pady=(6, 12))
        self.entry = tk.Entry(ur, textvariable=self.url, font=(FONT, 13), relief="flat", bg=CARD, fg=DEEP,
                              insertbackground=VIOLET, highlightthickness=2, highlightbackground=BORDER,
                              highlightcolor=VIOLET)
        self.entry.pack(side="left", fill="x", expand=True, ipady=7)
        BigButton(ur, self.tr("paste"), self._paste, w=90, h=36, bg=BG, primary=False).pack(side="left", padx=(8, 0))

        mf = tk.Frame(body, bg=BG)
        mf.pack(anchor="w", pady=(0, 10))
        Pill(mf, self.tr("video"), "video", self.mode, self._on_mode, bg=BG, pad_x=18, h=38).pack(side="left", padx=(0, 6))
        Pill(mf, self.tr("audio"), "audio", self.mode, self._on_mode, bg=BG, pad_x=18, h=38).pack(side="left")

        self.opts = tk.Frame(body, bg=BG)
        self.opts.pack(fill="x")
        self.vcard, vin = self._card(self.opts, self.tr("vtitle"))
        self._label(vin, self.tr("resolution")).grid(row=0, column=0, sticky="w", padx=(0, 8))
        self._combo(vin, self.res_values(), self.i_res, "i_res", 16).grid(row=0, column=1, padx=(0, 24))
        self._label(vin, self.tr("format")).grid(row=0, column=2, sticky="w", padx=(0, 8))
        self._combo(vin, VIDEO_FORMATS, self.i_vfmt, "i_vfmt", 8).grid(row=0, column=3)
        self.acard, ain = self._card(self.opts, self.tr("atitle"))
        self._label(ain, self.tr("quality")).grid(row=0, column=0, sticky="w", padx=(0, 8))
        self._combo(ain, self.aq_values(), self.i_aq, "i_aq", 16).grid(row=0, column=1, padx=(0, 24))
        self._label(ain, self.tr("format")).grid(row=0, column=2, sticky="w", padx=(0, 8))
        self._combo(ain, AUDIO_FORMATS, self.i_afmt, "i_afmt", 8).grid(row=0, column=3)
        self._on_mode()

        ex = tk.Frame(body, bg=BG)
        ex.pack(fill="x", pady=(12, 0))
        self._label(ex, self.tr("saveto"), bg=BG, size=11, fg=MUTED).grid(row=0, column=0, sticky="w")
        tk.Label(ex, textvariable=self.out_dir, bg=BG, fg=DEEP, font=(FONT, 11), anchor="w", width=38).grid(
            row=0, column=1, sticky="w", padx=8)
        BigButton(ex, self.tr("change"), self._choose_dir, w=96, h=30, bg=BG, primary=False).grid(row=0, column=2)
        self._label(ex, self.tr("cookies"), bg=BG, size=11, fg=MUTED).grid(row=1, column=0, sticky="w", pady=(8, 0))
        bf = tk.Frame(ex, bg=BG)
        bf.grid(row=1, column=1, columnspan=2, sticky="w", padx=8, pady=(8, 0))
        self._combo(bf, self.browser_values(), self.i_browser, "i_browser", 10).pack(side="left")
        self.hint = tk.Label(bf, text="", bg=BG, fg=MUTED, font=(FONT, 11))
        self.hint.pack(side="left")
        self._on_platform()

        act = tk.Frame(body, bg=BG)
        act.pack(fill="x", pady=(18, 10))
        self.btn = BigButton(act, self.tr("download"), self._start, w=340, h=50)
        self.btn.pack(side="left")
        self.btn.set_enabled(not self.busy)
        BigButton(act, self.tr("openfolder"), lambda: subprocess.run(["open", self.out_dir.get()]), w=160, h=50,
                  primary=False).pack(side="left", padx=(12, 0))

        self.bar = Progress(body, w=W - 56)
        self.bar.pack(anchor="w")
        self.status = tk.Label(body, text="", bg=BG, fg=MUTED, font=(FONT, 12), anchor="w", width=62)
        self.status.pack(anchor="w", pady=(8, 0))
        self._set_status(self.status_key, self.status_color)

        tk.Frame(body, bg=BORDER, height=1).pack(fill="x", pady=(14, 8))
        tk.Label(body, text=self.tr("disclaimer"), bg=BG, fg=MUTED, font=(FONT, 10), justify="left",
                 wraplength=W - 56, anchor="w").pack(anchor="w")

    # ---------- eventos ----------
    def _close_lang_menu(self):
        pop = getattr(self, "_pop", None)
        if pop is not None:
            try:
                pop.destroy()
            except tk.TclError:
                pass
            self._pop = None
        fid = getattr(self, "_pop_bind", None)
        if fid:
            self.unbind("<Button-1>", fid)
            self._pop_bind = None

    def _lang_menu(self, hd, x, y, width):
        if getattr(self, "_pop", None) is not None:
            self._close_lang_menu()
            return
        pop = tk.Frame(self, bg=VIOLET)  # panel dentro de la ventana (más fiable que un Toplevel en macOS)
        inner = tk.Frame(pop, bg=CARD)
        inner.pack(padx=2, pady=2, fill="both", expand=True)
        for code, name in LANGS.items():
            cur = code == self.lang
            row = tk.Label(inner, text=("✓  " if cur else "     ") + name, anchor="w", bg="#EEE9FF" if cur else CARD,
                           fg=DEEP, font=(FONT, 13, "bold" if cur else "normal"), padx=14, pady=7, cursor="pointinghand")
            row.pack(fill="x")
            row.bind("<Enter>", lambda e, r=row: r.config(bg="#DDD6FE"))
            row.bind("<Leave>", lambda e, r=row, c=cur: r.config(bg="#EEE9FF" if c else CARD))
            row.bind("<Button-1>", lambda e, c=code: (self._close_lang_menu(), self._set_lang(c)))
        pop.update_idletasks()
        pop.place(x=x, y=y, width=max(width, pop.winfo_reqwidth()))
        pop.lift()
        self._pop = pop
        self.after_idle(lambda: setattr(self, "_pop_bind", self.bind("<Button-1>", lambda e: self._close_lang_menu(), add="+")))

    def _set_lang(self, code):
        if code == self.lang:
            return
        self.lang = code
        try:
            CONFIG.write_text(json.dumps({"lang": code}))
        except OSError:
            pass
        self._rebuild()

    def _set_status(self, key, color=MUTED, raw=None):
        """key: clave de traducción; raw: texto ya formateado (p. ej. progreso)."""
        self.status_key, self.status_color = key, color
        try:
            self.status.config(text=raw if raw is not None else self.tr(key), fg=color)
        except tk.TclError:
            pass

    def _paste(self):
        try:
            self.url.set(self.clipboard_get().strip())
        except tk.TclError:
            pass

    def _paste_if_url(self):
        try:
            c = self.clipboard_get().strip()
            if c.startswith("http"):
                self.url.set(c)
        except tk.TclError:
            pass

    def _on_url(self):
        u = self.url.get().strip()
        p = detect_platform(u) or (OTHER if u.startswith("http") else None)
        if p:
            self.platform.set(p)
            self._on_platform()

    def _on_platform(self):
        if self.platform.get() in NEEDS_LOGIN:
            self.hint.config(text=self.tr("login_hint"), fg=WARN)
        else:
            self.hint.config(text=self.tr("cookies_hint"), fg=MUTED)

    def _on_mode(self):
        self.vcard.pack_forget()
        self.acard.pack_forget()
        (self.vcard if self.mode.get() == "video" else self.acard).pack(fill="x")

    def _choose_dir(self):
        d = filedialog.askdirectory(initialdir=self.out_dir.get())
        if d:
            self.out_dir.set(d)

    # ---------- descarga ----------
    def _opts(self):
        out = Path(self.out_dir.get()).expanduser()
        out.mkdir(parents=True, exist_ok=True)
        o = {
            "outtmpl": str(out / "%(title).150B [%(id)s].%(ext)s"),
            "noplaylist": True,
            "windowsfilenames": True,
            "retries": 10,
            "fragment_retries": 10,
            "concurrent_fragment_downloads": 4,
            "quiet": True,
            "no_warnings": True,
            "noprogress": True,
            "progress_hooks": [self._hook],
            "js_runtimes": {"node": {}},
            **({"ffmpeg_location": find_ffmpeg()} if find_ffmpeg() else {}),
            "remote_components": {"ejs:github"},
        }
        if self.mode.get() == "audio":
            fmt, kbps = AUDIO_FORMATS[self.i_afmt], AUDIO_KBPS[self.i_aq]
            o["format"] = "bestaudio/best"
            pp = {"key": "FFmpegExtractAudio", "preferredcodec": fmt}
            if fmt in ("mp3", "m4a", "opus"):
                pp["preferredquality"] = "0" if kbps is None else str(kbps)
            o["postprocessors"] = [pp]
        else:
            h = HEIGHTS[self.i_res]
            hf = f"[height<={h}]" if h else ""
            fmt = VIDEO_FORMATS[self.i_vfmt]
            if fmt == "mp4":
                o["format"] = f"bv*{hf}[ext=mp4]+ba[ext=m4a]/bv*{hf}+ba/b{hf}"
            elif fmt == "webm":
                o["format"] = f"bv*{hf}[ext=webm]+ba[ext=webm]/bv*{hf}+ba/b{hf}"
            else:
                o["format"] = f"bv*{hf}+ba/b{hf}"
            o["merge_output_format"] = fmt
        if self.i_browser > 0:
            o["cookiesfrombrowser"] = (BROWSERS[self.i_browser],)
        return o

    def _hook(self, d):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            if total:
                pct = d["downloaded_bytes"] * 100 / total
                self.after(0, lambda: self.bar.set(pct))
            msg = f"{self.tr('downloading')}  {d.get('_percent_str', '').strip()}   {d.get('_speed_str', '').strip()}   ETA {d.get('_eta_str', '').strip()}"
            self.after(0, lambda: self._set_status("downloading", DEEP, raw=msg))
        elif d["status"] == "finished":
            self.after(0, lambda: self._set_status("processing", DEEP))

    def _start(self):
        url = self.url.get().strip()
        if not url.startswith("http"):
            messagebox.showwarning("MetAI Toru", self.tr("invalid_url"))
            return
        sel, det = self.platform.get(), detect_platform(url)
        if sel and sel != OTHER and det and sel != det:
            if not messagebox.askyesno("MetAI Toru", self.tr("mismatch", sel=sel, det=det)):
                return
        if self.busy:
            return
        self.busy = True
        self.btn.set_enabled(False)
        self.bar.set(0)
        self._set_status("starting", DEEP)
        threading.Thread(target=self._run, args=(url,), daemon=True).start()

    def _run(self, url):
        def fail(msg):
            self._set_status("error", ERR)
            if "not a bot" in msg or "Sign in to confirm" in msg:
                if self.i_browser == 0:
                    for name, path in BROWSER_APPS.items():
                        if Path(path).exists() or name == "safari":
                            self.i_browser = BROWSERS.index(name)
                            break
                    self._rebuild()
                msg = self.tr("bot")
            messagebox.showerror("MetAI Toru", msg[:600])

        try:
            with yt_dlp.YoutubeDL(self._opts()) as ydl:
                ydl.download([url])
            self.after(0, lambda: (self.bar.set(100), self._set_status("done", OK)))
        except DownloadError as e:
            msg = self.tr("drm") if "DRM" in str(e).upper() else str(e)
            self.after(0, lambda: fail(msg))
        except Exception as e:
            self.after(0, lambda: fail(str(e)))
        finally:
            self.busy = False
            self.after(0, lambda: self.btn.set_enabled(True))


if __name__ == "__main__":
    App().mainloop()
