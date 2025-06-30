"""
Funcții pentru generarea vizualizărilor în aplicația ArtAdvisor.
Include funcții pentru crearea graficelor și interpretarea vizuală a datelor.
"""

import plotly.graph_objects as go
from config import EMOTION_GROUPS

def create_emotion_radar_chart(emotions_dict):
    """Creează un grafic radar pentru emoții cu maximum 6 emoții."""
    if not emotions_dict:
        return None
    
    # Limitează la primele 6 emoții pentru vizualizare optimă
    emotions_items = list(emotions_dict.items())[:6]
    emotions = [item[0] for item in emotions_items]
    values = [item[1] for item in emotions_items]
    values_percent = [v * 100 for v in values]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values_percent,
        theta=emotions,
        fill='toself',
        name='Emoții Detectate',
        line=dict(color='#f7c873', width=3),
        fillcolor='rgba(247, 200, 115, 0.3)',
        marker=dict(size=8, color='#f7c873')
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                ticksuffix='%',
                tickfont=dict(size=12, color='white'),
                gridcolor='rgba(255, 255, 255, 0.3)'
            ),
            angularaxis=dict(
                tickfont=dict(size=14, color='white'),
                gridcolor='rgba(255, 255, 255, 0.3)'
            ),
            bgcolor='rgba(0, 0, 0, 0)'
        ),
        showlegend=False,
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        font=dict(color='white'),
        height=500
    )
    
    return fig
