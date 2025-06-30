from openai import OpenAI
from PIL import Image
import base64
from io import BytesIO
from config import ARTIST_PERSONAS

def get_openai_client():
    """Obține clientul OpenAI cu cheia API din Streamlit secrets."""
    import streamlit as st
    return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def show_streamlit_error(message):
    """Afișează o eroare în Streamlit (import lazy)."""
    import streamlit as st
    st.error(message)

def encode_image_to_base64(pil_image):
    """Convertește o imagine PIL în format base64."""
    buffered = BytesIO()
    pil_image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def generate_narrative_description(predictions: dict, style: str, image: Image.Image):
    """Generează descrierea narativă folosind OpenAI API, analizând atât textul, cât și imaginea."""
    try:
        client = get_openai_client()
        
        top_style = predictions['stil']['predictions_sorted'][0][0]
        top_author_raw = predictions['autor']['predictions_sorted'][0][0].replace('_', ' ')
        top_author = f"{top_author_raw} – sau un artist cu un stil similar"
        filtered_emotions = predictions['emotie'].get('predictions_sorted', [])
        emotion_string = ', '.join([f"{k}" for k, v in filtered_emotions]) or "emoții subtile"
        
        style_prompts = {
            "🎨 Poetic": f"""Acționează ca un poet romantic care analizează arta. Folosește metafore incredibile și limbaj liric.
            Pe baza imaginii și indiciilor AI, creează o descriere POETICĂ (maxim 4-5 fraze) ca un poem în proză:
            - Stilul artistic detectat: {top_style}  
            - Artistul probabil: {top_author}
            - Emoțiile probabile: {emotion_string}

Fă-o să sune ca un poem! Folosește comparații cu natura, sentimente profunde, metafore despre culori ca "dans de fluturi" sau "simfonia culorilor". Menționează artistul poetic.""",

            "🧠 Analitic": f"""Acționează ca un profesor universitar expert în istoria artei. Fii tehnic și precis!
            Pe baza imaginii și indiciilor AI, creează o analiză TEHNICĂ și ACADEMICĂ (maxim 4-5 fraze):
            - Stilul artistic detectat: {top_style}
            - Artistul probabil: {top_author}  
            - Emoțiile probabile: {emotion_string}

Analizează tehnica picturii, compoziția, folosirea culorilor, perspectiva. Fii ca un manual de artă - serios și erudit. Explică DE CE artistul a ales aceste tehnici.""",

            "😢 Emoțional": f"""Acționează ca un critic de artă sensibil care simte profund fiecare operă. Fii emoțional și introspectiv!
            Pe baza imaginii și indiciilor AI, creează o descriere EMOȚIONALĂ care să atingă sufletul (maxim 4-5 fraze):
            - Stilul artistic detectat: {top_style}
            - Artistul probabil: {top_author}
            - Emoțiile probabile: {emotion_string}

Descrie ce SIMȚI când te uiți la operă. Vorbește despre emoțiile pe care le transmite, despre cum te face să te simți. Fii profund și sensibil.""",

            "😂 Amuzant": f"""Acționează ca un comediant care face stand-up despre artă! Fii AMUZANT și fă glume inteligente!
            Pe baza imaginii și indiciilor AI, creează o descriere HILARĂ care să mă facă să râd (maxim 4-5 fraze):
            - Stilul artistic detectat: {top_style}
            - Artistul probabil: {top_author}
            - Emoțiile probabile: {emotion_string}

Fă glume despre operă, despre artist, despre culorile folosite! Compară cu lucruri funny din viața modernă. Fii sarcastic dar inteligent. Să fie o descriere care să mă facă să râd cu lacrimi!""",

            "🕰 Istoric": f"""Acționează ca un istoric specializat în istoria artei. Fii ca un documentar BBC!
            Pe baza imaginii și indiciilor AI, creează o descriere ISTORICĂ precisă (maxim 4-5 fraze):
            - Stilul artistic detectat: {top_style}
            - Artistul probabil: {top_author}
            - Emoțiile probabile: {emotion_string}

Pune opera în context istoric! Vorbește despre perioada în care a fost creată, despre mișcarea artistică, despre influențele sociale și culturale. Fii ca un documentar serios."""
        }
        
        prompt_text = style_prompts.get(style, style_prompts["🎨 Poetic"])

        base64_image = encode_image_to_base64(image)

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        import streamlit as st
        st.error(f"Eroare OpenAI: {e}")
        return None

