from pydantic import BaseModel
from fastapi import FastAPI, Query
from typing import List, Optional
from starlette.responses import Response
from pathlib import Path

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

class hesObject():
    hes_predmeta = dict() # svi predmeti globalna promjenjiva, za naziv predmeta dobijam predmet
    hes_ispita = dict() # svi ispiti, za id ispita dobijam ispit
    hes_ispit_predmet = dict() #ispiti - predmeti, za dati ispit dobijamo predmet

db = hesObject()

@app.post("/predmet/", response_model=PredmetOut)
async def create_predmet(predmet: PredmetIn):
   #predmet.naziv = Query(min_length=3, default="Matematika") #da li funkcionise da je minimalna duzina svakog predmeta 3
    db.hes_predmeta[predmet.naziv] = predmet
    return predmet


@app.post("/ispit/", response_model=IspitOut, responses={ 404: {"opis": "Predmet ne postoji!"}}, response_class =Response)
async def create_ispit(ispit: IspitIn, naziv_predmeta: str):
    if db.hes_predmeta[str]:
        db.hes_predmeta[naziv_predmeta].ispiti.add(ispit)
        db.hes_ispita[ispit.id] = ispit
        db.hes_ispit_predmet[ispit] = db.hes_predmeta[naziv_predmeta]
    else:
        return Response(status_code=404)
    return ispit


@app.delete("/predmet/{predmet_id}", responses={ 200: {"opis": "Predmet uspjesno obrisan!"},
                                            404: {"opis": "Predmet nije pronadjen!"}},
                                            response_class=Response)
async def delete_predmet(predmet: str):
    if db.hes_predmeta[predmet]:
        for ispit in db.hes_predmeta[predmet].ispiti: #brisemo sve ispite za dati predmet
            db.hes_ispita[ispit.id] = None
            db.hes_ispit_predmet[ispit.id] = None
        db.hes_predmeta[predmet] = None
        return Response(status_code=200)
    else:
        return Response(status_code=404)


@app.delete("/ispit-hard/{ispit_id}", responses={ 200: {"opis": "Ispit uspjesno obrisan!"},
                                              404: {"opis": "Ispit nije pronadjen!"}},
                                              response_class=Response) #hard delete ispita
async def delete_ispit(ispit: int):
    if db.hes_ispita[ispit]:
        predmet = db.hes_ispit_predmet[ispit] #na kojem predmetu se nalazi ispit, da ga obrisemo
        db.hes_predmeta[predmet].ispiti.remove(db.hes_ispita[ispit]) #brisanje ispita sa datog predmeta
        db.hes_ispita[ispit] = None #brisanje ispita iz hesa svih ispita
        db.hes_ispit_predmet[ispit] = None #jer dati ispit vise ne postoji
        return Response(status_code=200)
    else:
        return Response(status_code=404)


@app.delete("/ispit-soft/{ispit_id}", responses={200: {"opis": "Ispit uspjesno obrisan!"},
                                              404: {"opis": "Ispit nije pronadjen!"}},
                                              response_class=Response) #soft delete ispita
async def delete_ispit(ispit: int):
    if db.hes_ispita[ispit] and db.hes_ispita[ispit].vidljiv == True:
        db.hes_ispita[ispit].vidljiv = False
        for dispit in db.hes_predmeta[ispit].ispiti:
            if dispit.id == ispit:
                dispit.vidljiv = False
        return Response(status_code=200)
    else:
        return Response(status_code=404)


@app.patch("/predmet/{predmet_id}")
async def edit_predmet(predmet: str, edit: str): #edit -> sta editujemo u predmetu (ideja)
    db.hes_predmeta[predmet].edit = sys.argv[1]


@app.on_event("startup") #deserijalizacija
async def startup_event():
    correct_path = Path("C:/Users/aleks/PycharmProjects/eIndex/datoteka.dat") #prevodjenje putanje u putanju za odgovarajuci
    infile = open(correct_path, "rb")                                         #operativni sistem
    new_ob = pickle.load(infile)
    infile.close()


@app.on_event("shutdown") #serijalizacija
def shutdown_event():
    correct_path = Path("C:/Users/aleks/PycharmProjects/eIndex/datoteka.dat")
    outfile = open(correct_path, "wb")
    pickle.dump(db, outfile)
    outfile.close()