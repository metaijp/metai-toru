# MetAI Toru

[日本語](#日本語) | [English](#english) | [Español](#español)

---

## 日本語

**MetAI Toru（取る）** は、動画と音声をダウンロードするmacOS向けのツールです。
[yt-dlp](https://github.com/yt-dlp/yt-dlp) を使っています。

### 必要なもの
- macOS
- Python 3（仮想環境 `.venv`）
- ffmpeg：`brew install ffmpeg`
- Node.js：`brew install node`

### 使い方
```bash
./dl.py URL              # 動画をダウンロード
./dl.py URL --audio      # 音声のみ（mp3）
./dl.py URL -q 720       # 最大の高さを指定
```

### 注意
個人利用が前提です。
各サービスの利用規約と著作権を守ってご利用ください。
DRM保護されたコンテンツはダウンロードできません。

---

## English

**MetAI Toru** (取る, "to take") is a macOS tool for downloading video and audio.
It is built on [yt-dlp](https://github.com/yt-dlp/yt-dlp).

### Requirements
- macOS
- Python 3 (virtual environment `.venv`)
- ffmpeg: `brew install ffmpeg`
- Node.js: `brew install node`

### Usage
```bash
./dl.py URL              # download a video
./dl.py URL --audio      # audio only (mp3)
./dl.py URL -q 720       # set a maximum height
```

### Notice
For personal use only.
Please respect each service's terms of use and copyright.
DRM-protected content cannot be downloaded.

---

## Español

**MetAI Toru** (取る, "tomar") es una herramienta para macOS que descarga video y audio.
Está basada en [yt-dlp](https://github.com/yt-dlp/yt-dlp).

### Requisitos
- macOS
- Python 3 (entorno virtual `.venv`)
- ffmpeg: `brew install ffmpeg`
- Node.js: `brew install node`

### Uso
```bash
./dl.py URL              # descargar un video
./dl.py URL --audio      # solo audio (mp3)
./dl.py URL -q 720       # altura máxima
```

### Aviso
Solo para uso personal.
Respeta los términos de uso y los derechos de autor de cada servicio.
El contenido con protección DRM no se puede descargar.
