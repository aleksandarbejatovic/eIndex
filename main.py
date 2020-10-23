from pydantic import BaseModel
from fastapi import FastAPI, Query
from typing import List, Optional

import sys
import datetime
import pickle


app = FastAPI()


class IspitIn(BaseModel):
    id: int #redni broj ispita u datoj skolskoj godini 1,2,3,4,5....
    vrijeme: datetime.date
    mjesto: str
    isPolozen: bool = False
    isPrijavljen: bool = False
    isPrisustvovao: bool = False
    bodovi: int = 50
    vidljiv: bool = True #promjenjivu vidljiv koristim za soft delete, u slucaju brisanja, setuje se samo vidljiv na false


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
    ispiti: List[Optional[IspitIn]] = None


class IspitOut(BaseModel):
    isPolozen: bool


class PredmetOut(BaseModel):
    naziv: str
    profesor: str
    ispiti: IspitOut


hes_predmeta = dict() #svi predmeti globalna promjenjiva, za naziv predmeta dobijam predmet
hes_ispita = dict() #svi ispiti, za id ispita dobijam ispit
hes_ispit_predmet = dict() #ispiti - predmeti, za dati ispit dobijamo predmet


@app.post("/dodaj-predmet/", response_model=PredmetOut)
async def create_predmet(predmet: PredmetIn):
   #predmet.naziv = Query(min_length=3, default="Matematika") #da li funkcionise da je minimalna duzina svakog predmeta 3
    hes_predmeta[predmet.naziv] = predmet
    return predmet


@app.post("/dodaj-ispit/", response_model=IspitOut)
async def create_ispit(ispit: IspitIn, naziv_predmeta: str):
    if hes_predmeta[str]:
        hes_predmeta[naziv_predmeta].ispiti.add(ispit)
        hes_ispita[ispit.id] = ispit
        hes_ispit_predmet[ispit] = hes_predmeta[naziv_predmeta]
    else:
        print("Ne postoji dati predmet!")
    return ispit


@app.delete("/obrisi-predmet/")
async def delete_predmet(predmet: str):
    if hes_predmeta[predmet]:
        for ispit in hes_predmeta[predmet].ispiti: #brisemo sve ispite za dati predmet
            hes_ispita[ispit.id] = None
            hes_ispit_predmet[ispit.id] = None
        hes_predmeta[predmet] = None
    else:
        print("Ne postoji dati predmet!")


@app.delete("/obrisi-ispit-hard/") #hard delete ispita
async def delete_ispit(ispit: int):
    if hes_ispita[ispit]:
        predmet = hes_ispit_predmet[ispit] #na kojem predmetu se nalazi ispit, da ga obrisemo
        hes_predmeta[predmet].ispiti.remove(hes_ispita[ispit]) #brisanje ispita sa datog predmeta
        hes_ispita[ispit] = None #brisanje ispita iz hesa svih ispita
        hes_ispit_predmet[ispit] = None #jer dati ispit vise ne postoji
    else:
        print("Ne postoji dati ispit!")


@app.delete("/obrisi-ispit-soft/") #soft delete ispita
async def delete_ispit(ispit: int):
    if hes_ispita[ispit] and hes_ispita[ispit].vidljiv == True:
        hes_ispita[ispit].vidljiv = False
        i = 0
        while i < len(hes_ispit_predmet[ispit].ispiti):
            if(hes_ispit_predmet[ispit].ispiti[i].id == ispit):
                hes_ispit_predmet[ispit].ispiti[i].vidljiv = False
                i = len(hes_ispit_predmet[ispit].ispiti)
            i+=1
    else:
        print("Ispit ne postoji ili je obrisan!")


@app.put("/edit-predmet/")
async def edit_predmet(predmet: str, edit: str): #edit -> sta editujemo u predmetu
    hes_predmeta[predmet].edit = sys.argv[1]


@app.on_event("startup")
async def startup_event():
    file = open(r"C:\\datoteka.txt", "r") #potrebno dovrsiti

@app.on_event("shutdown")
def shutdown_event():
    file = open(r"C:\\datoteka.txt", "w") #potrebno dovrsiti
