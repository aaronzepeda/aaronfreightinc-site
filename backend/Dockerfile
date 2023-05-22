# project/backend/Dockerfile

# Install dependencies
FROM ubuntu:latest
RUN apt-get update
RUN apt-get install -y tesseract-ocr
RUN apt-get install -y poppler-utils
RUN apt-get install -y pango1.0-tools


FROM python:3.10.7
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN touch .env
RUN touch dependencies/
RUN python manage.py makemigrations
RUN python manage.py migrate
# RUN echo "yes" | python manage.py collectstatic
CMD python manage.py collectstatic --noinput && gunicorn ---bind 0.0.0.0:8000 --worker-class=gevent --worker-connections=1000 --workers=5 backend.wsgi
