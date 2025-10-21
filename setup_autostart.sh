#!/usr/bin/env bash
set -e

# --- Configuration ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LAUNCHER_PATH="$SCRIPT_DIR/server_launcher.py"
SERVICE_NAME="server-launcher"
USER_NAME=$(whoami)

echo "Installing auto-start for $SERVICE_NAME"
echo "Detected OS: $(uname -s)"

OS_TYPE=$(uname -s)

# --- Linux (systemd user service) ---
if [[ "$OS_TYPE" == "Linux" ]]; then
    mkdir -p ~/.config/systemd/user/

    SERVICE_FILE=~/.config/systemd/user/$SERVICE_NAME.service
    cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=Local Server Launcher for your Firefox extension

[Service]
ExecStart=/usr/bin/env python3 $LAUNCHER_PATH
Restart=always
WorkingDirectory=$SCRIPT_DIR

[Install]
WantedBy=default.target
EOF

    echo "Created systemd service at $SERVICE_FILE"

    systemctl --user daemon-reload
    systemctl --user enable "$SERVICE_NAME"
    systemctl --user start "$SERVICE_NAME"

    echo "✅ Linux setup done. Service enabled and started."
    systemctl --user status "$SERVICE_NAME" --no-pager

# --- macOS (LaunchAgent) ---
elif [[ "$OS_TYPE" == "Darwin" ]]; then
    mkdir -p ~/Library/LaunchAgents/
    PLIST=~/Library/LaunchAgents/com.${USER_NAME}.${SERVICE_NAME}.plist

    cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" \
"http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.${USER_NAME}.${SERVICE_NAME}</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/env</string>
        <string>python3</string>
        <string>$LAUNCHER_PATH</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>WorkingDirectory</key>
    <string>$SCRIPT_DIR</string>
    <key>StandardOutPath</key>
    <string>$SCRIPT_DIR/server_launcher.log</string>
    <key>StandardErrorPath</key>
    <string>$SCRIPT_DIR/server_launcher.err</string>
</dict>
</plist>
EOF

    echo "Created LaunchAgent at $PLIST"
    launchctl unload "$PLIST" 2>/dev/null || true
    launchctl load "$PLIST"

    echo "✅ macOS setup done. The service will start automatically at login."

# --- Windows (via PowerShell autostart registry) ---
elif [[ "$OS_TYPE" == "MINGW"* || "$OS_TYPE" == "CYGWIN"* || "$OS_TYPE" == "MSYS"* ]]; then
    # Detect Windows via Git Bash / WSL
    echo "Windows detected. Creating autostart via PowerShell registry entry..."
    powershell.exe -Command "
        \$WScript = [System.Environment]::GetFolderPath('Startup')
        \$Shortcut = Join-Path \$WScript 'server-launcher.lnk'
        \$Target = 'pythonw.exe'
        \$Args = '\"$LAUNCHER_PATH\"'
        \$WshShell = New-Object -ComObject WScript.Shell
        \$ShortcutFile = \$WshShell.CreateShortcut(\$Shortcut)
        \$ShortcutFile.TargetPath = \$Target
        \$ShortcutFile.Arguments = \$Args
        \$ShortcutFile.WorkingDirectory = '$SCRIPT_DIR'
        \$ShortcutFile.Save()
    "
    echo "✅ Windows setup done. Shortcut created in Startup folder."

else
    echo "❌ Unsupported OS: $OS_TYPE"
    exit 1
fi

echo "✅ Auto-start installation complete!"
