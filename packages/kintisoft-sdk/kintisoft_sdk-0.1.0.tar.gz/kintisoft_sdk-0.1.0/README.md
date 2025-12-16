# kintisoft-sdk (Python)
### SDK oficial de Python para la API pública de KintiSoft

El **SDK oficial de KintiSoft para Python** permite integrar de forma sencilla la API pública de KintiSoft en scripts, aplicaciones backend, servicios y automatizaciones.

Incluye:

- Cliente HTTP listo para producción  
- Manejo de errores con excepciones tipadas  
- Soporte para múltiples tenants  

---

## Instalación

```bash
pip install kintisoft-sdk
```

---

## Configuración básica

```python
from kintisoft_sdk import KintiSoftClient

client = KintiSoftClient(
    tenant="acme",
    api_key="pk_live_xxxxxx",
)
```

---

## Manejo de errores

El SDK lanza `KintiSoftError` cuando:

- La API devuelve errores (`4xx` o `5xx`)  
- Hay timeouts  
- Ocurre un problema de red  

---

## Opciones avanzadas

```python
client = KintiSoftClient(
    tenant="acme",
    api_key="pk_live_xxxxxx",
    base_url_override="https://acme.staging.tudominio.com/api/v1",
    timeout=15.0,
)
```

---

## Estructura interna

```
kintisoft_sdk/
  __init__.py
  client.py
  http_client.py
  prospects.py
  exceptions.py
```

---

## Publicación en PyPI

```bash
python -m build
twine upload dist/*
```

---

## Licencia

MIT License
