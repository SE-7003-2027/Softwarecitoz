# Runbook de la API

## Rotación de la clave de firma JWT

1. Genera un par nuevo: `uv run python scripts/gen_jwt_key.py <kid>` (por defecto el kid es `AAAA-MM`).
2. Agrega la clave pública nueva a `JWT_PUBLIC_KEYS_JSON` junto a la actual y despliega. Todas las réplicas pueden verificar con ambas.
3. Cambia `JWT_ACTIVE_KID` y `JWT_PRIVATE_KEY_PEM` a la nueva y despliega.
4. Espera al menos `ACCESS_TTL` (15 min) y quita la clave pública anterior de `JWT_PUBLIC_KEYS_JSON`.

Si la clave privada se filtra, quítala de inmediato (pasos 1–4 sin esperar en el 4). Los access tokens viejos dejan de validar, pero los usuarios no pierden la sesión: renuevan con su refresh token y reciben un access firmado con la clave nueva.

## Limpieza diaria de sesiones

`uv run python -m scripts.cleanup_auth` desde `apps/api/`. Borra refresh tokens expirados hace más de 7 días y familias terminadas hace más de 90.

## Revocar sesiones de un usuario (ban o borrado)

```sql
UPDATE app_users SET status = 'banned' WHERE id = :user_id;
UPDATE auth_session_families SET revoked_at = now(), revoke_reason = 'banned'
WHERE user_id = :user_id AND revoked_at IS NULL;
```

El refresh y las rutas sensibles fallan al instante; las rutas de lectura, en ≤ 15 min.
