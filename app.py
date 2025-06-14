from flask import Flask, request, jsonify
from datetime import date
from docx import Document
from fpdf import FPDF
from bs4 import BeautifulSoup
import requests
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText

app = Flask(__name__)

RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL", "a.utrera@bevicis.com")
SENDER_EMAIL = "a.utrera@bevicis.com"
APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")

def auditar_url(url):
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        html = r.text.lower()

        def presente(busqueda):
            return "Sí" if any(t in html for t in busqueda) else "No"

        resultado = [
            ("Certificado HTTPS", "Sí" if url.startswith("https://") else "No"),
            ("Aviso legal", presente(["aviso legal", "/aviso-legal"])),
            ("Política de privacidad", presente(["privacidad", "/privacidad"])),
            ("Política de cookies", presente(["cookies", "/cookies"])),
            ("Banner de cookies", presente(["cookiebot", "consentmanager", "cookielaw"])),
            ("Formulario de contacto", "Sí" if soup.find("form") else "No"),
            ("Google Analytics", presente(["gtag", "google-analytics", "ga.js"])),
            ("Facebook Pixel", presente(["fbq", "facebook.com/tr"]))
        ]
        return resultado
    except Exception as e:
        return [("Error al acceder a la web", "No se pudo analizar", str(e))]

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

@app.route("/auditar", methods=["POST"])
def auditar():
    data = request.get_json()
    empresa = data.get("empresa", "Cliente")
    url = data.get("url", "https://example.com")
    tipo = data.get("tipo", "informativa")
    fecha = date.today().isoformat()

    tabla = auditar_url(url)

    word_name = f"Informe_{empresa}_{fecha}.docx".replace(" ", "_")
    pdf_name = f"Informe_{empresa}_{fecha}.pdf".replace(" ", "_")

    doc = Document()
    doc.add_picture("logo.png", width=None)
    doc.add_heading("Informe de Auditoría Legal Web", level=1)
    doc.add_paragraph(f"Cliente: {empresa}")
    doc.add_paragraph(f"Web auditada: {url}")
    doc.add_paragraph(f"Fecha de auditoría: {fecha}")
    doc.add_heading("Resumen del análisis", level=2)

    table = doc.add_table(rows=1, cols=2)
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "Área auditada"
    hdr_cells[1].text = "¿Cumple?"
    for item in tabla:
        row_cells = table.add_row().cells
        row_cells[0].text = item[0]
        row_cells[1].text = item[1]

    doc.add_heading("Recomendaciones", level=2)
    for item in tabla:
        if item[1] == "No":
            doc.add_paragraph(f"🔴 Revisar el punto: {item[0]}", style="List Bullet")

    doc.add_paragraph("Este informe ha sido generado por BEVICIS.")
    doc.save(word_name)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.image("logo.png", x=10, y=8, w=40)
    pdf.ln(30)
    pdf.cell(200, 10, txt="Informe de Auditoría Legal Web", ln=True, align="C")
    pdf.cell(200, 10, txt=f"Cliente: {empresa}", ln=True)
    pdf.cell(200, 10, txt=f"Web auditada: {url}", ln=True)
    pdf.cell(200, 10, txt=f"Fecha: {fecha}", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(60, 10, "Área auditada", 1)
    pdf.cell(40, 10, "¿Cumple?", 1)
    pdf.ln()
    pdf.set_font("Arial", size=12)
    for item in tabla:
        pdf.cell(60, 10, item[0], 1)
        pdf.cell(40, 10, item[1], 1)
        pdf.ln()
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Recomendaciones:", ln=True)
    pdf.set_font("Arial", size=12)
    for item in tabla:
        if item[1] == "No":
            pdf.cell(200, 10, f"- Revisar el punto: {item[0]}", ln=True)
    pdf.ln(10)
    pdf.cell(200, 10, "Este informe ha sido generado por BEVICIS.", ln=True)
    pdf.output(pdf_name)

    asunto = f"Informe de Auditoría Legal Web – {empresa}"
    cuerpo = (
        f"Hola Alejandro,

"
        f"Adjunto encontrarás el informe de auditoría legal para {empresa} realizado el {fecha}.

"
        f"Saludos,
Sistema automático de auditorías – BEVICIS"
    )
    enviar_email(asunto, cuerpo, [word_name, pdf_name])

    return jsonify({"status": "ok", "mensaje": "Informe auditado y enviado por correo."})

@app.route("/", methods=["GET"])
def home():
    return "API de auditorías BEVICIS operativa"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
