# Visión general


## Diagrama de alto nivel

igual esta hecho con mermaid

``` mermaid
flowchart LR
    U[Usuario] --> FE[Frontend]
    FE -->|HTTP / REST| BE[Backend API]
    BE --> DB[(Base de datos)]
    BE --> Q[[Cola de trabajos]]
    Q --> W[Workers]
    W --> DB
    BE --> EXT[Servicios externos]
```

## Componentes

| Componente         | Responsabilidad                                |
|--------------------|------------------------------------------------|
| Frontend           | UI, navegación, estado de sesión               |
| Backend API        | lógica de negocio, autenticación, orquestación |
| Cola / Workers     | tareas asíncronas y trabajos programados       |
| Base de datos      | persistencia                                   |
| Servicios externos | pagos, correo, etc.                            |

## Flujo de una petición típica

Tenemos que describir el flujo de nuestra app, incluso poner como actor
a las apis externas
