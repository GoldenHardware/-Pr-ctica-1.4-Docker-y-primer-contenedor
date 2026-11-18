# Arquitectura: instalación directa frente a contenedor

En este documento comparo las dos formas en las que he desplegado el mismo backend de FastAPI en mi máquina virtual con Ubuntu Server 24.04: instalándolo directamente en el sistema (práctica 1.3, con un entorno virtual y Gunicorn) y metiéndolo en un contenedor Docker (esta práctica). Al final explico qué aporta llevar esto a la nube.

## 1. Máquina virtual y contenedor

Antes de comparar, conviene tener clara la diferencia entre una máquina virtual y un contenedor, porque en mi caso uso las dos cosas a la vez: el contenedor corre dentro de la VM de VirtualBox.

```
      MÁQUINA VIRTUAL                         CONTENEDORES

  +---------+ +---------+              +---------+ +---------+
  |  App A  | |  App B  |              |  App A  | |  App B  |
  +---------+ +---------+              +---------+ +---------+
  | Libs    | | Libs    |              | Libs    | | Libs    |
  +---------+ +---------+              +---------+ +---------+
  | SO      | | SO      |              |     Docker Engine     |
  | invitado| | invitado|              +-----------------------+
  +---------+ +---------+              |  SO anfitrión (kernel |
  |      Hipervisor       |            |      compartido)      |
  +-----------------------+            +-----------------------+
  |       Hardware        |            |       Hardware        |
  +-----------------------+            +-----------------------+
```

| Aspecto | Máquina virtual | Contenedor |
|---|---|---|
| Qué virtualiza | El hardware completo | Solo el espacio de usuario (procesos) |
| Kernel | Cada VM tiene el suyo | Comparten el kernel del anfitrión |
| Aislamiento | Muy fuerte, a nivel de hardware | A nivel de procesos, con namespaces y cgroups |
| Peso | Varios GB (un sistema operativo entero) | MB (mi imagen ocupa 201 MB y el contenido real 48,7 MB) |
| Arranque | Minutos, tiene que arrancar un SO | Segundos o menos (en `docker ps` sale "Up Less than a second") |
| Recursos | Se reserva RAM y CPU fijas para cada VM | Usa solo lo que consume el proceso |
| Uso típico | Tener otro sistema operativo, aislar servidores enteros | Empaquetar y desplegar aplicaciones |

Lo he visto en la práctica: la VM de Ubuntu Server tarda en arrancar y ocupa bastante disco, mientras que el contenedor de la API se crea y arranca en menos de un segundo, y pararlo, borrarlo y volver a crearlo no cuesta nada.

## 2. Instalación directa (práctica 1.3)

En la 1.3 instalé todo sobre el propio Ubuntu:

```
Ubuntu Server 24.04 (VM)
 |- Python 3.13 (repositorio deadsnakes)
 |- ~/practica-1.3/venv (fastapi, uvicorn, gunicorn)
 |- gunicorn app.main:app ... --bind 127.0.0.1:8000
```

Ventajas:

- No hay ninguna capa extra, el proceso corre directamente en el sistema y el rendimiento es el máximo.
- Es fácil de entender y depurar: los ficheros, los logs y el proceso están a la vista.
- No hace falta instalar ni aprender Docker.

Inconvenientes:

- Depende de lo que tenga el sistema. Ubuntu 24.04 trae Python 3.12 y tuve que añadir el repositorio deadsnakes para tener la 3.13. En otra máquina habría que repetir todo eso y podría salir diferente.
- Si en el mismo servidor tengo varias aplicaciones que necesitan versiones distintas de Python o de librerías, pueden chocar.
- Para llevarlo a otra máquina hay que repetir la instalación a mano paso por paso.
- Para quitarlo hay que desinstalar cosas y pueden quedar restos en el sistema.
- Para que arranque solo al iniciar el servidor hay que crear un servicio de systemd.

## 3. Contenedor Docker (práctica 1.4)

En esta práctica la aplicación va dentro de una imagen:

```
Ubuntu Server 24.04 (VM)
 |- Docker Engine 29.10.0
     |- Imagen api-practica:1.0 (python:3.13-slim + fastapi + uvicorn + app/)
         |- Contenedor api-backend  (puerto 8080 de la VM -> 8000 del contenedor)
```

Ventajas:

- La imagen lleva dentro Python 3.13, las librerías con versiones fijadas y el código. No me ha hecho falta instalar Python 3.13 en el sistema para esta práctica, viene en la imagen base python:3.13-slim.
- Es reproducible: con el Dockerfile cualquiera construye exactamente la misma imagen, y la imagen funciona igual en mi VM, en el PC de otro compañero o en un servidor en la nube.
- Aislamiento: el contenedor tiene su propio sistema de ficheros y su red, no toca nada del sistema ni de otras aplicaciones.
- El ciclo de vida es muy sencillo: `docker run`, `stop`, `start`, `restart`, `rm`. Borrar el contenedor no deja nada en el sistema, y la imagen sigue para volver a crearlo.
- Se pueden levantar varios contenedores de la misma imagen para escalar.

Inconvenientes:

