# ADR 0002: Elección de HTML, CSS y JavaScript para el Desarrollo del Frontend


- **Estado:** Aprobado

## Contexto

Para el desarrollo de la app web, se necesita la implementación de una
interfaz de usuario (Frontend) encargada de: 1. Presentar de manera
clara e intuitiva los formularios de registro, inicio de sesión y
gestión de perfil del jugador. 2. Visualizar la biblioteca de
videojuegos sincronizada desde Steam y los juegos de mesa agregados
manualmente. 3. Mostrar las tarjetas de perfiles sugeridos por el
algoritmo de emparejamiento, resaltando juegos en común y franjas
horarias. 4. Consumir la API RESTful expuesta por el Backend en Python
para enviar y recibir información en formato JSON.

## Decisión

Decidimos adoptar el conjunto de **HTML, CSS y JavaScript** como las
tecnologías base para la construcción de la interfaz grafica del
Frontend.

La decisión se tomó por:

- Los integrantes del equipo contamos con conocimientos previos en el
  desarrollo con la pila estándar de la web (HTML, CSS, JS), lo que
  elimina la curva de aprendizaje inicial para el frontend.
- Son los lenguajes nativos soportados por todos los navegadores web
  modernos, lo que garantiza que la plataforma sea accesible desde
  cualquier dispositivo.
- JavaScript nativo (`fetch` / `async-await`) permite consumir las
  respuestas en formato JSON expuestas por la API RESTful en FastAPI de
  manera limpia y ligera.

## Consecuencias

- **Consecuencias Positivas:**
  - Alta velocidad de desarrollo y maquetación desde los primeros
    Sprints al dominar las bases de la web.
  - Cero tiempo invertido en tecnologias mas robustas pero mas complejas
    e innecesarias para este proyecto.
  - Código ligero, de carga rapida y facil de revisar o modificar
    durante las modificaciones.
- **Consecuencias Negativas:**
  - Al no utilizar un framework como React, el manejo del estado global
    de la aplicación debera programarse y gestionarse manualmente en
    JavaScript.
