# 0002 - Estrategia de caché
Equipo
2026-02-01

**Estado:** Aceptada

## Contexto

*Problemas de latencia / carga que motivan una capa de caché.*

## Opciones consideradas

| Opción                    | Pros            | Contras                        |
|---------------------------|-----------------|--------------------------------|
| Sin caché                 | simple          | no escala                      |
| Caché en memoria          | rápido          | no compartida entre instancias |
| Caché distribuida (Redis) | compartida, TTL | infra adicional                |

## Decisión

*Elegimos **X** con TTL de *N* y invalidación por evento.*

## Consecuencias

- Positivas: *…*
- Negativas / trade-offs: *…*
