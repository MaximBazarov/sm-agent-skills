#!/usr/bin/env bash
#
# Generate reference/API-SURFACE.md from a StateManagement checkout.
#
#   generate-api-surface.sh <library-repo> [ref] [output-file]
#
# Two callers, one script:
#
#   Release      run it in this repo against the library tag the plugin version mirrors,
#                and commit the result.
#   Drift        a skill found the committed anchor disagrees with the consumer's
#                Package.resolved, so it runs this against the resolved version and
#                writes into a git-ignored path in the consumer's repo.
#
# The surface is extracted from the built module, never parsed out of source, so it
# cannot describe a symbol the compiler does not have.

set -euo pipefail

SCRIPTS=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

REPO=$(cd "${1:?usage: generate-api-surface.sh <library-repo> [ref] [output-file]}" && pwd)
REF=${2:-HEAD}
OUT=${3:-"$(dirname "$SCRIPTS")/reference/API-SURFACE.md"}

TARGET_TRIPLE=arm64-apple-macosx12.0
MODULES=(StateManagement StateManagementTestingSupport)

export DEVELOPER_DIR=${DEVELOPER_DIR:-/Applications/Xcode.app/Contents/Developer}
SDK=$(xcrun --sdk macosx --show-sdk-path)

WORK=$(mktemp -d)
CHECKOUT="$WORK/checkout"
GRAPHS="$WORK/graphs"
mkdir -p "$GRAPHS"

# A detached worktree, so generating never disturbs the caller's checkout.
git -C "$REPO" worktree add -q --detach "$CHECKOUT" "$REF"
cleanup() {
    git -C "$REPO" worktree remove --force "$CHECKOUT" 2>/dev/null || true
    rm -rf "$WORK"
}
trap cleanup EXIT

ANCHOR=$(git -C "$CHECKOUT" rev-parse HEAD)
# The tag pointing at the anchor is the release; a commit with no tag says so.
RELEASE=$(git -C "$CHECKOUT" describe --tags --exact-match HEAD 2>/dev/null || echo "untagged (${ANCHOR:0:12})")

echo "Generating API surface" >&2
echo "  repo    $REPO" >&2
echo "  ref     $REF" >&2
echo "  release $RELEASE" >&2
echo "  anchor  $ANCHOR" >&2

cd "$CHECKOUT"
for module in "${MODULES[@]}"; do
    swift build --target "$module" >&2
done

MODULE_DIR="$CHECKOUT/.build/$(basename "$TARGET_TRIPLE" | sed 's/[0-9.]*$//')/debug/Modules"
[ -d "$MODULE_DIR" ] || MODULE_DIR=$(find "$CHECKOUT/.build" -type d -name Modules | head -1)

# Not GROUPS: bash reserves that name for the caller's group IDs.
MODULE_GROUPS=()
for module in "${MODULES[@]}"; do
    swift symbolgraph-extract \
        -module-name "$module" \
        -target "$TARGET_TRIPLE" \
        -sdk "$SDK" \
        -I "$MODULE_DIR" \
        -output-dir "$GRAPHS" \
        -minimum-access-level public >&2

    # Extension graphs are named Module@Other.symbols.json and belong to the same module.
    paths=$(find "$GRAPHS" -name "$module.symbols.json" -o -name "$module@*.symbols.json" \
        | sort | paste -sd, -)
    MODULE_GROUPS+=("$module=$paths")
done

SWIFT_VERSION=$(swift --version 2>/dev/null | head -1)
mkdir -p "$(dirname "$OUT")"
python3 "$SCRIPTS/render_api_surface.py" \
    "$RELEASE" "$ANCHOR" "\`swift symbolgraph-extract\` ($SWIFT_VERSION)" \
    "${MODULE_GROUPS[@]}" > "$OUT"

echo "Wrote $OUT ($(wc -l < "$OUT") lines)" >&2
