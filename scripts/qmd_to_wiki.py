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
Normalmente para que la carpeta se cree en la raiz se usa <tmp> = ../_gfm_out

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

# Estructura de la wiki: lista ordenada de secciones, cada una con sus páginas.
# Es la fuente de verdad para nombres, ORDEN y agrupación del _Sidebar.md.
# Cada página es (ruta relativa del .qmd dentro de docs/, nombre de página wiki sin .md).
# Al agregar un .qmd nuevo, añádelo a la sección que le corresponde aquí.
WIKI_STRUCTURE: list[tuple[str, list[tuple[str, str]]]] = [
    ("Inicio", [
        ("index.qmd", "Home"),
        ("00-prd/PRD.qmd", "PRD"),
    ]),
    ("Primeros pasos", [
        ("01-primeros-pasos/requisitos.qmd", "Primeros-pasos-Requisitos"),
        ("01-primeros-pasos/entorno-local.qmd", "Primeros-pasos-Entorno-local"),
        ("01-primeros-pasos/estructura-repo.qmd", "Primeros-pasos-Estructura-del-repositorio"),
    ]),
    ("Diseño del sistema", [
        ("02-diseno-sistema/vision-general.qmd", "Diseno-Vision-general"),
        ("02-diseno-sistema/frontend.qmd", "Diseno-Frontend"),
        ("02-diseno-sistema/backend.qmd", "Diseno-Backend"),
        ("02-diseno-sistema/base-de-datos.qmd", "Diseno-Base-de-datos"),
    ]),
    ("Detalles de implementación", [
        ("03-implementacion/index.qmd", "Implementacion"),
        ("03-implementacion/api-autenticacion.qmd", "Implementacion-API-Autenticacion"),
        ("03-implementacion/api-endpoints.qmd", "Implementacion-API-Endpoints"),
        ("03-implementacion/despliegue-ambientes.qmd", "Implementacion-Despliegue-Ambientes"),
        ("03-implementacion/despliegue-ci-cd.qmd", "Implementacion-Despliegue-CI-CD"),
        ("03-implementacion/despliegue-variables-entorno.qmd", "Implementacion-Despliegue-Variables-de-entorno"),
    ]),
    ("Guías de desarrollo", [
        ("04-guias-desarrollo/convenciones-codigo.qmd", "Desarrollo-Convenciones-de-codigo"),
        ("04-guias-desarrollo/git-workflow.qmd", "Desarrollo-Git-workflow"),
        ("04-guias-desarrollo/testing.qmd", "Desarrollo-Testing"),
        ("04-guias-desarrollo/troubleshooting.qmd", "Desarrollo-Troubleshooting"),
    ]),
    ("Decisiones técnicas (ADRs)", [
        ("05-decisiones-tecnicas/index.qmd", "ADRs"),
        ("05-decisiones-tecnicas/0001-eleccion-de-framework.qmd", "ADR-0001-Eleccion-de-framework"),
        ("05-decisiones-tecnicas/0002-estrategia-de-cache.qmd", "ADR-0002-Estrategia-de-cache"),
    ]),
    ("Changelog", [
        ("06-changelog/index.qmd", "Changelog"),
        ("06-changelog/v0.1.0.qmd", "Changelog-v0.1.0"),
    ]),
]

# Mapeo plano derivado (ruta .qmd -> nombre de página wiki). Se usa para resolver
# enlaces internos y para el bucle de conversión.
PAGE_MAP: dict[str, str] = {
    key: page for _, pages in WIKI_STRUCTURE for key, page in pages
}

# Títulos legibles para el sidebar, por si el .md generado no arranca con un "# ...".
SIDEBAR_LABELS: dict[str, str] = {
    "Home": "Inicio",
    "PRD": "PRD",
    "Primeros-pasos-Requisitos": "Requisitos",
    "Primeros-pasos-Entorno-local": "Entorno local",
    "Primeros-pasos-Estructura-del-repositorio": "Estructura del repositorio",
    "Diseno-Vision-general": "Visión general",
    "Diseno-Frontend": "Frontend",
    "Diseno-Backend": "Backend",
    "Diseno-Base-de-datos": "Base de datos",
    "Implementacion": "Visión general",
    "Implementacion-API-Autenticacion": "API — Autenticación",
    "Implementacion-API-Endpoints": "API — Endpoints",
    "Implementacion-Despliegue-Ambientes": "Despliegue — Ambientes",
    "Implementacion-Despliegue-CI-CD": "Despliegue — CI / CD",
    "Implementacion-Despliegue-Variables-de-entorno": "Despliegue — Variables de entorno",
    "Desarrollo-Convenciones-de-codigo": "Convenciones de código",
    "Desarrollo-Git-workflow": "Git workflow",
    "Desarrollo-Testing": "Testing",
    "Desarrollo-Troubleshooting": "Troubleshooting",
    "ADRs": "Índice de ADRs",
    "ADR-0001-Eleccion-de-framework": "ADR-0001 — Elección de framework",
    "ADR-0002-Estrategia-de-cache": "ADR-0002 — Estrategia de caché",
    "Changelog": "Changelog",
    "Changelog-v0.1.0": "v0.1.0",
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


def sidebar_label(page_name: str) -> str:
    """Título a mostrar en el sidebar: el override de SIDEBAR_LABELS o el propio nombre de página."""
    return SIDEBAR_LABELS.get(page_name, page_name.replace("-", " "))


def write_sidebar() -> Path:
    """Genera wiki-md/_Sidebar.md con las secciones y el orden de WIKI_STRUCTURE."""
    lines: list[str] = []
    for section_title, pages in WIKI_STRUCTURE:
        lines.append(f"### {section_title}")
        lines.append("")
        for _, page_name in pages:
            lines.append(f"- [{sidebar_label(page_name)}]({page_name})")
        lines.append("")
    out_path = WIKI_MD / "_Sidebar.md"
    out_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return out_path


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

    sidebar_path = write_sidebar()
    written.append(sidebar_path.name)

    # Borrar .md huérfanos: páginas que ya no están en PAGE_MAP (p. ej. tras renombrar
    # una carpeta o una página). Se conservan _Sidebar.md y _Footer.md.
    keep = {f"{p}.md" for p in PAGE_MAP.values()} | {"_Sidebar.md", "_Footer.md"}
    removed = []
    for existing in WIKI_MD.glob("*.md"):
        if existing.name not in keep:
            existing.unlink()
            removed.append(existing.name)
    if removed:
        print(f"Eliminados {len(removed)} archivos huérfanos en {WIKI_MD}:")
        for name in removed:
            print(f"  - {name}")

    print(f"Escritos {len(written)} archivos en {WIKI_MD}:")
    for name in written:
        print(f"  - {name}")

    missing = [k for k in PAGE_MAP if not (GFM_DIR / k.replace(".qmd", ".md")).exists()]
    if missing:
        print("AVISO: entradas en PAGE_MAP sin archivo .qmd/.md correspondiente:", missing, file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
