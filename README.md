# DICOM
Este repositorio funciona para la simulación por medio de dockers un servidor-cliente, donde tambien podre efectuar una tercero con un evento malicioso.

## Generar dockers
Para poder generar los dockers o contenedores, usaremos el docker compose. en la carpeta donde se encuentra ```docker-compose.yml``` ejecutaremos el siguiente comando:

```shell
sudo docker compose -d --build
```

Cuando ya desees terminar los contenedores simplemente ejecuta

```shell
sudo docker compose down
```

Y para ver el estado de los contenedores:

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