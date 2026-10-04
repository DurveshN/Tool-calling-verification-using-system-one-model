#!/usr/bin/env bash
# Provision an Ubuntu 24.04 host for the main run (Docker + uv + Harbor 0.23.0 + Node 22 + dataset).
# Usage on the VM: bash setup_vm.sh  (then place .env in the repo root with chmod 600)
set -euo pipefail
REPO_URL="${REPO_URL:-https://github.com/DurveshN/Tool-calling-verification-using-system-one-model.git}"
REPO_DIR="${REPO_DIR:-$HOME/prototype}"
EXPECTED_DATASET_SHA="561f0e327c7d79eb3be1859b8d35727fb4a7e5648d5b657026a3e317fd3937f1"

sudo apt-get update -qq
sudo apt-get install -y -qq docker.io docker-compose-v2 git python3 curl ca-certificates >/dev/null
sudo usermod -aG docker "$USER"
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash - >/dev/null
sudo apt-get install -y -qq nodejs >/dev/null

curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null
export PATH="$HOME/.local/bin:$PATH"
uv tool install "harbor==0.23.0" >/dev/null

[ -d "$REPO_DIR/.git" ] || git clone -q "$REPO_URL" "$REPO_DIR"

mkdir -p "$HOME/datasets"
[ -d "$HOME/datasets/terminal-bench" ] || (cd "$HOME/datasets" && sg docker -c "harbor datasets download terminal-bench@2.0 -o $HOME/datasets" >/dev/null)
SHA=$(cd "$HOME/datasets" && find terminal-bench -type f | sort | xargs -d '\n' sha256sum | sha256sum | cut -d' ' -f1)
echo "dataset sha256: $SHA"
[ "$SHA" = "$EXPECTED_DATASET_SHA" ] || { echo "DATASET HASH MISMATCH (expected $EXPECTED_DATASET_SHA)" >&2; exit 4; }

echo "harbor: $(harbor --version)  node: $(node --version)  docker: $(docker --version)"
echo "setup ok. Next: put .env in $REPO_DIR (chmod 600), re-login for docker group."
