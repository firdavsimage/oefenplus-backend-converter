# Python bazaviy imij
FROM python:3.10-slim

# Ishchi papkani belgilash
WORKDIR /app

# Talablar faylini nusxalash va o‘rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Loyihani ichkariga nusxalash
COPY . .

# Portni ochish (5000 — Flask porti)
EXPOSE 5000

# Flask appni Gunicorn orqali ishga tushirish
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
