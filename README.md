# 🌡️ ThermoCentral — Monitoraggio Temperatura per Aziende Agricole (CFR Toscana)

**ThermoCentral** è un'applicazione web sviluppata in Python con **Streamlit** e studiata specificamente per dispositivi mobile per il monitoraggio della temperatura oraria ed istantanea delle centraline meteo del **Centro Funzionale Regionale (CFR Toscana)** posizionate in prossimità delle aziende agricole.

---

## 🚀 Caratteristiche Principali

- 📱 **Interfaccia Mobile-First Integrata**: Selezione della stazione meteorologica direttamente in prima pagina tramite pulsanti touch veloci a 1 tocco, senza dover aprire il menu laterale.
- 🌡️ **Temperatura Istantanea & Max Odierna**: Visualizzazione immediata dell'ultimo dato rilevato e della temperatura massima registrata con l'ora esplicita del picco.
- 📉 **Grafici 48 Ore Touch-Friendly**: Grafici continui ottimizzati per smartphone senza zoom o panning accidentali al tocco del dito.
- 📊 **Sintesi Confronto Giornaliero**: Confronto immediato tra le medie, massime e minime del giorno precedente e del giorno corrente.
- 🌐 **Fallback Automatico con Open-Meteo**: In caso di temporanea irreperibilità o manutenzione dei server CFR Toscana, l'app passa automaticamente al modello meteorologico Open-Meteo per garantire la continuità di servizio.
- 🏢 **Branding Personalizzato**: Integrazione del logo aziendale **L.M. Technical Assistance**.

---

## 📍 Stazioni Meteorologiche Monitorate

- 📍 **San Donato (Orbetello)** — `TOS03003099`
- 📍 **Stiacciole (Grosseto)** — `TOS11000042`
- 📍 **Follonica** — `TOS03002551`
- 📍 **Capalbio** — `TOS11000006`
- 📍 **Rispescia (Alberese)** — `TOS11000005`
- 📍 **Braccagni** — `TOS11000008`
- 📍 **Cesa** — `TOS11000037`

---

## 📁 Struttura del Repository

```text
├── app.py                     # Applicazione principale Streamlit (ThermoCentral)
├── logo lm chat gpt.png       # Logo aziendale per l'header dell'app
├── requirements.txt           # Dipendenze Python (Streamlit, OpenCV, Plotly, etc.)
├── .gitignore                 # Regole di esclusione file temporanei
└── .streamlit/
    └── config.toml            # Configurazione tema grafico e prestazioni
```

---

## ⚙️ Esecuzione Locale (Windows)

1. Apri la cartella del progetto.
2. Fai doppio clic sul file `avvia_app.bat`.
3. L'applicazione si avvierà ed aprirà automaticamente il browser su `http://localhost:8501`.

---

## ☁️ Deploy su Streamlit Community Cloud

1. Carica i file di questo progetto sul tuo repository GitHub [`App-visione-Temperatura-per-Diego`](https://github.com/lucamancio1975-sys/App-visione-Temperatura-per-Diego).
2. Accedi a [share.streamlit.io](https://share.streamlit.io) con il tuo account GitHub.
3. Clicca su **New app** -> Seleziona il repository `lucamancio1975-sys/App-visione-Temperatura-per-Diego`.
4. Imposta come file principale: `app.py`.
5. Clicca su **Deploy!**

---
*Fonte Dati: [Centro Funzionale Regionale Toscana (CFR)](https://www.cfr.toscana.it/)*
