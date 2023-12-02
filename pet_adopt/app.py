import json

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr
from tinydb import Query, TinyDB


class Customer(BaseModel):
    firstname: str
    lastname: str
    email: EmailStr
    address: str
    city: str
    zipcode: str
    rgpd_ok: bool = False
    docusign_link: str | None = None


app = FastAPI(title="PetAdopt")
db = TinyDB("data/db.json")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


def customer_form(
    firstname: str = Form(...),
    lastname: str = Form(...),
    email: str = Form(...),
    address: str = Form(...),
    city: str = Form(...),
    zipcode: str = Form(...),
    rgpd_ok: bool = Form(...),
):
    return Customer(
        firstname=firstname,
        lastname=lastname,
        email=email,
        address=address,
        city=city,
        zipcode=zipcode,
        rgpd_ok=rgpd_ok,
    )


def persist_customer(customer: Customer) -> None:
    customer_by_email = Query().email == customer.email
    if not db.search(customer_by_email):
        db.insert(customer.model_dump())
    else:
        db.update(customer.model_dump(), customer_by_email)


@app.post("/generate")
def generate_certificat(request: Request, customer: Customer = Depends(customer_form)):
    persist_customer(customer)
    return templates.TemplateResponse("index.html", {"request": request})
