import streamlit as st
import pandas as pd
import sqlite3

# =====================================================================
# INIZIALIZZAZIONE DATABASE PERMANENTE (SQLITE)
# =====================================================================
# Sostituisci la vecchia funzione inizializza_db_permanente con questa:
# =====================================================================
# INIZIALIZZAZIONE FORZATA E SICURA DEL DATABASE SQLITE
# =====================================================================
def inizializza_db_permanente():
    conn = sqlite3.connect("chefmargin.db")
    cursor = conn.cursor()
    # 1. Crea la tabella se manca
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dispensa (
            id_ingrediente TEXT PRIMARY KEY,
            nome TEXT,
            prezzo_kg REAL
        )
    """)
    
    # 2. Inserisce (o ripristina se mancanti) i tuoi 3 ingredienti core di base
    ingredienti_base = [
        ("ING-001", "Filetto di Salmone", 22.00),
        ("ING-002", "Patate", 2.00),
        ("ING-003", "Olio d'Oliva", 8.50)
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO dispensa (id_ingrediente, nome, prezzo_kg) 
        VALUES (?, ?, ?)
    """, ingredienti_base)
    
    conn.commit()
    conn.close()

# Avvia la creazione pulita del file di database
inizializza_db_permanente()



# Funzione per leggere la dispensa salvata nel file reale
def carica_dispensa_da_db():
    conn = sqlite3.connect("chefmargin.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id_ingrediente, nome, prezzo_kg FROM dispensa")
    righe = cursor.fetchall()
    conn.close()
    return {id_ing: {"nome": nome, "prezzo_kg": prezzo} for id_ing, nome, prezzo in righe}


# =====================================================================
# SCHERMATA DI ACCESSO (LOGIN)
# =====================================================================
if "autenticato" not in st.session_state:
    st.session_state.autenticato = False

if not st.session_state.autenticato:
    st.title("🔒 Accesso Riservato ChefMargin AI")
    password = st.text_input("Inserisci la chiave d'accesso per il ristorante:", type="password")
    if st.button("Entra nell'App"):
        if password == "3quarks": 
            st.session_state.autenticato = True
            st.rerun()
        else:
            st.error("Chiave errata. Contatta l'amministratore.")
    st.stop() 


# =====================================================================
# 1. IMPOSTAZIONI LAYOUT CELLULARE
# =====================================================================
st.set_page_config(
    page_title="ChefMargin AI",
    page_icon="👨‍🍳",
    layout="centered"
)

