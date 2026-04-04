cat > README.md << 'EOF'
# 🚀 Task Manager API

REST API для управления задачами с авторизацией пользователей, ролями и категориями.

Проект разработан на FastAPI с использованием PostgreSQL, SQLAlchemy и Docker.

---

# 📌 Возможности

- Регистрация пользователей  
- Авторизация (JWT токены)  
- Роли пользователей (admin / user)  
- Создание категорий  
- Создание задач  
- Обновление задач  
- Связь задач с пользователями и категориями  
- Docker-контейнеризация  
- PostgreSQL база данных  
- Swagger документация API  

---

# 🛠 Технологии

- Python 3.11  
- FastAPI  
- SQLAlchemy  
- PostgreSQL  
- Docker  
- JWT Authentication  
- Pydantic  

---

# ⚙️ Установка и запуск

## Клонировать репозиторий

git clone https://github.com/DemarevMaxim/Task_Manager_API.git  
cd Task_Manager_API  

## Запуск через Docker

docker compose up --build  

После запуска открой:

http://localhost:8000/docs  

---

# 🔐 Авторизация

POST /register

{
 "username": "admin",
 "password": "123",
 "role": "admin"
}

POST /login

{
 "username": "admin",
 "password": "123"
}

---

# 📂 Основные эндпоинты

POST /register — регистрация  
POST /login — авторизация  

POST /categories — создать категорию  
GET /categories — получить список  

POST /tasks — создать задачу  
PATCH /tasks/{task_id} — обновить задачу  

---

# 🎯 Цель проекта

Учебный backend-проект для практики FastAPI, JWT и Docker.

---

# 👨‍💻 Автор

Максим Демарев  
GitHub: https://github.com/DemarevMaxim

EOF
