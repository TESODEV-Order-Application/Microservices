FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ARG conn_str
ENV conn_str=${conn_str}

ARG rabbit_username
ENV rabbit_username=${rabbit_username}

ARG rabbit_password
ENV rabbit_password=${rabbit_password}

ARG ip
ENV ip=${ip}

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]