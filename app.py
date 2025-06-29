"""
ArtAdvisor
Aplicație pentru analiza opereror de artă
"""

import streamlit as st

# CONFIGURAREA OPTIMIZATĂ A PAGINII
st.set_page_config(
    page_title="ArtAdvisor", 
    page_icon="🎨", 
    layout="wide",
    initial_sidebar_state="collapsed",  # Maximizează spațiul de lucru
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "ArtAdvisor - Analizator de Artă"
    }
)

import sys
import types
import base64
from pathlib import Path

# Optimizare PyTorch pentru Streamlit
torch_classes = types.ModuleType("torch.classes")
torch_classes.__path__ = []
sys.modules["torch.classes"] = torch_classes

# Importă componentele UI (după st.set_page_config)
from ui_components.analysis_tab import render_analysis_tab
