import os
import smtplib
from email.message import EmailMessage
import httpx
import psycopg2
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Test Appointment Service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_URL = os.getenv("DATABASE_URL", "postgresql://qa_user:qa_pass@postgres:5432/test_db")
WIREMOCK_URL = os.getenv("WIREMOCK_URL", "http://wiremock:8080")
SMTP_HOST = os.getenv("SMTP_HOST", "mailpit")
SMTP_PORT = int(os.getenv("SMTP_PORT", "1025"))


class AppointmentIn(BaseModel):
    client_name: str
    email: str
    slot_time: str


def get_conn():
    return psycopg2.connect(DB_URL)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/appointments")
def list_appointments():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, client_name, email, slot_time, status FROM appointments ORDER BY id;")
        rows = cur.fetchall()
    return [
        {"id": r[0], "client_name": r[1], "email": r[2], "slot_time": r[3], "status": r[4]}
        for r in rows
    ]


@app.post("/api/appointments", status_code=201)
def create_appointment(item: AppointmentIn):
    # 1. Проверка внешнего сервиса через заглушку WireMock
    try:
        resp = httpx.post(f"{WIREMOCK_URL}/api/verify-slot", json={"slot": item.slot_time}, timeout=3.0)
        if resp.status_code != 200:
            raise HTTPException(status_code=502, detail="External verification failed")
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="WireMock unavailable")

    # 2. Сохранение в тестовую БД
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO appointments (client_name, email, slot_time) VALUES (%s, %s, %s) RETURNING id;",
            (item.client_name, item.email, item.slot_time),
        )
        new_id = cur.fetchone()[0]
        conn.commit()

    # 3. Отправка письма в перехватчик Mailpit
    msg = EmailMessage()
    msg["Subject"] = f"Подтверждение записи #{new_id}"
    msg["From"] = "noreply@test-env.local"
    msg["To"] = item.email
    msg.set_content(f"Здравствуйте, {item.client_name}! Ваша запись на {item.slot_time} подтверждена.")
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.send_message(msg)

    return {"id": new_id, "status": "confirmed"}
