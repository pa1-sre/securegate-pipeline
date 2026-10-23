FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install - requirements.txt
COPY . .
CMD ["python", "app.py"]
