# Entorno local


## 1. Clonar el repo

``` bash
git clone <url-del-repo>
cd <repo>
```

<!-- ## 2. Variables de entorno
&#10;```bash
cp .env.example .env
# editar .env con los valores locales
``` -->

<!-- Ver [[Variables de entorno|Despliegue-Variables-de-entorno]] para el detalle de cada variable. -->

## 2. Levantar servicios

``` bash
docker compose up -d
```

| Servicio      | URL local             |
|---------------|-----------------------|
| Frontend      | http://localhost:3000 |
| Backend / API | http://localhost:8000 |
| Base de datos | localhost:            |

<!-- ## 4. Verificar
&#10;```bash
curl http://localhost:8000/health
``` -->
