# RAG Learning

Un proiect mic de invatare pentru Retrieval-Augmented Generation peste documente personale.

Varianta curenta ruleaza local, fara dependinte externe. Indexeaza fisiere Markdown si text,
cauta fragmente relevante cu embeddings deterministe prin hashing si compune un raspuns bazat
strict pe sursele gasite. Optional, poate folosi un LLM prin OpenAI Responses API pentru sinteza.

## Structura

- `data/` - pune aici notitele si documentele tale `.md` sau `.txt`
- `rag/` - codul aplicatiei
- `storage/rag.sqlite3` - baza locala generata dupa indexare

## Utilizare

```powershell
python -m rag ingest data
python -m rag ask "Ce obiective am pentru proiect?"
```

Cu LLM:

```powershell
$env:OPENAI_API_KEY="..."
$env:OPENAI_MODEL="modelul-tau"
python -m rag ask "Ce obiective am pentru proiect?" --llm
```

## Comenzi

```powershell
python -m rag ingest data --reset
python -m rag search "rag local" --top-k 5
python -m rag ask "Cum functioneaza proiectul?"
```

## Cum functioneaza

RAG inseamna Retrieval-Augmented Generation:

1. `ingest` citeste documentele si le sparge in fragmente.
2. Fiecare fragment primeste un vector numeric local.
3. `ask` transforma intrebarea intr-un vector si cauta fragmente apropiate.
4. Fara `--llm`, aplicatia afiseaza pasajele relevante.
5. Cu `--llm`, aplicatia trimite doar pasajele relevante catre model, nu intreaga colectie.

Am folosit OpenAI Responses API deoarece documentatia oficiala il descrie ca interfata principala
pentru generarea de raspunsuri text. Modelul ramane configurabil prin `OPENAI_MODEL`, ca sa nu
legam proiectul de un nume de model care se poate schimba.
