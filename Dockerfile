# Python bazaviy imij
FROM python:3.10-slim

# Ishchi papkani belgilash
WORKDIR /app

# Talablar faylini ko‘chirish va o‘rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kodni ko‘chirish
COPY . .

# Port ochish
EXPOSE 10000

# Loyihani ishga tushurish (gunicorn yordamida)
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
