#!/bin/bash
# Genera "MetAI Toru.app" apuntando a esta carpeta (icono y nombre propios en el Dock).
set -e
cd "$(dirname "$0")"
D="$(pwd)"
APP="$D/MetAI Toru.app"

# Entorno virtual + dependencias
[ -d .venv ] || python3 -m venv .venv
.venv/bin/pip install -q -U -r requirements.txt

# Icono .icns a partir de assets/icon.png
TMP="$(mktemp -d)"; ICONSET="$TMP/i.iconset"; mkdir -p "$ICONSET"
for s in 16 32 128 256 512; do
  sips -z $s $s assets/icon.png --out "$ICONSET/icon_${s}x${s}.png" >/dev/null
  sips -z $((s*2)) $((s*2)) assets/icon.png --out "$ICONSET/icon_${s}x${s}@2x.png" >/dev/null
done
iconutil -c icns "$ICONSET" -o "$TMP/icon.icns"

rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
cp "$TMP/icon.icns" "$APP/Contents/Resources/icon.icns"

cat > "$APP/Contents/MacOS/MetAIToru" <<LAUNCH
#!/bin/bash
# exec mantiene el proceso asociado a este .app (icono y nombre en el Dock)
export PATH="\$PATH:/opt/homebrew/bin:/opt/homebrew/opt/ffmpeg-full/bin:/usr/local/bin"
exec "$D/.venv/bin/python" "$D/gui.py"
LAUNCH
chmod +x "$APP/Contents/MacOS/MetAIToru"

cat > "$APP/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleExecutable</key><string>MetAIToru</string>
<key>CFBundleIdentifier</key><string>jp.met-ai.toru</string>
<key>CFBundleName</key><string>MetAI Toru</string>
<key>CFBundleDisplayName</key><string>MetAI Toru</string>
<key>CFBundleIconFile</key><string>icon</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>CFBundleShortVersionString</key><string>1.0</string>
<key>CFBundleVersion</key><string>1</string>
<key>LSMinimumSystemVersion</key><string>11.0</string>
<key>NSHighResolutionCapable</key><true/>
</dict></plist>
PLIST

codesign --force --deep -s - "$APP" >/dev/null 2>&1 || true
rm -rf "$TMP"
echo "✓ $APP"
