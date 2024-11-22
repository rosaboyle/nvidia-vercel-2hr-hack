FROM python:3.10

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY main.py ./

CMD ["uvicorn", "router:app", "--host", "0.0.0.0", "--port", "8000"]
