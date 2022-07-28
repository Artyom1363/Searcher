from pathlib import Path
print('Running' if __name__ == '__main__' else 'Importing', Path(__file__).resolve())
# print("config was imported")
USER = 'elastic'
ELASTIC_PASSWORD = 'hLdAqRF9CMXiIZgwd-pT'
ELASTIC_PORT = "localhost:9200"
PATH_TO_CRT = 'http_ca.crt'
ELASTIC_URL = f"https://{USER}:{ELASTIC_PASSWORD}@{ELASTIC_PORT}"