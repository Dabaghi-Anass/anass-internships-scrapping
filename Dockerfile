FROM python:3.11-slim

RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN echo "0 0 * * * cd /app && /usr/local/bin/python /app/linkedin.py >> /var/log/cron.log 2>&1" > /etc/cron.d/linkedin-cron

RUN chmod 0644 /etc/cron.d/linkedin-cron

RUN crontab /etc/cron.d/linkedin-cron

RUN touch /var/log/cron.log

RUN echo '#!/bin/bash\n\
cron\n\
uvicorn server:app --host 0.0.0.0 --port 8000\n\
' > /app/start.sh && chmod +x /app/start.sh

EXPOSE 8000

CMD ["uvicorn", "server:app"]