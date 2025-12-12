# AWS [Aplicacion interna de duppla]

La herramienta de AWS tiene una librería de Boto3 para poder interactuar con la API de AWS. Este paquete de Python está diseñado exclusivamente para el uso interno de duppla a través de los diversos repositorios de la organización.

> [!IMPORTANT]
> Este paquete no está disponible para su uso externo.

## Instalación

```bash
pip install duppla_aws
```

> [!NOTE]
> Para más información sobre la librería Boto3, visite [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) y para detalles sobre los servicios de AWS, consulte la [Documentación de AWS](https://docs.aws.amazon.com/).

## Quieres aportar?

### Prerrequistos

Es necesario que ejecutes el siguiente comando para instalar las dependencias de desarrollo:

```python
pip install -r dist_requirements.txt
```

### Desplegar

#### Alternativa 1: GitHub Actions

Este repositorio cuenta con un flujo de trabajo de GitHub Actions que se encarga de desplegar el paquete cuando desees (on demand). Para ello, es necesario que ejecutes la acción `Deploy` en la pestaña de `Actions` de este repositorio.

#### Alternativa 2: CLI

Para desplegar el paquete, es necesario que ejecutes, en orden, los siguientes comandos:

```bash
python setup.py sdist bdist_wheel
twine upload dist/*
```

Recuerda que necesitas un API token, pregunta al dueño del repositorio o a los administradores de la organización.

### Recuerda

Recuerda, el objetivo de este repositorio es tener cosas simples, funcionales y que sean de utilidad para la organización.
