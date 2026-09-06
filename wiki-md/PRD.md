

Los jugadores de videojuegos no tienen una manera explicita y sencilla
de encontrar compañeros compatibles para jugar partidas cooperativas. De
la misma manera los amantes de los juegos de mesa no tienen una forma de
conocer gente que tenga sus mismos gustos por algun juego, la forma mas
viable es solo con conocidos cercanos. Aqui es donde entra nuestra
propuesta de **conectar usuarios mediante una pagina web**, donde los
jugadores puedan tener su perfil, teniendo la opcion de enlazarlo con el
existente de Steam, su biblioteca de juegos de steam, lo que ha jugado
recientemente, sus logros, horarios disponibles para jugar, gustos de
juegos de mesa y otras propiedades

**El objetivo es**, en base a lo dicho en sus perfiles y algun
motor/metodo de emparejamiento, conectar usuarios compatibles con
intereses similares para armar partidas de videojuegos y/o de juegos de
mesa.

## El sistema debe tener las funciones:

- Registro de cuentas
- Creacion de perfil (guardando todo lo necesario)
- Autenticacion de usuarios
- Conexion con las APIs externas propuestas
- Motor de emparejamiento de perfiles
- Mando de solicitudes entre perfiles
- Autenticacion por OAuth
- Chat de mensajes y voz para conexion entre usuarios

## Historias de Usuario

- **Vincular cuenta de Steam**\
  Como usuario, quiero conectar mi cuenta de Steam para importar
  automaticamente mi biblioteca de juegos, perfil basico y actividad
  reciente a mi perfil.
- **Completar datos de la cuenta**\
  Como usuario, quiero completar mi perfil con informacion como horarios
  disponibles para jugar, videojuegos preferidos, y más.
- **Buscar juegos de mesa**\
  Como usuario, quiero buscar y agregar juegos de mesa a mi perfil para
  que el sistema sepa que titulos tengo o me interesa jugar.
- **Encontrar usuarios**\
  Como usuario, quiero visualizar perfiles compatibles y que compartan
  mis gustos y juegos cooperativos.
- **Consultar perfil y biblioteca de otro usuario**\
  Como usuario, quiero revisar la informacion, juegos en comun, logros y
  estadisticas detalladas de otro jugador antes de hacer match para
  conocerlo mejor.
- **Hacer match** Como usuario, quiero hacer match con otro usuario
  compatible, para organizar partidas juntos.
- **Chatear con matches**\
  Como usuario, quiero comunicarme a traves de un chat interno con los
  usuarios con quienes haya hecho match para coordinar los detalles de
  la partida.

## Podriamos ver para tener despues:

- Incluir otras bibliotecas de videjuegos como Epic Games, Riot Games, y
  mas.
- Implementacion de geolocalizacion para mejorar el emparejamiento de
  jugadores de juegos de mesa.
- Implementacion de emparejamiento de escuadrones, donde se emparejen
  mas de dos personas para juegos con equipos de 3 o mas jugadores por
  equipo.

## Las metricas de exito son:

- Obtener exitosamente las bibliotecas y la informacion mediante
  llamadas a los endpoints de la Steam Web API.
- Emparejamientos con logica, donde se tenga certeza que se recomiendan
  perfiles compatibles.
- Porcentaje de emparejamiento, donde se calcule porcentaje de que se
  mantenga una conexion sobre un emparejamiento (mediante matches).
- Funcionamiento del registro de usuarios, emparejamiento de usuarios y
  conexion de usuarios.

## Se contempla que:

- El funcionamiento de la sincronizacion automatica depende de que los
  servidores externos de Steam esten operativos y mantengan la
  estructura activa de sus endpoints.
- La extraccion de horas de juego y titulos comprados requiere que la
  cuenta del usuario sea publica en Steam.
- Hay riesgo del aumento en los tiempos de latencia si la API de Steam
  tarda mas de lo esperado en responder durante horas pico de trafico.
