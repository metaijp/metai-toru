<p align="center"><img src="assets/icon.png" width="128" alt="MetAI Toru"></p>

# MetAI Toru 取る

🌐 **English** · [日本語](#日本語) · [Español](#español)

---

## English

A small macOS app (Python + Tk, powered by [yt-dlp](https://github.com/yt-dlp/yt-dlp)) to download video and audio from the web for **personal use**.

**Features**
- Platform buttons: YouTube, X / Twitter, Facebook, Instagram, TikTok and **Other** (any site supported by yt-dlp). The platform is auto-detected from the URL.
- Video: resolution (best, 4K, 1440p … 240p) and format (mp4, mkv, webm).
- Audio only: quality (best … 96 kbps) and format (mp3, m4a, opus, flac, wav).
- Browser cookies (Brave, Chrome, Safari, Firefox, Edge) for content that requires login (YouTube bot check, Instagram, Facebook…).
- UI in 8 languages (English default, 日本語, Español, Français, Deutsch, Português, 中文, 한국어). The choice is remembered.

**Requirements:** macOS, Python 3.10+, [ffmpeg](https://ffmpeg.org) and Node.js (`brew install ffmpeg node`).

**Install & run**
```bash
git clone <this-repo> && cd <this-repo>
./build_app.sh        # creates .venv and "MetAI Toru.app"
open "MetAI Toru.app"
```
You can also use the command line: `./dl.py "URL" [-q 720] [-a] [--browser brave]`.

**Notes**
- **DRM-protected content** (e.g. Mediaset Infinity, Netflix, Disney+) is not supported and this tool does not try to bypass it.
- YouTube may require cookies: pick your browser in "Cookies from" (you must be signed in there).

**Disclaimer:** the company is not responsible for how users use this application. Respect copyright and each website's terms of use.

---

## 日本語

**個人利用**を目的に、ウェブ上の動画・音声をダウンロードする macOS 向けの小さなアプリです(Python + Tk、[yt-dlp](https://github.com/yt-dlp/yt-dlp) を使用)。

**機能**
- プラットフォームボタン:YouTube、X / Twitter、Facebook、Instagram、TikTok、**その他**(yt-dlp が対応する任意のサイト)。URL から自動判別します。
- 動画:解像度(最高画質、4K、1440p 〜 240p)と形式(mp4、mkv、webm)を選択。
- 音声のみ:音質(最高 〜 96 kbps)と形式(mp3、m4a、opus、flac、wav)を選択。
- ブラウザの Cookie(Brave、Chrome、Safari、Firefox、Edge)を利用可能。ログインが必要なコンテンツ(YouTube のボット確認、Instagram、Facebook など)に対応。
- 8 言語に対応(英語が既定、日本語、スペイン語、フランス語、ドイツ語、ポルトガル語、中国語、韓国語)。選択は保存されます。

**必要なもの:** macOS、Python 3.10 以上、[ffmpeg](https://ffmpeg.org)、Node.js(`brew install ffmpeg node`)。

**インストールと起動**
```bash
git clone <このリポジトリ> && cd <このリポジトリ>
./build_app.sh        # .venv と「MetAI Toru.app」を作成
open "MetAI Toru.app"
```
コマンドラインでも使えます:`./dl.py "URL" [-q 720] [-a] [--browser brave]`

**注意**
- **DRM で保護されたコンテンツ**(Mediaset Infinity、Netflix、Disney+ など)には対応しておらず、回避も行いません。
- YouTube では Cookie が必要になる場合があります。「Cookie の取得元」でブラウザを選択してください(そのブラウザで YouTube にログインしている必要があります)。

**免責事項:** 本アプリの利用方法について、当社は責任を負いません。著作権と各サイトの利用規約をお守りください。

---

## Español

Pequeña app para macOS (Python + Tk, con [yt-dlp](https://github.com/yt-dlp/yt-dlp)) para descargar vídeo y audio de internet para **uso personal**.

**Funciones**
- Botones de plataforma: YouTube, X / Twitter, Facebook, Instagram, TikTok y **Otros** (cualquier web compatible con yt-dlp). La plataforma se detecta sola a partir de la URL.
- Vídeo: resolución (mejor, 4K, 1440p … 240p) y formato (mp4, mkv, webm).
- Solo audio: calidad (mejor … 96 kbps) y formato (mp3, m4a, opus, flac, wav).
- Cookies del navegador (Brave, Chrome, Safari, Firefox, Edge) para contenido que pide login (comprobación anti-bot de YouTube, Instagram, Facebook…).
- Interfaz en 8 idiomas (inglés por defecto, 日本語, Español, Français, Deutsch, Português, 中文, 한국어). La elección se recuerda.

**Requisitos:** macOS, Python 3.10+, [ffmpeg](https://ffmpeg.org) y Node.js (`brew install ffmpeg node`).

**Instalar y ejecutar**
```bash
git clone <este-repositorio> && cd <este-repositorio>
./build_app.sh        # crea .venv y "MetAI Toru.app"
open "MetAI Toru.app"
```
También se puede usar por terminal: `./dl.py "URL" [-q 720] [-a] [--browser brave]`.

**Notas**
- El contenido **protegido con DRM** (p. ej. Mediaset Infinity, Netflix, Disney+) no está soportado y esta herramienta no intenta saltarse esa protección.
- YouTube puede pedir cookies: elige tu navegador en «Cookies de» (debes tener la sesión iniciada en él).

**Aviso:** la empresa no se hace responsable del uso que los usuarios den a esta aplicación. Respeta los derechos de autor y las condiciones de cada web.
