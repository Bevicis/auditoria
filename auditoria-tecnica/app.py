from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import time

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "API BEVICIS – Auditoría Técnica (CDP) en Render"

@app.route("/auditar", methods=["POST"])
def auditar():
    data = request.get_json()
    empresa = data.get("empresa", "Empresa")
    url = data.get("url")

    options = Options()
    options.binary_location = "/usr/bin/chromium"
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(10)

    logs = driver.get_log("performance")
    scripts_detectados = [json.loads(entry["message"])["message"]
                          for entry in logs
                          if "Network.requestWillBeSent" in entry["message"]]

    urls = [m["params"]["request"]["url"] for m in scripts_detectados if "request" in m["params"]]

    def contiene(patrones):
        return any(any(p in u for p in patrones) for u in urls)

    resultado = {
        "empresa": empresa,
        "Cookiebot": "sí" if contiene(["cookiebot"]) else "no",
        "Google Tag Manager": "sí" if contiene(["gtm.js", "googletagmanager"]) else "no",
        "Google Analytics": "sí" if contiene(["google-analytics", "gtag/js", "ga.js"]) else "no",
        "Facebook Pixel": "sí" if contiene(["facebook.com/tr", "fbq"]) else "no"
    }

    driver.quit()
    return jsonify(resultado)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
