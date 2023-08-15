FROM python:3.11-slim

RUN apt-get upgrade -y && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential git && \
    apt-get clean -y

WORKDIR /app

COPY requirements.txt .
RUN pip install -r /app/requirements.txt

# With `docker compose`, dev. directory already mounted at /app
#COPY . .

CMD ["./start.sh"]
