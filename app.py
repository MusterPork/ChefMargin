import streamlit as st
import pandas as pd


# SCHERMATA DI ACCESSO (LOGIN)
if "autenticato" not in st.session_state:
    st.session_state.autenticato = False

if not st.session_state.autenticato:
    st.title("🔒 Accesso Riservato ChefMargin AI")
    password = st.text_input("Inserisci la chiave d'accesso per il ristorante:", type="password")
    if st.button("Entra nell'App"):
        if password == "3quarks": # Scegli la tua password
            st.session_state.autenticato = True
            st.rerun()
        else:
            st.error("Chiave errata. Contatta l'amministratore.")
    st.stop() # Blocca il resto del codice se non sei autenticato

# 1. IMPOSTAZIONI LAYOUT CELLULARE
st.set_page_config(
    page_title="ChefMargin AI",
    page_icon="👨‍🍳",
    layout="centered"
)

# Stile CSS per rendere i bottoni grandi (stile mobile) e i blocchi dei costi più carini
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

# 2. CARICAMENTO DEL TUO DATABASE CORE CORRETTO (Session State)
if "database_dispensa" not in st.session_state:
    st.session_state.database_dispensa = {
        "ING-001": {"nome": "Filetto di Salmone", "prezzo_kg": 22.00},
        "ING-002": {"nome": "Patate", "prezzo_kg": 2.00},
        "ING-003": {"nome": "Olio d'Oliva", "prezzo_kg": 8.50}
    }

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

# 3. NAVIGAZIONE SEMPLICE (BARRA LATERALE)
st.sidebar.title("👨‍🍳 ChefMargin AI")
st.sidebar.write("Menu Principale")

sezione = st.sidebar.radio(
    "Seleziona la sezione:",
    ["📊 Calcolatore", "🗄️ Database Costi", "📜 Ricettario"]
)

# =====================================================================
# SEZIONE 1: IL CALCOLATORE (LOGICA DEL TUO CODICE CORE)
# =====================================================================
if sezione == "📊 Calcolatore":
    st.header("📊 Calcolatore Margini")
    
    # Selezione dinamica del piatto
    opzioni_piatti = {id_r: r["nome_piatto"] for id_r, r in st.session_state.database_ricette.items()}
    id_selezionato = st.selectbox("Seleziona il piatto da analizzare:", list(opzioni_piatti.keys()), format_func=lambda x: opzioni_piatti[x])
    
    piatto = st.session_state.database_ricette[id_selezionato]
    
    # Permette allo chef di testare un cambio prezzo del menu al volo sul telefono
    prezzo_menu_dinamico = st.number_input("Prezzo di Vendita sul Menu (€)", value=piatto["prezzo_menu"], step=0.50)
    
    # --- ESECUZIONE CALCOLI ESATTI DEL TUO CODICE ---
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
    
    incidenza_food_cost_puro = (costo_ingredienti / prezzo_menu_dinamico) * 100
    incidenza_costo_reale = (costo_reale_produzione / prezzo_menu_dinamico) * 100
    prezzo_consigliato = costo_reale_produzione * 3.33

    # --- INTERFACCIA GRAFICA CARINA PER IL CELLULARE ---
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

    # --- LOGICA SEMAFORI CON LE TUE NUOVE SOGLIE (40% e 50%) ---
    if incidenza_costo_reale <= 40.0:
        st.success(f"🟢 VERDE - Margine perfetto ({incidenza_costo_reale:.1f}%). Il piatto paga energia, personale e genera utile.")
    elif 40.0 < incidenza_costo_reale <= 50.0:
        st.warning(f"🟡 GIALLO - Attenzione ({incidenza_costo_reale:.1f}%). Le bollette o i tempi di cottura stanno tagliando i profitti.")
    else:
        st.error(f"🔴 ROSSO - Emergenza Margini! ({incidenza_costo_reale:.1f}%) Stai regalando il piatto.")
        st.info(f"👉 CONSIGLIO: Per rientrare nei costi, porta il prezzo sul menu a almeno € {prezzo_consigliato:.2f}")

