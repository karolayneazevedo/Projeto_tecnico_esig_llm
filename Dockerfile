FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential curl git

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
EXPOSE 8501

CMD ["sh", "-c", "streamlit run app/views/front.py & python app.py"]
