# ---------- Dockerfile ----------


dockerfile = """
FROM python:3.10
WORKDIR /app
COPY . /app
RUN pip install fastapi uvicorn python-multipart
EXPOSE 10000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
"""


with open("Dockerfile", "w") as f:
f.write(dockerfile)
