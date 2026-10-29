FROM python:3.11-slim
# Deps con wheels manylinux: doctor esperado 9/9 sin modelos (fail-closed OK)
RUN pip install --no-cache-dir numpy pillow tflite-runtime cryptography
WORKDIR /agf
COPY . .
RUN python agf.py doctor || true
CMD ["python", "agf.py", "doctor"]
