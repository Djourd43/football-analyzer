import streamlit as st
import time
import json
from datetime import datetime
import pandas as pd

st.set_page_config(
    page_title="⚽ Analyseur Match Football",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .block-container {
        padding-top: 0.3rem;
        padding-bottom: 0.3rem;
        padding-left: 0.4rem;
        padding-right: 0.4rem;
    }
    .stButton>button {
        width: 100%;
        height: 42px;
        font-size: 11px;
        font-weight: bold;
        margin: 1px 0;
        border-radius: 5px;
        padding: 1px 2px;
        line-height: 1.1;
    }
    h1 {
        font-size: 18px !important;
        margin-bottom: 2px !important;
    }
    hr { margin: 3px 0 !important; }
    [data-testid="column"] { padding: 0 2px !important; }
    .stTextInput input { font-size: 12px; padding: 3px 6px; }
    .timer {
        font-size: 40px;
        font-weight: bold;
        text-align: center;
        color: #2c3e50;
        line-height: 1;
    }
    .separator {
        height: 5px;
        background-color: #bdc3c7;
        border-radius: 3px;
        margin: 4px 0;
    }
    /* Boutons label non cliquables */
    .label-btn {
        width: 100%;
        height: 42px;
        font-size: 11px;
        font-weight: bold;
        border-radius: 5px;
        border: none;
        cursor: default;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        line-height: 1.2;
        margin: 1px 0;
    }
</style>
""", unsafe_allow_html=True)

# ─── INITIALISATION ───────────────────────────────────────────────────────────
STATS_KEYS = [
    'buts', 'ballons_surface', 'occasions',
    'tirs_hc', 'tirs_contres', 'tirs_cadres',
    'e25_g', 'e25_a', 'e25_d',
    'sdb_courte_perdue', 'sdb_courte_med',
    'sdb_longue_perdue', 'sdb_longue_med',
    'renvers', 'percu', 'par_dessus',
    'rcp_hte', 'rcp_med', 'rcp_bass',
    'duel_aer_perdu', 'duel_aer_gagne',
    'duel_sol_perdu', 'duel_sol_gagne',
    'cinquante_perdu', 'cinquante_gagne',
    'touche_perdue', 'touche_gardee',
    'touche_ar', 'touche_lat', 'touche_av',
    'cf_1', 'cf_23', 'cf_combine',
    'cf_adv', 'cf_cont_hc', 'cf_cadre',
    'corner_1er', 'corner_23', 'corner_combine',
    'corner_adv', 'corner_cont_hc', 'corner_cadre',
    'fautes', 'cartons', 'hors_jeu'
]

def init_stats():
    return {k: 0 for k in STATS_KEYS}

if 'stats'            not in st.session_state: st.session_state.stats            = {'home': init_stats(), 'away': init_stats()}
if 'match_start_time' not in st.session_state: st.session_state.match_start_time = None
if 'match_running'    not in st.session_state: st.session_state.match_running    = False
if 'action_history'   not in st.session_state: st.session_state.action_history   = []
if 'home_team_name'   not in st.session_state: st.session_state.home_team_name   = "Équipe Domicile"
if 'away_team_name'   not in st.session_state: st.session_state.away_team_name   = "Équipe Adverse"

# ─── FONCTIONS ────────────────────────────────────────────────────────────────
def start_match():
    st.session_state.match_start_time = time.time()
    st.session_state.match_running = True

def stop_match():
    st.session_state.match_running = False

def reset_match():
    st.session_state.stats            = {'home': init_stats(), 'away': init_stats()}
    st.session_state.match_start_time = None
    st.session_state.match_running    = False
    st.session_state.action_history   = []

def get_elapsed_time():
    if st.session_state.match_running and st.session_state.match_start_time:
        e = int(time.time() - st.session_state.match_start_time)
        return f"{e//60:02d}:{e%60:02d}"
    return "00:00"

def increment_stat(team, stat):
    st.session_state.action_history.append({
        'team': team, 'stat': stat,
        'time': round(time.time() - (st.session_state.match_start_time or 0), 1),
        'timestamp': datetime.now().isoformat()
    })
    st.session_state.stats[team][stat] += 1

def undo_last_action():
    if not st.session_state.action_history:
        st.toast("Aucune action à annuler"); return
    last = st.session_state.action_history.pop()
    st.session_state.stats[last['team']][last['stat']] = max(0, st.session_state.stats[last['team']][last['stat']] - 1)
    st.toast(f"↶ Annulé : {last['stat']} ({last['team']})")

# ─── RENDU D'UNE ÉQUIPE ───────────────────────────────────────────────────────
def render_team(team, is_home):
    s   = st.session_state.stats[team]
    bg  = "#c0392b" if is_home else "#2c3e50"
    fg  = "white"

    # Bouton cliquable normal
    def btn(col, label, key):
        with col:
            if st.button(f"{label}  {s[key]}", key=f"{team}_{key}", use_container_width=True):
                increment_stat(team, key)
                st.rerun()

    # Bouton label non cliquable — affiche la somme de deux clés
    def lbl(col, label, key_a, key_b=None):
        total = s[key_a] + (s[key_b] if key_b else 0)
        with col:
            st.markdown(
                f"<div class='label-btn' style='background:{bg};color:{fg};'>"
                f"{label}<br><strong>{total}</strong></div>",
                unsafe_allow_html=True
            )

    def sep():
        st.markdown("<div class='separator'></div>", unsafe_allow_html=True)

    # Injection couleur pour les boutons cliquables de cette équipe
    color_css = f"""
    <style>
    [data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"]
    div[data-testid="column"] button {{
        background-color: {bg} !important;
        color: {fg} !important;
        border: none !important;
    }}
    </style>""" if is_home else f"""
    <style>
    /* Pas de surcharge pour l'équipe adverse */
    </style>"""
    st.markdown(color_css, unsafe_allow_html=True)

    # ── Ligne 1 : BUT | BAL.SURF. | OCCAS.
    c1, c2, c3 = st.columns(3)
    btn(c1, "⚽ BUT",       "buts")
    btn(c2, "🎯 BAL.SURF.", "ballons_surface")
    btn(c3, "💡 OCCAS.",    "occasions")

    # ── Ligne 2 : TIRS HC | CONTRÉ | CADRÉ
    c1, c2, c3 = st.columns(3)
    btn(c1, "❌ TIRS HC", "tirs_hc")
    btn(c2, "🚫 CONTRÉ",  "tirs_contres")
    btn(c3, "✅ CADRÉ",   "tirs_cadres")

    sep()

    # ── Ligne 3 : 25M G | 25M A | 25M D
    c1, c2, c3 = st.columns(3)
    btn(c1, "⬅️ 25M G", "e25_g")
    btn(c2, "⬆️ 25M A", "e25_a")
    btn(c3, "➡️ 25M D", "e25_d")

    # ── Ligne 4 : SDB COURTE [label] | PERDUE | MÉDIANE
    c1, c2, c3 = st.columns(3)
    lbl(c1, "SDB COURTE", "sdb_courte_perdue", "sdb_courte_med")
    btn(c2, "PERDUE ❌",  "sdb_courte_perdue")
    btn(c3, "MÉDIANE ✅", "sdb_courte_med")

    # ── Ligne 5 : SDB LONGUE [label] | PERDUE | MÉDIANE
    c1, c2, c3 = st.columns(3)
    lbl(c1, "SDB LONGUE", "sdb_longue_perdue", "sdb_longue_med")
    btn(c2, "PERDUE ❌",  "sdb_longue_perdue")
    btn(c3, "MÉDIANE ✅", "sdb_longue_med")

    # ── Ligne 6 : RENVERS. | PERCU. | PAR-DESS.
    c1, c2, c3 = st.columns(3)
    btn(c1, "↔️ RENVERS.", "renvers")
    btn(c2, "💥 PERCU.",   "percu")
    btn(c3, "🔝 PAR-DESS.", "par_dessus")

    # ── Ligne 7 : RCP HTE | RCP MÉD | RCP BASS.
    c1, c2, c3 = st.columns(3)
    btn(c1, "🔺 RCP HTE",  "rcp_hte")
    btn(c2, "➡️ RCP MÉD",  "rcp_med")
    btn(c3, "🔻 RCP BASS.", "rcp_bass")

    sep()

    # ── Ligne 8 : D. AÉRIEN [label] | PERDU | GAGNÉ
    c1, c2, c3 = st.columns(3)
    lbl(c1, "✈️ D. AÉRIEN", "duel_aer_perdu", "duel_aer_gagne")
    btn(c2, "PERDU ❌",      "duel_aer_perdu")
    btn(c3, "GAGNÉ ✅",      "duel_aer_gagne")

    # ── Ligne 9 : D. SOL [label] | PERDU | GAGNÉ
    c1, c2, c3 = st.columns(3)
    lbl(c1, "👟 D. SOL", "duel_sol_perdu", "duel_sol_gagne")
    btn(c2, "PERDU ❌",   "duel_sol_perdu")
    btn(c3, "GAGNÉ ✅",   "duel_sol_gagne")

    # ── Ligne 10 : 50/50 [label] | PERDU | GAGNÉ
    c1, c2, c3 = st.columns(3)
    lbl(c1, "⚖️ 50/50", "cinquante_perdu", "cinquante_gagne")
    btn(c2, "PERDU ❌",   "cinquante_perdu")
    btn(c3, "GAGNÉ ✅",   "cinquante_gagne")

    sep()

    # ── Ligne 11 : TOUCHES [label] | PERDUE | GARDÉE
    c1, c2, c3 = st.columns(3)
    lbl(c1, "🏳️ TOUCHES", "touche_perdue", "touche_gardee")
    btn(c2, "PERDUE ❌",    "touche_perdue")
    btn(c3, "GARDÉE ✅",    "touche_gardee")

    # ── Ligne 12 : AR | LAT | AV
    c1, c2, c3 = st.columns(3)
    btn(c1, "↙️ AR",  "touche_ar")
    btn(c2, "⬆️ LAT", "touche_lat")
    btn(c3, "↗️ AV",  "touche_av")

    sep()

    # ── Ligne 13 : CF 1ER | 2ND ou 3EME | COMBINÉ
    c1, c2, c3 = st.columns(3)
    btn(c1, "CF 1️⃣",      "cf_1")
    btn(c2, "2️⃣ ou 3️⃣", "cf_23")
    btn(c3, "COMBINÉ",     "cf_combine")

    # ── Ligne 14 : ADV | CONT. ou H.C | CADRÉ
    c1, c2, c3 = st.columns(3)
    btn(c1, "ADV ❌",          "cf_adv")
    btn(c2, "CONT. ou H.C 🚫", "cf_cont_hc")
    btn(c3, "CADRÉ ✅",        "cf_cadre")

    sep()

    # ── Ligne 15 : CORNER 1ER | 2ND ou 3EME | COMBINÉ
    c1, c2, c3 = st.columns(3)
    btn(c1, "⛳️ 1ER",   "corner_1er")
    btn(c2, "2ND ou 3EME", "corner_23")
    btn(c3, "COMBINÉ",     "corner_combine")

    # ── Ligne 16 : ADV | CONTRÉ ou H.C | CADRÉ
    c1, c2, c3 = st.columns(3)
    btn(c1, "ADV ❌",             "corner_adv")
    btn(c2, "CONTRÉ ou H.C 🚫",  "corner_cont_hc")
    btn(c3, "CADRÉ ✅",           "corner_cadre")

    sep()

    # ── Ligne 17 : FAUTES | CARTONS | HJ
    c1, c2, c3 = st.columns(3)
    btn(c1, "FAUTES ❌",   "fautes")
    btn(c2, "CARTONS 🟨", "cartons")
    btn(c3, "HJ 🏁",      "hors_jeu")


# ─── MISE EN PAGE PRINCIPALE ──────────────────────────────────────────────────
st.markdown("# ⚽ Analyseur de Match")

c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
with c1:
    st.markdown(f"<div class='timer'>{get_elapsed_time()}</div>", unsafe_allow_html=True)
with c2:
    if st.button("▶️ Démarrer", use_container_width=True): start_match()
with c3:
    if st.button("⏸️ Pause", use_container_width=True): stop_match()
with c4:
    if st.button("🔄 Reset", use_container_width=True): reset_match(); st.rerun()

st.divider()

col_hn, col_an = st.columns(2)
with col_hn:
    st.session_state.home_team_name = st.text_input(
        "🏠 Nom Équipe Domicile", value=st.session_state.home_team_name, key="home_name")
with col_an:
    st.session_state.away_team_name = st.text_input(
        "✈️ Nom Équipe Adverse", value=st.session_state.away_team_name, key="away_name")

st.divider()

col_home, col_away = st.columns(2)
with col_home:
    render_team('home', is_home=True)
with col_away:
    render_team('away', is_home=False)

st.divider()

c_undo, c_json, c_csv = st.columns(3)
with c_undo:
    if st.button("↶ Annuler la dernière action", use_container_width=True):
        undo_last_action(); st.rerun()
with c_json:
    data = {
        'match_info': {
            'home_team': st.session_state.home_team_name,
            'away_team': st.session_state.away_team_name,
            'duration':  get_elapsed_time()
        },
        'stats':          st.session_state.stats,
        'action_history': st.session_state.action_history
    }
    st.download_button("📥 Télécharger JSON",
                       data=json.dumps(data, indent=2, ensure_ascii=False),
                       file_name=f"match_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                       mime="application/json", use_container_width=True)
with c_csv:
    rows = [{'Statistique': k,
             st.session_state.home_team_name: st.session_state.stats['home'][k],
             st.session_state.away_team_name: st.session_state.stats['away'][k]}
            for k in STATS_KEYS]
    st.download_button("📥 Télécharger CSV",
                       data=pd.DataFrame(rows).to_csv(index=False),
                       file_name=f"match_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                       mime="text/csv", use_container_width=True)

if st.session_state.match_running:
    time.sleep(1)
    st.rerun()
