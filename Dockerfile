FROM python:3.9

ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE order_project.settings

WORKDIR /code

COPY requirements.txt /code/
RUN pip install -r requirements.txt

COPY . /code/

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]