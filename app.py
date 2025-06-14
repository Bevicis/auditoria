from flask import Flask, request, jsonify
from datetime import date
from docx import Document
from fpdf import FPDF
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText

app = Flask(__name__)

RECEIVER_EMAIL = "utrera.alejandro@gmail.com"
SENDER_EMAIL = "utrera.alejandro@gmail.com"
APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")

def enviar_email(asunto, cuerpo, archivos):
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = asunto
    msg.attach(MIMEText(cuerpo, "plain"))

    for archivo in archivos:
        with open(archivo, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(archivo))
        part["Content-Disposition"] = f'attachment; filename="{os.path.basename(archivo)}"'
        msg.attach(part)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)

@app.route("/", methods=["GET"])
def home():
    return "Webhook de auditoría con envío por email activo."

@app.route("/auditar", methods=["POST"])
def auditar():
    data = request.get_json()
    empresa = data.get("empresa", "Cliente")
    url = data.get("url", "https://example.com")
    tipo = data.get("tipo", "informativa")
    fecha = date.today().isoformat()

    word_name = f"Informe_{empresa}_{fecha}.docx".replace(" ", "_")
    pdf_name = f"Informe_{empresa}_{fecha}.pdf".replace(" ", "_")

    doc = Document()
    doc.add_heading("Informe de Auditoría Legal Web", 0)
    doc.add_paragraph(f"Empresa: {empresa}")
    doc.add_paragraph(f"URL: {url}")
    doc.add_paragraph(f"Tipo de página: {tipo}")
    doc.add_paragraph(f"Fecha de auditoría: {fecha}")
    doc.add_paragraph("Cumplimiento RGPD + LSSI: TODO")
    doc.save(word_name)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Informe de Auditoría Legal Web", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Empresa: {empresa}", ln=True)
    pdf.cell(200, 10, txt=f"URL: {url}", ln=True)
    pdf.cell(200, 10, txt=f"Tipo: {tipo}", ln=True)
    pdf.cell(200, 10, txt=f"Fecha: {fecha}", ln=True)
    pdf.output(pdf_name)

    asunto = f"Informe de Auditoría Legal Web – {empresa}"
    cuerpo = (
    f"Hola Alejandro,\n\n"
    f"Adjunto encontrarás el informe de auditoría legal para {empresa} realizado el {fecha}.\n\n"
    f"Saludos,\nSistema automático de auditorías."
)

    enviar_email(asunto, cuerpo, [word_name, pdf_name])

    return jsonify({"status": "ok", "mensaje": "Correo enviado con los informes adjuntos."})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
