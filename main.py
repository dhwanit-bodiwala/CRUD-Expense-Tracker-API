from contextlib import asynccontextmanager
from datetime import date, datetime, time, timezone
from typing import Annotated, Generic, TypeVar
import calendar
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlmodel import Field, SQLModel, Session, create_engine, select


class Product(SQLModel, table=True):
    product_id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False, index=True)
    amount: int = Field(default=0)
    category: str = Field(nullable=False, index=True)
    desc: str | None = Field(default=None, nullable=True)
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=True, index=True)


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connection_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connection_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


class BodyCreate(SQLModel):
    name: str
    amount: int
    category: str
    desc: str | None = None


T = TypeVar("T")


class Response(BaseModel, Generic[T]):
    data: T


SessionDep = Annotated[Session, Depends(get_session)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        if not session.exec(select(Product)).first():
            session.add_all([
                Product(name="test123", category="Food", date=datetime.now()),
                Product(name="test456", category="Transport", date=datetime.now())
            ])
            session.commit()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def intro():
    return {"Message": "Expense Tracker"}


@app.get("/expenses", response_model=Response[list[Product]])
async def show_expenses(session: SessionDep, category: str | None = None, start_date: datetime | None = None, end_date: datetime | None = None):

    query = select(Product)

    if category:
        query = query.where(Product.category == category)

    if start_date:
        query = query.where(Product.date >= start_date)

    if end_date:
        query = query.where(Product.date <= end_date)

    data = session.exec(query).all()

    return {"data": data}


@app.get("/expenses/{id}", response_model=Response[Product])
async def search_expenses(id: int, session: SessionDep):

    data = session.get(Product, id)

    if not data:
        raise HTTPException(status_code=404, detail="Expense not found")

    return {"data": data}


@app.post("/expenses", response_model=Response[Product])
async def add_expenses(body: BodyCreate, session: SessionDep):

    db_product = Product.model_validate(body)

    session.add(db_product)
    session.commit()
    session.refresh(db_product)

    return {"data": db_product}


@app.put("/expenses/{id}", response_model=Response[Product])
async def update_expenses(id: int, body: BodyCreate, session: SessionDep):

    data = session.get(Product, id)

    if not data:
        raise HTTPException(status_code=404, detail="Expense not found")

    data.name = body.name
    data.amount = body.amount
    data.category = body.category
    data.desc = body.desc

    session.add(data)
    session.commit()
    session.refresh(data)

    return {"data": data}


@app.delete("/expenses/{id}", status_code=204)
async def delete_expenses(id: int, session: SessionDep):

    data = session.get(Product, id)

    if not data:
        raise HTTPException(status_code=404, detail="Expense not found")

    session.delete(data)
    session.commit()

    return None


@app.get("/summary/monthly")
async def monthly_summary(session: SessionDep, year: int, month: int, category: str | None = None):

    days = calendar.monthrange(year, month)[1]

    startdate = datetime.combine(date(year, month, 1), time.min)
    enddate = datetime.combine(date(year, month, days), time.max)

    query = select(Product)

    if startdate:
        query = query.where(Product.date >= startdate)

    if enddate:
        query = query.where(Product.date < enddate)

    if category:
        query = query.where(Product.category == category)

    data = session.exec(query).all()

    total = 0
    by_category = {}

    for item in data:
        total += item.amount
        by_category[item.category] = by_category.get(item.category, 0) + item.amount

    return {"total": total, "by category": by_category}