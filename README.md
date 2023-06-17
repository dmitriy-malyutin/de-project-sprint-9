# Проектная работа по облачным технологиям

## Общая схема системы

![schema.png](img%2Fschema.png)

**Registry link:** cr.yandex/crpjgpaag26iltnsft12/solution

## Описание файлов и папок

### docker-compose.yaml

Файл docker-compose.yaml содержит конфигурацию для запуска и управления несколькими контейнерами Docker.

### helm

Папка helm содержит файлы, используемые для развертывания Kubernetes-приложений с помощью Helm.

### docker_build

В папке docker_build лежит dockerfile, который используется для сборки Docker-образа используемого решением.

### service_cdm

Папка service_cdm содержит исходный код сервиса CDM.

### service_dds

Папка service_dds содержит исходный код сервиса DDS.

### service_stg

Папка service_stg содержит исходный код сервиса STG.
