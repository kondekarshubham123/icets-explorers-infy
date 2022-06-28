FROM python:3.8.13-slim
ADD . /usr/app/icets-explorers-infy
WORKDIR /usr/app/icets-explorers-infy
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python","manage.py"]