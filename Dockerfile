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

# Inter
RUN curl -L https://github.com/rsms/inter/releases/download/v4.0/Inter-4.0.zip \
    -o /tmp/inter.zip \
    && unzip /tmp/inter.zip -d /tmp/inter \
    && mkdir -p /usr/share/fonts/truetype/inter \
    && find /tmp/inter -name "*.ttf" -exec cp {} /usr/share/fonts/truetype/inter/ \; \
    && rm -rf /tmp/inter /tmp/inter.zip

# Raleway
RUN curl -L "https://fonts.google.com/download?family=Raleway" \
    -o /tmp/raleway.zip \
    && unzip /tmp/raleway.zip -d /tmp/raleway \
    && mkdir -p /usr/share/fonts/truetype/raleway \
    && find /tmp/raleway -name "*.ttf" -not -path "*/static/*" -exec cp {} /usr/share/fonts/truetype/raleway/ \; \
    && rm -rf /tmp/raleway /tmp/raleway.zip

# Lato
RUN curl -L "https://fonts.google.com/download?family=Lato" \
    -o /tmp/lato.zip \
    && unzip /tmp/lato.zip -d /tmp/lato \
    && mkdir -p /usr/share/fonts/truetype/lato \
    && find /tmp/lato -name "*.ttf" -exec cp {} /usr/share/fonts/truetype/lato/ \; \
    && rm -rf /tmp/lato /tmp/lato.zip

RUN fc-cache -fv

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]