#!/bin/sh
# build_lci.sh — compila e instala el runtime LOLCODE de referencia (lci)
# en un host limpio, sin sudo, para que los e2e de este repo puedan correr.
#
#   sh tools/build_lci.sh            # v1.3  (la referencia documentada)
#   sh tools/build_lci.sh --master   # master (2026-10-31: v0.11.2)
#
# Destino: ~/.local/bin/lci (sobrevive reinicios; NO es parte del repo:
# este repo no distribuye ningun intérprete, solo este script de build).
# Requiere: git, cmake, make, c++. Sin cmake 3.31+ el script rebaja
# cmake_minimum_required en su copia local de trabajo (workaround medido
# el 2026-10-31 en Ubuntu 24.04 con cmake 3.28.3).
set -eu

REF="v1.3"
if [ "${1:-}" = "--master" ]; then
    REF="master"
elif [ -n "${1:-}" ]; then
    echo "uso: sh tools/build_lci.sh [--master]" >&2
    exit 2
fi

PREFIX="${HOME}/.local/bin"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/lci-build-XXXXXX")"
SRC="https://github.com/justinmeza/lci"

trap 'rm -rf "$WORK"' EXIT

echo "== lci desde ${SRC} rama ${REF}"
git clone --quiet --depth 1 --branch "$REF" -c advice.detachedHead=false "$SRC" "$WORK/lci"
cd "$WORK/lci"

CMAKE_MAJ="$(cmake --version | head -1 | sed 's/.* \([0-9]*\)\..*/\1/')"
CMAKE_MIN="$(sed -n 's/^cmake_minimum_required(VERSION \([0-9.]*\)).*/\1/p' CMakeLists.txt)"
echo "== cmake del host: $(cmake --version | head -1) (el proyecto pide ${CMAKE_MIN})"
case "$CMAKE_MAJ" in
    3)
        HOST_MINOR="$(cmake --version | head -1 | sed 's/.* 3\.\([0-9]*\).*/\1/')"
        NEED_MINOR="$(printf '%s' "$CMAKE_MIN" | sed 's/3\.\([0-9]*\).*/\1/')"
        if [ "$HOST_MINOR" -lt "$NEED_MINOR" ]; then
            echo "== workaround: cmake_minimum_required -> 3.${HOST_MINOR} en la copia local"
            sed -i "s/^cmake_minimum_required(VERSION .*)/cmake_minimum_required(VERSION 3.${HOST_MINOR})/" CMakeLists.txt
        fi
        ;;
esac

mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release > "$WORK/cmake.log" 2>&1 || {
    echo "cmake falto; log:" >&2; cat "$WORK/cmake.log" >&2; exit 1; }
make -j"$(nproc)" > "$WORK/make.log" 2>&1 || {
    echo "make falto; log:" >&2; tail -20 "$WORK/make.log" >&2; exit 1; }

mkdir -p "$PREFIX"
cp lci "$PREFIX/lci"
chmod +x "$PREFIX/lci"

printf 'HAI 1.2\n  VISIBLE "lci ok"\nKTHXBYE\n' > "$WORK/smoke.lol"
OUT="$("$PREFIX/lci" "$WORK/smoke.lol")"
echo "== instalado: $("$PREFIX/lci" --version 2>&1 | head -1)"
echo "== smoke: $OUT"
[ "$OUT" = "lci ok" ] || { echo "smoke fallto" >&2; exit 1; }
echo "== listo: $PREFIX/lci"
