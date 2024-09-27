# Dockerfile
FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

# Cài đặt các gói cần thiết cho Chrome và ChromeDriver
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    gnupg \
    --no-install-recommends

# Cài đặt các gói cần thiết cho Chrome
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    gnupg \
    --no-install-recommends

# Tải về và thêm key của Google Chrome
RUN curl -sSL https://dl.google.com/linux/linux_signing_key.pub | apt-key add -

# Thêm nguồn APT của Chrome vào danh sách
RUN echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

# Cài đặt Google Chrome
RUN apt-get update && apt-get install -y \
    google-chrome-stable \
    --no-install-recommends

# Cài đặt Flask, Selenium và chromedriver-autoinstaller cho Python
RUN pip install selenium chromedriver-autoinstaller
# Set working directory
WORKDIR /app

# Copy requirements.txt file and install dependencies
COPY requirements.txt .

RUN pip install chromedriver-autoinstaller
# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port 5000 for Flask
EXPOSE 5000
CMD python init_db.py
#ENTRYPOINT ["python", "app.py", "run"]
