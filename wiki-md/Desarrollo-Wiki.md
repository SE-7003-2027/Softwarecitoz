# Forma de agregar contenido en wiki


Esta guía explica cómo agregar o modificar documentación para que se
publique correctamente en la GitHub Wiki del repositorio.

[Funcionamiento general](#funcionamiento) [Modificar una página
existente](#caso_1) [Agregar un archivo en una sección
existente](#caso_2) [Crear una nueva sección](#caso_3)

## Cómo funciona la publicación

#### funcionamiento

La documentación **se escribe en `docs/`** como archivos `.qmd`
(Quarto). La wiki se genera de forma automática; **nunca se edita a
mano**, es decir, nunca tocar la carpeta `wiki-md/`.

Un flujo es disparado por GitHub Actions
(`.github/workflows/publish-wiki.yml`) en cada `push` a `main` que toque
`docs/**` o `scripts/qmd_to_wiki.py`:

1.  `quarto render docs --to gfm` convierte los `.qmd` a Markdown plano
    (GFM) en un directorio temporal (`_gfm_out/`).
2.  `scripts/qmd_to_wiki.py` toma esos `.md`, los renombra al nombre de
    página que usa la wiki, reescribe los enlaces internos a formato
    `[[Texto|Pagina-Wiki]]`, regenera `wiki-md/_Sidebar.md` y borra las
    páginas huérfanas o a las que no se les hace referencia.
3.  El workflow commitea `wiki-md/` de vuelta en el repo
    (`docs: sincronizar wiki-md desde docs [skip ci]`) y luego hace push
    del contenido de `wiki-md/` al repositorio `.wiki`.

Reglas:

- **Nunca toques `wiki-md/`.** Es salida generada. Cualquier cambio
  manual ahí lo sobreescribe el bot en el siguiente push a `main`.
- **Nunca edites la wiki desde la interfaz de GitHub.** El siguiente
  sync lo revierte.
- Los cambios **solo aparecen en la wiki tras hacer merge a `main`**. En
  una rama de feature no se publica nada.
- El nombre del archivo `.qmd` **no** es el nombre de la página en la
  wiki. El mapeo vive en `scripts/qmd_to_wiki.py` (constante
  `WIKI_STRUCTURE`). Es decir en el script es donde defines el nombre de
  tu archivo en la wiki

## Correrlo de forma local antes de un push

Desde la raíz del repo:

``` bash
quarto render docs --to gfm --output-dir ../_gfm_out
QUARTO_GFM_DIR=_gfm_out python3 scripts/qmd_to_wiki.py
```

Inspecciona el `git diff` de `wiki-md/` para ver cómo quedará la wiki,
pero **no commitees `wiki-md/`** (lo hace Actions). Si solo querías
validar, descarta esos cambios: `git checkout -- wiki-md/`.

------------------------------------------------------------------------

## Caso 1: modificar un archivo existente

#### caso_1

El caso más simple.

1.  Edita el `.qmd` correspondiente en `docs/`.
2.  Si agregas enlaces a otras páginas de la documentación, usa rutas
    relativas al `.qmd` destino, ejemplo: `[[Testing|Desarrollo-Testing]]` o
    `[[Requisitos|Primeros-pasos-Requisitos]]`. El script los
    convierte a `[[...]]` automáticamente. Enlaces a `.qmd` que no estén
    en el mapeo se dejan tal cual (quedarán rotos en la wiki).
3.  **No** hay que tocar `_quarto.yml` ni `scripts/qmd_to_wiki.py`.
4.  Verifica localmente (sección anterior), abre PR, y al hacer merge a
    `main` se publica.

------------------------------------------------------------------------

## Caso 2: agregar un archivo nuevo en una sección existente

#### caso_2

Ejemplo: agregar `docs/04-guias-desarrollo/nueva-guia.qmd`.

1.  **Crea el `.qmd`** con front matter (un estilo) mínimo:

    ``` markdown
    ---
    title: "Nombre visible de la página"
    ---

    Contenido en md...
    ```

2.  **Regístralo en `scripts/qmd_to_wiki.py`.** En `WIKI_STRUCTURE`,
    dentro de la sección que corresponde, añade una tupla
    `("ruta/relativa/dentro-de-docs.qmd", "Nombre-De-Pagina-Wiki")`:

    ``` python
    ("Guías de desarrollo", [
        ("04-guias-desarrollo/convenciones-codigo.qmd", "Desarrollo-Convenciones-de-codigo"),
        ("04-guias-desarrollo/git-workflow.qmd", "Desarrollo-Git-workflow"),
        ("04-guias-desarrollo/nueva-guia.qmd", "Desarrollo-Nueva-guia"),  # <- nueva
        ...
    ]),
    ```

    Convención del nombre de página: prefijo de la sección + guiones,
    sin espacios ni acentos (mira los ejemplos que ya son parte de la
    wiki).

3.  *(Opcional)* Si el título auto-derivado no te gusta para el sidebar,
    añade una entrada en `SIDEBAR_LABELS` con la clave = nombre de
    página wiki.

4.  PR → merge a `main` → publicado.

------------------------------------------------------------------------

## Caso 3: agregar una sección nueva (carpeta nueva)

#### caso_3

Ejemplo: crear `docs/08-operacion/`.

1.  **Crea la carpeta y su `index.qmd` (obligatorio).** Toda sección
    nueva debe tener `index.qmd`; es la página de entrada de la sección.

        docs/08-operacion/
        ├── index.qmd        <- obligatorio
        ├── runbooks.qmd
        └── monitoreo.qmd

    El `index.qmd` puede usar un bloque `listing:` para auto-listar las
    páginas de la carpeta (mira `docs/03-implementacion/index.qmd` o
    `docs/07-spikes/index.qmd` como referencia).

2.  **Agrega la sección completa a `WIKI_STRUCTURE` en
    `scripts/qmd_to_wiki.py`**, respetando el orden en que quieres que
    aparezca en el `_Sidebar.md` (el orden de la lista = orden en la
    wiki):

    ``` python
    ("Operación", [
        ("08-operacion/index.qmd", "Operacion"),
        ("08-operacion/runbooks.qmd", "Operacion-Runbooks"),
        ("08-operacion/monitoreo.qmd", "Operacion-Monitoreo"),
    ]),
    ```

3.  **Añade los `SIDEBAR_LABELS`** para las páginas nuevas si quieres
    títulos legibles distintos al nombre de página.

4.  **Actualiza `docs/_quarto.yml`** para el sitio HTML:

    - En `website.sidebar.contents`, agrega la sección:

      ``` yaml
      - section: "Operación"
        contents: "08-operacion/*.qmd"
      ```

    - *(Opcional)* En `website.navbar.left`, agrega un enlace a
      `08-operacion/index.qmd` si quieres que salga en la barra
      superior.

5.  PR → merge a `main` → publicado.

------------------------------------------------------------------------

## Renombrar o borrar páginas / carpetas

- **Renombrar**: cambia la ruta y/o el nombre de página en
  `WIKI_STRUCTURE` (y en `_quarto.yml` si aplica). El script borra
  automáticamente el `.md` viejo de `wiki-md/` por quedar huérfano.
  **Ojo**: la GitHub Wiki no maneja redirects; los enlaces externos a la
  página vieja quedarán rotos.

> La última parte es muy importante, pues si cambias de nombre un
> archivo todas sus referencias quedarán, por tanto, trata de no cambiar
> el nombre de archivos

- **Borrar**: elimina el `.qmd`, quita su entrada de `WIKI_STRUCTURE`,
  `SIDEBAR_LABELS` y `_quarto.yml`. El `.md` correspondiente se elimina
  en el siguiente sync.

## Checklist rápido

| Acción | `.qmd` en `docs/` | `qmd_to_wiki.py` | `_quarto.yml` | `wiki-md/` |
|----|----|----|----|----|
| Modificar archivo | editar | — | — | no tocar |
| Archivo nuevo (sección existente) | crear | agregar a `WIKI_STRUCTURE` (+ `SIDEBAR_LABELS` opc.) | solo si la sección usa lista explícita | no tocar |
| Sección nueva (carpeta) | crear carpeta + `index.qmd` obligatorio | agregar sección a `WIKI_STRUCTURE` (+ `SIDEBAR_LABELS`) | agregar `section` en sidebar (+ navbar opc.) | no tocar |
| Renombrar / borrar | mover / borrar `.qmd` | actualizar / quitar entradas | actualizar / quitar entradas | no tocar (se limpia solo) |
