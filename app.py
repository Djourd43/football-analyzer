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
        padding-top: 0.5rem;
        padding-bottom: 0.5rem;
        padding-left: 0.5rem;
        padding-right: 0.5rem;
    }
    .stButton>button {
        width: 100%;
        height: 52px;
        font-size: 13px;
        font-weight: bold;
        margin: 1px 0;
        border-radius: 6px;
        padding: 2px 4px;
        line-height: 1.2;
    }
    .team-header {
        font-size: 18px;
        font-weight: bold;
        text-align: center;
        padding: 8px;
        border-radius: 8px;
        margin-bottom: 6px;
    }
    .stat-display {
        padding: 8px;
        text-align: center;
        font-weight: bold;
        border-radius: 6px;
        margin: 1px 0;
        font-size: 14px;
    }
    .timer {
        font-size: 48px;
        font-weight: bold;
        text-align: center;
        color: #2c3e50;
        line-height: 1;
        margin-bottom: 4px;
    }
    h1 {
        font-size: 22px !important;
        margin-bottom: 4px !important;
        padding-bottom: 0 !important;
    }
    hr {
        margin: 4px 0 !important;
    }
    [data-testid="column"] {
        padding: 0 3px !important;
    }
    .stTextInput input {
        font-size: 14px;
        padding: 4px 8px;
    }
