FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
COPY packages/ /packages/

RUN pip install --upgrade pip --no-index --find-links=/packages/ || true && \
    pip install --no-cache-dir --no-index --find-links=/packages/ -r requirements.txt && \
    pip install --no-index --find-links=/packages/ psycopg2-binary gunicorn

COPY . .

RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["gunicorn", "royelhotel.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]
