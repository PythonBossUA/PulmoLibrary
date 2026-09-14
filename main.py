from typing import Annotated
from datetime import date

from fastapi import FastAPI, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
database = Annotated[AsyncSession, Depends(get_session)]

months_dict = {
    1: "Січня",
    2: "Лютого",
    3: "Березня",
    4: "Квітня",
    5: "Травня",
    6: "Червня",
    7: "Липня",
    8: "Серпня",
    9: "Вересня",
    10: "Жовтня",
    11: "Листопада",
    12: "Грудня"
}


@app.get("/")
async def index(request: Request):
    current_date = date.today()

    return templates.TemplateResponse(
        request,
        "index.html",
        context={
            "schedule": f"{current_date.day} {months_dict[current_date.month]} · "
                        f"{
                        "Сьогодні ми працюємо😄 · з 10:00 до 19:00"
                        if current_date.weekday() not in (0, 5)  # 0 - понеділок; 5 - субота
                        else "Сьогодні ми відпочиваємо🥺 · вихідні понеділок та субота"
                        }"
        }
    )
