FROM thuonghai2711/ubuntu-novnc-pulseaudio:22.04

USER root

ENV DEBIAN_FRONTEND=noninteractive \
    PORT=10000 \
    AUDIO_PORT=1699 \
    WEBSOCKIFY_PORT=6900 \
    VNC_PORT=5900 \
    SCREEN_WIDTH=1024 \
    SCREEN_HEIGHT=768 \
    SCREEN_DEPTH=24

RUN apt-get update && \
    apt-get purge -y firefox* || true && \
    apt-get install -y --no-install-recommends \
        wget \
        ca-certificates \
        gdebi-core && \
    wget -q -O /tmp/chrome.deb \
        https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    gdebi -n /tmp/chrome.deb && \
    rm -f /tmp/chrome.deb && \
    mkdir -p /home/ubuntu/.local/share && \
    chown -R ubuntu:ubuntu /home/ubuntu && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER ubuntu
WORKDIR /home/ubuntu

EXPOSE 10000 5900 6900 1699

CMD ["/opt/bin/entry_point.sh"]
