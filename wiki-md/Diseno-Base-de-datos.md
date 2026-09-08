# Base de datos


## Motor

## Modelo de datos

Lo podemos hacer con mermeid (ejemplo rapido) o dbdiagram.io (es muy
bueno)

``` mermaid
erDiagram
    USUARIO ||--o{ SESION : tiene
    USUARIO ||--o{ RECURSO : posee
    RECURSO ||--o{ ITEM : contiene
```

## Tablas principales

| Tabla      | Descripción                     |
|------------|---------------------------------|
| `usuarios` | cuentas                         |
| `sesiones` | tokens / sesiones activas       |
| `recursos` | *entidad principal del dominio* |

<!-- ## Migraciones
Es un tema que ya se vera despues pero es indispensable para cosas en produccion
&#10;```bash
# crear migración
npm run migrate:make <nombre>
&#10;# aplicar
npm run migrate:up
&#10;# revertir
npm run migrate:down
``` -->

<!-- - Las migraciones viven en `apps/api/migrations/`.
- Nunca editar una migración ya aplicada en un ambiente compartido. -->
