# RAG Learning

Scopul proiectului este sa construim un asistent local pentru documente personale.
Asistentul trebuie sa poata indexa notite, jurnale, idei de proiect si fisiere text.

MVP-ul are trei componente:

1. Ingestie: citeste fisiere Markdown si text din folderul `data`.
2. Retrieval: transforma fiecare fragment intr-un vector local si cauta fragmente relevante.
3. Raspuns: afiseaza pasajele cele mai utile, impreuna cu sursa lor.

O directie buna pentru urmatoarea etapa este conectarea unui model LLM pentru sinteza.
Modelul ar trebui sa primeasca doar fragmentele gasite si sa citeze sursele in raspuns.

Pentru date personale, proiectul trebuie sa ramana explicit si controlabil:
documentele stau local, indexul sta local, iar integrarea cu servicii externe ar trebui sa fie optionala.
