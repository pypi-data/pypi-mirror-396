#!/bin/bash
# Setup script to install git hooks
#
# Usage: ./scripts/setup-hooks.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HOOKS_DIR="$PROJECT_ROOT/hooks"
GIT_HOOKS_DIR="$PROJECT_ROOT/.git/hooks"

echo "🔧 Setting up git hooks..."

# Check if we're in a git repository
if [ ! -d "$PROJECT_ROOT/.git" ]; then
    echo "❌ Error: Not a git repository. Run this script from the project root."
    exit 1
fi

# Create .git/hooks directory if it doesn't exist
mkdir -p "$GIT_HOOKS_DIR"

# Install pre-commit hook
if [ -f "$HOOKS_DIR/pre-commit" ]; then
    echo "📋 Installing pre-commit hook..."
    cp "$HOOKS_DIR/pre-commit" "$GIT_HOOKS_DIR/pre-commit"
    chmod +x "$GIT_HOOKS_DIR/pre-commit"
    echo "✅ Pre-commit hook installed at .git/hooks/pre-commit"
else
    echo "⚠️  Warning: hooks/pre-commit not found"
fi

# TODO: Add more hooks here as needed (pre-push, commit-msg, etc.)

echo ""
echo "✅ Git hooks setup complete!"
echo ""
echo "The pre-commit hook will now run these checks before each commit:"
echo "  • cargo fmt --check (code formatting)"
echo "  • cargo clippy (linting)"
echo "  • cargo check (build verification)"
echo "  • cargo test --lib (library tests)"
echo "  • cargo test --tests (integration tests)"
echo "  • cargo test --doc (doctests)"
echo ""
echo "To skip the pre-commit hook, use: git commit --no-verify"
