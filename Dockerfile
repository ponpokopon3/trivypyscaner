FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV TRIVY_VERSION=0.64.1

WORKDIR /app

# パッケージリスト更新 + 必須パッケージのインストール
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    tar \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Trivy のダウンロードとインストール
RUN curl -fsSL -o trivy.tar.gz https://github.com/aquasecurity/trivy/releases/download/v${TRIVY_VERSION}/trivy_${TRIVY_VERSION}_Linux-64bit.tar.gz && \
    tar -xzf trivy.tar.gz && \
    mv trivy /usr/local/bin/ && \
    rm trivy.tar.gz

# Pythonスクリプトと設定ファイルをコピー
COPY main.py ./
COPY entrypoint.sh ./
COPY requirements.txt ./

RUN pip install -r requirements.txt

RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