# =====================================================================
# SEZIONE 2: DATABASE COSTI (DISPENSA, PERSONALE, ENERGIA)
# =====================================================================
elif sezione == "🗄️ Database Costi":
    st.header("🗄️ Database Costi Operativi")
    
    tab1, tab2, tab3 = st.tabs(["🥩 Dispensa", "👨‍🍳 Personale", "⚡ Utenze"])
    
    with tab1:
        st.subheader("Aggiorna o Aggiungi Prezzi Ingredienti")
        # Menu per selezionare un ingrediente esistente da modificare
        ing_scelto = st.selectbox("Seleziona ingrediente da aggiornare:", list(st.session_state.database_dispensa.keys()), format_func=lambda x: st.session_state.database_dispensa[x]["nome"])
        nuovo_prezzo = st.number_input("Nuovo prezzo al KG (€)", value=st.session_state.database_dispensa[ing_scelto]["prezzo_kg"], step=0.50)
        
        if st.button("Aggiorna Prezzo Dispensa"):
            st.session_state.database_dispensa[ing_scelto]["prezzo_kg"] = nuovo_prezzo
            st.success(f"🔄 Prezzo aggiornato nel database per: {st.session_state.database_dispensa[ing_scelto]['nome']}")
            
        st.write("#### Stato attuale dispensa:")
        st.dataframe(pd.DataFrame.from_dict(st.session_state.database_dispensa, orient='index'), use_container_width=True)

    with tab2:
        st.subheader("Costo Orario Personale")
        st.session_state.database_personale["STAFF-01"]["costo_orario"] = st.number_input("Paga Oraria Cuoco (€/ora)", value=st.session_state.database_personale["STAFF-01"]["costo_orario"])
        st.info("I calcoli del calcolatore si aggiorneranno automaticamente basandosi su questo valore.")

    with tab3:
        st.subheader("Consumo Energetico Attrezzature")
        st.session_state.database_attrezzature["EQ-01"]["costo_minuto"] = st.number_input("Costo Forno al Minuto (€)", value=st.session_state.database_attrezzature["EQ-01"]["costo_minuto"], format="%.2f")
        st.session_state.database_attrezzature["EQ-02"]["costo_minuto"] = st.number_input("Costo Fornello Gas al Minuto (€)", value=st.session_state.database_attrezzature["EQ-02"]["costo_minuto"], format="%.2f")

# =====================================================================
# SEZIONE 3: RICETTARIO
# =====================================================================
elif sezione == "📜 Ricettario":
    st.header("📜 Il tuo Ricettario Avanzato")
    st.write("Elenco dei piatti registrati e dei relativi tempi tecnici:")
    
    for id_r, r in st.session_state.database_ricette.items():
        with st.expander(f"📖 {r['nome_piatto']} — Menu: € {r['prezzo_menu']:.2f}"):
            st.write("**⚙️ Dettagli Processo Produttivo:**")
            
            # Controlla che i blocchi FOR e IF sottostanti abbiano esattamente questi spazi:
            for legame in st.session_state.lavoro_ricetta:
                if legame["id_ricetta"] == id_r:
                    st.write(f"- ⏱️ Tempo Impiattamento/Lavoro: {legame['minuti_dedicati']} minuti")
                    
            for legame in st.session_state.cottura_ricetta:
                if legame["id_ricetta"] == id_r:
                    nome_eq = st.session_state.database_attrezzature[legame["id_attrezzatura"]]["nome"]
                    st.write(f"- 🔥 Cottura in {nome_eq}: {legame['minuti_utilizzo']} minuti")
            
            st.write("**🛒 Ingredienti Associati:**")
            for legame in st.session_state.ingredienti_ricetta:
                if legame["id_ricetta"] == id_r:
                    nome_ing = st.session_state.database_dispensa[legame["id_ingrediente"]]["nome"]
                    st.write(f"• {nome_ing}: {legame['grammi_usati']}g")
