#!/usr/bin/env python3
"""Genera los custom.txt firmados de OPBro Remoto.

El binario (ver src/common.rs, read_custom_client) exige que custom.txt sea
base64(mensaje Ed25519 firmado) donde el mensaje es el JSON de configuracion.
La clave publica de verificacion esta embebida en src/common.rs (const KEY).

Uso:
    python3 opbro/gen_custom.py [--key RUTA_SEED] [--server hbbs.x] [--relay hbbr.x] [--hbbs-key B64]

Por defecto usa la clave privada en ../../opbro-keys/custom_signing.key (fuera
del repo, NO commitear nunca). Genera opbro/custom-client.txt y
opbro/custom-admin.txt.
"""

import argparse
import base64
import json
import os
import sys

from nacl.signing import SigningKey

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_KEY = os.path.normpath(
    os.path.join(HERE, "..", "..", "opbro-keys", "custom_signing.key")
)

# Clave publica de hbbs (id_ed25519.pub). Mientras no exista el servidor se usa
# una clave vacia valida (32 bytes cero): las conexiones fallaran hasta
# reemplazarla por la real y regenerar los custom.txt.
PLACEHOLDER_HBBS_KEY = base64.b64encode(bytes(32)).decode()


def sign_payload(payload: dict, seed_path: str) -> str:
    with open(seed_path) as f:
        seed = bytes.fromhex(f.read().strip())
    sk = SigningKey(seed)
    msg = json.dumps(payload, separators=(",", ":")).encode()
    signed = bytes(sk.sign(msg))  # formato de libsodium: firma(64) || mensaje
    return base64.b64encode(signed).decode()


def build_payloads(server: str, relay: str, hbbs_key: str) -> dict:
    override = {
        "custom-rendezvous-server": server,
        "relay-server": relay,
        "key": hbbs_key,
    }
    # Cliente: solo conexiones entrantes, configuracion bloqueada.
    cliente = {
        "app-name": "OPBro-Remoto",
        "override-settings": override,
        "default-settings": {
            "hide-server-settings": "Y",
            "hide-network-settings": "Y",
            "hide-proxy-settings": "Y",
            "hide-websocket-settings": "Y",
            "hide-stop-service": "Y",
        },
        "conn-type": "incoming",
        "disable-settings": "Y",
        "disable-ab": "Y",
        "disable-account": "Y",
    }
    # Administrador: solo saliente (visor), sin paneles de servicio/entrante.
    admin = {
        "app-name": "OPBro-Remoto-Admin",
        "override-settings": override,
        "default-settings": {
            "hide-server-settings": "Y",
        },
        "conn-type": "outgoing",
    }
    return {"client": cliente, "admin": admin}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", default=os.environ.get("OPBRO_SIGNING_KEY", DEFAULT_KEY))
    ap.add_argument("--server", default="hbbs.opbro.cl")
    ap.add_argument("--relay", default="hbbr.opbro.cl")
    ap.add_argument("--hbbs-key", default=PLACEHOLDER_HBBS_KEY)
    args = ap.parse_args()

    if not os.path.exists(args.key):
        print(f"ERROR: no existe la clave privada: {args.key}", file=sys.stderr)
        return 1

    payloads = build_payloads(args.server, args.relay, args.hbbs_key)
    for name, payload in payloads.items():
        out = os.path.join(HERE, f"custom-{name}.txt")
        with open(out, "w") as f:
            f.write(sign_payload(payload, args.key))
        print(f"escrito {out}")

    vk = SigningKey(bytes.fromhex(open(args.key).read().strip())).verify_key
    print(f"clave publica (va en src/common.rs KEY): "
          f"{base64.b64encode(bytes(vk)).decode()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
