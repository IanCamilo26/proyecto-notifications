from dotenv import load_dotenv
load_dotenv()   # carga variables desde .env en la raíz del proyecto-notifications

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import smtplib
import os
from email.message import EmailMessage

app = FastAPI(title="Notification Service")

class NotifyPayload(BaseModel):
    subject: str
    message: str
    email: EmailStr  # destinatario

def send_smtp_mail(subject: str, message: str, to_email: str):
    """
    Envía correo por SMTP usando variables de entorno.
    Lanza excepción si falla.
    """
    SMTP_HOST = os.getenv("EMAIL_HOST")
    SMTP_PORT = int(os.getenv("EMAIL_PORT", "587"))
    SMTP_USER = os.getenv("EMAIL_HOST_USER")
    SMTP_PASS = os.getenv("EMAIL_HOST_PASSWORD")
    FROM = os.getenv("DEFAULT_FROM_EMAIL", "noreply@example.com")
    USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() in ("1","true","yes")

    if not SMTP_HOST:
        raise RuntimeError("SMTP not configured (EMAIL_HOST missing)")

    msg = EmailMessage()
    msg["From"] = FROM
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(message)

    # conectar y enviar
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as smtp:
        if USE_TLS:
            smtp.starttls()
        if SMTP_USER and SMTP_PASS:
            smtp.login(SMTP_USER, SMTP_PASS)
        smtp.send_message(msg)

@app.post("/notify", status_code=204)
def notify(payload: NotifyPayload):
    """
    Recibe JSON {subject, message, email} y envía correo por SMTP.
    Retorna 204 No Content en éxito.
    """
    try:
        send_smtp_mail(payload.subject, payload.message, payload.email)
    except Exception as e:
        # registrar (stdout) y devolver 500
        print("Error sending mail:", e)
        raise HTTPException(status_code=500, detail=str(e))
    return None

@app.get("/health")
async def health():
    """Health check simple: responde 200 OK (útil para docker/k8s)."""
    return {"status": "ok"}

@app.get("/ready")
async def ready():
    """
    Readiness check: intenta conectarse al servidor SMTP si EMAIL_HOST está configurado.
    - Si EMAIL_HOST no está presente, devuelve 200 (no obligatorio en entorno local).
    - Si está presente, intenta abrir conexión TCP y devuelve 200 o 500 según resultado.
    """
    SMTP_HOST = os.getenv("EMAIL_HOST")
    SMTP_PORT = int(os.getenv("EMAIL_PORT", "587"))

    if not SMTP_HOST:
        # Si no hay SMTP configurado, consideramos el servicio 'ready' de todos modos.
        return {"ready": True, "reason": "smtp not configured"}

    try:
        # intentamos conectar de forma liviana (solo abrir socket vía smtplib)
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=5) as smtp:
            # no enviamos login ni correo, solo conexión
            pass
        return {"ready": True}
    except Exception as e:
        # si falla la conexión, devuelvo 503 para que orquestadores no envíen tráfico
        raise HTTPException(status_code=503, detail=f"smtp unreachable: {e}")