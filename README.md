# Auditoría RGPD Webhook

Este proyecto genera informes en PDF y Word basados en los datos enviados vía POST desde Zapier o cualquier cliente externo.

## Endpoints

- `GET /` - comprobación de funcionamiento
- `POST /auditar` - recibe JSON con empresa, url, tipo y email, y genera los informes.

## Requisitos

- Python 3
- Flask
- FPDF
- python-docx

## Ejemplo de JSON:

```json
{
  "empresa": "BEVICIS",
  "url": "https://bevicis.com",
  "tipo": "informativa",
  "email": "contacto@bevicis.com"
}
```
