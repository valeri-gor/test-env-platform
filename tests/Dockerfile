FROM python:3.11-slim
WORKDIR /tests
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY test_e2e.py .
CMD ["pytest", "-v", "--alluredir=/allure-results"]
