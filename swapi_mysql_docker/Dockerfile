FROM apache/airflow:2.9.2
# Install extra Python deps into the active Airflow virtualenv as the non-root 'airflow' user
USER airflow
RUN python -m pip install --no-cache-dir requests pymysql
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
