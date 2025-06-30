import streamlit as st
from PIL import Image
import tempfile
import os
import csv
from datetime import datetime
from streamlit_cropper import st_cropper

from predict import get_all_predictions
from utils.ai_services import generate_narrative_description, synthesize_audio_openai, ask_gpt_about_painting
from utils.data_management import save_analysis_metadata, save_feedback_to_csv
from utils.visualizations import create_emotion_radar_chart
from utils.pdf_generator_advanced import generate_pdf_report, check_pdf_capabilities

def render_analysis_tab():
    """Renderează tab-ul de analiză a operelor de artă."""
    
    st.markdown('<h2 class="main-title">Analiză Operă de Artă</h2>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle-text" style="text-align: center;">Descoperă secretele și emoțiile ascunse în fiecare creație artistică</p>', unsafe_allow_html=True)
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align: center; margin: 1rem 0;">
        <h3 style="color: #D4AF37; margin-bottom: 0.5rem;">Încarcă Opera de Artă</h3>
        <p style="color: rgba(255, 255, 255, 0.7); font-size: 1rem;">
            Selectează o imagine clară a operei pe care dorești să o analizezi
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Formte acceptate: JPG, PNG, JPEG", 
        type=['jpg', 'png', 'jpeg'],
        help="Pentru rezultate optime, folosește imagini cu rezoluție bună și iluminare uniformă",
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        
                
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0;">
            <h4 style="color: #D4AF37; margin-bottom: 1rem;">Ajustare Imagine (Opțional)</h4>
            <p style="color: rgba(255, 255, 255, 0.7);">
                Poți recadra imaginea pentru a te concentra pe zona principală a operei.<br>
                <em>Trageți și redimensionați zona albastră pentru a selecta regiunea dorită.</em>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Cropping tool
        cropped_img = st_cropper(
            image, 
            realtime_update=True, 
            box_color='#64A9F0',
            aspect_ratio=None
        )
        
        # Preview pentru imaginea cropată
        if cropped_img:
            with st.expander("Previzualizare Imagine Ajustată", expanded=False):
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.image(cropped_img, caption="Imaginea care va fi analizată", use_container_width=True)
                st.markdown("""
                <p style="text-align: center; color: rgba(255, 255, 255, 0.6); font-style: italic;">
                    Aceasta este imaginea care va fi trimisă către sistemul de analiză
                </p>
                """, unsafe_allow_html=True)
        
        # Toggle pentru stilul descrierii narative 
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0;">
            <h4 style="color: #D4AF37; margin-bottom: 1rem;">Personalizare Interpretare</h4>
            <p style="color: rgba(255, 255, 255, 0.7);">
                Alege stilul în care dorești să fie generată interpretarea narativă.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        style_option = st.selectbox(
            "Stilul descrierii narative:",
            ["Poetic", "Analitic", "Emoțional", "Amuzant", "Istoric"],
            index=0,
            help="Alege tonul în care dorești să fie scrisă interpretarea operei"
        )
        
        # Toggle pentru raport PDF/HTML
        pdf_capabilities = check_pdf_capabilities()
        if pdf_capabilities['weasyprint'] or pdf_capabilities['pdfkit']:
            toggle_text = "Generează și raport PDF pentru download"
            toggle_help = "Activează această opțiune pentru a primi un raport PDF downloadabil cu rezultatele analizei"
        else:
            toggle_text = "Generează și raport HTML pentru download" 
            toggle_help = "Activează această opțiune pentru a primi un raport HTML downloadabil cu rezultatele analizei (convertibil în PDF)"
        
        show_report_toggle = st.toggle(
            toggle_text, 
            value=False,
            help=toggle_help
        )
        
        # Buton pentru analiză
        if st.button("Începe Analiza Completă", type="primary", use_container_width=True):
            with st.spinner("Se analizează opera de artă... Acest proces poate dura câteva secunde."):
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_img_file:
                        cropped_img.save(temp_img_file.name)
                        temp_img_path = temp_img_file.name

                    # Progres indicator pentru utilizator
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Obține predicțiile
                    status_text.text("Analizez stilul artistic și autorul...")
                    progress_bar.progress(25)
                    predictions = get_all_predictions(temp_img_path)
                    
                    # Generează descrierea narativă îmbunătățită cu stilul selectat
                    status_text.text("Creez interpretarea narativă în stilul selectat...")
                    progress_bar.progress(50)
                    
                    style_map = {
                        "Poetic": "🎨 Poetic",
                        "Analitic": "🧠 Analitic", 
                        "Emoțional": "😢 Emoțional",
                        "Amuzant": "😂 Amuzant",
                        "Istoric": "🕰 Istoric"
                    }
                    selected_style = style_map.get(style_option, "🎨 Poetic")  # Folosește stilul selectat
                    
                    narrative = generate_narrative_description(predictions, selected_style, cropped_img)
                    
                    # Generează audio în română
                    if narrative and narrative != "Nu s-a putut genera descrierea narativă. Vă rugăm să încercați din nou.":
                        status_text.text("Generez narațiunea audio în română...")
                        progress_bar.progress(75)
                        audio_fp = synthesize_audio_openai(narrative)
                        st.session_state['audio'] = audio_fp
                    else:
                        st.session_state['audio'] = None
                    
                    # Finalizare și salvare rezultate
                    status_text.text("Salvez rezultatele și pregătesc raportul...")
                    progress_bar.progress(90)
                    

                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    st.session_state['analysis_results'] = {
                        'predictions': predictions,
                        'narrative': narrative,
                        'timestamp': timestamp,
                        'style_option': selected_style,
                        'cropped_image': cropped_img,
                        'original_image': image,
                        'show_report_pdf': show_report_toggle
                    }
                    
                    # Salvează metadatele pentru galerie
                    success, img_path, meta_path = save_analysis_metadata(
                        predictions, 
                        narrative, 
                        cropped_img, 
                        timestamp
                    )
                    
                    progress_bar.progress(100)
                    status_text.text("Analiza completă!")
                    
                    if success:
                        st.success("Analiza a fost completată cu succes! Interpretarea apare mai jos.")
                        st.rerun()
                    else:
                        st.warning(f"Analiza s-a finalizat, dar există o problemă la salvare: {meta_path}")
                    
                except Exception as e:
                    st.error(f"A apărut o eroare în timpul analizei: {str(e)}")
                    st.info("Încercați din nou sau contactați suportul tehnic.")
                finally:                    
                    if 'temp_img_path' in locals() and os.path.exists(temp_img_path):
                        os.unlink(temp_img_path)
                    if 'progress_bar' in locals():
                        progress_bar.empty()
                    if 'status_text' in locals():
                        status_text.empty()
    
    if 'analysis_results' in st.session_state and st.session_state.analysis_results:
        st.markdown("---")
        
        predictions = st.session_state.analysis_results['predictions']
        narrative = st.session_state.analysis_results['narrative']
        
        # SECȚIUNEA NARATIVĂ
        if narrative:
            st.markdown("""
            <div class="narrative-section">
                <h2 class="narrative-title">Interpretarea Operei</h2>
                <div class="narrative-content">
                    {}
                </div>
            """.format(narrative), unsafe_allow_html=True)
            
            if 'audio' in st.session_state and st.session_state.audio:
                st.markdown("""
                <div class="audio-player">
                    <div class="audio-title">Ascultă Interpretarea</div>
                """, unsafe_allow_html=True)
                
                try:
                    st.session_state.audio.seek(0)
                    st.audio(st.session_state.audio, format='audio/mp3', autoplay=False)
                    
                except Exception as e:
                    st.markdown("""
                    <div class="audio-info" style="color: #ff6b6b;">
                        Eroare la redarea audio: {}
                    </div>
                    """.format(str(e)), unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="audio-player">
                    <div class="audio-info">
                        Audio indisponibil pentru această interpretare
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        
        st.markdown("""
        <h1 class="main-title">Analiza Tehnică Detaliată</h1>
        <h5 class="subtle-text">Rezultatele algoritmilor</h5>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3, gap="large")

        # === COLOANA 1: TOP 3 STILURI ARTISTICE ===
        with col1:
            st.markdown("""
            <h3 class="section-title">Top 3 Stiluri Artistice</h3>
            
            """, unsafe_allow_html=True)
            
            if predictions.get('stil') and predictions['stil'].get('predictions_sorted'):
                styles_data = predictions['stil']['predictions_sorted'][:3]
                
                # Container pentru rezultate cu stil modern
                for i, (style, confidence) in enumerate(styles_data):
                    style_name = style.replace('_', ' ').title()
                    
                    # Card individual pentru fiecare stil cu clasa de rank
                    st.markdown(f"""
                    <div class="result-item progress-rank-{i+1}">
                        <div class="result-header">
                            <span class="result-rank">#{i+1}</span>
                            <span class="result-name">{style_name}</span>
                        </div>
                        <div class="result-confidence">{confidence:.1%} </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Progress bar stilizat cu transparență bazată pe ranking
                    st.progress(confidence, text="")
                    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
                
                # Heatmap pentru Stil
                if 'gradcam_image' in predictions.get('stil', {}):
                    st.markdown("""
                    <div class="heatmap-section">
                        <h4>Zona de Interes - Stil</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    st.image(predictions['stil']['gradcam_image'], 
                            caption="Heatmap pentru detectarea stilului artistic", 
                            use_container_width=True)
                
                
        # === COLOANA 2: TOP 3 AUTORI PROBABLI ===
        with col2:
            st.markdown("""
                <h3 class="section-title">Top 3 Autori Probabli</h3>
            """, unsafe_allow_html=True)
            
            if predictions.get('autor') and predictions['autor'].get('predictions_sorted'):
                authors_data = predictions['autor']['predictions_sorted'][:3]
                
                # Container pentru rezultate
                for i, (author, confidence) in enumerate(authors_data):
                    author_name = author.replace('_', ' ').title()
                    
                    # Card individual pentru fiecare autor cu clasa de rank
                    st.markdown(f"""
                    <div class="result-item progress-rank-{i+1}">
                        <div class="result-header">
                            <span class="result-rank">#{i+1}</span>
                            <span class="result-name">{author_name}</span>
                        </div>
                        <div class="result-confidence">{confidence:.1%} </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Progress bar stilizat cu transparență bazată pe ranking
                    st.progress(confidence, text="")
                    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
                
                # Heatmap pentru Autor
                if 'gradcam_image' in predictions.get('autor', {}):
                    st.markdown("""
                    <div class="heatmap-section">
                        <h4>Zona de Interes - Autor</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    st.image(predictions['autor']['gradcam_image'], 
                            caption="Heatmap pentru detectarea autorului", 
                            use_container_width=True)
                
                
        # COLOANA 3: ANALIZA EMOȚIONALĂ
        with col3:
            st.markdown("""
            <h3 class="section-title">Analiza Emoțională</h3>
            """, unsafe_allow_html=True)
            
            if predictions.get('emotie') and predictions['emotie'].get('predictions_sorted'):
                emotions_dict = {emotion: score for emotion, score in predictions['emotie']['predictions_sorted'][:6]}
                
                radar_chart = create_emotion_radar_chart(emotions_dict)
                if radar_chart:
                    st.plotly_chart(radar_chart, use_container_width=True, config={'displayModeBar': False})
                

                st.markdown("""
                <div class="emotions-list">
                    <h4>Top 5 Emoții Detectate</h4>
                
                """, unsafe_allow_html=True)
                
                for i, (emotion, score) in enumerate(predictions['emotie']['predictions_sorted'][:5]):
                    emotion_name = emotion.replace('_', ' ').title()
                    st.markdown(f"""
                    <div class="emotion-item">
                        <span class="emotion-rank">#{i+1}</span>
                        <span class="emotion-name">{emotion_name}</span>
                        <span class="emotion-score">{score:.1%}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown('<div class="no-prediction">Nu s-au detectat emoții</div>', unsafe_allow_html=True)

        # SECȚIUNEA DE ÎNTREBĂRI GPT DESPRE PICTURĂ
        st.markdown("---")
        st.markdown("""
        <h2 class="main-title">Întreabă despre această operă</h2>
        <p class="subtitle-text" style="text-align: center;">
            Ai întrebări despre culori, tehnici, simboluri sau semnificații? Întreabă un expert!
        </p>
        """, unsafe_allow_html=True)
        
        user_prompt = st.text_input(
            "Scrie întrebarea ta despre pictură:",
            placeholder="Ex: Ce transmite această cromatică? De ce artistul a ales aceste culori? Ce simbolizează elementele din fundal?",
            help="Poți întreba despre orice aspect al operei: tehnici, culori, emoții, simboluri, context istoric, etc."
        )

        if user_prompt and st.button("Trimite întrebarea către Expert", type="primary", use_container_width=True):
            with st.spinner("Expertul analizează întrebarea ta..."):
                gpt_response = ask_gpt_about_painting(user_prompt, predictions)
                if gpt_response:
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, rgba(100, 169, 240, 0.1), rgba(212, 175, 55, 0.1)); 
                                 padding: 1.5rem; border-radius: 15px; border: 1px solid rgba(212, 175, 55, 0.3); margin: 1rem 0;">
                        <h4 style="color: #D4AF37; margin-bottom: 1rem;">Răspunsul Expertului:</h4>
                    """, unsafe_allow_html=True)
                    st.write(gpt_response)
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.error("Nu am putut obține un răspuns. Te rog încearcă din nou.")
        
        # SECȚIUNEA DE FEEDBACK
        st.markdown("---")
        st.markdown("""
        <h3 class="section-title">Feedback despre analiză</h3>
        <p style="color: rgba(255, 255, 255, 0.7); text-align: center;">
            Ajută-ne să îmbunătățim sistemul oferind feedback despre corectitudinea analizei
        </p>
        """, unsafe_allow_html=True)
        
        feedback = st.radio(
            "A fost corectă predicția?", 
            ["Da, analiza este corectă", "Nu, analiza are erori", "Nu sunt sigur"],
            horizontal=True,
            index=0
        )

        user_comment = ""
        correct_style = ""
        correct_author = ""

        if feedback == "Nu, analiza are erori":
            user_comment = st.text_area(
                "Ce nu a fost corect? (opțional)", 
                placeholder="Ex: Stilul nu pare corect, nu pare deloc impresionist... Autorul nu poate fi acesta pentru că...",
                help="Comentariile tale ne ajută să îmbunătățim algoritmii de analiză"
            )
            
            col_style, col_author = st.columns(2)
            with col_style:
                correct_style = st.text_input(
                    "Stilul corect ar fi fost:",
                    placeholder="Ex: Romantism, Baroc, etc."
                )
            with col_author:
                correct_author = st.text_input(
                    "Autorul corect ar fi fost:",
                    placeholder="Ex: Van Gogh, Monet, etc."
                )

        if st.button("Trimite feedback", use_container_width=True):
            # Implementarea salvării feedback-ului
            feedback_data = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "filename": "uploaded_image", 
                "stil_prezis": predictions['stil']['predictions_sorted'][0][0] if predictions.get('stil') else "N/A",
                "autor_prezis": predictions['autor']['predictions_sorted'][0][0] if predictions.get('autor') else "N/A",
                "emotii_prezise": ', '.join([e for e, p in predictions['emotie']['predictions_sorted']]) if predictions.get('emotie') else "N/A",
                "feedback": "pozitiv" if feedback == "Da, analiza este corectă" else ("negativ" if feedback == "Nu, analiza are erori" else "neutru"),
                "comentariu_utilizator": user_comment,
                "stil_corect_utilizator": correct_style,
                "autor_corect_utilizator": correct_author
            }
            
            # Salvează feedback-ul în CSV
            save_feedback_to_csv(feedback_data)
            
            if feedback == "Da, analiza este corectă":
                st.success("Mulțumim pentru confirmare! Ne bucurăm că analiza a fost corectă.")
            elif feedback == "Nu, analiza are erori":
                st.success("Feedback salvat! Îți mulțumim pentru observațiile detaliate - ne vor ajuta să îmbunătățim sistemul.")
            else:
                st.info("Mulțumim pentru feedback!")
        
        # OPȚIUNEA DE DESCĂRCARE PDF 
        if st.session_state.analysis_results.get('show_report_pdf', False):
            st.markdown("---")
            
            report_title = "Descărcare Raport HTML"
            report_description = """
            Generează și descarcă un raport complet în format HTML cu analiza acestei opere<br>
            <em style="color: #64A9F0;">📄 Pentru PDF: deschide fișierul HTML în browser → Ctrl+P → "Salvează ca PDF"</em><br>
            <em style="color: #90EE90;">✅ Format recomandat pentru Windows - 100% compatibil</em>
            """
            button_text = "Generează și Descarcă Raport HTML"
            file_extension = "html"
            file_mime = "text/html"
            success_message = "Raportul HTML a fost generat cu succes! 🎉"
            info_message = """
            💡 **Pentru a converti în PDF:**
            1. Deschide fișierul HTML în browser (dublu-click)
            2. Apasă **Ctrl+P** 
            3. Selectează **"Salvează ca PDF"**
            4. Alege locația și salvează
            
            📄 Raportul HTML arată identic cu versiunea PDF și se printează perfect!
            """
            
            st.markdown(f"""
            <h3 class="section-title">{report_title}</h3>
            <p style="color: rgba(255, 255, 255, 0.7); text-align: center;">
                {report_description}
            </p>
            """, unsafe_allow_html=True)
            
            if st.button(button_text, type="primary", use_container_width=True):
                with st.spinner(f"Generez raportul {file_extension.upper()}..."):
                    report_buffer = generate_pdf_report(st.session_state.analysis_results)
                    if report_buffer:
                        st.download_button(
                            label=f"Descarcă Raportul {file_extension.upper()}",
                            data=report_buffer,
                            file_name=f"ArtAdvisor_Analiza_{st.session_state.analysis_results['timestamp']}.{file_extension}",
                            mime=file_mime,
                            use_container_width=True
                        )
                        st.success(success_message)
                        st.info(info_message)
                    else:
                        st.error(f"Eroare la generarea raportului HTML. Te rog încearcă din nou.")

        
    if 'analysis_results' not in st.session_state or not st.session_state.analysis_results:
        st.markdown("""
        <div style="text-align: center; margin: 4rem 0; padding: 3rem; 
                    background: rgba(100, 169, 240, 0.08); border-radius: 20px; 
                    border: 1px solid rgba(100, 169, 240, 0.2);">
            <h3 style="color: #D4AF37; margin-bottom: 1.5rem;">Bun venit la ArtAdvisor!</h3>
            <p style="color: rgba(255, 255, 255, 0.8); font-size: 1.1rem; line-height: 1.6;">
                Încarcă o operă de artă mai sus pentru a descoperi:<br><br>
                <strong>Stilul artistic</strong> și tehnicile folosite<br>
                <strong>Autorul probabil</strong> sau școala artistică<br>
                <strong>Emoțiile transmise</strong> prin culori și forme<br>
                <strong>Interpretarea narativă</strong> citită în română<br><br>
                <em style="color: #64A9F0;">Analiza detaliată a operei tale în câteva secunde!</em>
            </p>
        </div>
        """, unsafe_allow_html=True)
