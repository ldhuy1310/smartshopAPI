# Dockerfile
FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    gnupg \
    --no-install-recommends

RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    gnupg \
    --no-install-recommends

RUN curl -sSL https://dl.google.com/linux/linux_signing_key.pub | apt-key add -

RUN echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

RUN apt-get update && apt-get install -y \
    google-chrome-stable \
    --no-install-recommends

RUN pip install selenium chromedriver-autoinstaller
WORKDIR /app

COPY requirements.txt .

RUN pip install chromedriver-autoinstaller
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
CMD python init_db.py
#ENTRYPOINT ["python", "app.py", "run"]
