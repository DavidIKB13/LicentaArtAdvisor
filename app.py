"""
ArtAdvisor
Aplicație pentru analiza opereror de artă
Versiunea finală optimizată
"""

import streamlit as st

# --- CONFIGURAREA OPTIMIZATĂ A PAGINII (TREBUIE SĂ FIE PRIMA COMANDĂ!) ---
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
from ui_components.gallery_tab import render_gallery_tab
from ui_components.search_tab import render_search_tab
from ui_components.artist_chat_tab import render_artist_chat_tab
from ui_components.music_gen_tab import render_music_gen_tab
from ui_components.emotional_lab_tab import render_emotional_lab_tab
from ui_components.emotional_journeys_tab import render_emotional_journeys_tab
from ui_components.art_therapy_tab import render_art_therapy_tab

# Cache optimizat pentru fișiere CSS
@st.cache_data(ttl=3600)  # Cache 1 oră
def load_css_optimized():
    """Încarcă toate stilurile CSS într-un singur fișier optimizat."""
    css_content = ""
    
    # Încarcă stilurile  principale
    style_path = Path("static/style_ultra_premium.css")
    if style_path.exists():
        with open(style_path, 'r', encoding='utf-8') as f:
            css_content += f.read()
    
    # Încarcă stilurile galerie 
    gallery_path = Path("static/gallery_ultra_premium.css")
    if gallery_path.exists():
        with open(gallery_path, 'r', encoding='utf-8') as f:
            css_content += f.read()
    
    return css_content

@st.cache_data(ttl=3600)
def get_base64_img(image_path):
    """Cache optimizat pentru imagini."""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return ""

# Aplică CSS-ul optimizat o singură dată per sesiune
css_styles = load_css_optimized()
if css_styles:
    st.markdown(f"<style>{css_styles}</style>", unsafe_allow_html=True)

# Inițializare state pentru navigare ultra-rapidă
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "analysis"

# Header modern
st.markdown("""
<div class="header">
    <h1 style="color: #D4AF37; text-align: center; margin: 0; font-family: 'Playfair Display', serif; font-size: 2.5rem; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">
        ArtAdvisor 
    </h1>
    </div>
""", unsafe_allow_html=True)

# Navigare cu butoane optimizate
st.markdown('<div class="nav-container">', unsafe_allow_html=True)

# Container pentru butoane - layout optimizat pentru 8 tab-uri
col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)

with col1:
    if st.button("Analiză Operă", 
                 key="btn_analysis",
                 use_container_width=True, 
                 type="primary" if st.session_state.current_tab == "analysis" else "secondary"):
        st.session_state.current_tab = "analysis"

with col2:
    if st.button("Galerie", 
                 key="btn_gallery",
                 use_container_width=True, 
                 type="primary" if st.session_state.current_tab == "gallery" else "secondary"):
        st.session_state.current_tab = "gallery"

with col3:
    if st.button("Căutare Avansată", 
                 key="btn_search",
                 use_container_width=True, 
                 type="primary" if st.session_state.current_tab == "search" else "secondary"):
        st.session_state.current_tab = "search"

with col4:
    if st.button("Chat Artist", 
                 key="btn_chat",
                 use_container_width=True, 
                 type="primary" if st.session_state.current_tab == "chat" else "secondary"):
        st.session_state.current_tab = "chat"

with col5:
    if st.button("Muzică", 
                 key="btn_music",
                 use_container_width=True, 
                 type="primary" if st.session_state.current_tab == "music" else "secondary"):
        st.session_state.current_tab = "music"

with col6:
    if st.button("Laborator Emoțional", 
                 key="btn_emotional_lab",
                 use_container_width=True, 
                 type="primary" if st.session_state.current_tab == "emotional_lab" else "secondary"):
        st.session_state.current_tab = "emotional_lab"

with col7:
    if st.button("Călătorii Emoționale", 
                 key="btn_emotional_journeys",
                 use_container_width=True, 
                 type="primary" if st.session_state.current_tab == "emotional_journeys" else "secondary"):
        st.session_state.current_tab = "emotional_journeys"

with col8:
    if st.button("Art-Terapie", 
                 key="btn_art_therapy",
                 use_container_width=True, 
                 type="primary" if st.session_state.current_tab == "art_therapy" else "secondary"):
        st.session_state.current_tab = "art_therapy"

st.markdown('</div>', unsafe_allow_html=True)

# Separator elegant
st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

# Randează tab-ul selectat cu încărcare optimizată
current_tab = st.session_state.current_tab

