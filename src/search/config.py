# from pathlib import Path
# print('*' * 100)
# print('Running' if __name__ == '__main__' else 'Importing', Path(__file__).resolve())

USER = 'elastic'
ELASTIC_PASSWORD = 'hLdAqRF9CMXiIZgwd-pT'
ELASTIC_PORT = "localhost:9200"
PATH_TO_CRT = 'security/http_ca.crt'
ELASTIC_URL = f"https://{USER}:{ELASTIC_PASSWORD}@{ELASTIC_PORT}"