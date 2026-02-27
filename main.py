from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from tinydb import TinyDB, Query
import random

app = FastAPI(title="Il Mio Torneo API")


db = TinyDB("torneo_db.json")
squadre_table = db.table("squadre")
gironi_table = db.table("gironi")

TeamQuery = Query()
GironeQuery = Query()


class Team(BaseModel):
    nome: str
    capitano: str
    classe: str
    giocatori: int

class AggiornaGirone(BaseModel):
    vincitore1: int
    vincitore2: int
    punteggio1: int
    punteggio2: int
    punteggio3: int
    punteggio4: int



def genera_nuovo_id(table):
    records = table.all()
    if not records:
        return 1
    return max(item["id"] for item in records) + 1


@app.get("/squadre")
def leggi_tutto_il_squadre():
    return {"squadre": squadre_table.all()}


@app.get("/squadre/{team_id}")
def leggi_singolo_team(team_id: int):
    team = squadre_table.get(TeamQuery.id == team_id)
    if not team:
        raise HTTPException(status_code=404, detail="team non trovato")
    return team


@app.post("/squadre", status_code=status.HTTP_201_CREATED)
def aggiungi_team(nuovo_team: Team):

    nuovo_id = genera_nuovo_id(squadre_table)

    team_data = {
        "id": nuovo_id,
        "nome": nuovo_team.nome,
        "capitano": nuovo_team.capitano,
        "classe": nuovo_team.classe,
        "giocatori": nuovo_team.giocatori,
        "stato": "iscritto",
        "posizioneFinale": "iscritto"
    }

    squadre_table.insert(team_data)

    return {"messaggio": "team aggiunto con successo!", "dati": team_data}


@app.put("/squadre/{team_id}")
def aggiorna_team(team_id: int, team_aggiornato: Team):

    team = squadre_table.get(TeamQuery.id == team_id)

    if not team:
        raise HTTPException(status_code=404, detail="team non trovato")

    stato_attuale = team["stato"]
    posizione_attuale = team["posizioneFinale"]

    squadre_table.update({
        "nome": team_aggiornato.nome,
        "capitano": team_aggiornato.capitano,
        "classe": team_aggiornato.classe,
        "giocatori": team_aggiornato.giocatori,
        "stato": stato_attuale,
        "posizioneFinale": posizione_attuale
    }, TeamQuery.id == team_id)

    return {"messaggio": "team aggiornato!"}


@app.delete("/squadre/{team_id}")
def elimina_team(team_id: int):

    if not squadre_table.get(TeamQuery.id == team_id):
        raise HTTPException(status_code=404, detail="team non trovato")

    squadre_table.remove(TeamQuery.id == team_id)

    return {"messaggio": f"team {team_id} eliminato"}



@app.get("/gironi")
def leggi_tutti_i_gironi():
    return {"gironi": gironi_table.all()}


@app.get("/gironi/{girone_id}")
def leggi_singolo_girone(girone_id: int):
    girone = gironi_table.get(GironeQuery.id == girone_id)

    if not girone:
        raise HTTPException(status_code=404, detail="Girone non trovato")

    return girone


@app.put("/gironi/{girone_id}")
def aggiorna_punteggi_girone(girone_id: int, dati: AggiornaGirone):

    girone = gironi_table.get(GironeQuery.id == girone_id)

    if not girone:
        raise HTTPException(status_code=404, detail="Girone non trovato")

    gironi_table.update({
        "vincitore1": dati.vincitore1,
        "vincitore2": dati.vincitore2,
        "punteggio1": dati.punteggio1,
        "punteggio2": dati.punteggio2,
        "punteggio3": dati.punteggio3,
        "punteggio4": dati.punteggio4
    }, GironeQuery.id == girone_id)

    return {"messaggio": "Girone aggiornato!"}


@app.post("/gironi/genera", status_code=status.HTTP_201_CREATED)
def genera_gironi_automaticamente():

    squadre_iscritte = [
        team for team in squadre_table.all()
        if team["stato"] == "iscritto"
    ]

    if len(squadre_iscritte) < 4:
        raise HTTPException(
            status_code=400,
            detail="Servono almeno 4 squadre"
        )

    random.shuffle(squadre_iscritte)

    gironi_table.truncate()

    nuovo_id = 1

    for i in range(0, len(squadre_iscritte), 4):

        gruppo = squadre_iscritte[i:i+4]

        while len(gruppo) < 4:
            gruppo.append({"id": 0})

        girone_data = {
            "id": nuovo_id,
            "vincitore1": 0,
            "vincitore2": 0,
            "IDsquadra1": gruppo[0]["id"],
            "punteggio1": 0,
            "IDsquadra2": gruppo[1]["id"],
            "punteggio2": 0,
            "IDsquadra3": gruppo[2]["id"],
            "punteggio3": 0,
            "IDsquadra4": gruppo[3]["id"],
            "punteggio4": 0
        }

        gironi_table.insert(girone_data)

        for team in gruppo:
            if team["id"] != 0:
                squadre_table.update(
                    {"stato": f"girone {nuovo_id}"},
                    TeamQuery.id == team["id"]
                )

        nuovo_id += 1

    return {"messaggio": "Gironi generati con successo"}