# Použitie oficiálneho Python kontajnera ako základu
FROM python:3.10

# Pracovný adresár v kontajneri
WORKDIR /app

# Kopírovanie zdrojových súborov do pracovného adresára v kontajneri
COPY . /app

# Inštalácia závislostí
RUN pip install -r requirements.txt

# Exponovanie portu, na ktorom beží aplikácia
EXPOSE 5000

COPY requirements.txt .

# Spustenie aplikácie
CMD [ "python", "app.py" ]