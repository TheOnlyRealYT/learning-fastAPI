FROM python:3.14


WORKDIR /gym


COPY ./requirements.txt /gym/requirements.txt


RUN pip install --no-cache-dir --upgrade -r /gym/requirements.txt


COPY . /gym/app


CMD ["fastapi", "run", "app/app.py", "--port", "80"]