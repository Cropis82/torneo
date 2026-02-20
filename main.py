from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

# Inizializziamo il nostro server HTTP
app = FastAPI(title="Il Mio Torneo API")

# Il nostro "Database" finto (in memoria)
squadre = {
    1: {"nome": "Fettucine FC", "capitano": "Gianni Rossi", "classe": "4Z inf3", "giocatori": 7},
    2: {"nome": "Pitoni da campo", "capitano": "Serpente Solido", "classe": "5O con2", "giocatori": 7}
}

# Definiamo come deve essere fatto il BODY di una Request per un nuovo team
class team(BaseModel):
    nome: str
    prezzo: str
    classe: str
    giocatori: int

# ---------------------------------------------------------
# 1. METODO GET: Leggere dati (Status code di default 200 OK)
# ---------------------------------------------------------
@app.get("/squadre")
def leggi_tutto_il_squadre():
    """Restituisce tutte le squadre."""
    return {"squadre": squadre}

@app.get("/squadre/{team_id}")
def leggi_singolo_team(team_id: int):
    """Cerca un team specifico tramite il suo ID nell'URL."""
    if team_id not in squadre:
        # Se non esiste, scateniamo un Errore 404 (Not Found)
        raise HTTPException(status_code=404, detail="team non trovato")
    return squadre[team_id]

# ---------------------------------------------------------
# 2. METODO POST: Creare un nuovo dato
# ---------------------------------------------------------
# Diciamo al server di rispondere con "201 Created" se ha successo
@app.post("/squadre", status_code=status.HTTP_201_CREATED)
def aggiungi_team(nuovo_team: team): # Il server si aspetta un Body!
    """Aggiunge un nuovo team alle squadre."""
    nuovo_id = max(squadre.keys()) + 1
    # Salviamo il team usando i dati ricevuti nel Request Body
    squadre[nuovo_id] = {"nome": nuovo_team.nome, "prezzo": nuovo_team.prezzo}
    return {"messaggio": "team aggiunto con successo!", "dati": squadre[nuovo_id]}

# ---------------------------------------------------------
# 3. METODO PUT: Aggiornare un dato esistente
# ---------------------------------------------------------
@app.put("/squadre/{team_id}")
def aggiorna_team(team_id: int, team_aggiornato: team):
    """Modifica un team esistente."""
    if team_id not in squadre:
        raise HTTPException(status_code=404, detail="team non trovato, impossibile aggiornare")
    
    squadre[team_id] = {"nome": team_aggiornato.nome, "prezzo": team_aggiornato.prezzo}
    return {"messaggio": "team aggiornato!", "dati": squadre[team_id]}

# ---------------------------------------------------------
# 4. METODO DELETE: Cancellare un dato
# ---------------------------------------------------------
@app.delete("/squadre/{team_id}")
def elimina_team(team_id: int):
    """Rimuove un team dalle squadre."""
    if team_id not in squadre:
        raise HTTPException(status_code=404, detail="team non trovato, impossibile eliminare")
    
    del squadre[team_id]
    return {"messaggio": f"team {team_id} eliminato dalle squadre"}
