from pydantic import BaseModel
from fastapi import FastAPI, Query
from typing import List, Optional

import datetime
import pickle


app = FastAPI()


class IspitIn(BaseModel):
    vrijeme: datetime.date
    mjesto: str
    isPolozen: bool = False
    isPrijavljen: bool = False
    isPrisustvovao: bool = False
    bodovi: int = 50


class PredmetIn(BaseModel):
    naziv: str
    profesor: str
    asistent: str
    predavanja_mjesto: str
    predavanja_vrijeme: datetime.date
    vjezbe_mjesto: str
    vjezbe_vrijeme: datetime.date
    lab_mjesto: str
    lab_vrijeme: datetime.datetime
    ispiti: Optional[IspitIn] = None


class IspitOut(BaseModel):
    isPolozen: bool


class PredmetOut(BaseModel):
    naziv: str
    profesor: str
    ispiti: IspitOut


hes_predmeta = dict()
hes_ispita = dict()


@app.post("/dodaj-predmet/", response_model=PredmetOut)
async def create_predmet(predmet: PredmetIn):
   #predmet.naziv = Query(min_length=3, default="Matematika") #da li funkcionise da je minimalna duzina svakog predmeta 3
    hes_predmeta[predmet.naziv] = predmet
    return predmet


@app.post("/dodaj-ispit/", response_model=IspitOut)
async def create_ispit(ispit: IspitIn):
    hes_ispita[ispit.naziv] = ispit
    return ispit


@app.delete("/obrisi-predmet/")
async def delete_predmet(predmet: str):
    hes_predmeta[predmet.naziv] = None  #da li je dovoljno samo odraditi pop ili je potrebnno i del lista_predmeta(i)


@app.delete("/obrisi-ispit/")
async def delete_ispit(ispit: str):
    predmet = hes_ispita[ispit]
    hes_predmeta[predmet] = None