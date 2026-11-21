FROM apache/airflow:3.4.0

USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends openjdk-21-jre-headless && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64

USER airflow

RUN pip install --no-cache-dir \
    "apache-airflow==3.4.0" \
    "pyspark==4.0.1" \
    "pandas==2.3.3" \
    "pyarrow==22.0.0" \
    "mysql-connector-python" \
    "openpyxl==3.1.5" \
    "python-dotenv==1.1.1" \
    "loguru==0.7.3"
