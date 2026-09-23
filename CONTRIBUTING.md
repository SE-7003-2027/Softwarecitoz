# Guía de contribución - Chaos

¡Gracias por contribuir a **Chaos**, el matcher de partidas para videojuegos y
juegos de mesa! Este documento explica cómo está organizado el trabajo del
equipo, qué se espera de cada contribución, y contiene **todas las
plantillas del proyecto** listas para copiar a su archivo correspondiente.

Para instalación, stack y cómo levantar el proyecto localmente, ver el
[README](README.md).

---

## Índice

1. [Cómo reportar un bug](#cómo-reportar-un-bug)
2. [Cómo proponer una feature](#cómo-proponer-una-feature)
3. [Cómo reportar documentación desactualizada](#cómo-reportar-documentación-desactualizada)
4. [Buenas prácticas con Issues](#buenas-prácticas-con-issues)
5. [Estándares de código](#estándares-de-código)
6. [Proceso de revisión de código](#proceso-de-revisión-de-código)
7. [Estrategia de ramas](#estrategia-de-ramas)
8. [Convención de commits](#convención-de-commits)
9. [Definición de "Listo" y "Listo para revisión"](#definición-de-listo-y-listo-para-revisión)
10. [Plantilla - Issue: Bug report](#plantilla---issue-bug-report)
11. [Plantilla - Issue: Feature request](#plantilla---issue-feature-request)
12. [Plantilla - Issue: Documentación](#plantilla---issue-documentación)
13. [Plantilla - Pull Request](#plantilla---pull-request)
14. [Plantilla - ADR](#plantilla---adr-architecture-decision-record)
15. [Plantilla - RFC](#plantilla---rfc)
16. [Plantilla - Spike](#plantilla---spike)
17. [Plantilla - Release notes / Changelog](#plantilla---release-notes--changelog)

---

## Cómo reportar un bug

1. Busca en los **Issues** existentes (abiertos y cerrados) para evitar
   duplicados.
2. Si no existe, crea un issue nuevo usando la plantilla de [Bug report](#plantilla--issue-bug-report)
   más abajo (o la que aparece automáticamente en GitHub al elegir "New issue" -> "Bug report").
3. Incluye pasos de reproducción claros, comportamiento esperado vs. actual,
   y entorno. Sin esto, el issue puede marcarse con `question` (falta
   información) y quedar en espera hasta que la completes.
4. Etiqueta con `bug` y, si aplica, con el componente afectado
   (`frontend`, `backend`, `matcher`, `api`, `db`).

## Cómo proponer una feature

1. Revisa el [PRD](docs/00-prd/PRD.qmd) y los ADRs existentes - puede que la
   decisión ya esté tomada (o descartada) ahí.
2. Abre un issue usando la plantilla de [Feature request](#plantilla--issue-feature-request)
   más abajo o desde Github.
3. Si la propuesta implica una **decisión de arquitectura**, usa:
   - Un [RFC](#plantilla--rfc) cuando la decisión **todavía está en discusión**
     y quieres alinear al equipo antes de comprometerte.
   - Un [ADR](#plantilla--adr-architecture-decision-record) cuando la
     decisión **ya se tomó** y solo la estás dejando registrada.
4. Si hay incertidumbre técnica antes de comprometerse, usa primero un [Spike](#plantilla--spike) con tiempo acotado.
5. Las features se discuten y priorizan en la reunión semanal del equipo (o
   async en el canal del equipo) antes de empezar a programar.

## Cómo reportar documentación desactualizada

Si detectas que una página de la wiki, un `.qmd` de `docs/`, o que el README no
corresponden a lo que hace el código:

1. Abre un issue con la plantilla de [Documentación](#plantilla--issue-documentación).
2. Cita explícitamente el/los archivo(s) desactualizados (ruta completa).
3. Explica qué falta actualizar o qué está mal.
4. Etiqueta con `documentation`.

## Buenas prácticas con Issues

Un issue no es solo un título: la descripción debe alcanzar para que
**cualquier integrante del equipo, sin más contexto que el issue mismo,
pueda tomarlo y resolverlo**. Antes de crear uno, verifica que no exista ya
(abierto o cerrado).

Usa estas herramientas para mantenerlos organizados:

- **Labels:** ver la tabla completa abajo. Todo issue debe llevar al menos
  la de **Tipo**.
- **Assignees:** asigna el issue a quien vaya a resolverlo. Un issue sin
  asignar está disponible para tomarse.
- **Milestones:** agrupan issues por objetivo o etapa del proyecto.
- **References:** si un issue está relacionado con otro, o con un PR que lo
  resuelve parcialmente, referencia el número (`#12`).

### Labels

Usamos seis categorías de label. Un issue típico lleva **Tipo** siempre, y
**Componente** cuando se sabe de entrada; **Prioridad** y **Estimación** se
asignan después, en triage/planeación - no las pongas tú mismo al abrir un
bug o feature si no eres quien va a estimarlo. **Resolución** la pone quien
cierra el issue, no quien lo abre.

| Categoría | Labels | Cuándo usarla | ¿Quién la asigna? |
|---|---|---|---|
| **Tipo** (obligatoria) | `bug` - `enhancement` - `documentation` - `question` - `chore` | `bug` = algo no funciona como debería. `enhancement` = feature nueva o mejora. `documentation` = documentación desactualizada/faltante. `question` = duda que no implica una tarea concreta todavía. `chore` = mantenimiento (deps, CI, config) | Quien abre el issue (las plantillas ya la traen por defecto) |
| **Componente** | `frontend` - `backend` - `matcher` - `api` - `db` | Qué parte del sistema toca | Quien abre el issue, si lo sabe; si no, se agrega en triage |
| **Prioridad** | `prioridad: alta` - `prioridad: media` - `prioridad: baja` | Alta = bloquea a otros o es crítico. Media = importante, no urgente. Baja = nice-to-have | El equipo, en la reunión de planeación/triage |
| **Estimación** | `1 punto` - `2 puntos` - `3 puntos` - `5 puntos` - `8 puntos` - `13 puntos` | Ver abajo | El equipo, en planeación |
| **Resolución** | `duplicate` - `invalid` - `wontfix` | `duplicate` = ya hay otro issue igual. `invalid` = no es un bug real / no aplica. `wontfix` = válido, pero no se va a trabajar | Quien revisa y cierra el issue |
 
**Sobre la estimación ("puntos"):** usamos *story points* con la serie de
Fibonacci (1, 2, 3, 5, 8, 13), como se hace convencionalmente en la
industria. Son una medida **relativa** de esfuerzo, complejidad e
incertidumbre combinados.

## Estándares de código

Las reglas de nomenclatura, indentación, comentarios y demás convenciones de
estilo por lenguaje viven en la [Guía de estilo](docs/04-guias-desarrollo/convenciones-codigo.qmd)
del equipo.

## Proceso de revisión de código

- Todo cambio entra por **Pull Request** hacia `main`. Nadie hace push directo
  a `main`.
- **Mínimo 3 aprobaciones** de otros integrantes del equipo.
- El autor del PR **no se auto-aprueba** ni mergea su propio PR sin la
  aprobación pendiente.
- Si el PR lleva más de 3-4 días sin revisión, es válido pedir la revisión
  directamente a un compañero.
- Ver también la [Definición de Listo](#definición-de-listo-y-listo-para-revisión) más abajo.

### Responsabilidades de quien abre el PR (requester)

- Mantener la rama limpia: solo los commits necesarios en un orden que le
  permita al revisor entender el porqué de los cambios.
- Rebasar contra `main` antes de pedir revisión.
- Verificar que las pruebas pasan y/o que la funcionalidad es correcta en la
  rama *antes* de abrir el PR.
- Si el revisor deja comentarios, resolverlos en un commit aparte y, si se desea, reordenar u
  aplastar los commits justo antes del merge final.

### Responsabilidades de quien revisa (reviewer)

- Verificar que el sistema se comporta tal como describe el PR.
- Verificar que las pruebas pasan.
- Verificar que la rama está rebasada con `main` y que los commits siguen la
  convención del equipo.
- Responder con rapidez para no bloquear al requester.
- Si propone un cambio de algoritmo o enfoque, acompañarlo de fuentes,
  pros/contras o un ejemplo.

---

## Estrategia de ramas

Usamos **GitHub Flow** (trunk-based simplificado): una sola rama de larga
duración con `main` siempre desplegable y ramas cortas por tarea que se
mergean rápido vía PR y después se eliminan. Para más información ver 
[GitHub Flow](https://docs.github.com/en/get-started/using-github/github-flow)

### Nomenclatura de ramas

[Conventional Branch](https://conventionalbranch.org/) define **solo 5
tipos** a propósito. Todo lo que no sea feature/bug/hotfix/release cae en `chore/`, 
incluyendo documentación y configuración de CI.

| Prefijo (alias corto) | Uso | Ejemplo |
|---|---|---|
| `feature/` (`feat/`) | Nueva funcionalidad | `feature/matcher-por-horario` |
| `bugfix/` (`fix/`) | Corrección de bug | `bugfix/steam-timeout` o `fix/steam-timeout` |
| `hotfix/` | Corrección urgente sobre `main` ya en producción | `hotfix/login-roto` |
| `release/` | Preparación de una versión | `release/v0.2.0` |
| `chore/` | Todo lo demás: documentación, CI, config, dependencias, refactors internos, tests sueltos | `chore/actualizar-fastapi`, `chore/guia-contribucion` |

Formato: `<tipo>/<descripcion-en-kebab-case>` - minúsculas, guiones, **sin**
guion bajo ni espacios. Se puede incluir el número de issue al final: `bugfix/steam-timeout-42`.

### Ramas protegidas

`main` está protegida:

- Requiere Pull Request (no push directo).
- Requiere al menos **3 aprobaciones**.
- Requiere que la rama esté actualizada con `main` antes de mergear.
- No permite force-push ni borrado.

---

## Convención de commits

Basada en [Conventional Commits v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/).

```
<tipo>(<alcance opcional>): <descripción corta en imperativo>

[cuerpo opcional: qué y por qué, no cómo]

[footer opcional: BREAKING CHANGE, Closes #123]
```

### Commits atómicos

- Un commit = un cambio lógico coherente. Si tu mensaje necesita "y" para
  describirlo, probablemente son dos commits.
- Evita mezclar refactor + feature en el mismo commit.

### Tipos permitidos

| Tipo       | Uso                                                        |
|------------|-------------------------------------------------------------|
| `feat`     | nueva funcionalidad para el usuario                        |
| `fix`      | corrección de un bug                                        |
| `docs`     | cambios solo en documentación                               |
| `style`    | formato, espacios, punto y coma - sin cambio de lógica       |
| `refactor` | cambio de código que no arregla bug ni añade feature         |
| `test`     | agregar o corregir pruebas                                   |
| `chore`    | tareas de mantenimiento (deps, config, CI)                   |
| `perf`     | mejora de rendimiento                                        |

---

## Definición de "Listo" y "Listo para revisión"

### Antes de abrir un PR (Listo para revisión)

- [ ] El código compila/corre localmente sin errores.
- [ ] Se agregaron o actualizaron tests para el cambio.
- [ ] El branch está actualizado con `main` (rebase o merge reciente).
- [ ] La descripción del PR explica el *qué* y el *por qué*.
- [ ] Se actualizó documentación relevante (README, ADR, `.qmd` en `docs/`)
      si el cambio lo amerita.
- [ ] No quedan `console.log`, `print()` de debug ni código comentado sin usar.

### Para considerar un PR aprobable (Listo)

- [ ] Cumple los criterios de aceptación del issue/feature relacionado.
- [ ] Al menos 3 aprobaciones de otros integrantes.
- [ ] Sin conflictos de merge pendientes.
- [ ] Si el cambio afecta variables de entorno o el esquema de base de
      datos, se documentó explícitamente en el PR.
- [ ] Si introduce una decisión de arquitectura relevante, tiene un ADR
      asociado (aprobado o al menos propuesto).

---

## Plantilla - Issue: Bug report

Vive en [`.github/ISSUE_TEMPLATE/bug_report.md`](.github/ISSUE_TEMPLATE/bug_report.md).
Ese es el archivo real que GitHub carga automáticamente al elegir
"New issue" -> "Bug report". Debe llevar:

- **Checklist previo:** confirmar que no existe ya el issue, que el bug se
  reproduce de forma consistente, y en qué versión/rama se está.
- **Descripción del bug:** cualquiera del equipo, sin más
  contexto que el issue, debe poder entender y resolverlo.
- **Pasos para reproducir**, numerados.
- **Comportamiento esperado vs. actual**.
- **Entorno:** componente afectado (frontend/backend/matcher/api/db),
  versión/rama/commit, SO, navegador o versión de Python si aplica.
- **Severidad:** crítica / alta / media / baja.
- **Capturas o evidencia**, si ayudan.

Label por defecto: `bug`.

---

## Plantilla - Issue: Feature request

Vive en [`.github/ISSUE_TEMPLATE/feature_request.md`](.github/ISSUE_TEMPLATE/feature_request.md).
Debe llevar:

- **Problema que resuelve:** la necesidad real detrás de la feature.
- **Solución propuesta**.
- **Componentes o archivos afectados**, si ya se sabe (opcional).
- **Alternativas consideradas** y por qué se prefiere esta.
- **Impacto y prioridad sugerida**, y si requiere abrir antes un
  [RFC](#plantilla--rfc), [ADR](#plantilla--adr-architecture-decision-record)
  o [Spike](#plantilla--spike).
- **Criterios de aceptación**, como checklist.

Label por defecto: `enhancement`.

---

## Plantilla - Issue: Documentación

Vive en [`.github/ISSUE_TEMPLATE/documentation.md`](.github/ISSUE_TEMPLATE/documentation.md).
Debe llevar:

- **Archivo(s) afectado(s)**, con ruta completa (`docs/...qmd`, `README.md`,
  etc.).
- **Qué está desactualizado o falta** - específico.
- **Cómo debería quedar**, si ya se sabe la información correcta.
- **Contexto adicional**, como el PR/commit que dejó la documentación
  desactualizada.

Label por defecto: `documentation`.

---

## Plantilla - Pull Request

Vive en [`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md).Se autocompleta al abrir cualquier PR. Debe llevar:

- **Descripción del cambio:** qué y por qué, con contexto.
- **Issue relacionado** (`Closes #N`).
- **Tipo de cambio**, como checklist con los tipos de [Conventional Commits](#convención-de-commits)
  (`feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `BREAKING CHANGE`).
- **Cómo se probó**, con los comandos o pasos concretos.
- **Checklist de revisión**, alineado con la [Definición de Listo](#definición-de-listo-y-listo-para-revisión).
- **Screenshots**, si el cambio afecta la UI.

---

## Plantilla - ADR (Architecture Decision Record)

Guardar como `docs/05-decisiones-tecnicas/000N-titulo-corto.qmd` (siguiente
número consecutivo). Registrar el archivo en `scripts/qmd_to_wiki.py`
(`WIKI_STRUCTURE`) para que se publique en la wiki.

```markdown
---
title: "ADR NNNN: <Título corto de la decisión>"
date: YYYY-MM-DD
author: <nombre>
---

- **Estado:** Propuesta <!-- Propuesta - Aceptada - Rechazada - Reemplazada por 000M -->

## Contexto

<!-- ¿Qué problema o necesidad técnica origina esta decisión? ¿Qué
     restricciones existen (tiempo, conocimiento del equipo, stack ya
     elegido, etc.)? -->

## Decisión

<!-- Qué se decidió, en una o dos frases claras, seguido de la
     justificación. -->

Decidimos adoptar **___** por las siguientes razones:

-
-

## Alternativas consideradas

<!-- Al menos una alternativa real, con su ventaja y la razón de descarte. -->

- **Alternativa A:**
  - *Ventaja:*
  - *Causa de descarte:*

## Consecuencias

- **Consecuencias positivas:**
  -
  -
- **Consecuencias negativas:**
  -
  -

## Preguntas abiertas

<!-- Opcional: dudas que quedan pendientes de resolver tras esta decisión. -->

-
```

---

## Plantilla - RFC

Un RFC (*Request for Comments*) es una **propuesta abierta a discusión**,
distinta del ADR: mientras el ADR documenta una decisión ya tomada, el RFC
se usa cuando el equipo todavía necesita alinearse, hay más de una opción
razonable, o quedan preguntas abiertas que se quieren resolver en conjunto
antes de comprometerse. Cuando el equipo llega a un acuerdo sobre un RFC,
normalmente se cierra con un ADR corto que lo referencia.

Guardar como `docs/05-decisiones-tecnicas/rfc-000N-titulo-corto.qmd`
(siguiente número consecutivo de RFC, independiente de la numeración de
ADRs). Registrar el archivo en `scripts/qmd_to_wiki.py` (`WIKI_STRUCTURE`)
para que se publique en la wiki.

```markdown
---
title: "RFC NNNN: <Título corto de la propuesta>"
date: YYYY-MM-DD
author: <nombre>
---

- **Estado:** En discusión <!-- En discusión - Aceptado - Rechazado - Cerrado sin acción - Convertido en ADR NNNN -->

## Resumen

<!-- Una o dos frases: qué se propone y por qué, para quien no quiera leer todo el documento. -->

## Motivación / Contexto

<!-- ¿Qué problema hay que resolver? ¿Por qué es necesario decidir esto ahora?
     ¿Qué pasa si no se resuelve? -->

## Propuesta

<!-- La propuesta concreta. Puede incluir diagramas, ejemplos de uso, o
     fragmentos de diseño. -->

**La propuesta** es.

## Pros y contras

- **Pros:**
  -
  -
- **Contras:**
  -
  -

## Alternativas consideradas

<!-- Otras opciones evaluadas, aunque no se recomienden, para dejar
     evidencia de que se pensaron. -->

- **Alternativa A:**
  -

## Impacto

<!-- A qué partes del sistema o del equipo afecta esta propuesta si se acepta. -->

## Preguntas abiertas

<!-- Dudas que el equipo debe resolver en la discusión antes de aceptar o
     rechazar el RFC. -->

-

## Resolución

<!-- Completar una vez que el equipo decide. Ej.: "Aceptado el DD/MM,
     resumido en ADR 000N" o "Rechazado: se opta por la alternativa A". -->
```

---

## Plantilla - Spike

Guardar como `docs/07-spikes/spike-tema-corto.qmd`. Registrar el archivo en
`scripts/qmd_to_wiki.py` (`WIKI_STRUCTURE`). Un spike es investigación con
tiempo acotado, no implementación final y su entregable es conocimiento y una recomendación.

```markdown
---
title: "Spike: <Tema a investigar>"
date: YYYY-MM-DD
author: <nombre>
---

**Objetivo del spike:** <!-- qué se busca averiguar y para qué se usará el resultado -->

**Pregunta a responder:** <!-- pregunta concreta y cerrada, ej. "¿La API X puede devolver Y en menos de Z segundos?" -->

**Timebox:** <!-- ej. "4 horas", "1 día", "hasta el viernes" -->

---

## Contexto

<!-- Por qué surge esta pregunta ahora. -->

## Investigación / Candidatas evaluadas

<!-- Qué se probó: librerías, APIs, enfoques. Puede tener una sub-sección
     por cada opción evaluada, con su estado (oficial/no oficial,
     documentada/no, límites, riesgos). -->

### Opción 1: <nombre>

- **Estado:**
- **Qué ofrece:**
- **Requisitos técnicos:**
- **Riesgos / limitaciones:**

## Hallazgos

<!-- Resumen de lo que se aprendió, con evidencia (links, resultados de
     pruebas, benchmarks). -->

## Recomendación final

<!-- Qué se recomienda hacer con esta información: adoptar, descartar,
     investigar más, escalar a un ADR. -->

## Próximos pasos

- [ ]
- [ ]

## Fuentes consultadas

| Recurso | Enlace |
|---|---|
|  |  |
```

---

## Plantilla - Release notes / Changelog

Basada en [Keep a Changelog](https://keepachangelog.com/es-ES/). Guardar
como `docs/06-changelog/vX.Y.Z.qmd` (Semantic Versioning: MAJOR.MINOR.PATCH).
Solo incluir las secciones que apliquen; borrar las vacías.

```markdown
---
title: "vX.Y.Z"
date: YYYY-MM-DD
description: "Descripción corta de una línea sobre este release"
---

## Added

<!-- Funcionalidad nueva -->

-

## Changed

<!-- Cambios en funcionalidad existente -->

-

## Deprecated

<!-- Funcionalidad que seguirá funcionando pero se eliminará pronto -->

-

## Removed

<!-- Funcionalidad eliminada -->

-

## Fixed

<!-- Bugs corregidos -->

-

## Security

<!-- Correcciones relacionadas a vulnerabilidades -->

-
```
