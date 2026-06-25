import streamlit as st
import time
import json
import csv
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
    .stButton>button {
        width: 100%;
        height: 70px;
        font-size: 18px;
        font-weight: bold;
        margin: 3px 0;
        border-radius: 8px;
    }
    .team-header {
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    .stat-display {
        padding: 12px;
        text-align: center;
        font-weight: bold;
        border-radius: 8px;
        margin: 3px 0;
        font-size: 18px;
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

if 'match_start_time' not in st.session_state:
    st.session_state.match_start_time = None
if 'match_running' not in st.session_state:
    st.session_state.match_running = False
if 'action_history' not in st.session_state:
    st.session_state.action_history = []
if 'home_team_name' not in st.session_state:
    st.session_state.home_team_name = "Équipe Domicile"
if 'away_team_name' not in st.session_state:
    st.session_state.away_team_name = "Équipe Adverse"

def start_match():
    st.session_state.match_start_time = time.time()
    st.session_state.match_running = True

def stop_match():
    st.session_state.match_running = False

def reset_match():
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
    st.session_state.match_start_time = None
    st.session_state.match_running = False
    st.session_state.action_history = []

def increment_stat(team, stat):
    action = {
        'type': 'stat_increment',
        'team': team,
        'stat': stat,
        'time': time.time() - (st.session_state.match_start_time or 0),
        'timestamp': datetime.now().isoformat()
    }
    st.session_state.action_history.append(action)
    st.session_state.stats[team][stat] += 1

def increment_tir(team, sub_stat):
    increment_stat(team, sub_stat)
    st.session_state.stats[team]['tirs'] = (
        st.session_state.stats[team]['tirs_hors'] +
        st.session_state.stats[team]['tirs_cadre'] +
        st.session_state.stats[team]['tirs_contres']
    )

def undo_last_action():
    if not st.session_state.action_history:
        st.warning("Aucune action à annuler")
        return
    last = st.session_state.action_history.pop()
    if last['type'] == 'stat_increment':
        team = last['team']
        stat = last['stat']
        st.session_state.stats[team][stat] = max(0, st.session_state.stats[team][stat] - 1)
        if stat in ['tirs_hors', 'tirs_cadre', 'tirs_contres']:
            st.session_state.stats[team]['tirs'] = (
                st.session_state.stats[team]['tirs_hors'] +
                st.session_state.stats[team]['tirs_cadre'] +
                st.session_state.stats[team]['tirs_contres']
            )
        st.success(f"✅ Action annulée : {stat}")

def get_elapsed_time():
    if st.session_state.match_running and st.session_state.match_start_time:
        elapsed = int(time.time() - st.session_state.match_start_time)
        minutes = elapsed // 60
        seconds = elapsed % 60
        return f"{minutes:02d}:{seconds:02d}"
    return "00:00"

def export_json():
    data = {
        'match_info': {
            'home_team': st.session_state.home_team_name,
            'away_team': st.session_state.away_team_name,
            'duration': get_elapsed_time()
        },
        'stats': st.session_state.stats,
        'action_history': st.session_state.action_history
    }
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    st.download_button(
        label="📥 Télécharger JSON",
        data=json_str,
        file_name=f"match_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        use_container_width=True
    )

def export_csv():
    data = []
    for stat in st.session_state.stats['home'].keys():
        data.append({
            'Statistique': stat,
            st.session_state.home_team_name: st.session_state.stats['home'][stat],
            st.session_state.away_team_name: st.session_state.stats['away'][stat]
        })
    df = pd.DataFrame(data)
    csv_str = df.to_csv(index=False)
    st.download_button(
        label="📥 Télécharger CSV",
        data=csv_str,
        file_name=f"match_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )

st.title("⚽ Analyseur de Match de Football")

col_timer1, col_timer2, col_timer3 = st.columns([1, 2, 1])
with col_timer2:
    st.markdown(f"<h1 style='text-align: center; font-size: 56px; color: #2c3e50;'>{get_elapsed_time()}</h1>", unsafe_allow_html=True)
    
    col_start, col_stop, col_reset = st.columns(3)
    with col_start:
        if st.button("▶️ Démarrer", use_container_width=True):
            start_match()
    with col_stop:
        if st.button("⏸️ Pause", use_container_width=True):
            stop_match()
    with col_reset:
        if st.button("🔄 Reset", use_container_width=True):
            reset_match()
            st.rerun()

st.divider()

col_home_name, col_away_name = st.columns(2)
with col_home_name:
    st.session_state.home_team_name = st.text_input(
        "🏠 Équipe Domicile",
        value=st.session_state.home_team_name,
        key="home_name_input"
    )
with col_away_name:
    st.session_state.away_team_name = st.text_input(
        "✈️ Équipe Adverse",
        value=st.session_state.away_team_name,
        key="away_name_input"
    )

st.divider()

col_home, col_away = st.columns(2)

stat_labels = {
    'buts': '⚽ But',
    'ballons_surface': '🎯 Ballons Surface',
    'occasions': '💡 Occasions',
    'tirs': '🎯 TIRS TOTAL',
    'tirs_hors': '❌ Hors Cadre',
    'tirs_cadre': '✅ Cadré',
    'tirs_contres': '🛡️ Contré',
    'entree_25m_gauche': '⬅️ Entrée 25m G',
    'entree_25m_axe': '⬆️ Entrée 25m Axe',
    'entree_25m_droite': '➡️ Entrée 25m D',
    'centres_gauche': '↖️ Centre G',
    'centres_axe': '⬆️ Centre Axe',
    'centres_droite': '↗️ Centre D',
    'corners_gauche': '🚩 Corner G',
    'coups_francs': '🎯 Coup Franc',
    'corners_droite': '🚩 Corner D',
    'fautes': '🟡 Fautes',
    'hors_jeu': '🚫 Hors-jeu',
    'cartons': '🟥 Cartons'
}

stat_order = [
    'buts', 'ballons_surface', 'occasions',
    'tirs',
    'tirs_hors', 'tirs_cadre', 'tirs_contres',
    'entree_25m_gauche', 'entree_25m_axe', 'entree_25m_droite',
    'centres_gauche', 'centres_axe', 'centres_droite',
    'corners_gauche', 'coups_francs', 'corners_droite',
    'fautes', 'hors_jeu', 'cartons'
]

with col_home:
    st.markdown(f"<div class='team-header' style='background-color: #c0392b; color: white;'>{st.session_state.home_team_name}</div>", unsafe_allow_html=True)
    
    for stat in stat_order:
        label = stat_labels[stat]
        count = st.session_state.stats['home'][stat]
        
        if stat in ['tirs_hors', 'tirs_cadre', 'tirs_contres']:
            if st.button(f"{label}: {count}", key=f"home_{stat}", use_container_width=True):
                increment_tir('home', stat)
                st.rerun()
        elif stat == 'tirs':
            st.markdown(f"<div class='stat-display' style='background-color: #34495e; color: white;'>{label}: {count}</div>", unsafe_allow_html=True)
        else:
            if st.button(f"{label}: {count}", key=f"home_{stat}", use_container_width=True):
                increment_stat('home', stat)
                st.rerun()

with col_away:
    st.markdown(f"<div class='team-header' style='background-color: #7f8c8d; color: white;'>{st.session_state.away_team_name}</div>", unsafe_allow_html=True)
    
    for stat in stat_order:
        label = stat_labels[stat]
        count = st.session_state.stats['away'][stat]
        
        if stat in ['tirs_hors', 'tirs_cadre', 'tirs_contres']:
            if st.button(f"{label}: {count}", key=f"away_{stat}", use_container_width=True):
                increment_tir('away', stat)
                st.rerun()
        elif stat == 'tirs':
            st.markdown(f"<div class='stat-display' style='background-color: #34495e; color: white;'>{label}: {count}</div>", unsafe_allow_html=True)
        else:
            if st.button(f"{label}: {count}", key=f"away_{stat}", use_container_width=True):
                increment_stat('away', stat)
                st.rerun()

st.divider()

col_undo, col_export1, col_export2 = st.columns(3)
with col_undo:
    if st.button("↶ Annuler", use_container_width=True):
        undo_last_action()
        st.rerun()
with col_export1:
    export_json()
with col_export2:
    export_csv()

if st.session_state.match_running:
    time.sleep(1)
    st.rerun()
