#!/usr/bin/env python3
"""Descargador de vídeos para uso personal, basado en yt-dlp.

Uso:
    ./dl.py URL [URL ...]
    ./dl.py URL --audio              # solo audio (mp3)
    ./dl.py URL -q 720               # altura máxima
    ./dl.py URL --browser chrome     # usar cookies del navegador (si requiere login)
    ./dl.py URL --list               # ver formatos sin descargar
"""
import argparse
import sys
from pathlib import Path

import yt_dlp
from yt_dlp.utils import DownloadError


def build_opts(args):
    out_dir = Path(args.output).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    opts = {
        "outtmpl": str(out_dir / "%(title).150B [%(id)s].%(ext)s"),
        "noplaylist": not args.playlist,
        "merge_output_format": "mp4",
        "restrictfilenames": False,
        "windowsfilenames": True,
        "retries": 10,
        "fragment_retries": 10,
        "concurrent_fragment_downloads": 4,
        "progress": True,
        "js_runtimes": {"node": {}},
        "remote_components": {"ejs:github"},
    }

    if args.audio:
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [
            {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}
        ]
    else:
        h = f"[height<={args.quality}]" if args.quality else ""
        opts["format"] = f"bv*{h}+ba/b{h}"

    if args.browser:
        opts["cookiesfrombrowser"] = (args.browser,)
    if args.cookies:
        opts["cookiefile"] = args.cookies
    if args.subs:
        opts.update(writesubtitles=True, subtitleslangs=["es", "en"])
    if args.list:
        opts["listformats"] = True
        opts["skip_download"] = True
    return opts


def main():
    p = argparse.ArgumentParser(description="Descargar vídeos de internet (yt-dlp)")
    p.add_argument("urls", nargs="+")
    p.add_argument("-o", "--output", default="~/Downloads/videos", help="carpeta de salida")
    p.add_argument("-q", "--quality", type=int, help="altura máxima, p. ej. 720")
    p.add_argument("-a", "--audio", action="store_true", help="solo audio (mp3)")
    p.add_argument("-p", "--playlist", action="store_true", help="descargar listas completas")
    p.add_argument("-s", "--subs", action="store_true", help="descargar subtítulos")
    p.add_argument("-l", "--list", action="store_true", help="listar formatos")
    p.add_argument("--browser", help="cookies del navegador: chrome, safari, firefox...")
    p.add_argument("--cookies", help="archivo cookies.txt")
    args = p.parse_args()

    failed = 0
    with yt_dlp.YoutubeDL(build_opts(args)) as ydl:
        for url in args.urls:
            try:
                ydl.download([url])
            except DownloadError as e:
                failed += 1
                msg = str(e)
                print(f"\n✗ {url}\n  {msg}", file=sys.stderr)
                if "DRM" in msg.upper():
                    print(
                        "  Este contenido está protegido con DRM (Widevine/FairPlay); "
                        "esta herramienta no lo puede descargar.",
                        file=sys.stderr,
                    )
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
