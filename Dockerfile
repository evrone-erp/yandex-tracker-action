FROM python:3.9-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .

RUN set -ex; \
  pip install --upgrade pip; \
  pip install -r requirements.txt

COPY . .

ENTRYPOINT [ "/entrypoint.sh" ]
CMD ["python", "/main.py"]
