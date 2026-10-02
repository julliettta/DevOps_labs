# Lab1 — nginx: reverse proxy, балансировка, HTTPS, виртуальные хосты

Nginx выступает точкой входа перед сервисом из Лабы 0: терминирует HTTPS, 
раздаёт статику фронтенда, проксирует API на два инстанса бэкенда 
с балансировкой нагрузки, и переживает падение одного из бэкендов.

## Стек

- **Reverse proxy / балансировщик:** nginx (Docker, образ nginx:alpine)
- **Backend:** Python, Flask (две копии на разных портах)
- **База данных:** PostgreSQL (Docker-контейнер, общий для обоих инстансов)
- **Сертификат:** самоподписанный SSL (openssl)


## Как запустить

### 1. Поднять базу данных

```bash
docker run --name lab0-postgres -e POSTGRES_PASSWORD=pass -e POSTGRES_DB=lab0 -p 5432:5432 -d postgres
```

### 2. Запустить два инстанса бэкенда

```bash
cd backend
pip install -r requirements.txt

PORT=5001 INSTANCE_ID=backend-1 python app.py   # в одном терминале
PORT=5002 INSTANCE_ID=backend-2 python app.py   # во втором терминале
```

### 3. Прописать домены в hosts-файл

Добавить в `C:\Windows\System32\drivers\etc\hosts` (от администратора):
127.0.0.1 lab1.local
127.0.0.1 site2.local


### 4. Создать сертификат (если ещё не создан)

```bash
cd nginx
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout certs/selfsigned.key -out certs/selfsigned.crt -subj "//CN=lab1.local"
```

### 5. Создать .htpasswd (если ещё не создан)

```bash
docker run --rm httpd:alpine htpasswd -nb admin admin123 > nginx/.htpasswd
```

### 6. Запустить nginx

```bash
MSYS_NO_PATHCONV=1 docker run -d --name lab1-nginx \
  -p 80:80 -p 443:443 \
  --add-host=host.docker.internal:host-gateway \
  -v "$(pwd)/nginx/nginx.conf:/etc/nginx/nginx.conf" \
  -v "$(pwd)/nginx/certs:/etc/nginx/certs" \
  -v "$(pwd)/nginx/errors:/etc/nginx/errors" \
  -v "$(pwd)/nginx/.htpasswd:/etc/nginx/.htpasswd" \
  -v "$(pwd)/frontend:/usr/share/nginx/frontend" \
  -v "$(pwd)/docs:/usr/share/nginx/docs" \
  -v "$(pwd)/site2:/usr/share/nginx/site2" \
  nginx:alpine
```

### 7. Открыть сайт

`https://lab1.local` (подтвердить предупреждение о самоподписанном сертификате).

Логин/пароль для `/admin`: `admin` / `admin123`
