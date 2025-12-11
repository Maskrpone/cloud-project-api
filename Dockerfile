FROM python:3.13-slim

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    unixodbc-dev \
		curl

RUN curl -sSL -O https://packages.microsoft.com/config/debian/11/packages-microsoft-prod.deb
RUN dpkg -i packages-microsoft-prod.deb
RUN rm packages-microsoft-prod.deb

RUN apt-get update && \
		ACCEPT_EULA=Y apt-get install -y msodbcsql18 && \
		ACCEPT_EULA=Y apt-get install -y mssql-tools18

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

CMD ["fastapi", "run", "app/main.py", "--port", "80"]