st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3em;
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
    }
    .cost-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 12px;
        border-left: 5px solid #FF4B4B;
        margin-bottom: 10px;
    }
    .metric-value {
        font-size: 22px;
        font-weight: bold;
        color: #111;
    }
    </style>
    """, unsafe_allow_html=True)


# =====================================================================
# 2. CARICAMENTO DATI (SESSION STATE + SQLITE)
# =====================================================================
# Carica la dispensa dal database SQL permanente invece che dal dizionario fisso
if "database_dispensa" not in st.session_state:
    st.session_state.database_dispensa = carica_dispensa_da_db()

if "database_personale" not in st.session_state:
    st.session_state.database_personale = {
        "STAFF-01": {"ruolo": "Capo Partita / Cuoco", "costo_orario": 16.50}
    }

if "database_attrezzature" not in st.session_state:
    st.session_state.database_attrezzature = {
        "EQ-01": {"nome": "Forno Convenzione Elettrico", "costo_minuto": 0.08},
        "EQ-02": {"nome": "Fornello a Gas Grande", "costo_minuto": 0.05}
    }

if "database_ricette" not in st.session_state:
    st.session_state.database_ricette = {
        "RIC-101": {"nome_piatto": "Salmone al Forno con Patate", "prezzo_menu": 18.00}
    }

if "ingredienti_ricetta" not in st.session_state:
    st.session_state.ingredienti_ricetta = [
        {"id_ricetta": "RIC-101", "id_ingrediente": "ING-001", "grammi_usati": 200},
        {"id_ricetta": "RIC-101", "id_ingrediente": "ING-002", "grammi_usati": 150},
        {"id_ricetta": "RIC-101", "id_ingrediente": "ING-003", "grammi_usati": 15}
    ]

if "lavoro_ricetta" not in st.session_state:
    st.session_state.lavoro_ricetta = [
        {"id_ricetta": "RIC-101", "id_personale": "STAFF-01", "minuti_dedicati": 4}
    ]

if "cottura_ricetta" not in st.session_state:
    st.session_state.cottura_ricetta = [
        {"id_ricetta": "RIC-101", "id_attrezzatura": "EQ-01", "minuti_utilizzo": 15}
    ]


# =====================================================================
# 3. NAVIGAZIONE SEMPLICE (BARRA LATERALE)
# =====================================================================
st.sidebar.title("👨‍🍳 ChefMargin AI")
st.sidebar.write("Menu Principale")

sezione = st.sidebar.radio(
    "Seleziona la sezione:",
    ["📊 Calcolatore", "🗄️ Database Costi", "📜 Ricettario"]
)


# =====================================================================
# SEZIONE 1: IL CALCOLATORE
# =====================================================================
if sezione == "📊 Calcolatore":
    st.header("📊 Calcolatore Margini")
    
    opzioni_piatti = {id_r: r["nome_piatto"] for id_r, r in st.session_state.database_ricette.items()}
    id_selezionato = st.selectbox("Seleziona il piatto da analizzare:", list(opzioni_piatti.keys()), format_func=lambda x: opzioni_piatti[x])
    
    piatto = st.session_state.database_ricette[id_selezionato]
    prezzo_menu_dinamico = st.number_input("Prezzo di Vendita sul Menu (€)", value=piatto["prezzo_menu"], step=0.50)
    
    costo_ingredienti = 0.0
    for legame in st.session_state.ingredienti_ricetta:
        if legame["id_ricetta"] == id_selezionato:
            ing = st.session_state.database_dispensa[legame["id_ingrediente"]]
            costo_ingredienti += (ing["prezzo_kg"] / 1000) * legame["grammi_usati"]

    costo_lavoro = 0.0
    for legame in st.session_state.lavoro_ricetta:
        if legame["id_ricetta"] == id_selezionato:
            pers = st.session_state.database_personale[legame["id_personale"]]
            costo_lavoro += (pers["costo_orario"] / 60) * legame["minuti_dedicati"]

    costo_energia = 0.0
    for legame in st.session_state.cottura_ricetta:
        if legame["id_ricetta"] == id_selezionato:
            eq = st.session_state.database_attrezzature[legame["id_attrezzatura"]]
            costo_energia += eq["costo_minuto"] * legame["minuti_utilizzo"]

    costo_reale_produzione = costo_ingredienti + costo_lavoro + costo_energia
    margine_lordo_euro = prezzo_menu_dinamico - costo_reale_produzione
    
    incidenza_food_cost_puro = (costo_ingredienti / prezzo_menu_dinamico) * 100 if prezzo_menu_dinamico > 0 else 0
    incidenza_costo_reale = (costo_reale_produzione / prezzo_menu_dinamico) * 100 if prezzo_menu_dinamico > 0 else 0
    prezzo_consigliato = costo_reale_produzione * 3.33

    st.write("### Dettaglio Costi Reali:")
    st.markdown(f"""
    <div class='cost-card'>🥩 <b>Costo Ingredienti (Food Cost):</b> <span class='metric-value'>€ {costo_ingredienti:.2f}</span> ({incidenza_food_cost_puro:.1f}% del menu)</div>
    <div class='cost-card'>👨‍🍳 <b>Costo Lavoro Umano (Labor Cost):</b> <span class='metric-value'>€ {costo_lavoro:.2f}</span></div>
    <div class='cost-card'>⚡ <b>Costo Gas/Elettricità (Energy Cost):</b> <span class='metric-value'>€ {costo_energia:.2f}</span></div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="💰 Costo Reale Totale", value=f"€ {costo_reale_produzione:.2f}")
    with col2:
        st.metric(label="💶 Guadagno Lordo", value=f"€ {margine_lordo_euro:.2f}")

    if incidenza_costo_reale <= 40.0:
        st.success(f"🟢 VERDE - Margine perfetto ({incidenza_costo_reale:.1f}%). Il piatto paga energia, personale e genera utile.")
    elif 40.0 < incidenza_costo_reale <= 50.0:
        st.warning(f"🟡 GIALLO - Attenzione ({incidenza_costo_reale:.1f}%). Le bollette o i tempi di cottura stanno tagliando i profitti.")
    else:
        st.error(f"🔴 ROSSO - Emergenza Margini! ({incidenza_costo_reale:.1f}%) Stai regalando il piatto.")
        st.info(f"👉 CONSIGLIO: Per rientrare nei costi, porta il prezzo sul menu a almeno € {prezzo_consigliato:.2f}")


# =====================================================================
# SEZIONE 2: DATABASE COSTI
# =====================================================================
elif sezione == "🗄️ Database Costi":
    st.header("🗄️ Database Costi Operativi")
    tab1, tab2, tab3 = st.tabs(["🥩 Dispensa", "👨‍🍳 Personale", "⚡ Utenze"])
    
    with tab1:
        st.subheader("Aggiorna o Aggiungi Prezzi Ingredienti")
        ing_scelto = st.selectbox("Seleziona ingrediente da aggiornare:", list(st.session_state.database_dispensa.keys()), format_func=lambda x: st.session_state.database_dispensa[x]["nome"])
        nuovo_prezzo = st.number_input("Nuovo prezzo al KG (€)", value=st.session_state.database_dispensa[ing_scelto]["prezzo_kg"], step=0.50)
        
        if st.button("Aggiorna Prezzo Dispensa"):
            # --- MODIFICA AGGIUNTA: Scrittura sul file database reale ---
            conn = sqlite3.connect("chefmargin.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE dispensa SET prezzo_kg = ? WHERE id_ingrediente = ?", (nuovo_prezzo, ing_scelto))
            conn.commit()
            conn.close()
            
            # Aggiorna la memoria locale dell'app per riflettere il cambio
            st.session_state.database_dispensa[ing_scelto]["prezzo_kg"] = nuovo_prezzo
            st.success(f"🔄 Prezzo aggiornato nel database per: {st.session_state.database_dispensa[ing_scelto]['nome']}")
            st.rerun()
            
