<p align="center"><img src="assets/icon.png" width="128" alt="MetAI Toru"></p>

# MetAI Toru 取る

[日本語](#日本語) | [English](#english) | [Español](#español)

---

## 日本語

**MetAI Toru（取る）** は、動画と音声をダウンロードするmacOS向けのアプリです。
[yt-dlp](https://github.com/yt-dlp/yt-dlp) を使っています。

### 使い方
1. **MetAI Toru** を開きます。
2. ダウンロードしたい動画の**リンクを貼り付け**ます（「貼り付け」ボタンも使えます）。
   YouTube、X / Twitter、Facebook、Instagram、TikTok は自動で判別されます。それ以外のサイトは **その他** を選びます。
3. **動画** か **音声のみ** を選び、解像度・形式（mp4 / mkv / webm、mp3 / m4a など）を選びます。
4. **ダウンロード** を押します。完了すると「✓ ダウンロード完了」と表示されます。
   ファイルは `~/Downloads/videos` に保存されます（「変更」で保存先を変えられます）。

右上の 🌐 から言語を切り替えられます（English / 日本語 / Español / Français / Deutsch / Português / 中文 / 한국어）。

> ログインが必要な動画（YouTube の「ボットではないこと」の確認、Instagram、Facebook など）は、「Cookie の取得元」でお使いのブラウザを選んでください。そのブラウザで該当サービスにログインしている必要があります。

### インストール
必要なもの：macOS、Python 3.10以上、`brew install ffmpeg node`

```bash
git clone https://github.com/metaijp/metai-toru.git && cd metai-toru
./build_app.sh        # 「MetAI Toru.app」を作成します
open "MetAI Toru.app"
```

ターミナルから使いたい場合：`./dl.py URL [-q 720] [--audio]`

### 注意
個人利用が前提です。
各サービスの利用規約と著作権を守ってご利用ください。
DRM保護されたコンテンツはダウンロードできません。
本アプリの利用方法について、当社は責任を負いません。

ライセンス：[MIT](LICENSE)

---

## English

**MetAI Toru** (取る, "to take") is a macOS app for downloading video and audio.
It is built on [yt-dlp](https://github.com/yt-dlp/yt-dlp).

### How to use
1. Open **MetAI Toru**.
2. **Paste the link** of the video you want (or press the *Paste* button).
   YouTube, X / Twitter, Facebook, Instagram and TikTok are detected automatically. For any other site, choose **Other**.
3. Choose **Video** or **Audio only**, then pick the resolution and format (mp4 / mkv / webm, or mp3 / m4a …).
4. Press **Download**. When it finishes you will see "✓ Download complete".
   Files are saved in `~/Downloads/videos` (use *Change* to pick another folder).

Use the 🌐 button at the top right to change the language (English / 日本語 / Español / Français / Deutsch / Português / 中文 / 한국어).

> For videos that need a login (YouTube's "confirm you're not a bot", Instagram, Facebook…), choose your browser in **Cookies from**. You must be signed in to that service in that browser.

### Install
Requirements: macOS, Python 3.10+, `brew install ffmpeg node`

```bash
git clone https://github.com/metaijp/metai-toru.git && cd metai-toru
./build_app.sh        # creates "MetAI Toru.app"
open "MetAI Toru.app"
```

Prefer the terminal? `./dl.py URL [-q 720] [--audio]`

### Notice
For personal use only.
Please respect each service's terms of use and copyright.
DRM-protected content cannot be downloaded.
The company is not responsible for how users use this application.

License: [MIT](LICENSE)

---

## Español

**MetAI Toru** (取る, "tomar") es una app para macOS que descarga vídeo y audio.
Está basada en [yt-dlp](https://github.com/yt-dlp/yt-dlp).

### Cómo se usa
1. Abre **MetAI Toru**.
2. **Pega el enlace** del vídeo que quieres (o pulsa el botón *Pegar*).
   YouTube, X / Twitter, Facebook, Instagram y TikTok se detectan solos. Para cualquier otra web, elige **Otros**.
3. Elige **Vídeo** o **Solo audio** y luego la resolución y el formato (mp4 / mkv / webm, o mp3 / m4a …).
4. Pulsa **Descargar**. Al terminar verás "✓ Descarga completada".
   Los archivos se guardan en `~/Downloads/videos` (con *Cambiar* eliges otra carpeta).

Con el botón 🌐 de arriba a la derecha cambias el idioma (English / 日本語 / Español / Français / Deutsch / Português / 中文 / 한국어).

> Para vídeos que piden login (la comprobación «no soy un robot» de YouTube, Instagram, Facebook…), elige tu navegador en **Cookies de**. Debes tener la sesión iniciada en ese servicio en ese navegador.

### Instalación
Requisitos: macOS, Python 3.10+, `brew install ffmpeg node`

```bash
git clone https://github.com/metaijp/metai-toru.git && cd metai-toru
./build_app.sh        # crea "MetAI Toru.app"
open "MetAI Toru.app"
```

¿Prefieres la terminal? `./dl.py URL [-q 720] [--audio]`

### Aviso
Solo para uso personal.
Respeta los términos de uso y los derechos de autor de cada servicio.
El contenido con protección DRM no se puede descargar.
La empresa no se hace responsable del uso que los usuarios den a esta aplicación.

Licencia: [MIT](LICENSE)
