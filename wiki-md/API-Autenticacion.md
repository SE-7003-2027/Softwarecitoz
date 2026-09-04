# Autenticación


## Esquema

puede ser JWT Bearer / OAuth2 para steam

## Obtener un token

``` bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "..."}'
```

Respuesta:

``` json
{ "access_token": "eyJ...", "expires_in": 3600 }
```

## Usar el token

``` bash
curl http://localhost:8000/recursos \
  -H "Authorization: Bearer eyJ..."
```

## Renovación

Los tipos de renovacion que manejariamos como ejemplo

| Token   | Duración | Cómo se renueva     |
|---------|----------|---------------------|
| access  | 1 h      | con `refresh_token` |
| refresh | 30 d     | re-login            |
