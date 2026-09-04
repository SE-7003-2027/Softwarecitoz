# Backend


## Servicios principales

| Servicio    | Responsabilidad         |
|-------------|-------------------------|
| Auth        | login, tokens, permisos |
| *Dominio A* | *…*                     |
| *Dominio B* | *…*                     |

## Colas y trabajos asíncronos

| Cola      | Productor  | Consumidor | Ejemplo de tarea       |
|-----------|------------|------------|------------------------|
| `emails`  | API        | worker     | envío de correos       |
| `reports` | API / cron | worker     | generación de reportes |

## Ejecución

``` bash
# desarrollo
npm run dev

# workers
npm run worker
```