</style>
""", unsafe_allow_html=True)

if 'stats' not in st.session_state:
    st.session_state.stats = {
        'home': {
            'buts': 0, 'tirs': 0, 'tirs_hors': 0, 'tirs_cadre': 0, 'tirs_contres': 0,
            'occasions': 0, 'ballons_surface': 0,
            'entree_25m_gauche': 0, 'entree_25m_axe': 0, 'entree_25m_droite': 0,
            'centres_gauche': 0, 'centres_axe': 0, 'centres_droite': 0,
            'corners_gauche': 0, 'corners_droite': 0,
            'coups_francs': 0, 'fautes': 0, 'cartons': 0, 'hors_jeu': 0
        },
        'away': {
            'buts': 0, 'tirs': 0, 'tirs_hors': 0, 'tirs_cadre': 0, 'tirs_contres': 0,
            'occasions': 0, 'ballons_surface': 0,
            'entree_25m_gauche': 0, 'entree_25m_axe': 0, 'entree_25m_droite': 0,
            'centres_gauche': 0, 'centres_axe': 0, 'centres_droite': 0,
            'corners_gauche': 0, 'corners_droite': 0,
            'coups_francs': 0, 'fautes': 0, 'cartons': 0, 'hors_jeu': 0
        }
    }

if 'match_start_time'  not in st.session_state: st.session_state.match_start_time  = None
if 'match_running'     not in st.session_state: st.session_state.match_running     = False
if 'action_history'    not in st.session_state: st.session_state.action_history    = []
if 'home_team_name'    not in st.session_state: st.session_state.home_team_name    = "Équipe Domicile"
if 'away_team_name'    not in st.session_state: st.session_state.away_team_name    = "Équipe Adverse"

def start_match():
    st.session_state.match_start_time = time.time()
    st.session_state.match_running = True

def stop_match():
    st.session_state.match_running = False

def reset_match():
    for team in ['home', 'away']:
        for k in st.session_state.stats[team]:
            st.session_state.stats[team][k] = 0
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
        'time': time.time() - (st.session_state.match_start_time or 0),
        'timestamp': datetime.now().isoformat()
    })
    st.session_state.stats[team][stat] += 1

def increment_tir(team, sub_stat):
    increment_stat(team, sub_stat)
    s = st.session_state.stats[team]
    s['tirs'] = s['tirs_hors'] + s['tirs_cadre'] + s['tirs_contres']

def undo_last_action():
    if not st.session_state.action_history:
        st.toast("Aucune action à annuler")
        return
    last = st.session_state.action_history.pop()
    team, stat = last['team'], last['stat']
    st.session_state.stats[team][stat] = max(0, st.session_state.stats[team][stat] - 1)
    if stat in ['tirs_hors', 'tirs_cadre', 'tirs_contres']:
        s = st.session_state.stats[team]
        s['tirs'] = s['tirs_hors'] + s['tirs_cadre'] + s['tirs_contres']
    st.toast(f"↶ Annulé : {stat} ({team})")

st.markdown("# ⚽ Analyseur de Match")

c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
with c1:
    st.markdown(f"<div class='timer'>{get_elapsed_time()}</div>", unsafe_allow_html=True)
with c2:
    if st.button("▶️ Démarrer", use_container_width=True): start_match()
with c3:
    if st.button("⏸️ Pause", use_container_width=True): stop_match()
with c4:
    if st.button("🔄 Reset", use_container_width=True):
        reset_match(); st.rerun()

st.divider()

col_hn, col_an = st.columns(2)
with col_hn:
    st.session_state.home_team_name = st.text_input(
        "🏠 Équipe Domicile", value=st.session_state.home_team_name, key="home_name")
with col_an:
    st.session_state.away_team_name = st.text_input(
        "✈️ Équipe Adverse", value=st.session_state.away_team_name, key="away_name")

st.divider()

def render_team(team, color):
    name = st.session_state.home_team_name if team == 'home' else st.session_state.away_team_name
    s = st.session_state.stats[team]

    st.markdown(f"<div class='team-header' style='background:{color};color:white'>{name}</div>",
                unsafe_allow_html=True)

    # Ligne 1 : But | Ballons Surface | Occasions
    a, b, c = st.columns(3)
    with a:
        if st.button(f"⚽ But\n{s['buts']}", key=f"{team}_buts", use_container_width=True):
            increment_stat(team, 'buts'); st.rerun()
    with b:
        if st.button(f"🎯 Ballons Surface\n{s['ballons_surface']}", key=f"{team}_ballons_surface", use_container_width=True):
            increment_stat(team, 'ballons_surface'); st.rerun()
    with c:
        if st.button(f"💡 Occasions\n{s['occasions']}", key=f"{team}_occasions", use_container_width=True):
            increment_stat(team, 'occasions'); st.rerun()

    # Ligne 2 : Tirs total + Hors Cadre | Cadré | Contré
    st.markdown(f"<div class='stat-display' style='background:#34495e;color:white'>🎯 Tirs total : {s['tirs']}</div>",
                unsafe_allow_html=True)
    a, b, c = st.columns(3)
    with a:
        if st.button(f"❌ Hors Cadre\n{s['tirs_hors']}", key=f"{team}_tirs_hors", use_container_width=True):
            increment_tir(team, 'tirs_hors'); st.rerun()
    with b:
        if st.button(f"✅ Cadré\n{s['tirs_cadre']}", key=f"{team}_tirs_cadre", use_container_width=True):
            increment_tir(team, 'tirs_cadre'); st.rerun()
    with c:
        if st.button(f"🛡️ Contré\n{s['tirs_contres']}", key=f"{team}_tirs_contres", use_container_width=True):
            increment_tir(team, 'tirs_contres'); st.rerun()

    # Ligne 3 : Entrée 25m G | Axe | D
    a, b, c = st.columns(3)
    with a:
        if st.button(f"⬅️ Entrée 25m G\n{s['entree_25m_gauche']}", key=f"{team}_e25g", use_container_width=True):
            increment_stat(team, 'entree_25m_gauche'); st.rerun()
    with b:
        if st.button(f"⬆️ Entrée 25m Axe\n{s['entree_25m_axe']}", key=f"{team}_e25a", use_container_width=True):
            increment_stat(team, 'entree_25m_axe'); st.rerun()
    with c:
        if st.button(f"➡️ Entrée 25m D\n{s['entree_25m_droite']}", key=f"{team}_e25d", use_container_width=True):
            increment_stat(team, 'entree_25m_droite'); st.rerun()

    # Ligne 4 : Centre G | Axe | D
    a, b, c = st.columns(3)
    with a:
        if st.button(f"↖️ Centre G\n{s['centres_gauche']}", key=f"{team}_cg", use_container_width=True):
            increment_stat(team, 'centres_gauche'); st.rerun()
    with b:
        if st.button(f"⬆️ Centre Axe\n{s['centres_axe']}", key=f"{team}_ca", use_container_width=True):
            increment_stat(team, 'centres_axe'); st.rerun()
    with c:
        if st.button(f"↗️ Centre D\n{s['centres_droite']}", key=f"{team}_cd", use_container_width=True):
            increment_stat(team, 'centres_droite'); st.rerun()

    # Ligne 5 : Corner G | Coup Franc | Corner D
    a, b, c = st.columns(3)
    with a:
        if st.button(f"🚩 Corner G\n{s['corners_gauche']}", key=f"{team}_corg", use_container_width=True):
            increment_stat(team, 'corners_gauche'); st.rerun()
    with b:
        if st.button(f"🎯 Coup Franc\n{s['coups_francs']}", key=f"{team}_cf", use_container_width=True):
            increment_stat(team, 'coups_francs'); st.rerun()
    with c:
        if st.button(f"🚩 Corner D\n{s['corners_droite']}", key=f"{team}_cord", use_container_width=True):
            increment_stat(team, 'corners_droite'); st.rerun()

    # Ligne 6 : Fautes | Hors-jeu | Cartons
    a, b, c = st.columns(3)
    with a:
        if st.button(f"🟡 Fautes\n{s['fautes']}", key=f"{team}_fautes", use_container_width=True):
            increment_stat(team, 'fautes'); st.rerun()
    with b:
        if st.button(f"🚫 Hors-jeu\n{s['hors_jeu']}", key=f"{team}_hj", use_container_width=True):
            increment_stat(team, 'hors_jeu'); st.rerun()
    with c:
        if st.button(f"🟥 Cartons\n{s['cartons']}", key=f"{team}_cartons", use_container_width=True):
            increment_stat(team, 'cartons'); st.rerun()

col_home, col_away = st.columns(2)
with col_home:
    render_team('home', '#c0392b')
with col_away:
    render_team('away', '#2c3e50')

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
            'duration': get_elapsed_time()
        },
        'stats': st.session_state.stats,
        'action_history': st.session_state.action_history
    }
    st.download_button(
        label="📥 Télécharger JSON",
        data=json.dumps(data, indent=2, ensure_ascii=False),
        file_name=f"match_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        use_container_width=True
    )
with c_csv:
    rows = [
        {'Statistique': k,
         st.session_state.home_team_name: st.session_state.stats['home'][k],
         st.session_state.away_team_name: st.session_state.stats['away'][k]}
        for k in st.session_state.stats['home']
    ]
    st.download_button(
        label="📥 Télécharger CSV",
        data=pd.DataFrame(rows).to_csv(index=False),
        file_name=f"match_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )

if st.session_state.match_running:
    time.sleep(1)
    st.rerun()
