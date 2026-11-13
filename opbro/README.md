# OPBro Remoto — configuración de cliente personalizado

Este directorio contiene la configuración pre-cargada (y firmada) que va
embebida en cada variante del cliente:

| Archivo | Variante | Efecto |
|---|---|---|
| `custom-client.txt` | Cliente | Solo conexiones entrantes, configuración bloqueada, servidor fijado |
| `custom-admin.txt` | Administrador | Solo saliente (visor), servidor fijado, UI normal |

Ambos se leen automáticamente en el arranque desde:

- **Windows portable**: se extraen junto al `.exe` (mismo directorio del ejecutable interno).
- **macOS**: `OPBro-Remoto.app/Contents/Resources/custom.txt`.

## Regenerar (cuando exista el servidor hbbs/hbbr)

1. Instalar PyNaCl: `pip3 install --user pynacl`
2. Ejecutar desde la raíz del repo:

   ```bash
   python3 opbro/gen_custom.py \
       --server TU_SERVIDOR_HBBS \
       --relay TU_SERVIDOR_HBBR \
       --hbbs-key "CONTENIDO_DE_id_ed25519.pub"
   ```

3. `--key` por defecto apunta a `../../opbro-keys/custom_signing.key`
   (semilla Ed25519 privada, guardada **fuera** del repo). Nunca subas esa
   clave a GitHub.

4. Volver a lanzar el build en GitHub Actions para regenerar los instalables
   portables.

## Firmado

El binario verifica la firma con la clave pública embebida en
`src/common.rs` (`const KEY`). Formato: `base64(firma_ed25519(64 bytes) || json)`.
