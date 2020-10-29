from pydantic import BaseModel
from fastapi import FastAPI
from typing import List, Optional
from starlette.responses import Response
from pathlib import Path

import sys
import datetime
import pickle


app = FastAPI()

identification = 0 #potrebno uvecati nakon svakog novog ispita

class IspitIn(BaseModel):
    id: int = identification #identifikacioni broj ispita, potrebno da bude jedinstven
    vrijeme: datetime.date #potrebno zamjeniti tip podatka, potrebno da bude tip date
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
    hes_predmeta = dict() #svi predmeti globalna promjenjiva, za naziv predmeta dobijam predmet
    hes_ispita = dict() #svi ispiti, za id ispita dobijam ispit
    hes_ispit_predmet = dict() #ispiti - predmeti, za dati ispit dobijamo predmet

db = hesObject()


@app.get("/predmet/") #da li kroz get treba unijeti sve atribute i vratiti objekat IspitIn ili nesto drugo?
async def read_predmet(naziv: str, profesor: str, asistent: str, predavanje_mjesto: str):
    PredmetIn.naziv=naziv
    PredmetIn.profesor=profesor
    PredmetIn.asistent=asistent
    PredmetIn.predavanje_mjesto=predavanje_mjesto
    return PredmetIn


@app.post("/predmet/", response_model=PredmetOut)
async def create_predmet(predmet: PredmetIn):
    db.hes_predmeta[predmet.naziv] = predmet
    return predmet


@app.post("/ispit/", response_model=IspitOut, responses={ 404: {"opis": "Predmet ne postoji!"}}, response_class=Response)
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


#@app.on_event("startup") #deserijalizacija
#async def startup_event():
#    correct_path = Path("C:/Users/aleks/PycharmProjects/eIndex/datoteka.dat") #prevodjenje putanje u putanju za odgovarajuci
#    with open(correct_path, "rb") as in_file:                                 #operativni sistem
#        data = pickle.load(in_file)
#    in_file.close()


#@app.on_event("shutdown") #serijalizacija
#def shutdown_event():
#    correct_path = Path("C:/Users/aleks/PycharmProjects/eIndex/datoteka.dat") #prevodjenje putanje u putanju za odgovarajuci
#    with open(correct_path, "wb") as out_file:                                #operativni sistem
#        pickle.dump(db, out_file)
#    out_file.close()