# cybersec-group47
 DP3T simulator with a combination of Shamir's secret sharing and succinct commitment to provide pseudo-authenticated data to epidemiologists.

**Leggi** ```Report.pdf``` **per informazioni sullo sviluppo del sistema**

Per utilizzare i server bisogna installare [pipenv](https://pypi.org/project/pipenv/), posizionarsi nella cartella
del progetto e lanciare ```pipenv install```.

Avere a disposizione un DBMS PostgreSQL con due database aventi la struttura definita
nei file contenuti in ```script_sql/``` e indicare il relativo url nei file
```main_svr/.env``` e ```lab_svr/.env```

Infine, per avviare i server basta aprire due terminali posizionati nella cartella del progetto e digitare 
```pipenv run python -m main_svr```, e sull'altro digitare ```pipenv run python -m lab_svr```