def synthesize_audio_openai(text: str) -> BytesIO | None:
    """Generează audio natural în română cu intonație expresivă și tonalitate plăcută."""
    try:
        client = get_openai_client()
        
      
        response = client.audio.speech.create(
            model="tts-1-hd",    
            voice="nova",         
            input=text,
            speed=0.95             
        )

        audio_bytes = BytesIO(response.content)
        return audio_bytes

    except Exception as e:
        show_streamlit_error(f"Nu s-a putut genera narațiunea audio expresivă: {e}")
        return None

def synthesize_audio_with_emotion(text: str, emotion_style: str = "warm") -> BytesIO | None:
    """
    Generează audio cu stil emoțional adaptat pentru o experiență și mai naturală.
    
    Args:
        text: Textul de citit
        emotion_style: "warm" (căldură), "dramatic" (dramatic), "contemplative" (contemplativ)
    """
    try:
        client = get_openai_client()
        
        voice_map = {
            "warm": "alloy",       
            "dramatic": "shimmer", 
            "contemplative": "fable" 
        }
        
        selected_voice = voice_map.get(emotion_style, "alloy")
        
        speed_map = {
            "warm": 0.95,
            "dramatic": 0.9,
            "contemplative": 0.85
        }
        speed = speed_map.get(emotion_style, 0.95)
        
        response = client.audio.speech.create(
            model="tts-1-hd",
            voice=selected_voice,
            input=text,
            speed=speed
        )

        return BytesIO(response.content)

    except Exception as e:
        show_streamlit_error(f"Nu s-a putut genera audio cu stil emoțional: {e}")
        return None

def chat_with_artist(artist_name: str, user_question: str, artwork_info: dict) -> str:
    """Creează un dialog cu artistul pe baza personalității sale."""
    try:
        client = get_openai_client()
        
        if artist_name not in ARTIST_PERSONAS:
            return "Ne pare rău, nu putem identifica artistul pentru a începe conversația."
        
        persona = ARTIST_PERSONAS[artist_name]
        
        full_prompt = f"""{persona['prompt']}
        
        Informații despre opera discutată:
        - Stil: {artwork_info.get('stil', 'necunoscut')}
        - Emoții detectate: {', '.join(artwork_info.get('emotii', []))}
        
        Întrebarea utilizatorului: {user_question}
        
        Răspunde ca {artist_name}, referindu-te la opera și la întrebarea utilizatorului."""
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.8,
            max_tokens=400
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        return f"Ne pare rău, a apărut o eroare în conversația cu artistul: {e}"


def ask_gpt_about_painting(user_question: str, predictions: dict) -> str:
    """
    Trimite o întrebare despre pictură către GPT și returnează răspunsul.
    Funcționalitate preluată din app.py original.
    """
    try:
        client = get_openai_client()
        
        style = predictions['stil']['predictions_sorted'][0][0] if predictions.get('stil', {}).get('predictions_sorted') else "Necunoscut"
        author = predictions['autor']['predictions_sorted'][0][0].replace('_', ' ') if predictions.get('autor', {}).get('predictions_sorted') else "Necunoscut"
        emotions = ', '.join([k for k, v in predictions['emotie']['predictions_sorted']]) if predictions.get('emotie', {}).get('predictions_sorted') else "emoții subtile"

        full_prompt = (
            f"Ești un expert în artă cu cunoștințe vaste despre pictură, tehnici artistice și istoria artei. "
            f"Îți ofer informațiile despre o pictură analizată cu AI:\n"
            f"- Stil artistic detectat: {style}\n"
            f"- Autor probabil: {author}\n"
            f"- Emoții transmise: {emotions}\n\n"
            f"Întrebarea utilizatorului: {user_question}\n\n"
            f"Te rog să răspunzi în română, în mod clar, util și educativ. "
            f"Explică conceptele artistice într-un mod accesibil și captivant."
        )

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.7,
            max_tokens=400
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        show_streamlit_error(f"Eroare la trimiterea întrebării către GPT: {e}")
        return None
