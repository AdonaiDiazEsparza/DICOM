# DICOM
Este repositorio funciona para la simulación por medio de dockers un servidor-cliente, donde tambien podré efectuar un agente tercero con un proposio "malicioso".

## Generar dockers
Para poder generar los dockers o contenedores, usaremos el docker compose. en la carpeta donde se encuentra ```docker-compose.yml``` ejecutaremos el siguiente comando:

```shell
sudo docker compose -d --build
```

Cuando ya desees terminar los contenedores simplemente ejecuta el siguiente comando. Igualmente debe ser en la ubicación del docker compose.

```shell
sudo docker compose down
```

Para ver el estado de los contenedores, usa el siguiente comando:

```shell
sudo docker ps
```

# Como interactuar con los contenedores
## Server
Para poder interactuar con este contenedor, puedes usar el siguiente comando:

```shell
sudo docker logs -f dicom_server
```

Si el contenedor esta activo nos sirve para observar los logs que genera el servidor

## Client

Para el cliente, tenemos que ejecutar scripts, esto se logra con los siguientes comandos:

```shell
sudo docker exec -it dicom_client /bin/bash
```

Este nos funciona para entrar por bash a nuestro contenedor, ya ahi podemos ejecutar los scripts

```shell
python client.py --help
```

Igualmente el comando para ejecutar la terminal en nuestro servidor es el mismo que el del cliente, solo que cambia el nombre del contenedor, en vez de ser ```dicom_client``` debe ser ```dicom_server```

# PROTOCOLO DICOM

<b>D</b>igital <b>I</b>maging and <b>Co</b>mmunication in <b>M</b>edicine (DICOM) protocolo  estandar utilizado para la captura, envio y almacenamiento de imagenes médicas y datos relacionados, es decir, es el protocolo que se utiliza en el sector médico para el intercambio y almacenamiento de estudios gráficos de pacientes incluyendo datos personales.

## Preambulo 
Esta prueba de concepto, teoría y parte del repositorio se basa en la información obtenida de internet y platicando con [Hokma](https://github.com/MrR0b0t19). Donde hacemos nuestra presentación en el evento de HackGDL.

Y para que sirve esto, bueno, es la simulación de una red que incluye el protocolo DICOM, al no tener tantos equipos tengo que crear algo virtual, todo con uso de dockers o contenedores construidos para poder generar incluso una red virtual en mi equipo.

## Conceptos

>Nota: antes de empezar a leer sugiero que investiguen un poco más debido a que esto es sacado de diferentes fuentes y la experencia de personas en esta área. 


En el hospital existe un sistema llamado RIS/PACs, este sistema se encarga de realizar la gestión y almacenamiento de los datos clinicos. Conformado por los dos componentes que van en el nombre del sistema:

- RIS: se encarga principalmente de la gestión administrativa y clínica de radiología, incluyendo la programación de estudios, registro de pacientes, generación de órdenes médicas, reportes radiológicos y seguimiento del historial clínico.

- PACS: Está diseñado para almacenar, indexar y distribuir imágenes médicas en formato DICOM provenientes de equipos como CT, MRI o rayos X, permitiendo que médicos y radiólogos accedan a los estudios desde estaciones de diagnóstico.


Estos dos componentes que crean el sistema, se integran junto con el protocolo DICOM que es el estandar de comunicación en el sector médico (Claro hablamos en temas de tecnología), los cuales envian los <b>archivos DICOM</b>.

Un archivo DICOM incluye su contenido multimodal que pueden ser imagenes 2D y 3D (radiografias, tomografias, resonancia, etc) e incluye metadatos, información detallada del paciente, información del estudio (los datos relacionados cómo fecha , tipo y médico solicitante) y parámetros técnicos de la captura.

## ¿Cómo funciona el protocolo DICOM?

Las transferencias y comúnicación de estos archivos con el protocolo DICOM utiliza TCP/IP y la comunicación funciona entre diversos nodos.

Cualquier computadora o dispositivo que se encuentre conectado a la red pueda manejar y comunicarse con el protocolo DICOM funciona cómo un nodo.

Los nodos funcionan de dos maneras, SCP o SCU:

- SCP (Service Class Provider) puede ser el que actue cómo servidor.

- SCU (Service Class User) es el que funciona cómo cliente.

Entonces, ya teniendo conocimiento entre el rol de cada nodo, depende de como pueda solicitar y mover los datos.
Estas peticiones se realizan con diferentes servicios que manejan el flujo de la información:

- C-ECHO: Este servicio funciona cómo un ping al servidor

- C-STORE: Este servicio funciona para enviar un archivo y que el servidor debe almacenar.

- C-FIND: este servicio funciona para encontrar un archivo con la información de algún cliente.

- C-MOVE: Funciona para mover los archivos, es decir con este servicio puedes mover del servidor a otro nodo de la red.

- C-GET: Obtiene un archivo del servidor.

## Simulación técnica

Supongamos que queremos obtener información de una red hospitalaria, este incluye el protocolo DICOM. ¿Cómo podriamos nosotros estar desde nuestras casas y a la vez estar conectado?

Bueno, podriamos utilizar a alguien que incluya un dispositivo que se conecte a la red, por ejemplo podriamos conectar a la red alguna Raspberry o un dispositivo. En este repositorio simulamos la red con dockers los cuales integran un servidor, un cliente y nuestro agente malicioso. 

El servidor funciona como el sistema de almacenamiento, el cual recibe archivos y puede proveerlos dependiendo de lo que pida el cliente. 

El rol del cliente lo que hace es enviar archivos al servidor para que este los almacene y a su vez este poder hacer peticiones y recibirlos.

Nuestro agente malicioso, tiene el proposito de obtener información, generar e incluir archivos en el servidor.

### ¿Cómo podriamos realizar el ataque?

Al estar el agente malicioso conectado a la red, nosotros podemos hacer peticiones al servidor, este no valida si es un dispositivo legitimo, solamente recibe la petición y realiza la acción del servicio que se le envíe.

Por ejemplo nosotros descargamos un archivo de algún paciente, lo que hacemos ahora es modificar este archivo e integrarle un payload o un shellcode. ¿Porqué agregamos esto?

Hokma nos indicó que en cada computadora que tuviera el programa para visualizar los estudios, este ejecutaba una terminal o un command prompt al momento de abrir un estudio. Si nosotros incluimos algun payload malicioso en un archivo DICOM, este se va ejecutar cuando el personal de medicina visualice el archivo que nosotros modifiquemos.

En conclusión esto nos funciona como un vector de ataque, con un equipo en el cual podemos hacer modificaciones de manera remota. Así podriamos cambiar nuestros payloads y modificar los archivos a nuestro antojo, cargandolos en el servidor esperando a que alguna persona lo descargue y se .

## Conclusion 
El protocolo DICOM puede ser usado cómo vector de ataque si no se realiza una buena implementación de seguridad del sistema, en este caso que hemos visto, los datos son entregados y recibidos por cualquier cliente o dispositivo que este dentro de la red y maneje el protocolo, comprometiendo no solamente los datos de los pacientes, sino la red e infraestructura del hospital por realizar ejecuciones de terminales en los programas de los visualizadores.