try:
    if current_tab == "analysis":
        render_analysis_tab()
    elif current_tab == "gallery":
        render_gallery_tab()
    elif current_tab == "search":
        render_search_tab()
    elif current_tab == "chat":
        render_artist_chat_tab()
    elif current_tab == "music":
        render_music_gen_tab()
    elif current_tab == "emotional_lab":
        render_emotional_lab_tab()
    elif current_tab == "emotional_journeys":
        render_emotional_journeys_tab()
    elif current_tab == "art_therapy":
        render_art_therapy_tab()
except Exception as e:
    st.error(f"Eroare la încărcarea secțiunii: {str(e)}")
    st.info("Vă rugăm să reîncărcați pagina.")

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
    <div style="text-align: center; padding: 20px 0;">
        <h3 style="color: #D4AF37;text-align: center; margin: 0; font-family: 'Playfair Display', serif;">
            ArtAdvisor 
        </h3>
        <p style="color: rgba(255, 255, 255, 0.7); margin: 10px 0 0 0; font-size: 0.95rem;">
            Descoperă frumusețea și secretele artei
        </p>
        <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(212, 175, 55, 0.2);">
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# CSS suplimentar pentru stiluri moderne extra
st.markdown("""
<style>
.header {
    background: linear-gradient(135deg, #181C24, #0E1117);
    padding: 25px;
    border-radius: 15px;
    margin-bottom: 25px;
    border: 2px solid rgba(212, 175, 55, 0.3);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}

.nav-container {
    margin-bottom: 25px;
}

.separator {
    height: 2px;
    background: linear-gradient(90deg, transparent, #D4AF37, transparent);
    margin: 20px 0;
    border-radius: 1px;
}

.main-content {
    min-height: 60vh;
    margin-bottom: 30px;
}

.footer {
    background: linear-gradient(135deg, #0E1117, #181C24);
    border-radius: 15px;
    margin-top: 30px;
    border: 1px solid rgba(212, 175, 55, 0.2);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}

/* Optimizare butoane navigare */
.stButton > button {
    background: linear-gradient(135deg, #1e2833, #0f1419) !important;
    border: 1px solid rgba(212, 175, 55, 0.3) !important;
    color: rgba(255, 255, 255, 0.9) !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
    border-radius: 8px !important;
    height: 45px !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #2a3441, #1a1f26) !important;
    border-color: #D4AF37 !important;
    color: #D4AF37 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(212, 175, 55, 0.2) !important;
}

.stButton > button[data-baseweb="button"][kind="primary"] {
    background: linear-gradient(135deg, #D4AF37, #B8941F) !important;
    border: 1px solid #D4AF37 !important;
    color: #000 !important;
    font-weight: 600 !important;
}

/* Animații fade-in pentru conținut */
.main-content > div {
    animation: fadeInUp 0.3s ease-out;
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Responsive optimizat */
@media (max-width: 768px) {
    .header h1 {
        font-size: 1.8rem !important;
    }
    
    .stButton > button {
        height: 40px !important;
        font-size: 0.85rem !important;
    }
}
</style>
""", unsafe_allow_html=True)

# Optimizări suplimentare pentru performanță maximă
@st.cache_data(ttl=1800, show_spinner=False)  # Cache 30 minute
def optimize_uploaded_image(uploaded_file, max_size=(1024, 1024)):
    """
    Optimizează imaginea încărcată pentru procesare rapidă.
    Reduce dimensiunea fără a afecta calitatea analizei.
    """
    try:
        from PIL import Image
        import io
        
        # Deschide imaginea din upload
        image = Image.open(uploaded_file).convert('RGB')
        
        # Verifică dacă trebuie redimensionată
        if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
            # Calculează noua dimensiune păstrând proporțiile
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Salvează în buffer optimizat
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='JPEG', quality=85, optimize=True)
        img_buffer.seek(0)
        
        return img_buffer, image.size
    except Exception as e:
        return uploaded_file, None

@st.cache_data(ttl=900, show_spinner=False)  # Cache 15 minute pentru metadata
def load_emotion_database():
    """Încarcă baza de date cu emoții cu cache optimizat."""
    import json
    try:
        with open("utils/emotion_database.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

@st.cache_data(ttl=1200, show_spinner=False)  # Cache 20 minute
def load_narrative_templates():
    """Încarcă template-urile pentru narațiuni cu cache."""
    return {
        "introducere": "Această operă de artă dezvăluie o lume fascinantă de ",
        "stil": "Stilul artistic identificat sugerează ",
        "autor": "Tehnica și abordarea sunt reminiscente ",
        "emotie": "Paleta emoțională transmite ",
        "concluzie": "În ansamblu, această creație "
    }
