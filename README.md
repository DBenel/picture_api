# Proyecto de Consolidacion

Este proyecto de consolidación para la maestría de Data Engineer en Mbit School - España consta de dos microservicios: una API con Flask y una base de datos en MySQL.

**El Objetivo de la API** es poder subir imágenes, que estas sean etiquetadas según su contenido y almacenar la información obtenida. En la DDBB se almacenará en una tabla la ruta de escritura de la imagen y en otra tabla las etiquetas para respectiva imagen.

Para obtener los tags se hará uso de dos API:
1. [imagekit.io](https://docs.imagekit.io/api-reference/upload-file-api/server-side-file-upload#uploading-base64-encoded-file-with-some-tags): Permite subir la imagen a la nube de forma pública.
2. https://imagga.com/ : Para extraer tags a partir de la imagen subida anteriormente.

Se hace uso de docker para poder desplegar estos microservicios en contenedores distintos.

La estructura del proyecto es la siguiente:

```
/picture_api
    /application
        /config
            /credentials.json
        /controllers
            /controller_picture.py
        /models
            /model_picture.py
        /views
            /view_picture.py
        /__init__.py

    /Compose
        /API
            /.env
            /Dockerfile
            /requirements.txt
        /MySQL
            /production.env
            /Dockerfile
            /pictures_tables.sql
    /data/storage/imagens

```

Es necesario el archivo `credentials.json` para obtener accesos a la DDBB de MySQL, credenciales de ImageKit y Imagga, la estructura es la siguiente:

```json
{
    "mysql_credential" : {
        "user": "",
        "password": "",
        "host": "",
        "database": ""
    },
    "ImageKit_credential" : {
        "private_key" : "",
        "public_key": "",
        "url_endpoint": ""
    },
    "Imagga_credential": {
        "api_key": "",
        "api_secret": ""
    },
    "main_path": "/var/lib/docker/volumes/data/storage"
}
```
(**Nota:** la ruta main_path definida aquí, es la misma que el volumen que figura en el Composer, si usted va a ejecutar en local puede cambiar a la ruta */data/storage/imagens* o la que desee.)

El archivo `/Compose/API/.env` contiene la variable de entorno HOST de MySQL, esto depende del nombre que se asigne al contenedor de la DDBB en el archivo `docker-composer`.
```
MYSQL_HOST=compose-mysql
```
El archivo `/Compose/MySQL/production.env` contiene las variables de entorno para la correcta configuración del contenedor de MySQL.
```
# cat .env
MYSQL_ROOT_PASSWORD=
MYSQL_DATABASE=
MYSQL_USER=
MYSQL_PASSWORD=
```
## Definición de API

**Picture_api** tiene los siguientes endpoitns:
### POST image
Parámetros necesarios:
- Imagen [`data`]: Obligatorio
- `min_confidence`: Imagga pondera cada tag con un nivel de confianza. Puede definir un nivel de confianza mínimo, por defecto será **80**.

Resultado:
- `id`: identificador de la imagen
- `size`: tamaño de la imagen en KB
- `date`: fecha en la que se registró la imagen, en formato `YYYY-MM-DD HH:MM:SS`
- `tags`: lista de objetos identificando las tags asociadas a la imágen. Cada objeto tendrá el siguiente formato:
    - `tag`: nombre de la tag
    - `confidence`: confianza con la que la etiqueta está asociada a la imagen
- `data`: imagen como string codificado en base64

### GET Images
Parámetros necesario:
- `min_date / max_date`: Puede definir ambos o al menos uno de ellos.
- `tags`: Puede ser uno o varios. Se envían en texto plano separado por comas **"kitty, cat, feline"**

Resultado:
- `id`: identificador de la imagen
- `size`: tamaño de la imagen en KB
- `date`: fecha en la que se registró la imagen, en formato `YYYY-MM-DD HH:MM:SS`
- `tags`: lista de nombres de tags asociados a la imágen

### GET Image
Parámetro necesario:
- `id`: identificador de la imagen

Resultado:
- `id`: identificador de la imagen
- `size`: tamaño de la imagen en KB
- `date`: fecha en la que se registró la imagen, en formato `YYYY-MM-DD HH:MM:SS`
- `tags`: lista de objetos identificando las tags asociadas a la imágen. Cada objeto tendrá el siguiente formato:
    - `tag`: nombre de la tag
    - `confidence`: confianza con la que la etiqueta está asociada a la imagen
- `data`: imagen como string codificado en base64

### GET Tags
Parámetro necesario:
- `min_date / max_date`: Puede definir ambos o al menos uno de ellos.

Resultado:
- `tag`: nombre de la etiqueta
- `n_images`: número de imágenes que tienen asociada esta tag
- `min_confidence`
- `max_confidence`
- `mean_confidence`

Elaborado por: Daniel Benel