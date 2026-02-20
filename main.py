from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI(title="Il Mio Torneo API")

squadre = {
    1: {"nome": "Fettucine FC", "capitano": "Gianni Rossi", "classe": "4Z inf3", "giocatori": 7, "stato": "iscritto", "posizioneFinale": "iscritto"},
    2: {"nome": "Pitoni da campo", "capitano": "Serpente Solido", "classe": "5O con2", "giocatori": 7, "stato": "iscritto", "posizioneFinale": "iscritto"}
}

class team(BaseModel):
    nome: str
    capitano: str
    classe: str
    giocatori: int


@app.get("/squadre")
def leggi_tutto_il_squadre():
    """Restituisce tutte le squadre."""
    return {"squadre": squadre}

@app.get("/squadre/{team_id}")
def leggi_singolo_team(team_id: int):
    """Cerca un team specifico tramite il suo ID nell'URL."""
    if team_id not in squadre:
        raise HTTPException(status_code=404, detail="team non trovato")
    return squadre[team_id]


@app.post("/squadre", status_code=status.HTTP_201_CREATED)
def aggiungi_team(nuovo_team: team):
    """Aggiunge un nuovo team alle squadre, inizializzando le statistiche del torneo."""
    nuovo_id = max(squadre.keys()) + 1 if squadre else 1
    
    squadre[nuovo_id] = {
        "nome": nuovo_team.nome, 
        "capitano": nuovo_team.capitano, 
        "classe": nuovo_team.classe, 
        "giocatori": nuovo_team.giocatori,
        "stato": "iscritto",
        "posizioneFinale": "iscritto"
    }
    return {"messaggio": "team aggiunto con successo!", "dati": squadre[nuovo_id]}


@app.put("/squadre/{team_id}")
def aggiorna_team(team_id: int, team_aggiornato: team):
    """Modifica un team esistente mantenendo inalterato il suo stato nel torneo."""
    if team_id not in squadre:
        raise HTTPException(status_code=404, detail="team non trovato, impossibile aggiornare")
    
    stato_attuale = squadre[team_id].get("stato", "iscritto")
    posizione_attuale = squadre[team_id].get("posizioneFinale", "iscritto")
    
    squadre[team_id] = {
        "nome": team_aggiornato.nome, 
        "capitano": team_aggiornato.capitano, 
        "classe": team_aggiornato.classe, 
        "giocatori": team_aggiornato.giocatori,
        "stato": stato_attuale,
        "posizioneFinale": posizione_attuale
    }
    return {"messaggio": "team aggiornato!", "dati": squadre[team_id]}


@app.delete("/squadre/{team_id}")
def elimina_team(team_id: int):
    """Rimuove un team dalle squadre."""
    if team_id not in squadre:
        raise HTTPException(status_code=404, detail="team non trovato, impossibile eliminare")
    
    del squadre[team_id]
    return {"messaggio": f"team {team_id} eliminato dalle squadre"}