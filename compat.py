"""Diferencias entre sistemas (macOS / Windows / Linux): rutas de ffmpeg y node, abrir carpetas, etc."""
import glob
import os
import shutil
import subprocess
import sys

IS_MAC = sys.platform == "darwin"
IS_WIN = sys.platform == "win32"


def _windows_registry_path():
    """PATH guardado en el registro (Máquina + Usuario).

    Si ffmpeg/node se instalaron con winget después de abrir la sesión, o la app se abre desde un acceso
    directo, el PATH del proceso puede no incluirlos todavía."""
    try:
        import winreg
    except ImportError:
        return []
    out = []
    for root, key in ((winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"),
                      (winreg.HKEY_CURRENT_USER, r"Environment")):
        try:
            with winreg.OpenKey(root, key) as k:
                val, _ = winreg.QueryValueEx(k, "Path")
                out += [os.path.expandvars(p) for p in val.split(os.pathsep) if p]
        except OSError:
            pass
    return out


def _extra_dirs():
    if IS_MAC:
        # Al abrir la app desde el Dock el PATH es mínimo: añade las rutas de Homebrew / MacPorts.
        return ["/opt/homebrew/bin", "/opt/homebrew/opt/ffmpeg-full/bin", "/usr/local/bin", "/opt/local/bin"]
    if IS_WIN:
        local = os.environ.get("LOCALAPPDATA", "")
        pf = os.environ.get("ProgramFiles", r"C:\Program Files")
        home = os.path.expanduser("~")
        dirs = _windows_registry_path() + [
            os.path.join(local, "Microsoft", "WinGet", "Links"),
            os.path.join(pf, "nodejs"),
            os.path.join(os.environ.get("ProgramData", r"C:\ProgramData"), "chocolatey", "bin"),
            os.path.join(home, "scoop", "shims"),
        ]
        # winget (Gyan.FFmpeg / BtbN) deja ffmpeg en ...\WinGet\Packages\<id>\<versión>\bin
        dirs += sorted(glob.glob(os.path.join(local, "Microsoft", "WinGet", "Packages", "*FFmpeg*", "*", "bin")),
                       reverse=True)
        return dirs
    return ["/usr/local/bin", "/usr/bin"]


def extend_path():
    """Añade al PATH del proceso las carpetas habituales de ffmpeg y node (sin duplicados)."""
    cur = os.environ.get("PATH", "").split(os.pathsep)
    norm = {os.path.normcase(os.path.normpath(p)) for p in cur if p}
    for d in _extra_dirs():
        n = os.path.normcase(os.path.normpath(d)) if d else ""
        if d and n not in norm and os.path.isdir(d):
            cur.append(d)
            norm.add(n)
    os.environ["PATH"] = os.pathsep.join(p for p in cur if p)


def find_ffmpeg():
    return shutil.which("ffmpeg")


def find_node():
    return shutil.which("node")


def tool_opts():
    """Opciones de yt-dlp con las rutas de ffmpeg y node (runtime JS para YouTube)."""
    extend_path()
    o = {"remote_components": {"ejs:github"}}
    node = find_node()
    o["js_runtimes"] = {"node": {"path": node} if node else {}}
    ff = find_ffmpeg()
    if ff:
        o["ffmpeg_location"] = ff
    return o


def max_title_len(out_dir, default=150):
    """En Windows la ruta completa no debe pasar de ~260 caracteres (MAX_PATH)."""
    if not IS_WIN:
        return default
    # " [id].ext" + sufijos temporales (.part, .f137, .temp) ≈ 40 caracteres
    return max(40, min(default, 259 - len(str(out_dir)) - 40))


def open_folder(path):
    path = str(path)
    os.makedirs(path, exist_ok=True)
    if IS_WIN:
        os.startfile(path)  # noqa: S606 — Explorador de archivos
    elif IS_MAC:
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def installed_browsers():
    """Navegadores instalados, en orden de preferencia para leer cookies."""
    if IS_MAC:
        apps = {"brave": "/Applications/Brave Browser.app", "chrome": "/Applications/Google Chrome.app",
                "firefox": "/Applications/Firefox.app", "edge": "/Applications/Microsoft Edge.app"}
        return [n for n, p in apps.items() if os.path.exists(p)] + ["safari"]
    if IS_WIN:
        local = os.environ.get("LOCALAPPDATA", "")
        roam = os.environ.get("APPDATA", "")
        # Firefox primero: yt-dlp no puede descifrar las cookies de Chrome/Edge en Windows
        # (cifrado "App-Bound" desde Chrome 127) y además están bloqueadas mientras el navegador está abierto.
        profiles = {"firefox": os.path.join(roam, "Mozilla", "Firefox", "Profiles"),
                    "brave": os.path.join(local, "BraveSoftware", "Brave-Browser", "User Data"),
                    "edge": os.path.join(local, "Microsoft", "Edge", "User Data"),
                    "chrome": os.path.join(local, "Google", "Chrome", "User Data")}
        return [n for n, p in profiles.items() if os.path.isdir(p)]
    home = os.path.expanduser("~")
    profiles = {"firefox": os.path.join(home, ".mozilla", "firefox"),
                "chrome": os.path.join(home, ".config", "google-chrome"),
                "brave": os.path.join(home, ".config", "BraveSoftware"),
                "edge": os.path.join(home, ".config", "microsoft-edge")}
    return [n for n, p in profiles.items() if os.path.isdir(p)]


def set_app_id():
    """Windows: icono y nombre propios en la barra de tareas (en lugar de los de python.exe)."""
    if IS_WIN:
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("MetAI.Toru")
        except Exception:
            pass


def utf8_console():
    """Evita UnicodeEncodeError (✓, ✗, títulos en japonés…) en consolas de Windows con cp932/cp1252."""
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(errors="replace")
        except Exception:
            pass
