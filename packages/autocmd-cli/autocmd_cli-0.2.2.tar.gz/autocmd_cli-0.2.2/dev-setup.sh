#!/bin/bash
# Development setup for autocmd

AUTOCMD_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Setting up autocmd development environment..."

# Detect user's shell (not the script's shell)
USER_SHELL=$(basename "$SHELL")

if [[ "$USER_SHELL" == "zsh" ]]; then
    RC_FILE="$HOME/.zshrc"
    ALIAS_CMD="alias autocmd-dev='f() { if [[ \"\$1\" == \"--reset\" ]]; then uv run $AUTOCMD_DIR/src/autocmd_cli/__init__.py --reset; return; fi; local cmd=\$(uv run $AUTOCMD_DIR/src/autocmd_cli/__init__.py \"\$@\"); if [ -n \"\$cmd\" ]; then print -z \"\$cmd\"; fi }; f'"
elif [[ "$USER_SHELL" == "bash" ]]; then
    RC_FILE="$HOME/.bashrc"
    if [[ ! -f "$RC_FILE" ]]; then
        RC_FILE="$HOME/.bash_profile"
    fi
    ALIAS_CMD="alias autocmd-dev='f() { if [[ \"\$1\" == \"--reset\" ]]; then uv run $AUTOCMD_DIR/src/autocmd_cli/__init__.py --reset; return; fi; local cmd=\$(uv run $AUTOCMD_DIR/src/autocmd_cli/__init__.py \"\$@\"); if [ -n \"\$cmd\" ]; then READLINE_LINE=\"\$cmd\"; READLINE_POINT=\${#READLINE_LINE}; fi }; f'"
else
    echo "Unsupported shell: $USER_SHELL. Please use zsh or bash."
    exit 1
fi

# Check if alias already exists
if grep -q "alias autocmd-dev=" "$RC_FILE" 2>/dev/null; then
    echo "✓ autocmd-dev alias already exists in $RC_FILE"
else
    echo "" >> "$RC_FILE"
    echo "# autocmd development alias" >> "$RC_FILE"
    echo "$ALIAS_CMD" >> "$RC_FILE"
    echo "✓ Added autocmd-dev alias to $RC_FILE"
fi

echo ""
echo "Setup complete! Run:"
echo "  source $RC_FILE"
echo ""
echo "Then use 'autocmd-dev' for development (always uses latest code):"
echo "  autocmd-dev \"check git status\""
