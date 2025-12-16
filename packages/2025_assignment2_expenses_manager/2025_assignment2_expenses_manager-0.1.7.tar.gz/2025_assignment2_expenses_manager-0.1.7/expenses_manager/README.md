# Expense Manager

Expense Manager è una semplice applicazione Python/FastAPI per gestire le spese.  
Permette di aggiungere, aggiornare, cancellare e filtrare le spese, generare statistiche e esportare i dati.


## Tecnologie

- Python 3.10+
- FastAPI
- Pydantic
- SQLAlchemy (ORM)
- SQLite database
- Poetry per gestione delle dipendenze e virtual environment

## Installazione

1. Clona il repository:

```bash
git clone <repo_url>
cd 2025_assignment2_expenses_manager
```

2. Installa le dipendenze con Poetry:

```bash
poetry install
```

3. Avvia l’applicazione:

```bash
poetry run uvicorn expenses_manager.api.main:app --reload
```

## Endpoints

- GET /: Verifica stato API
- POST /api/expenses: Aggiungi una nuova spesa
- GET /api/expenses: Lista spese con filtri
- GET /api/expenses/{id}: Recupera spesa per ID
- PUT /api/expenses/{id}: Aggiorna spesa
- DELETE /api/expenses/{id}: Cancella spesa (soft delete)
- GET /api/stats/total_by_category: Totale spese per categoria
- GET /api/stats/monthly_summary: Riepilogo mensile spese
- GET /api/export: Esporta le spese in CSV