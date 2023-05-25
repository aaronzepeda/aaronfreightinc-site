# project/backend/Dockerfile

FROM python:3.10.7
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY . /app
WORKDIR /app
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 tesseract-ocr poppler-utils pango1.0-tools -y
RUN pip install -r requirements.txt
RUN touch .env
# RUN echo "yes" | python manage.py collectstatic
RUN python manage.py collectstatic --noinput
CMD python manage.py makemigrations && python manage.py migrate && gunicorn backend.wsgi:application --bind 0.0.0.0:8000
