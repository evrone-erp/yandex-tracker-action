FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && pip install --upgrade --no-cache-dir pip wheel setuptools

COPY . .

RUN pip install -r requirements.txt

ENTRYPOINT [ "/entrypoint.sh" ]
CMD [ "python", "/main.py" ]
