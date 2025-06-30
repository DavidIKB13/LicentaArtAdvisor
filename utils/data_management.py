import os
import json
import glob
import numpy as np
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity
from config import ALL_EMOTIONS

# Cache optimizat pentru citirea fișierelor JSON
def get_artwork_details_cached(json_file_path, file_mtime):
    """Încarcă detaliile unei opere de artă cu cache bazat pe modificare."""
    import streamlit as st
    
    @st.cache_data(ttl=300, show_spinner=False)
    def _load_cached(path, mtime):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            return None
    
    return _load_cached(json_file_path, file_mtime)

# Cache pentru lista completă de opere
def get_all_artworks_cached(gallery_dir="gallery_uploads", sort_by_date=True):
    """Încarcă toate operele de artă din galerie cu cache optimizat."""
    import streamlit as st
    
    @st.cache_data(ttl=60, show_spinner=False)
    def _load_all_cached(dir_path, sort_flag):
        artworks = []
        
        if os.path.exists(dir_path):
            json_files = glob.glob(os.path.join(dir_path, "art_*.json"))
            
            if sort_flag:
                json_files.sort(key=os.path.getmtime, reverse=True)
            
            for json_file in json_files:
                
                file_mtime = os.path.getmtime(json_file)
                metadata = get_artwork_details_cached(json_file, file_mtime)
                
                if metadata:
                    image_file = json_file.replace('.json', '.png')
                    if os.path.exists(image_file):
                        artworks.append({
                            'metadata': metadata,
                            'image_path': image_file,
                            'json_path': json_file
                        })
        
        return artworks
    
    return _load_all_cached(gallery_dir, sort_by_date)

def save_analysis_metadata(predictions, narrative, cropped_image, timestamp_str):
    """Salvează metadatele analizei pentru galerie."""
    try:
        gallery_dir = "gallery_uploads"
        os.makedirs(gallery_dir, exist_ok=True)
        
        image_filename = f"art_{timestamp_str}.png"
        metadata_filename = f"art_{timestamp_str}.json"
        
        image_path = os.path.join(gallery_dir, image_filename)
        metadata_path = os.path.join(gallery_dir, metadata_filename)
        
        cropped_image.save(image_path)
        
        metadata = {
            "timestamp": timestamp_str,
            "stil_dominant": predictions['stil']['predictions_sorted'][0][0] if predictions.get('stil', {}).get('predictions_sorted') else "N/A",
            "stil_scor": predictions['stil']['predictions_sorted'][0][1] if predictions.get('stil', {}).get('predictions_sorted') else 0,
            "autor_probabil": predictions['autor']['predictions_sorted'][0][0].replace('_', ' ') if predictions.get('autor', {}).get('predictions_sorted') else "N/A",
            "autor_scor": predictions['autor']['predictions_sorted'][0][1] if predictions.get('autor', {}).get('predictions_sorted') else 0,
            "emotii_detectate": {emotion: score for emotion, score in predictions['emotie']['predictions_sorted']} if predictions.get('emotie', {}).get('predictions_sorted') else {},
            "descriere_narrativa": narrative or "N/A",
            "data_analiza": datetime.now().strftime("%d.%m.%Y %H:%M")
        }
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        return True, image_path, metadata_path
    except Exception as e:
        return False, None, str(e)

def search_by_emotion(target_emotions, gallery_dir="gallery_uploads"):
    """Caută opere de artă pe baza emoțiilor selectate."""
    if not target_emotions:
        return []
    
    # Creează vectorul țintă
    target_vector = np.zeros(len(ALL_EMOTIONS))
    for emotion in target_emotions:
        if emotion in ALL_EMOTIONS:
            target_vector[ALL_EMOTIONS.index(emotion)] = 1.0
    
    results = []
    
    if os.path.exists(gallery_dir):
        json_files = glob.glob(os.path.join(gallery_dir, "art_*.json"))
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                emotions_detected = metadata.get('emotii_detectate', {})
                
                # Creează vectorul pentru această operă
                artwork_vector = np.zeros(len(ALL_EMOTIONS))
                for emotion, score in emotions_detected.items():
                    if emotion in ALL_EMOTIONS:
                        artwork_vector[ALL_EMOTIONS.index(emotion)] = score
                
                # Calculează similaritatea cosinus
                if np.linalg.norm(artwork_vector) > 0 and np.linalg.norm(target_vector) > 0:
                    similarity = cosine_similarity([target_vector], [artwork_vector])[0][0]
                    
                    image_file = json_file.replace('json', 'png')
                    if os.path.exists(image_file):
                        results.append({
                            'image_path': image_file,
                            'metadata': metadata,
                            'similarity': similarity
                        })
            except Exception as e:
                continue
    
    # Sortează după similaritate
    results.sort(key=lambda x: x['similarity'], reverse=True)
    return results[:10]  # Returnează primele 10 rezultate

def get_artwork_details(json_file_path):
    """Încarcă detaliile unei opere de artă din fișierul JSON. (Funcție backwards-compatible)"""
    file_mtime = os.path.getmtime(json_file_path) if os.path.exists(json_file_path) else 0
    return get_artwork_details_cached(json_file_path, file_mtime)

def get_all_artworks(gallery_dir="gallery_uploads", sort_by_date=True):
    """Încarcă toate operele de artă din galerie. (Funcție backwards-compatible)"""
    return get_all_artworks_cached(gallery_dir, sort_by_date)

def save_feedback_to_csv(feedback_data):
    """
    Salvează feedback-ul utilizatorului într-un fișier CSV.
    Funcționalitate preluată din app.py original.
    """
    import csv
    import os
    from datetime import datetime
    
    try:
        file_path = "feedback_logs.csv"
        file_exists = os.path.exists(file_path)
        
        # Asigură-te că feedback_data are toate câmpurile necesare
        if 'timestamp' not in feedback_data:
            feedback_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(file_path, mode='a', newline='', encoding='utf-8') as f:
            fieldnames = [
                'timestamp', 'filename', 'stil_prezis', 'autor_prezis', 'emotii_prezise',
                'feedback', 'comentariu_utilizator', 'stil_corect_utilizator', 'autor_corect_utilizator'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(feedback_data)
        
        return True
        
    except Exception as e:
        print(f"Eroare la salvarea feedback-ului: {e}")
        return False
