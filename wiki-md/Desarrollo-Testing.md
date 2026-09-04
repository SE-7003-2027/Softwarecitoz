# Testing


## Tipos de prueba

| Tipo | Herramienta | Qué cubre |
|----|----|----|
| Unitarias | las del lenguaje | funciones y componentes aislados |
| Integración | *…* | varios módulos juntos + DB de prueba |
| Vi que existe E2E ej. Playwright para flujos completos de usuario |  |  |

## Comandos

``` bash
npm test              # todas
npm run test:unit
```

## Convenciones

- Los archivos de prueba van junto al código: `foo.ts` → `foo.test.ts`.
- Cada bug corregido lleva una prueba que lo reproduce.
- Objetivo de cobertura: *p. ej. 80%* en lógica de negocio.
