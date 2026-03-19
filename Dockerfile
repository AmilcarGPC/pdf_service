FROM python:3.11-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    libffi8 \
    shared-mime-info \
    fonts-liberation \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Descargar e instalar Inter desde GitHub (sin depender de Google Fonts en runtime)
RUN curl -L https://github.com/rsms/inter/releases/download/v4.0/Inter-4.0.zip \
    -o /tmp/inter.zip \
    && unzip /tmp/inter.zip -d /tmp/inter \
    && mkdir -p /usr/share/fonts/truetype/inter \
    && find /tmp/inter -name "*.ttf" -exec cp {} /usr/share/fonts/truetype/inter/ \; \
    && fc-cache -fv \
    && rm -rf /tmp/inter /tmp/inter.zip

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]