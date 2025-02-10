FROM python:3.10.15-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY StocksService/stock_portfolio.py .
COPY StocksService/stock_portfolio_API.py .
COPY StocksService/run.py .


ENV FLASK_APP=stock-portfolio.py
ENV NINJA_API_KEY=T6x6QsSBjaxT+BssCEg4VQ==wwU7bHC7P9hlXitc
EXPOSE 8000

CMD ["python", "run.py"]