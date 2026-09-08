# CI / CD


## Pipeline

``` mermaid
flowchart LR
    PR[Pull Request] --> L[Lint]
    L --> T[Tests]
    T --> B[Build]
    B --> D{¿Rama?}
    D -->|main| S[Deploy staging]
    D -->|tag vx.y.z| P[Deploy prod]
```

## Etapas

| Etapa          | Se ejecuta en  | Falla si              |
|----------------|----------------|-----------------------|
| Lint           | cada push / PR | hay errores de estilo |
| Tests          | cada push / PR | alguna prueba falla   |
| Build          | cada push / PR | el build no compila   |
| Deploy staging | merge a `main` | falla el despliegue   |
| Deploy prod    | tag `vx.y.z`   | falla el despliegue   |

## Herramienta

podemos usar GitHub Actions y poner todo lo de workflows en
`.github/workflows/`.\_
