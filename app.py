
from flask import Flask, request, jsonify
from docx import Document
from fpdf import FPDF
import os
import datetime

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Webhook de auditoría activo."

@app.route("/auditar", methods=["POST"])
def auditar():
    data = request.get_json()
    empresa = data.get("empresa", "Cliente")
    url = data.get("url", "https://example.com")
    tipo = data.get("tipo", "informativa")
    email = data.get("email", "email@cliente.com")
    fecha = datetime.date.today().isoformat()

    # Crear Word
    doc = Document()
    doc.add_heading('Informe de Auditoría Legal Web', 0)
    doc.add_paragraph(f'Empresa: {empresa}')
    doc.add_paragraph(f'URL: {url}')
    doc.add_paragraph(f'Tipo de página: {tipo}')
    doc.add_paragraph(f'Email de contacto: {email}')
    doc.add_paragraph(f'Fecha de auditoría: {fecha}')
    doc.add_paragraph('Cumplimiento RGPD + LSSI: TODO')

    word_name = f"Informe_{empresa}_{fecha}.docx".replace(" ", "_")
    doc.save(word_name)

    # Crear PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Informe de Auditoría Legal Web", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Empresa: {empresa}", ln=True)
    pdf.cell(200, 10, txt=f"URL: {url}", ln=True)
    pdf.cell(200, 10, txt=f"Tipo: {tipo}", ln=True)
    pdf.cell(200, 10, txt=f"Email: {email}", ln=True)
    pdf.cell(200, 10, txt=f"Fecha: {fecha}", ln=True)

    pdf_name = f"Informe_{empresa}_{fecha}.pdf".replace(" ", "_")
    pdf.output(pdf_name)

    return jsonify({
        "status": "ok",
        "empresa": empresa,
        "word_file": word_name,
        "pdf_file": pdf_name
    })

if __name__ == "__main__":
import os
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
