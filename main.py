from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import UserResponse
from database import (
    engine,
    Base,
    get_db
)

from models import User, Task, Category

from schemas import (
    UserCreate,
    UserResponse,
    TaskCreate,
    TaskResponse,
    TaskUpdate,
    CategoryCreate,
    CategoryResponse
)

from auth import (
    hash_password,
    verify_password,
    create_access_token
)

from fastapi.security import OAuth2PasswordBearer
from jose import jwt


app = FastAPI()

Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login"
)


# 📌 Получение пользователя по токену

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    payload = jwt.decode(
        token,
        "mysecretkey",
        algorithms=["HS256"]
    )

    user_id = payload.get("user_id")

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=401
        )

    return user


# 📌 Регистрация

@app.post("/register",
          response_model=UserResponse)

def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    hashed = hash_password(user.password)

    new_user = User(
        username=user.username,
        password=hashed,
        role=user.role
    )

    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    return new_user


# 📌 Логин

from fastapi.security import OAuth2PasswordRequestForm


@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    db_user = db.query(User).filter(
        User.username == form_data.username
    ).first()

    if not db_user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username"
        )

    if not verify_password(
        form_data.password,
        db_user.password
    ):
        raise HTTPException(
            status_code=400,
            detail="Incorrect password"
        )

    token = create_access_token(
        {"user_id": db_user.id}
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# 📌 Создание задачи

@app.post("/tasks",
          response_model=TaskResponse)

def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    new_task = Task(
        title=task.title,
        owner_id=user.id,
        category_id=task.category_id,
        status="new"
    )

    db.add(new_task)

    db.commit()

    db.refresh(new_task)

    return new_task

# ✏️ Обновление задачи
@app.patch("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    # обновляем только переданные поля
    if task_update.title is not None:
        task.title = task_update.title

    if task_update.category_id is not None:
        task.category_id = task_update.category_id

    db.commit()
    db.refresh(task)

    return task
# 📌 Удаление задачи (ТОЛЬКО ADMIN)

@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    if user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admin can delete tasks"
        )

    task = db.query(Task).filter(
        Task.id == task_id
    ).first()

    # ВАЖНАЯ ПРОВЕРКА
    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    db.delete(task)

    db.commit()

    return {"message": "Deleted by admin"}
# 📋 Получение задач

@app.get("/tasks", response_model=list[TaskResponse])
def get_tasks(
    skip: int = 0,
    limit: int = 10,
    order: str = "asc",
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    if order == "desc":
        order_by = Task.id.desc()
    else:
        order_by = Task.id.asc()

    # Если admin — показать все задачи
    if user.role == "admin":
        tasks = db.query(Task)\
            .order_by(order_by)\
            .offset(skip)\
            .limit(limit)\
            .all()

    else:
        # Если обычный user — только свои
        tasks = db.query(Task).filter(
            Task.owner_id == user.id
        ).order_by(order_by)\
         .offset(skip)\
         .limit(limit)\
         .all()

    return tasks
# ✏️ Обновление задачи

@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task: TaskCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    db_task = db.query(Task).filter(
        Task.id == task_id
    ).first()

    if not db_task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    # Проверка прав
    if user.role != "admin" and db_task.owner_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="Not allowed to edit this task"
        )

    # Обновление
    db_task.title = task.title

    db.commit()
    db.refresh(db_task)

    return db_task
# 📄 Получение одной задачи

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    db_task = db.query(Task).filter(
        Task.id == task_id
    ).first()

    if not db_task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    # Проверка доступа
    if user.role != "admin" and db_task.owner_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="Not allowed to view this task"
        )

    return db_task
@app.get("/users", response_model=list[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Только admin может смотреть пользователей
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admin can view users"
        )

    users = db.query(User).all()

    return users
@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Not authorized"
        )

    return task
@app.post("/categories", response_model=CategoryResponse)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db)
):
    db_category = Category(name=category.name)

    db.add(db_category)
    db.commit()
    db.refresh(db_category)

    return db_category


@app.get("/categories", response_model=list[CategoryResponse])
def get_categories(
    db: Session = Depends(get_db)
):
    categories = db.query(Category).all()

    return categories
@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    db.delete(task)
    db.commit()

    return {"message": "Task deleted"}
@app.delete("/categories/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    db.delete(category)
    db.commit()

    return {"message": "Category deleted"}
