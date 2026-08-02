import streamlit as st
import cv2
import numpy as np
import requests
import os
import datetime
import pytz
import pandas as pd
import plotly.graph_objects as go

# --- CONFIGURAZIONE PAGINA STREAMLIT ---
st.set_page_config(
    page_title="ThermoCentral 🌡️",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS per estetica mobile-first e carte KPI
st.markdown("""
<style>
    .main {
        background-color: #f8fafc;
    }
    /* Disabilita drag e ingrandimento Plotly */
    .modebar, .plotly .modebar, .plotly .draglayer {
        pointer-events: none !important;
    }
    /* Cursore a manina per il menu di selezione stazioni */
    div[data-testid="stSelectbox"] *,
    div[data-baseweb="select"] *,
    div[data-baseweb="popover"] * {
        cursor: pointer !important;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 16px 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border: 1px solid #e2e8f0;
        margin-bottom: 12px;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0f172a;
        margin-top: 4px;
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #475569;
        margin-top: 4px;
    }
    .badge-fallback {
        background-color: #fef3c7;
        color: #92400e;
        padding: 8px 14px;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 500;
        border: 1px solid #fde68a;
        margin-top: 10px;
    }
    .badge-cfr {
        background-color: #dcfce7;
        color: #166534;
        padding: 8px 14px;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 500;
        border: 1px solid #bbf7d0;
        margin-top: 10px;
    }
    /* Stili pulsanti rapidi stazioni */
    div.stButton > button {
        width: 100%;
        border-radius: 10px;
        font-weight: 600;
        padding: 8px 6px;
        font-size: 0.88rem;
    }
    .welcome-card {
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
        color: white;
        padding: 24px 20px;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 10px 20px -5px rgba(37, 99, 235, 0.3);
    }
    .welcome-card h2 {
        color: white !important;
        margin-bottom: 8px;
        font-size: 1.35rem;
    }
    .welcome-card p {
        color: #dbeafe;
        font-size: 0.95rem;
        margin-bottom: 0px;
    }
</style>
""", unsafe_allow_html=True)

# --- ANAGRAFICA STAZIONI CFR TOSCANA ---
STAZIONI_CFR = {
    "san_donato": {
        "nome": "San Donato (Orbetello)",
        "codice": "TOS03003099",
        "lat": 42.554,
        "lon": 11.237,
        "quota_m": 21,
        "url_grafico_cfr": "https://www.cfr.toscana.it/monitoraggio/image.php?id=TOS03003099&title=TOS03003099_termo&name=../tmp_cfr/td7c1e10c5c3c7dab855a6acc1b2ef2ca.png&type=termo",
        "url_csv_sir": "http://www.sir.toscana.it/archivio/download.php?IDST=termo_csv&IDS=TOS03003099"
    },
    "stiacciole": {
        "nome": "Stiacciole (Grosseto)",
        "codice": "TOS11000042",
        "lat": 42.767,
        "lon": 11.162,
        "quota_m": 43,
        "url_grafico_cfr": "https://www.cfr.toscana.it/monitoraggio/image.php?id=TOS11000042&title=TOS11000042_termo&name=../tmp_cfr/t55d58291d3f78ef6492c074958d02b5e.png&type=termo",
        "url_csv_sir": "http://www.sir.toscana.it/archivio/download.php?IDST=termo_csv&IDS=TOS11000042"
    },
    "follonica": {
        "nome": "Follonica",
        "codice": "TOS03002459",
        "lat": 42.924,
        "lon": 10.760,
        "quota_m": 5,
        "url_grafico_cfr": "https://www.cfr.toscana.it/monitoraggio/image.php?id=TOS03002459&title=TOS03002459_termo&name=../tmp_cfr/t70657d168fba8ee39fc6c664df951702.png&type=termo",
        "url_csv_sir": "http://www.sir.toscana.it/archivio/download.php?IDST=termo_csv&IDS=TOS03002459"
    },
    "capalbio": {
        "nome": "Capalbio",
        "codice": "TOS11000006",
        "lat": 42.405,
        "lon": 11.392,
        "quota_m": 110,
        "url_grafico_cfr": "https://www.cfr.toscana.it/monitoraggio/image.php?id=TOS11000006&title=TOS11000006_termo&name=../tmp_cfr/t028de8d84d15b401fc42ace828716a38.png&type=termo",
        "url_csv_sir": "http://www.sir.toscana.it/archivio/download.php?IDST=termo_csv&IDS=TOS11000006"
    },
    "rispescia": {
        "nome": "Rispescia (Alberese)",
        "codice": "TOS11000005",
        "lat": 42.706,
        "lon": 11.145,
        "quota_m": 15,
        "url_grafico_cfr": "https://www.cfr.toscana.it/monitoraggio/image.php?id=TOS11000005&title=TOS11000005_termo&name=../tmp_cfr/tfacaf1e3377dc3f45a29a720a82e9120.png&type=termo",
        "url_csv_sir": "http://www.sir.toscana.it/archivio/download.php?IDST=termo_csv&IDS=TOS11000005"
    },
    "braccagni": {
        "nome": "Braccagni",
        "codice": "TOS11000008",
        "lat": 42.845,
        "lon": 11.082,
        "quota_m": 18,
        "url_grafico_cfr": "https://www.cfr.toscana.it/monitoraggio/image.php?id=TOS11000008&title=TOS11000008_termo&name=../tmp_cfr/td9bf3bdbcbd6354c72cf4faf0fe517a5.png&type=termo",
        "url_csv_sir": "http://www.sir.toscana.it/archivio/download.php?IDST=termo_csv&IDS=TOS11000008"
    },
    "cesa": {
        "nome": "Cesa",
        "codice": "TOS11000037",
        "lat": 43.308,
        "lon": 11.828,
        "quota_m": 246,
        "url_grafico_cfr": "https://www.cfr.toscana.it/monitoraggio/image.php?id=TOS11000037&title=TOS11000037_termo&name=../tmp_cfr/t18a78281011c5681ea060e7b9831b700.png&type=termo",
        "url_csv_sir": "http://www.sir.toscana.it/archivio/download.php?IDST=termo_csv&IDS=TOS11000037"
    }
}

# --- COSTANTI DI CALIBRAZIONE GEOMETRICA PER TEMPERATURA ---
Y_0 = 375      # Pixel Y corrispondente a 0 °C (bordo inferiore griglia)
Y_MAX = 50     # Pixel Y per la scala massima (bordo superiore griglia)
DY = Y_0 - Y_MAX # 325 pixel di escursione verticale

def get_mappa_mezzore_48h():
    """
    Ritorna un dizionario con la mappatura pixel X per 96 intervalli di 30 minuti nelle 48 ore.
    Calibrato con precisione matematica sulla griglia del CFR Toscana:
    Ieri 00:00 = 70px, Oggi 00:00 = 325px, Fine griglia Oggi 24:00 = 580px.
    Sequenza di passi alternati per 2 ore: [21, 22, 21, 21] px.
    """
    map_mezzore = {}
    ieri_2h = {
        0: 70, 2: 91, 4: 113, 6: 134, 8: 155, 10: 176,
        12: 198, 14: 219, 16: 240, 18: 261, 20: 283, 22: 304
    }
    oggi_2h = {
        0: 325, 2: 346, 4: 368, 6: 389, 8: 410, 10: 431,
        12: 453, 14: 474, 16: 495, 18: 516, 20: 538, 22: 559
    }
    
    for day_off, grid_2h in [(-1, ieri_2h), (0, oggi_2h)]:
        for h_even in sorted(grid_2h.keys()):
            x_even = grid_2h[h_even]
            map_mezzore[(day_off, float(h_even))] = x_even
            
            if h_even < 22:
                x_next_even = grid_2h[h_even + 2]
                dx = x_next_even - x_even
                map_mezzore[(day_off, h_even + 0.5)] = int(round(x_even + dx * 0.25))
                map_mezzore[(day_off, h_even + 1.0)] = int(round(x_even + dx * 0.50))
                map_mezzore[(day_off, h_even + 1.5)] = int(round(x_even + dx * 0.75))
            else:
                dx = 21.0
                map_mezzore[(day_off, 22.5)] = int(round(x_even + dx * 0.25))
                map_mezzore[(day_off, 23.0)] = int(round(x_even + dx * 0.50))
                map_mezzore[(day_off, 23.5)] = int(round(x_even + dx * 0.75))
                
    return map_mezzore

def get_mappa_ore_48h():
    """Compatibilità per parti di codice che usano la mappa oraria."""
    map_m = get_mappa_mezzore_48h()
    return {(d, int(h)): x for (d, h), x in map_m.items() if h.is_integer()}

# --- COMPUTER VISION: PARSING GRAFICO CFR ---

def rileva_valore_massimo_temperatura(img):
    """Rileva la scala Y misurando le linee di griglia su più colonne per massima robustezza."""
    if img is None:
        return 34.0
    conteggi = []
    for x in [140, 220, 300, 420, 500]:
        linee_grigie = 0
        in_linea = False
        for y in range(55, 370):
            b, g, r = img[y, x]
            if abs(int(b) - 192) < 18 and abs(int(g) - 192) < 18 and abs(int(r) - 192) < 18:
                if not in_linea:
                    linee_grigie += 1
                    in_linea = True
            else:
                in_linea = False
        if linee_grigie > 0:
            conteggi.append(linee_grigie)
            
    if conteggi:
        return (max(conteggi) + 1) * 2.0
    return 34.0

def trova_pixel_blu_in_colonna(img, x_target_orig, zoom_factor=4):
    """
    Identifica le coordinate Y del tracciato blu della temperatura a risoluzione 4x (Super-Resolution Zoom).
    Ritorna (y_min_equiv, y_centroid_equiv).
    y_min_equiv: punto di picco massimo del tracciato blu con precisione sub-pixel (±0.03 °C)
    y_centroid_equiv: centro di massa del tratto blu
    """
    if img is None:
        return None, None
        
    if img.shape[0] == 480 and zoom_factor > 1:
        img_4x = cv2.resize(img, (img.shape[1] * zoom_factor, img.shape[0] * zoom_factor), interpolation=cv2.INTER_CUBIC)
    else:
        img_4x = img
        zoom_factor = max(1, img.shape[0] // 480)
        
    Y_0_4x = Y_0 * zoom_factor
    Y_MAX_4x = Y_MAX * zoom_factor
    
    hsv_4x = cv2.cvtColor(img_4x, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([85, 20, 20])
    upper_blue = np.array([145, 255, 255])
    mask_4x = cv2.inRange(hsv_4x, lower_blue, upper_blue)
    
    x_4x = int(round(x_target_orig * zoom_factor))
    window_4x = 2 * zoom_factor
    y_pixels = []
    
    y_min_bound = max(0, int(Y_MAX_4x))
    y_max_bound = min(mask_4x.shape[0] - 1, int(Y_0_4x))
    
    for dx in range(-window_4x, window_4x + 1):
        cx = x_4x + dx
        if 0 <= cx < mask_4x.shape[1]:
            for y in range(y_min_bound, y_max_bound + 1):
                if mask_4x[y, cx] == 255:
                    y_pixels.append(y)
                    
    if not y_pixels:
        return None, None
        
    y_sorted = sorted(y_pixels)
    top_k = max(1, len(y_sorted) // 10)
    y_top_fine = float(np.mean(y_sorted[:top_k]))
    y_centroid_fine = float(np.mean(y_pixels))
    
    return y_top_fine / zoom_factor, y_centroid_fine / zoom_factor

def genera_overlay_scansione(img_path, scan_records, val_max_t):
    """Disegna i punti di scansione ed i valori di temperatura sul grafico originale."""
    img = cv2.imread(img_path)
    if img is None:
        return None
    
    map_48h = get_mappa_ore_48h()
    for rec in scan_records:
        day_off = -1 if rec["Giorno"] == "Ieri" else 0
        h = int(rec["Ora"].split(":")[0])
        key = (day_off, h)
        if key in map_48h:
            x = map_48h[key]
            y = rec["y_pixel"]
            val = rec["Temperatura (°C)"]
            if y is not None:
                y_int = int(round(y))
                cv2.circle(img, (x, y_int), 4, (0, 0, 255), -1)
                cv2.circle(img, (x, y_int), 5, (255, 255, 255), 1)
                cv2.putText(
                    img, f"{val:.1f}°", (x - 8, y_int - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.28, (0, 0, 0), 1, cv2.LINE_AA
                )
    
    out_dir = os.path.join(".", "scarichi_temp")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "overlay_temperatura.png")
    cv2.imwrite(out_path, img)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# --- OPEN-METEO FALLBACK API ---

def recupera_fallback_open_meteo(lat, lon):
    """Recupera la serie di temperatura 48h da Open-Meteo se il server CFR non risponde."""
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&hourly=temperature_2m&timezone=Europe%2FRome"
        f"&past_days=1&forecast_days=1&models=icon_eu"
    )
    res = requests.get(url, timeout=4.0)
    if res.status_code != 200:
        raise Exception(f"Open-Meteo HTTP {res.status_code}")
    
    data = res.json()
    times = data["hourly"]["time"]
    temps = data["hourly"]["temperature_2m"]
    
    rome_tz = pytz.timezone('Europe/Rome')
    now = datetime.datetime.now(rome_tz)
    oggi_str = now.strftime("%Y-%m-%d")
    ieri_str = (now - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    
    records = []
    for t_str, temp in zip(times, temps):
        dt = datetime.datetime.fromisoformat(t_str)
        date_part = dt.strftime("%Y-%m-%d")
        time_part = dt.strftime("%H:00")
        
        if date_part == ieri_str:
            records.append({
                "Giorno": "Ieri",
                "Data": (now - datetime.timedelta(days=1)).strftime("%d/%m/%Y"),
                "Ora": time_part,
                "Etichetta": f"Ieri {time_part}",
                "Temperatura (°C)": round(temp, 1),
                "Temperatura_raw": round(temp, 1),
                "y_pixel": None
            })
        elif date_part == oggi_str:
            if dt <= now:
                records.append({
                    "Giorno": "Oggi",
                    "Data": now.strftime("%d/%m/%Y"),
                    "Ora": time_part,
                    "Etichetta": f"Oggi {time_part}",
                    "Temperatura (°C)": round(temp, 1),
                    "Temperatura_raw": round(temp, 1),
                    "y_pixel": None
                })
    return records

# --- GESTIONE DATI CON CACHING ---

@st.cache_data(ttl=900, show_spinner=False)
def carica_dati_temperatura(stazione_key):
    """
    Download grafico CFR, estrazione Computer Vision ed eventuale Fallback Open-Meteo.
    Cache di 15 minuti (ttl=900s).
    """
    info = STAZIONI_CFR[stazione_key]
    url_grafico = info["url_grafico_cfr"]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0",
        "Referer": "https://www.cfr.toscana.it/monitoraggio/index.php",
    }
    
    records = []
    used_fallback = False
    img_path = None
    val_max_t = 34.0
    
    try:
        res = requests.get(url_grafico, headers=headers, timeout=2.0)
        if res.status_code == 200:
            temp_dir = os.path.join(".", "scarichi_temp")
            os.makedirs(temp_dir, exist_ok=True)
            img_path = os.path.join(temp_dir, f"{stazione_key}_termo.png")
            with open(img_path, "wb") as f:
                f.write(res.content)
            
            img = cv2.imread(img_path)
            if img is not None:
                val_max_t = rileva_valore_massimo_temperatura(img)
                zoom_factor = 4
                img_4x = cv2.resize(img, (640 * zoom_factor, 480 * zoom_factor), interpolation=cv2.INTER_CUBIC)
                
                map_mezzore = get_mappa_mezzore_48h()
                
                rome_tz = pytz.timezone('Europe/Rome')
                now = datetime.datetime.now(rome_tz)
                
                for (day_off, h_val), x_px in sorted(map_mezzore.items()):
                    giorno_label = "Ieri" if day_off == -1 else "Oggi"
                    dt_giorno = now - datetime.timedelta(days=1) if day_off == -1 else now
                    data_fmt = dt_giorno.strftime("%d/%m/%Y")
                    
                    h_int = int(h_val)
                    m_int = int(round((h_val - h_int) * 60))
                    ora_fmt = f"{h_int:02d}:{m_int:02d}"
                    
                    y_min, y_cent = trova_pixel_blu_in_colonna(img_4x, x_px, zoom_factor=4)
                    if y_cent is not None:
                        t_cent = val_max_t * ((Y_0 - y_cent) / DY)
                        t_cent = max(-10.0, min(t_cent, val_max_t + 5.0))
                        t_peak = val_max_t * ((Y_0 - y_min) / DY)
                        t_peak = max(-10.0, min(t_peak, val_max_t + 5.0))
                        
                        records.append({
                            "Giorno": giorno_label,
                            "Data": data_fmt,
                            "Ora": ora_fmt,
                            "Etichetta": f"{giorno_label} {ora_fmt}",
                            "Temperatura (°C)": round(t_cent, 1),
                            "Temperatura_medio": round(t_cent, 1),
                            "Temperatura_peak": round(t_peak, 1),
                            "Temperatura_raw": t_cent,
                            "y_pixel": round(y_cent, 2)
                        })
        else:
            used_fallback = True
    except Exception:
        used_fallback = True
        
    if used_fallback or len(records) == 0:
        try:
            records = recupera_fallback_open_meteo(info["lat"], info["lon"])
            used_fallback = True
        except Exception:
            records = []
            
    return records, used_fallback, img_path, val_max_t

# --- APPLICAZIONE STREAMLIT UI ---

def main():
    st.markdown(
        "<h1 style='margin-bottom: 2px;'>🌡️ ThermoCentral "
        "<span style='font-size: 0.55em; font-weight: normal; color: #64748b;'>"
        "(Microclima Agricolo)</span></h1>",
        unsafe_allow_html=True
    )
    
    alias_stazioni = {
        "sandonato": "san_donato",
        "san_donato": "san_donato",
        "stiacciole": "stiacciole",
        "follonica": "follonica",
        "capalbio": "capalbio",
        "rispescia": "rispescia",
        "braccagni": "braccagni",
        "cesa": "cesa"
    }
    
    tutte_chiavi = list(STAZIONI_CFR.keys())
    opzioni_display = {k: STAZIONI_CFR[k]["nome"] for k in tutte_chiavi}

    if "stazione_selezionata" not in st.session_state:
        query_param = st.query_params.get("stazione", "").lower().strip()
        st.session_state["stazione_selezionata"] = alias_stazioni.get(query_param, None)

    def imposta_stazione(key):
        st.session_state["stazione_selezionata"] = key
        if key:
            st.query_params["stazione"] = key

    selected_key = st.session_state.get("stazione_selezionata")
    
    st.markdown("<div style='margin-top: 10px; margin-bottom: 10px;'></div>", unsafe_allow_html=True)
    
    if not selected_key or selected_key not in STAZIONI_CFR:
        st.markdown(
            """
            <div class="welcome-card">
                <h2>📍 Seleziona una Stazione Meteorologica</h2>
                <p>Tocca una delle stazioni qui sotto per caricare immediatamente i dati della temperatura e i grafici.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(f"### 📍 Stazione Attiva: **{STAZIONI_CFR[selected_key]['nome']}**")

    st.markdown("**Seleziona stazione:**")
    cols = st.columns(3)
    for i, key in enumerate(tutte_chiavi):
        col = cols[i % 3]
        is_selected = (key == selected_key)
        nome_breve = STAZIONI_CFR[key]['nome'].split(' (')[0]
        label = f"✓ {nome_breve}" if is_selected else nome_breve
        btn_type = "primary" if is_selected else "secondary"
        
        if col.button(label, key=f"btn_main_{key}", type=btn_type, use_container_width=True):
            imposta_stazione(key)
            st.rerun()

    st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)
    
    logo_path = os.path.join(os.path.dirname(__file__), "logo lm chat gpt.png")
    if os.path.exists(logo_path):
        sb_col1, sb_col2, sb_col3 = st.sidebar.columns([1, 3, 1])
        with sb_col2:
            st.image(logo_path, width=140)
            
    st.sidebar.header("📍 Menu Stazioni")
    sb_index = tutte_chiavi.index(selected_key) if selected_key in tutte_chiavi else None
    sb_selected = st.sidebar.selectbox(
        "Oppure scegli dall'elenco:",
        options=tutte_chiavi,
        index=sb_index,
        placeholder="-- Seleziona una stazione --",
        format_func=lambda x: opzioni_display.get(x, x),
        key="sb_select_box"
    )
    
    if sb_selected != selected_key and sb_selected is not None:
        imposta_stazione(sb_selected)
        st.rerun()

    if not selected_key or selected_key not in STAZIONI_CFR:
        st.markdown("---")
        st.markdown(
            "<p style='text-align: center; color: #64748b; font-size: 0.85rem; margin-top: 20px;'>"
            "Origine dati: <b>Rete Centro Funzionale Regionale (CFR Toscana)</b> — "
            "<a href='https://www.cfr.toscana.it/' target='_blank' style='color: #2563eb; text-decoration: underline;'>www.cfr.toscana.it</a>"
            "</p>",
            unsafe_allow_html=True
        )
        return

    info_stazione = STAZIONI_CFR[selected_key]
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Dettagli Stazione:**")
    st.sidebar.write(f"• **Codice:** `{info_stazione['codice']}`")
    st.sidebar.write(f"• **Quota:** {info_stazione['quota_m']} m s.l.m.")
    st.sidebar.write(f"• **Coordinate:** {info_stazione['lat']}°N, {info_stazione['lon']}°E")
    
    if st.sidebar.button("🔄 Aggiorna Dati (Bypass Cache)", type="secondary"):
        st.cache_data.clear()
        st.rerun()

    with st.spinner(f"Caricamento dati per {info_stazione['nome']}..."):
        records, used_fallback, img_path, val_max_t = carica_dati_temperatura(selected_key)
        
    if not records:
        st.error("Impossibile recuperare i dati della temperatura.")
        return

    df = pd.DataFrame(records)
    df_ieri = df[df["Giorno"] == "Ieri"]
    df_oggi = df[df["Giorno"] == "Oggi"]
    
    ultimo_dato = df.iloc[-1]
    temp_istantanea = ultimo_dato["Temperatura (°C)"]
    ora_istantanea = ultimo_dato["Ora"]
    giorno_istantaneo = ultimo_dato["Giorno"]
    
    t_media_ieri = df_ieri["Temperatura (°C)"].mean() if not df_ieri.empty else 0.0
    
    if not df_oggi.empty:
        col_max = "Temperatura_raw" if "Temperatura_raw" in df_oggi.columns else "Temperatura (°C)"
        idx_max_oggi = df_oggi[col_max].idxmax()
        t_max_oggi = df_oggi.loc[idx_max_oggi, "Temperatura (°C)"]
        ora_max_oggi = df_oggi.loc[idx_max_oggi, "Ora"]
        
        idx_min_oggi = df_oggi[col_max].idxmin()
        t_min_oggi = df_oggi.loc[idx_min_oggi, "Temperatura (°C)"]
        ora_min_oggi = df_oggi.loc[idx_min_oggi, "Ora"]
    else:
        t_max_oggi, ora_max_oggi = 0.0, "--:--"
        t_min_oggi, ora_min_oggi = 0.0, "--:--"

    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">🌡️ Temp. Istantanea</div>
                <div class="metric-value" style="color: #2563eb;">{temp_istantanea:.1f} °C</div>
                <div class="metric-sub">Rilevata: <b>{giorno_istantaneo} ore {ora_istantanea}</b></div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with c2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">🔥 Max Odierna</div>
                <div class="metric-value" style="color: #dc2626;">{t_max_oggi:.1f} °C</div>
                <div class="metric-sub">Registrata alle ore <b>{ora_max_oggi}</b></div>
            </div>
            """,
            unsafe_allow_html=True
        )

    if used_fallback:
        st.markdown(
            '<div class="badge-fallback">⚠️ <b>Nota:</b> Server CFR momentaneamente non raggiungibile. Dati via modello meteo di backup.</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="badge-cfr">✅ <b>Dati scaricati con successo</b></div>',
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader("📉 Andamento Temperatura (48 Ore)")
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df["Etichetta"],
        y=df["Temperatura (°C)"],
        mode='lines+markers',
        name='Temperatura (°C)',
        line=dict(color='#2563eb', width=3.5),
        marker=dict(size=7, color='#1e40af', symbol='circle'),
        hovertemplate='<b>%{x}</b><br>Temperatura: <b>%{y:.1f} °C</b><extra></extra>'
    ))
    
    fig.add_hline(
        y=35.0,
        line=dict(color='#ef4444', width=1.5, dash='dash'),
        annotation_text="Soglia Calore Critico (35°C)",
        annotation_position="top left",
        annotation_font=dict(color='#ef4444', size=11)
    )
    
    fig.add_hline(
        y=15.0,
        line=dict(color='#3b82f6', width=1.5, dash='dash'),
        annotation_text="Soglia Minima Coltura (15°C)",
        annotation_position="bottom left",
        annotation_font=dict(color='#3b82f6', size=11)
    )
    
    if not df_oggi.empty:
        prima_ora_oggi = df_oggi.iloc[0]["Etichetta"]
        fig.add_shape(
            type="line",
            x0=prima_ora_oggi,
            x1=prima_ora_oggi,
            y0=0,
            y1=1,
            yref="paper",
            line=dict(color='#94a3b8', width=1.5, dash='dot')
        )
        fig.add_annotation(
            x=prima_ora_oggi,
            y=0.98,
            yref="paper",
            text="Inizio Oggi (00:00)",
            showarrow=False,
            xanchor="left",
            font=dict(color='#64748b', size=10)
        )
        
    y_min_val = max(-5, df["Temperatura (°C)"].min() - 3)
    y_max_val = max(38, df["Temperatura (°C)"].max() + 3)
    
    fig.update_layout(
        xaxis_title="Timeline Oraria (Ieri & Oggi)",
        yaxis_title="Temperatura (°C)",
        yaxis_range=[y_min_val, y_max_val],
        height=380,
        margin=dict(l=10, r=10, t=30, b=40),
        plot_bgcolor='white',
        paper_bgcolor='white',
        dragmode=False,
        hovermode="x unified",
        xaxis=dict(
            gridcolor='#f1f5f9',
            tickangle=-45,
            nticks=14,
            fixedrange=True
        ),
        yaxis=dict(
            gridcolor='#f1f5f9',
            fixedrange=True
        )
    )
    
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            'displayModeBar': False,
            'scrollZoom': False,
            'doubleClick': False,
            'showAxisDragHandles': False
        }
    )

    # --- SINTESI CONFRONTO GIORNALIERO ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📊 Confronto Termico Giornaliero")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 📅 Giorno Precedente (Ieri)")
        if not df_ieri.empty:
            col_max_i = "Temperatura_raw" if "Temperatura_raw" in df_ieri.columns else "Temperatura (°C)"
            idx_max_ieri = df_ieri[col_max_i].idxmax()
            t_max_ieri = df_ieri.loc[idx_max_ieri, "Temperatura (°C)"]
            ora_max_ieri = df_ieri.loc[idx_max_ieri, "Ora"]
            
            idx_min_ieri = df_ieri[col_max_i].idxmin()
            t_min_ieri = df_ieri.loc[idx_min_ieri, "Temperatura (°C)"]
            ora_min_ieri = df_ieri.loc[idx_min_ieri, "Ora"]
            
            st.write(f"• **Temperatura Media:** `{df_ieri['Temperatura (°C)'].mean():.1f} °C`")
            st.write(f"• **Temperatura Max:** `{t_max_ieri:.1f} °C` (alle {ora_max_ieri})")
            st.write(f"• **Temperatura Min:** `{t_min_ieri:.1f} °C` (alle {ora_min_ieri})")
    with c2:
        st.markdown("#### 📅 Giorno Corrente (Oggi)")
        if not df_oggi.empty:
            st.write(f"• **Temperatura Media Parziale:** `{df_oggi['Temperatura (°C)'].mean():.1f} °C`")
            st.write(f"• **Temperatura Max:** `{t_max_oggi:.1f} °C` (alle {ora_max_oggi})")
            st.write(f"• **Temperatura Min:** `{t_min_oggi:.1f} °C` (alle {ora_min_oggi})")

    # --- TABELLA ARCHIVIO ORARIO COMPLETA ---
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("📋 Tabella Archivio Orario Completa (48 Ore - Ogni 30 Minuti)", expanded=False):
        st.dataframe(
            df[["Giorno", "Data", "Ora", "Temperatura (°C)"]],
            use_container_width=True,
            hide_index=True
        )

    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #64748b; font-size: 0.85rem; margin-top: 20px;'>"
        "Origine dati: <b>Rete Centro Funzionale Regionale (CFR Toscana)</b> — "
        "<a href='https://www.cfr.toscana.it/' target='_blank' style='color: #2563eb; text-decoration: underline;'>www.cfr.toscana.it</a>"
        "</p>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
