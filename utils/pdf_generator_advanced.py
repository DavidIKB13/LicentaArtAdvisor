from io import BytesIO
from datetime import datetime
import tempfile
import os
import base64
from PIL import Image

def check_pdf_capabilities():
    import platform
    
    capabilities = {
        'weasyprint': False,
        'pdfkit': False,
        'reportlab': False
    }
    
    if platform.system() != "Windows":
        try:
            import weasyprint
            capabilities['weasyprint'] = True
        except ImportError:
            pass
    
    try:
        import pdfkit
        pdfkit.configuration()
        capabilities['pdfkit'] = True
    except (ImportError, OSError):
        pass
        
    try:
        import reportlab
        capabilities['reportlab'] = True
    except ImportError:
        pass
    
    return capabilities

def generate_html_content(analysis_results):
    """Generează conținutul HTML pentru raport."""
    predictions = analysis_results.get('predictions', {})
    narrative = analysis_results.get('narrative', '')
    timestamp = analysis_results.get('timestamp', datetime.now().strftime("%Y%m%d_%H%M%S"))
    style_option = analysis_results.get('style_option', 'Standard')
    
    image_base64 = ""
    if 'cropped_image' in analysis_results:
        buffered = BytesIO()
        analysis_results['cropped_image'].save(buffered, format="PNG")
        image_base64 = base64.b64encode(buffered.getvalue()).decode()
    
    try:
        date_formatted = datetime.strptime(timestamp, "%Y%m%d_%H%M%S").strftime("%d %B %Y, %H:%M")
    except:
        date_formatted = datetime.now().strftime("%d %B %Y, %H:%M")
    
    html_content = f"""
<!DOCTYPE html>
<html lang="ro">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Raport ArtAdvisor - Analiză Operă de Artă</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #fff;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 3px solid #D4AF37;
            padding-bottom: 20px;
        }}
        .header h1 {{
            color: #D4AF37;
            margin: 0;
            font-size: 2.5em;
        }}
        .header p {{
            color: #666;
            margin: 10px 0 0 0;
            font-style: italic;
        }}
        .info-section {{
            background-color: #f9f9f9;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 25px;
        }}
        .info-section h3 {{
            margin-top: 0;
            color: #2c3e50;
        }}
        .artwork-image {{
            text-align: center;
            margin: 25px 0;
        }}
        .artwork-image img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .narrative-section {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
            border-radius: 10px;
            margin: 25px 0;
            border-left: 5px solid #D4AF37;
        }}
        .narrative-section h2 {{
            color: #2c3e50;
            margin-top: 0;
        }}
        .results-section {{
            margin: 25px 0;
        }}
        .result-category {{
            margin-bottom: 20px;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 8px;
        }}
        .result-category h3 {{
            color: #34495e;
            margin-top: 0;
        }}
        .result-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }}
        .result-item:last-child {{
            border-bottom: none;
        }}
        .progress-bar {{
            width: 200px;
            height: 20px;
            background-color: #f0f0f0;
            border-radius: 10px;
            overflow: hidden;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #64A9F0, #D4AF37);
            border-radius: 10px;
        }}
        .gradcam-section {{
            margin: 25px 0;
            text-align: center;
        }}
        .gradcam-section img {{
            max-width: 400px;
            height: auto;
            border-radius: 8px;
            margin: 10px;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
            font-size: 0.9em;
        }}
        @media print {{
            body {{
                margin: 0;
                padding: 15px;
            }}
            .no-print {{
                display: none !important;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Raport de Analiză - ArtAdvisor</h1>
        <p>Sistem de Analiză Artistică</p>
    </div>
    
    <div class="info-section">
        <h3>Informații Generale</h3>
        <p><strong>Data analizei:</strong> {date_formatted}</p>
        <p><strong>Stil selectat pentru interpretare:</strong> {style_option}</p>
        <p><strong>Sistem:</strong> ArtAdvisor v2.0</p>
    </div>
    """
    
    if image_base64:
        html_content += f"""
    <div class="artwork-image">
        <img src="data:image/png;base64,{image_base64}" alt="Opera de artă analizată">
        <p><em>Opera de artă analizată</em></p>
    </div>
    """
    
    if narrative:
        html_content += f"""
    <div class="narrative-section">
        <h2>Interpretarea Operei</h2>
        <p>{narrative}</p>
    </div>
    """
    
    if predictions:
        html_content += """
    <div class="results-section">
        <h2>Rezultatele Analizei Tehnice</h2>
        """
        
        # Stilul artistic
        if 'stil' in predictions and predictions['stil'].get('predictions_sorted'):
            html_content += """
        <div class="result-category">
            <h3>Stil Artistic</h3>
            """
            for i, (style, confidence) in enumerate(predictions['stil']['predictions_sorted'][:3]):
                style_name = style.replace('_', ' ').title()
                progress_width = int(confidence * 100)
                html_content += f"""
            <div class="result-item">
                <span>#{i+1} {style_name}</span>
                <span>{confidence:.1%}</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {progress_width}%"></div>
            </div>
            """
            html_content += "</div>"
        
        # Autorul probabil
        if 'autor' in predictions and predictions['autor'].get('predictions_sorted'):
            html_content += """
        <div class="result-category">
            <h3>Autor Probabil</h3>
            """
            for i, (author, confidence) in enumerate(predictions['autor']['predictions_sorted'][:3]):
                author_name = author.replace('_', ' ').title()
                progress_width = int(confidence * 100)
                html_content += f"""
            <div class="result-item">
                <span>#{i+1} {author_name}</span>
                <span>{confidence:.1%}</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {progress_width}%"></div>
            </div>
            """
            html_content += "</div>"
        
        # Emoțiile detectate
        if 'emotie' in predictions and predictions['emotie'].get('predictions_sorted'):
            html_content += """
        <div class="result-category">
            <h3>Emoții Detectate</h3>
            """
            if predictions['emotie']['predictions_sorted']:
                for i, (emotion, score) in enumerate(predictions['emotie']['predictions_sorted'][:5]):
                    emotion_name = emotion.replace('_', ' ').title()
                    progress_width = int(score * 100)
                    html_content += f"""
            <div class="result-item">
                <span>#{i+1} {emotion_name}</span>
                <span>{score:.1%}</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {progress_width}%"></div>
            </div>
            """
            else:
                html_content += "<p><em>Nu au fost detectate emoții predominante (prag > 65%)</em></p>"
            html_content += "</div>"
        
        html_content += "</div>"
    
    gradcam_images = []
    if predictions:
        if 'stil' in predictions and 'gradcam_image' in predictions['stil']:
            gradcam_images.append(('Stil Artistic', predictions['stil']['gradcam_image']))
        if 'autor' in predictions and 'gradcam_image' in predictions['autor']:
            gradcam_images.append(('Autor', predictions['autor']['gradcam_image']))
    
    if gradcam_images:
        html_content += """
    <div class="gradcam-section">
        <h2>Explicații Vizuale (Grad-CAM)</h2>
        <p><em>Zonele mai luminoase reprezintă regiunile care au influențat cel mai mult decizia sistemului.</em></p>
        """
        
        for title, gradcam_img in gradcam_images:
            buffered = BytesIO()
            gradcam_img.save(buffered, format="PNG")
            gradcam_base64 = base64.b64encode(buffered.getvalue()).decode()
            html_content += f"""
        <div>
            <h4>Focus pentru {title}</h4>
            <img src="data:image/png;base64,{gradcam_base64}" alt="Grad-CAM {title}">
        </div>
        """
        
        html_content += "</div>"
    
    # Footer
    html_content += f"""
    <div class="footer">
        <p>Generat de ArtAdvisor - Sistem de Analiză Artistică</p>
        <p>Data generării: {datetime.now().strftime('%d %B %Y, %H:%M')}</p>
    </div>
</body>
</html>
    """
    
    return html_content

def generate_pdf_report(analysis_results):
    """
    Generează un raport HTML cu rezultatele analizei.
    HTML este mai stabil și poate fi convertit în PDF prin browser (Ctrl+P).
    """
    try:
        html_content = generate_html_content(analysis_results)
        
        # PRIORITIZEAZĂ HTML - mai stabil și funcționează întotdeauna
        print("Generating HTML report (recommended for Windows)")
        return BytesIO(html_content.encode('utf-8'))
        
    except Exception as e:
        print(f"Eroare la generarea raportului: {e}")
        # În caz de eroare totală, returnează HTML simplu
        try:
            simple_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Raport ArtAdvisor</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{ color: #D4AF37; }}
    </style>
</head>
<body>
    <h1>Raport de Analiză ArtAdvisor</h1>
    <p>Eroare la generarea raportului complet: {e}</p>
    <p>Data: {datetime.now().strftime('%d %B %Y, %H:%M')}</p>
    <p><strong>Soluție:</strong> Contactează echipa de suport pentru debugging.</p>
</body>
</html>
            """
            return BytesIO(simple_html.encode('utf-8'))
        except:
            return None
