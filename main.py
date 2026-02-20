from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import random

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

gironi = {
    1: {
        "vincitore1": 0, "vincitore2": 0, 
        "IDsquadra1": 1, "punteggio1": 0, 
        "IDsquadra2": 2, "punteggio2": 0, 
        "IDsquadra3": 3, "punteggio3": 0, 
        "IDsquadra4": 4, "punteggio4": 0
    }
}

class AggiornaGirone(BaseModel):
    vincitore1: int
    vincitore2: int
    punteggio1: int
    punteggio2: int
    punteggio3: int
    punteggio4: int


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


@app.get("/gironi")
def leggi_tutti_i_gironi():
    """Restituisce tutti i gironi di qualifica."""
    return {"gironi": gironi}


@app.get("/gironi/{girone_id}")
def leggi_singolo_girone(girone_id: int):
    """Cerca un girone specifico tramite il suo ID."""
    if girone_id not in gironi:
        raise HTTPException(status_code=404, detail="Girone non trovato")
    return gironi[girone_id]


@app.put("/gironi/{girone_id}")
def aggiorna_punteggi_girone(girone_id: int, dati_aggiornati: AggiornaGirone):
    """Aggiorna i punteggi e i vincitori di un girone specifico."""
    if girone_id not in gironi:
        raise HTTPException(status_code=404, detail="Girone non trovato, impossibile aggiornare")
    
    girone_attuale = gironi[girone_id]
    
    gironi[girone_id] = {
        "IDsquadra1": girone_attuale["IDsquadra1"],
        "IDsquadra2": girone_attuale["IDsquadra2"],
        "IDsquadra3": girone_attuale["IDsquadra3"],
        "IDsquadra4": girone_attuale["IDsquadra4"],
        "vincitore1": dati_aggiornati.vincitore1,
        "vincitore2": dati_aggiornati.vincitore2,
        "punteggio1": dati_aggiornati.punteggio1,
        "punteggio2": dati_aggiornati.punteggio2,
        "punteggio3": dati_aggiornati.punteggio3,
        "punteggio4": dati_aggiornati.punteggio4
    }
    
    return {"messaggio": "Punteggi del girone aggiornati!", "dati": gironi[girone_id]}


@app.post("/gironi/genera", status_code=status.HTTP_201_CREATED)
def genera_gironi_automaticamente():
    """Smista casualmente le squadre iscritte in gironi da 4."""
    
    squadre_iscritte = [
        id_team for id_team, dati in squadre.items() 
        if dati.get("stato") == "iscritto"
    ]
    
    if len(squadre_iscritte) < 4:
        raise HTTPException(
            status_code=400, 
            detail="Non ci sono abbastanza squadre per formare almeno un girone (minimo 4)."
        )
    
    random.shuffle(squadre_iscritte)
    
    gironi.clear()
    
    nuovo_id_girone = 1
    
    for i in range(0, len(squadre_iscritte), 4):
        gruppo = squadre_iscritte[i:i+4]
        
        while len(gruppo) < 4:
            gruppo.append(0)
        
        gironi[nuovo_id_girone] = {
            "vincitore1": 0, "vincitore2": 0,
            "IDsquadra1": gruppo[0], "punteggio1": 0,
            "IDsquadra2": gruppo[1], "punteggio2": 0,
            "IDsquadra3": gruppo[2], "punteggio3": 0,
            "IDsquadra4": gruppo[3], "punteggio4": 0
        }
        
        for id_team in gruppo:
            if id_team != 0:
                squadre[id_team]["stato"] = f"girone {nuovo_id_girone}"
                
        nuovo_id_girone += 1
        
    return {
        "messaggio": f"Smistamento completato! Generati {nuovo_id_girone - 1} gironi.", 
        "gironi": gironi
    }