- Hay que instalar Docker y aprender cómo funciona (imágenes, contenedores, puertos, volúmenes).
- Es una capa más que puede fallar y hace la depuración un poco más indirecta (hay que usar `docker logs` o entrar al contenedor).
- La imagen ocupa más que la aplicación sola, porque lleva una base de Debian con Python.
- Los datos que se guarden dentro del contenedor se pierden al borrarlo si no se usan volúmenes.
- El aislamiento es menor que el de una VM, porque comparten kernel.

## 4. Comparativa

| Criterio | Instalación directa | Contenedor |
|---|---|---|
| Preparación | Instalar Python 3.13, venv y dependencias en el sistema | Instalar Docker una vez y escribir un Dockerfile |
| Dependencias | En el sistema y en el venv | Dentro de la imagen |
| Reproducibilidad | Depende de la máquina | La misma imagen en cualquier sitio |
| Aislamiento | Ninguno entre aplicaciones (solo el venv) | Sistema de ficheros, procesos y red propios |
| Arranque y parada | Lanzar gunicorn a mano o con systemd | `docker run / stop / start / restart / rm` |
| Limpieza | Desinstalar a mano | `docker rm` y `docker rmi` |
| Rendimiento | Máximo | Prácticamente igual, la sobrecarga es mínima |
| Escalado | Más workers en la misma máquina | Más contenedores, en una o varias máquinas |
| Depuración | Directa | A través de `docker logs` y `docker exec` |

## 5. Cuándo usar cada opción

Usaría la instalación directa cuando:

- Es un servicio del sistema que cambia poco y está muy ligado a la máquina.
- Es un servidor pequeño con una sola aplicación y no compensa añadir Docker.
- Estoy aprendiendo o probando algo y quiero verlo todo sin capas por medio.

Usaría un contenedor cuando:

- La aplicación tiene dependencias propias (versión concreta de Python y librerías).
- Se va a desplegar en varios sitios: desarrollo, pruebas y producción, o en la nube.
- Hay varias aplicaciones en el mismo servidor que no deben molestarse.
- Se actualiza a menudo y quiero poder volver a la versión anterior cambiando solo la etiqueta de la imagen.

## 6. Por qué Docker para el backend y no para el servidor web

En mi proyecto tengo dos piezas: Apache, que instalé en las prácticas 2.x con sus VirtualHost y la autenticación básica, y el backend de FastAPI.

- El backend es la parte que más cambia y la que tiene dependencias propias de Python. Meterlo en un contenedor resuelve justo esos problemas: versión de Python, librerías fijadas y desplegar una versión nueva sin tocar el sistema.
- Apache es un servicio del sistema estable, que se instala con apt, se integra con systemd y se configura una vez. Es el que da la cara en los puertos 80 y 443, gestiona los dominios, HTTPS y los ficheros estáticos, y hace de proxy inverso hacia el backend. No gana tanto metiéndolo en un contenedor y en cambio complicaría cosas como los certificados o el acceso a los puertos bajos.

La arquitectura queda así:

```
Cliente --> Apache (80/443, VirtualHost, HTTPS, estáticos)
               |
               | proxy inverso (mod_proxy)
               v
            127.0.0.1:8080 --> contenedor api-backend (uvicorn, 8000)
```

En esta práctica he publicado el puerto con `-p 8080:8000`, que escucha en todas las interfaces de la VM. Para el despliegue final detrás de Apache lo correcto sería publicarlo solo en local con `-p 127.0.0.1:8080:8000`, igual que en la 1.3 Gunicorn escuchaba en 127.0.0.1, para que nadie pueda saltarse Apache.

## 7. Qué aporta desplegar en la nube

Una vez la aplicación está en una imagen, llevarla a la nube es el paso natural:

1. Subo la imagen a un registro de contenedores (Docker Hub, GitHub Container Registry, Amazon ECR, Google Artifact Registry...).
2. Un servicio de contenedores de la nube (Google Cloud Run, AWS ECS o App Runner, Azure Container Apps) descarga esa imagen y la ejecuta.

Lo que aporta frente a tenerlo en mi VM:

- No tengo que mantener el servidor: el proveedor se encarga del hardware, del sistema operativo y de las actualizaciones.
- Escalado automático: si hay muchas peticiones lanza más contenedores, y si no hay ninguna puede bajar a cero.
- Alta disponibilidad: puede repartir los contenedores en varias zonas, y si uno falla lo reinicia.
- Pago por uso: se paga por lo que se consume en vez de tener una máquina encendida siempre.
- HTTPS, dominio y balanceo de carga suelen venir incluidos.
- Despliegue continuo: se puede configurar para que cada vez que subo código se construya la imagen y se despliegue sola.

Inconvenientes de la nube: hay un coste mensual que hay que vigilar, se depende del proveedor (sus servicios y precios) y los datos están en servidores de un tercero.

La clave es que la misma imagen api-practica:1.0 que he probado en mi VM es la que se ejecutaría en la nube, sin cambiar nada. Eso es lo que no da la instalación directa, donde tendría que repetir todos los pasos en el servidor nuevo.

## 8. Conclusión

La instalación directa es más simple y no añade capas, pero ata la aplicación a la máquina. El contenedor necesita instalar Docker, pero a cambio empaqueta la aplicación con todo lo que necesita, la aísla, hace que el ciclo de vida sea muy fácil y la deja preparada para desplegarla en cualquier sitio, incluida la nube. Para mi proyecto lo más razonable es dejar Apache instalado en el sistema como servidor web y proxy inverso, y ejecutar el backend en un contenedor.
