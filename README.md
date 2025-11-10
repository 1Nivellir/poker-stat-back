# 🎰 Poker Tournament API

API для управления турнирами по покеру с полной системой аутентификации.

## 🚀 Быстрый старт

### Требования
- Python 3.13+
- PostgreSQL

### Установка

1. Клонируйте репозиторий
```bash
git clone <repository-url>
cd new-back
```

2. Создайте виртуальное окружение и активируйте его
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

3. Установите зависимости
```bash
pip install -r requirements.txt
```

4. Настройте переменные окружения

Создайте файл `.env` в корне проекта:
```env
# Database
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin
POSTGRES_DB=poker

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=11520  # 8 дней
REFRESH_TOKEN_EXPIRE_DAYS=30
```

5. Запустите PostgreSQL (используя Docker)
```bash
docker-compose up -d
```

6. Примените миграции
```bash
alembic upgrade head
```

7. Запустите сервер
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API будет доступен по адресу: http://localhost:8000

## 📚 Документация

- **Interactive API Docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative API Docs**: http://localhost:8000/redoc (ReDoc)

## 📡 API Эндпоинты

### 🔐 Аутентификация (публичные)

#### Регистрация
```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe"
}
```

#### Вход
```bash
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=password123
```

**Ответ:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

#### Обновление токена
```bash
POST /api/v1/auth/refresh-token
Content-Type: application/json

{
  "refresh_token": "eyJ..."
}
```

**Ответ:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

#### Получить информацию о текущем пользователе
```bash
GET /api/v1/auth/me
Authorization: Bearer eyJ...
```

### 🏆 Турниры (требуют авторизации)

#### Создать турнир
```bash
POST /api/v1/tournaments/
Authorization: Bearer eyJ...
Content-Type: application/json

{
  "name": "Sunday Tournament",
  "play_date": "2024-01-15T18:00:00Z",
  "buy_in": 100,
  "re_entry": 50,
  "bounty": 25,
  "prize": 500
}
```

#### Получить турниры
```bash
# Турниры за сегодня (по умолчанию)
GET /api/v1/tournaments/my_tourney/
Authorization: Bearer eyJ...

# С фильтрацией по датам
GET /api/v1/tournaments/my_tourney/?start_date=2024-01-01T00:00:00Z&end_date=2024-01-31T23:59:59Z
Authorization: Bearer eyJ...
```

#### Обновить турнир
```bash
PUT /api/v1/tournaments/{tourney_id}
Authorization: Bearer eyJ...
Content-Type: application/json

{
  "name": "Updated Tournament Name",
  "buy_in": 150
}
```

#### Удалить турнир
```bash
DELETE /api/v1/tournaments/{tourney_id}
Authorization: Bearer eyJ...
```

## 🎯 Основные возможности

### Аутентификация
- ✅ Регистрация пользователей
- ✅ Вход с JWT токенами (access + refresh)
- ✅ Обновление токенов
- ✅ Защищенные эндпоинты

### Турниры
- ✅ Создание турниров
- ✅ Получение списка турниров с фильтрацией по датам
- ✅ Автоматическая фильтрация (турниры за сегодня по умолчанию)
- ✅ Обновление турниров (PUT)
- ✅ Удаление турниров
- ✅ Проверка прав доступа (пользователь может управлять только своими турнирами)

## 🏗️ Структура проекта

```
new-back/
├── alembic/              # Миграции базы данных
│   └── versions/
├── app/
│   ├── api/
│   │   ├── routes/       # API роуты
│   │   │   ├── auth.py   # Аутентификация и регистрация
│   │   │   └── tourney.py # Турниры
│   │   ├── deps.py       # Зависимости (DB, CurrentUser)
│   │   └── main.py       # API роутер
│   ├── core/
│   │   ├── config.py     # Настройки
│   │   ├── db.py         # База данных
│   │   └── security.py   # JWT, хеширование
│   ├── crud.py           # CRUD операции
│   ├── models.py         # SQLModel модели
│   ├── middleware.py     # Middleware аутентификации
│   └── main.py           # FastAPI app
├── docker-compose.yaml   # PostgreSQL + pgAdmin
├── requirements.txt      # Python зависимости
└── alembic.ini          # Alembic конфигурация
```

## 🔧 Технологии

- **FastAPI** - современный веб-фреймворк
- **SQLModel** - ORM на основе Pydantic и SQLAlchemy
- **PostgreSQL** - база данных
- **Alembic** - миграции базы данных
- **JWT** - аутентификация
- **Bcrypt** - хеширование паролей
- **Pydantic** - валидация данных

## 🧪 Тестирование API

### С помощью curl

Регистрация:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","full_name":"Test User"}'
```

Вход:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=password123"
```

Создание турнира:
```bash
curl -X POST http://localhost:8000/api/v1/tournaments/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Sunday Tournament","buy_in":100}'
```

### С помощью Swagger UI

Перейдите на http://localhost:8000/docs и используйте интерактивную документацию.

## 🗄️ База данных

### Создание миграции
```bash
alembic revision --autogenerate -m "Description"
```

### Применение миграций
```bash
alembic upgrade head
```

### Откат миграции
```bash
alembic downgrade -1
```

## 🔒 Безопасность

- Пароли хешируются с помощью bcrypt
- JWT токены подписываются SECRET_KEY
- Access токены имеют ограниченный срок действия (8 дней по умолчанию)
- Refresh токены действуют дольше (30 дней по умолчанию)
- Проверка прав доступа к турнирам (пользователь может управлять только своими турнирами)

## 🚨 Коды ошибок

- `400` - Плохой запрос (например, email уже существует)
- `401` - Неавторизован (неверный токен или credentials)
- `403` - Запрещено (нет прав доступа)
- `404` - Не найдено
- `422` - Ошибка валидации

## 📝 Лицензия

MIT

