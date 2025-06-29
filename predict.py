from predictors.style_predictor import predict_style
from predictors.author_predictor import predict_author
import os
import streamlit as st
from PIL import Image

# Optimizare pentru imagini - redimensionare automată
@st.cache_data(ttl=300)
def optimize_image_for_analysis(image_path: str, max_size=(1024, 1024)):
    """
    Optimizează imaginea pentru analiză rapidă - redimensionează la o mărime rezonabilă.
    """
    try:
        with Image.open(image_path) as img:
            img = img.convert('RGB')
            
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                optimized_path = image_path.replace('.', '_optimized.')
                img.save(optimized_path, 'JPEG', quality=85, optimize=True)
                return optimized_path
            
            return image_path
    except Exception as e:
        print(f"Eroare la optimizarea imaginii: {e}")
        return image_path

@st.cache_data(ttl=600, show_spinner=False)
def get_all_predictions(image_path: str):
    """
    Funcția centrală ULTRA-OPTIMIZATĂ care primește o imagine și returnează toate predicțiile.
    Cu cache inteligent și optimizare de imagini.
    """
    if not os.path.exists(image_path):
        return {"error": f"Fișierul imagine nu a fost găsit: {image_path}"}

    optimized_path = optimize_image_for_analysis(image_path)
    
    # OPTIMIZARE 2: Apelăm fiecare predictor cu cache activ
    # Fiecare predictor își gestionează propriul cache pentru modele
    
    try:
        style_results = predict_style(optimized_path)
        author_results = predict_author(optimized_path)
        
        import operator
        
        if 'predictions' in style_results and not style_results.get('error'):
            style_results['predictions_sorted'] = sorted(
                style_results['predictions'].items(), 
                key=operator.itemgetter(1), 
                reverse=True
            )
        
        if 'predictions' in author_results and not author_results.get('error'):
            author_results['predictions_sorted'] = sorted(
                author_results['predictions'].items(), 
                key=operator.itemgetter(1), 
                reverse=True
            )
        
        final_predictions = {
            "stil": style_results,
            "autor": author_results,
            "optimized_image": optimized_path
        }
        
        return final_predictions
        
    except Exception as e:
        return {"error": f"Eroare în analiză: {str(e)}"}
