# Notification Service 📧

Microservicio de notificaciones desarrollado con FastAPI para el envío de correos electrónicos cuando se registran nuevos usuarios.

## Requisitos Previos

- Python 3.9 o superior
- pip (gestor de paquetes de Python)
- Cuenta en Mailtrap o servicio SMTP

## Instalación Local

### 1. Clonar el repositorio

```bash
cd proyecto-notifications
```

### 2. Crear y activar entorno virtual

**En Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**En Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crear un archivo `.env` en la raíz del proyecto:

```env
# Configuración SMTP (Mailtrap)
EMAIL_HOST=sandbox.smtp.mailtrap.io
EMAIL_PORT=2525
EMAIL_HOST_USER=your_mailtrap_user
EMAIL_HOST_PASSWORD=your_mailtrap_password
DEFAULT_FROM_EMAIL=noreply@example.com

# FastAPI
EMAIL_USE_TLS=True
```

### Obtener credenciales de Mailtrap

1. Regístrate en [Mailtrap.io](https://mailtrap.io)
2. Crea un inbox
3. Copia las credenciales SMTP:
   - Host: `sandbox.smtp.mailtrap.io`
   - Port: `2525`
   - Username: (tu username)
   - Password: (tu password)

## Ejecutar el Servidor

### Modo desarrollo con recarga automática

```bash
uvicorn app.main:app --reload --port 8080
```

El servidor estará disponible en: `http://localhost:8080`

### Ejecutar en un puerto específico

```bash
uvicorn app.main:app --reload --port 8080
```

### Modo producción

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080 --workers 4
```

## Endpoints Disponibles

### Enviar Notificación

**POST** `/notify/`

Envía una notificación por correo electrónico.

#### Request Body:

```json
{
  "subject": "Nuevo usuario: Juan Pérez",
  "message": "Se creó el usuario Juan Pérez (juan@example.com), (099123456)",
  "email": "juan@example.com"
}
```

#### Response (200 OK):

```json
{
  "status": "success",
  "message": "Notification sent successfully"
}
```

#### Response (500 Error):

```json
{
  "status": "error",
  "message": "Failed to send notification: [error details]"
}
```

### Health Check

**GET** `/health/`

Verifica el estado del servicio.

#### Response:

```json
{
  "status": "healthy",
  "service": "notification-service",
  "smtp_configured": true
}
```

## Probar el Servicio

### Usando curl

```bash
curl -X POST "http://localhost:8080/notify/" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Test Notification",
    "message": "This is a test message",
    "email": "test@example.com"
  }'
```

### Usando Python

```python
import requests

url = "http://localhost:8080/notify/"
payload = {
    "subject": "Test Notification",
    "message": "This is a test message",
    "email": "test@example.com"
}

response = requests.post(url, json=payload)
print(response.json())
```

### Usando Postman

1. Método: `POST`
2. URL: `http://localhost:8080/notify/`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON):
```json
{
  "subject": "Test",
  "message": "Test message",
  "email": "test@example.com"
}
```

## Estructura del Proyecto

```
proyecto-notifications/
├── app/
│   ├── __init__.py
│   ├── main.py          # Punto de entrada FastAPI
│   ├── config.py        # Configuración y variables de entorno
│   └── email_service.py # Lógica de envío de emails
├── requirements.txt
├── Dockerfile
├── .env.example
└── README.md
```

## Construir Imagen Docker

```bash
docker build -t proyecto-notifications:latest .
```

### Ejecutar contenedor localmente

```bash
docker run -p 8080:8080 \
  -e EMAIL_HOST=sandbox.smtp.mailtrap.io \
  -e EMAIL_PORT=2525 \
  -e EMAIL_HOST_USER=your_user \
  -e EMAIL_HOST_PASSWORD=your_password \
  proyecto-notifications:latest
```

## Configuración Avanzada

### Usar Gmail como SMTP

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=your_email@gmail.com
```

**Nota:** Para Gmail, necesitas crear una [contraseña de aplicación](https://support.google.com/accounts/answer/185833).

## Testing

### Test manual del endpoint

```bash
# Health check
curl http://localhost:8080/health/

# Enviar notificación de prueba
curl -X POST http://localhost:8080/notify/ \
  -H "Content-Type: application/json" \
  -d '{"subject":"Test","message":"Hello","email":"test@test.com"}'
```

## Logs y Debugging

### Ver logs en tiempo real

```bash
uvicorn app.main:app --reload --port 8080 --log-level debug
```

### Niveles de log disponibles:

- `critical`
- `error`
- `warning`
- `info` (default)
- `debug`

## Solución de Problemas

### Error: "Failed to send notification"

1. Verifica las credenciales SMTP en `.env`
2. Comprueba que el puerto esté correcto (2525 para Mailtrap)
3. Verifica que `EMAIL_USE_TLS` esté en `True`

### Error: "Connection refused"

1. Verifica que el servicio esté ejecutándose
2. Comprueba el puerto (debe ser 8080)
3. Revisa el firewall

### No llegan los correos

1. Verifica Mailtrap inbox
2. Revisa la consola del servicio por errores
3. Comprueba que el email en el payload sea válido

## Rendimiento

### Configuración de Workers

Para producción, usa múltiples workers:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080 --workers 4
```

### Timeout

Configura timeout para requests largos:

```bash
uvicorn app.main:app --timeout-keep-alive 75
```

## Seguridad

- Nunca subas el archivo `.env` al repositorio
- Usa variables de entorno en producción
- Implementa rate limiting
- Valida y sanitiza inputs
- Usa HTTPS en producción

## Dependencias Principales

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-dotenv==1.0.0
aiosmtplib==3.0.1
```

## Integración con Backend

El backend llama a este servicio cuando se crea un usuario:

```python
# En users/signals.py del backend
import requests

notification_url = os.getenv("NOTIFICATION_URL")
payload = {
    "subject": f"Nuevo usuario: {instance.name}",
    "message": f"Se creó el usuario {instance.name} ({instance.email}), ({instance.phone})",
    "email": instance.email
}

response = requests.post(notification_url, json=payload, timeout=5)
```

## Monitoreo

### Health Check Endpoint

```bash
# Verificar estado
curl http://localhost:8080/health/

# Respuesta esperada
{
  "status": "healthy",
  "service": "notification-service",
  "smtp_configured": true
}
```

## Autores

- Ian Camilo - Proyecto Final

## 🔗 Enlaces Útiles

- [Mailtrap](https://mailtrap.io/)
- [Uvicorn Documentation](https://www.uvicorn.org/)