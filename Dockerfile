FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y ffmpeg curl

WORKDIR /app

# Install Python requirements, including pydub and numpy
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src /app/src

ENV PYTHONPATH=/app/src

CMD ["uvicorn", "--app-dir", "src", "sdc.api:app", "--host", "0.0.0.0", "--port", "8000"]
