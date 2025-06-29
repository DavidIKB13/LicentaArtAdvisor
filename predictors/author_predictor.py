import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import streamlit as st
import operator
from torchcam.methods import GradCAM
import numpy as np
import cv2

MODEL_PATH = "models/model_autor.pth"
AUTHOR_LABELS = ["Amedeo_Modigliani", "Anthony_Van_Dyck", "Aubrey_Beardsley", "Childe_Hassam", "Claude_Monet", "Ernst_Ludwig_Kirchner", "Francisco_Goya", "Gustave_Dore", "Gustave_Loiseau", "Ilya_Repin", "Isaac_Levitan", "Ivan_Aivazovsky", "Ivan_Bilibin", "Ivan_Shishkin", "Kuzma_Petrov", "Martiros_Saryan", "Nicholas_Roerich", "Odilon_Redon", "Paul_Cezanne", "Peter_Paul_Rubens", "Pierre_Auguste_Renoir", "Raphael_Kirchner", "Rembrandt", "Rene_Magritte", "Salvador_Dali", "Vincent_Van_Gogh", "Zdislav_Beksinski"]
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

@st.cache_resource
def load_author_model():
    """
    Încarcă modelul de autor o singură dată.
    Arhitectura este definită direct, pentru a se potrivi perfect cu fișierul .pth salvat.
    """
    print("Încărcare model AUTOR... (rulează o singură dată)")
    model = models.efficientnet_b0(weights=None)
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.3),
        nn.Linear(in_features, len(AUTHOR_LABELS))
    )
    
    try:
        model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE, weights_only=True))
    except TypeError:
        model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    model.to(DEVICE)
    model.eval()
    return model

def get_prediction_transforms(img_size=224):
    return transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

def predict_author(image_path: str):
    """
    Predicția autorului cu Grad-CAM îmbunătățit (versiunea colegului integrată).
    Returnează format compatibil cu aplicația existentă: {"predictions_sorted": [...], "gradcam_image": ...}
    """
    model = load_author_model()
    try:
        transform = get_prediction_transforms()
        original_image = Image.open(image_path).convert('RGB')
        image_tensor = transform(original_image).unsqueeze(0).to(DEVICE)

        # Generarea Predicției și a Hărții Grad-CAM
        with GradCAM(model, target_layer=model.features[-1]) as cam_extractor:
            outputs = model(image_tensor)
            probabilities = torch.softmax(outputs, dim=1).cpu().squeeze()
            predicted_class_idx = probabilities.argmax().item()
            activation_map = cam_extractor(predicted_class_idx, outputs)
        
        results = {author: prob.item() for author, prob in zip(AUTHOR_LABELS, probabilities)}
        predictions_sorted = sorted(results.items(), key=operator.itemgetter(1), reverse=True)
        
        # Extragem harta Grad-CAM și o normalizăm
        cam = activation_map[0].squeeze(0) 
        cam_min, cam_max = cam.min(), cam.max()
        cam_normalized = (cam - cam_min) / (cam_max - cam_min + 1e-8)
        cam_np = cam_normalized.cpu().numpy()

        # Resize direct pe numpy array cu interpolare CUBIC pentru calitate mai bună
        cam_resized_np = cv2.resize(cam_np, original_image.size, interpolation=cv2.INTER_CUBIC)

        heatmap_colored = cv2.applyColorMap(np.uint8(255 * cam_resized_np), cv2.COLORMAP_JET)

        orig_np = np.array(original_image.convert("RGB"))
        if orig_np.shape[2] == 4:
            orig_np = orig_np[:, :, :3]

        overlay_np = cv2.addWeighted(heatmap_colored, 0.4, orig_np, 0.6, 0)

        overlay_img = Image.fromarray(overlay_np)

        return {"predictions_sorted": predictions_sorted, "gradcam_image": overlay_img}

    except Exception as e:
        print(f"Eroare detaliată în author_predictor: {e}")
        return {"error": str(e), "predictions_sorted": []}