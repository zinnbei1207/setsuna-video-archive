import base64, zlib
from pathlib import Path

for name in ('2026','2025','other'):
    payload = (Path('data') / f'import-{name}.b64').read_text(encoding='utf-8').strip()
    raw = zlib.decompress(base64.b64decode(payload))
    out = Path('data') / f'videos-{name}.json'
    out.write_bytes(raw)
    print(name, out.stat().st_size)
