#!/usr/bin/env python3
"""
Convierte los .qmd de docs/ a los .md planos que consume la GitHub Wiki
(carpeta wiki-md/), preservando el mapeo de nombres ya usado en el repo y
reescribiendo los enlaces internos a formato [[Pagina-Wiki]].

Uso:
    python3 scripts/qmd_to_wiki.py

Requiere que ya se haya corrido:
    quarto render docs --to gfm --output-dir <tmp>
y que ese <tmp> se pase por la env var QUARTO_GFM_DIR (ver workflow).
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_SRC = REPO_ROOT / "docs"
WIKI_MD = REPO_ROOT / "wiki-md"
GFM_DIR = Path(os.environ.get("QUARTO_GFM_DIR", REPO_ROOT / "_gfm_out"))

# Mapeo explícito: ruta relativa del .qmd (dentro de docs/) -> nombre de página de wiki (sin .md)
# Este mapeo es la fuente de verdad para nombres/orden; añade una entrada aquí
# cada vez que agregues un .qmd nuevo.
PAGE_MAP: dict[str, str] = {
    "index.qmd": "Home",
    "01-primeros-pasos/requisitos.qmd": "Primeros-pasos-Requisitos",
    "01-primeros-pasos/entorno-local.qmd": "Primeros-pasos-Entorno-local",
    "01-primeros-pasos/estructura-repo.qmd": "Primeros-pasos-Estructura-del-repositorio",
    "02-arquitectura/vision-general.qmd": "Arquitectura-Vision-general",
    "02-arquitectura/frontend.qmd": "Arquitectura-Frontend",
    "02-arquitectura/backend.qmd": "Arquitectura-Backend",
    "02-arquitectura/base-de-datos.qmd": "Arquitectura-Base-de-datos",
    "03-guias-desarrollo/convenciones-codigo.qmd": "Desarrollo-Convenciones-de-codigo",
    "03-guias-desarrollo/git-workflow.qmd": "Desarrollo-Git-workflow",
    "03-guias-desarrollo/testing.qmd": "Desarrollo-Testing",
    "03-guias-desarrollo/troubleshooting.qmd": "Desarrollo-Troubleshooting",
    "04-api/autenticacion.qmd": "API-Autenticacion",
    "04-api/endpoints.qmd": "API-Endpoints",
    "05-despliegue/ambientes.qmd": "Despliegue-Ambientes",
    "05-despliegue/ci-cd.qmd": "Despliegue-CI-CD",
    "05-despliegue/variables-entorno.qmd": "Despliegue-Variables-de-entorno",
    "06-decisiones-tecnicas/index.qmd": "ADRs",
    "06-decisiones-tecnicas/0001-eleccion-de-framework.qmd": "ADR-0001-Eleccion-de-framework",
    "06-decisiones-tecnicas/0002-estrategia-de-cache.qmd": "ADR-0002-Estrategia-de-cache",
    "changelog/index.qmd": "Changelog",
    "changelog/v0.1.0.qmd": "Changelog-v0.1.0",
}

TITLE_RE = re.compile(r'^title:\s*"?(.*?)"?\s*$', re.MULTILINE)
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
# Enlaces markdown a otro .qmd, p.ej. [texto](../04-api/endpoints.qmd) o (endpoints.qmd) o (endpoints.md tras render)
MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+?\.(?:qmd|md))\)")


def qmd_key_from_gfm_path(gfm_path: Path) -> str:
    rel = gfm_path.relative_to(GFM_DIR).with_suffix(".qmd")
    return rel.as_posix()


def resolve_link_target(current_key: str, target: str) -> str | None:
    """Resuelve un href relativo (a un .qmd) contra PAGE_MAP y devuelve el nombre de página wiki."""
    target = target.split("#")[0]
    if not target:
        return None
    current_dir = Path(current_key).parent
    candidate = (current_dir / target).as_posix()
    candidate = os.path.normpath(candidate).replace("\\", "/")
    candidate = re.sub(r"\.md$", ".qmd", candidate)
    return PAGE_MAP.get(candidate)


def rewrite_links(content: str, current_key: str) -> str:
    def _replace(m: re.Match) -> str:
        text, target = m.group(1), m.group(2)
        page = resolve_link_target(current_key, target)
        if page is None:
            return m.group(0)
        return f"[[{text}|{page}]]"

    return MD_LINK_RE.sub(_replace, content)


def strip_frontmatter_to_h1(content: str) -> str:
    m = FRONTMATTER_RE.match(content)
    if not m:
        return content
    fm = m.group(1)
    title_m = TITLE_RE.search(fm)
    body = content[m.end():].lstrip("\n")
    if title_m:
        return f"# {title_m.group(1)}\n\n{body}"
    return body


def main() -> int:
    if not GFM_DIR.exists():
        print(f"ERROR: no existe el directorio de salida gfm: {GFM_DIR}", file=sys.stderr)
        return 1

    gfm_files = sorted(GFM_DIR.rglob("*.md"))
    if not gfm_files:
        print(f"ERROR: no se encontraron .md en {GFM_DIR} (¿corriste quarto render --to gfm?)", file=sys.stderr)
        return 1

    WIKI_MD.mkdir(exist_ok=True)
    written = []

    for gfm_file in gfm_files:
        key = qmd_key_from_gfm_path(gfm_file)
        page_name = PAGE_MAP.get(key)
        if page_name is None:
            print(f"AVISO: {key} no está en PAGE_MAP, se omite (agrégalo en scripts/qmd_to_wiki.py)")
            continue

        content = gfm_file.read_text(encoding="utf-8")
        content = strip_frontmatter_to_h1(content)
        content = rewrite_links(content, key)

        out_path = WIKI_MD / f"{page_name}.md"
        out_path.write_text(content, encoding="utf-8")
        written.append(out_path.name)

    print(f"Escritos {len(written)} archivos en {WIKI_MD}:")
    for name in written:
        print(f"  - {name}")

    missing = [k for k in PAGE_MAP if not (GFM_DIR / k.replace(".qmd", ".md")).exists()]
    if missing:
        print("AVISO: entradas en PAGE_MAP sin archivo .qmd/.md correspondiente:", missing, file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
