FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    chromium chromium-driver fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 \
    libatk1.0-0 libcups2 libdbus-1-3 libgdk-pixbuf2.0-0 libnspr4 libnss3 libx11-xcb1 libxcomposite1 \
    libxdamage1 libxrandr2 xdg-utils wget unzip curl

ENV CHROME_BIN=/usr/bin/chromium

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8080
CMD ["python", "app.py"]
