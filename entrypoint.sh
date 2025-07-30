#!/bin/bash
set -e

echo ">>> Starting SBOM generation..."

# 出力先ディレクトリを作成（存在しない場合）
mkdir -p /app/sbom_outputs

# スクリプト実行
python main.py
