# Python 3.10 asosidagi minimal imij
FROM python:3.10-slim

# Ishchi katalog
WORKDIR /app

# Tizimga kerakli kutubxonalarni o‘rnatish
RUN apt-get update && apt-get install -y curl unzip && rm -rf /var/lib/apt/lists/*

# Talablar faylini nusxalash va kutubxonalarni o‘rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Loyihani nusxalash
COPY . .

# Portni ochish
EXPOSE 5000

# Flask appni ishga tushurish
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
