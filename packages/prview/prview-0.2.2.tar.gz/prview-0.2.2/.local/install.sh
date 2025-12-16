#!/bin/bash
# Install gh-dash-tui

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INSTALL_DIR="$HOME/.local/bin"

echo "Installing gh-dash-tui..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -q rich pyyaml pynput fastapi uvicorn jinja2

# Create install directory
mkdir -p "$INSTALL_DIR"

# Create wrapper script
cat > "$INSTALL_DIR/gh-dash" << EOF
#!/bin/bash
cd "$SCRIPT_DIR"
python3 "$SCRIPT_DIR/gh_dash.py" "\$@"
EOF

chmod +x "$INSTALL_DIR/gh-dash"

echo ""
echo "✓ Installed gh-dash to $INSTALL_DIR/gh-dash"
echo ""
echo "Make sure $INSTALL_DIR is in your PATH:"
echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
echo ""
echo "Usage:"
echo "  gh-dash                 # TUI - run once"
echo "  gh-dash --watch         # TUI - watch mode with keyboard nav"
echo "  gh-dash serve           # Web UI - beautiful dark theme dashboard"
echo "  gh-dash serve -p 3000   # Web UI on custom port"
echo "  gh-dash --help          # Show all options"
echo ""
echo "Config: ~/.config/gh-dash/config.yaml"
echo "Database: ~/.config/gh-dash/gh_dash.db"
