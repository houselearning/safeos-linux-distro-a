FROM debian:bookworm-slim@sha256:99c0b25c46d0214d5a2091092e7908907dcaecd6a962cde0ac700acee222b6f3

ENV DEBIAN_FRONTEND=noninteractive

RUN set -eux; \
    printf '%s\n' \
      'deb http://ftp.debian.org/debian bookworm main non-free-firmware' \
      > /etc/apt/sources.list; \
    rm -f /etc/apt/sources.list.d/*; \
    apt-get update; \
    apt-get install -y --no-install-recommends ca-certificates=20230311+deb12u1; \
    printf '%s\n' \
      'deb [check-valid-until=no] https://snapshot.debian.org/archive/debian/20261031T210000Z/ bookworm main non-free-firmware' \
      'deb [check-valid-until=no] https://snapshot.debian.org/archive/debian/20261031T210000Z/ bookworm-updates main non-free-firmware' \
      'deb [check-valid-until=no] https://snapshot.debian.org/archive/debian-security/20261031T210000Z/ bookworm-security main non-free-firmware' \
      > /etc/apt/sources.list; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
      build-essential=12.9 \
      cpio=2.13+dfsg-7.1 \
      debootstrap=1.0.128+nmu2+deb12u2 \
      git=1:2.39.5-0+deb12u3 \
      live-build=1:20230502 \
      python3=3.11.2-1+b1 \
      python3-yaml=6.0-3+b2 \
      xorriso=1.5.4-4; \
    mkdir -p /usr/share/safeos-builder; \
    dpkg-query -W -f='${binary:Package}=${Version}\n' | sort \
      > /usr/share/safeos-builder/package-versions.txt; \
    rm -rf /var/lib/apt/lists/*

CMD ["bash"]