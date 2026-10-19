"""Goya 58: project PDFs and final-delivery sheets -> page images for the /goya58/ page.

Writes <plain folder>/docs/<set>_<nn>.jpg (long side 2000 px, for the full-screen viewer)
and <set>_<nn>_t.jpg (thumbnail, long side 480 px). The lock script publishes docs/ encrypted.

    py -3 scripts/goya58_docs.py "D:/OneDrive/Escritorio/goya58-web"
"""
import io
import os
import sys

import fitz
from PIL import Image

SRC = r'J:\My Drive\00_Proyectos\01_seordezero\2026.03_OSCAR RODRIGUEZ'
FINAL = os.path.join(SRC, '20261008_ENTREGA FINAL')
PDFS = {  # set id -> pdf
    'techo': r'PRINTS\Page 1.pdf',
    'elev1': r'PRINTS\ELEVACION DORMITORIO.pdf',
    'elev2': r'PRINTS\20260324_ELEVACION DORMITORIO.pdf',
    'lev': r'PRINTS\20260415_DEPARTAMENTO GOYA 58 LEVANTAMIENTO.pdf',
    'rev1': r'20240415_Entrega(1RA REVISION).pdf',
    'rev2': r'20240422_Entrega(2DA REVISION).pdf',
    'opc': r'GOYA58_mobiliario_opciones.pdf',
}
ROOMS = ['ENTRADA', 'COMEDOR', 'SALÓN', 'SALÓN 2', 'DESPACHO', 'DORMITORIO']
FILES = {  # set id -> images of the final delivery, in room order
    'fichas': [os.path.join(FINAL, '00_SWATCHES', f'KEY_{r}.jpg') for r in ROOMS],
    'id': [os.path.join(FINAL, '01_VISTAS ID', f'{r}_ID.png') for r in ROOMS],
    'render': [os.path.join(FINAL, '02_VISTAS RENDER', f'{r}_RENDER.png') for r in ROOMS],
}


def save(im, out, name):
    im = im.convert('RGB')
    for suffix, side, q in (('', 2000, 84), ('_t', 480, 78)):
        c = im.copy()
        c.thumbnail((side, side), Image.LANCZOS)
        c.save(os.path.join(out, f'{name}{suffix}.jpg'), quality=q, optimize=True, progressive=True)


def main(plain):
    out = os.path.join(plain, 'docs')
    os.makedirs(out, exist_ok=True)
    for sid, rel in PDFS.items():
        doc = fitz.open(os.path.join(SRC, rel))
        for i, page in enumerate(doc, 1):
            z = 2000 / max(page.rect.width, page.rect.height)
            pix = page.get_pixmap(matrix=fitz.Matrix(z, z), alpha=False)
            save(Image.open(io.BytesIO(pix.tobytes('png'))), out, f'{sid}_{i:02d}')
        print(sid, len(doc))
    for sid, files in FILES.items():
        for i, f in enumerate(files, 1):
            save(Image.open(f), out, f'{sid}_{i:02d}')
        print(sid, len(files))


if __name__ == '__main__':
    main(sys.argv[1])
