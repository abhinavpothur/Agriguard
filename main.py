import httpx
import json
from pathlib import Path
from io import BytesIO

import torch
from PIL import Image, UnidentifiedImageError
from torchvision import transforms
from torchvision.models import efficientnet_b0
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
# Create the FastAPI application
app = FastAPI()
SENSOR_URL = "http://192.168.4.1/data"


@app.get("/sensors")
async def get_sensor_data():
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(SENSOR_URL)
            response.raise_for_status()
            return response.json()

    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Could not read hardware sensors: {exc}"
        )
# Enable frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Locate the project files
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "best_model.pt"
CLASSES_PATH = BASE_DIR / "models" / "classes.json"

# Select GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load class names
with open(CLASSES_PATH, "r", encoding="utf-8") as file:
    classes = json.load(file)

# Recreate the model architecture
model = efficientnet_b0(weights=None)
model.classifier[1] = torch.nn.Linear(
    model.classifier[1].in_features,
    len(classes)
)

# Load trained parameters
checkpoint = torch.load(
    MODEL_PATH,
    map_location=device,
    weights_only=True
)

model.load_state_dict(checkpoint["state"])
model = model.to(device)
model.eval()

print(f"Model loaded successfully on {device}")
print(f"Number of classes: {len(classes)}")

# Use the same validation preprocessing as training
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


# Basic API status endpoint
@app.get("/")
def home():
    return {
        "message": "Crop Disease Detection API is running!",
        "model_loaded": True,
        "number_of_classes": len(classes)
    }


# Image prediction endpoint
@app.post("/predict")
async def predict(file: UploadFile = File(...)):

    # Read and validate the uploaded image
    try:
        image_bytes = await file.read()

        image = Image.open(BytesIO(image_bytes)).convert("RGB")

    except (UnidentifiedImageError, OSError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="Please upload a valid image file."
        )

    # Preprocess the image
    image_tensor = preprocess(image).unsqueeze(0).to(device)

    # Run model inference
    with torch.inference_mode():
        outputs = model(image_tensor)
        probabilities = torch.softmax(outputs, dim=1)

        top_probabilities, top_indices = torch.topk(
            probabilities[0],
            k=min(3, len(classes))
        )

    # Prepare the top predictions
    predictions = []

    for probability, index in zip(
        top_probabilities.tolist(),
        top_indices.tolist()
    ):
        predictions.append({
            "class": classes[index],
            "confidence": round(probability, 4)
        })


    # Reject predictions with low confidence
    confidence_threshold = 0.17

    if predictions[0]["confidence"] < confidence_threshold:
        return {
            "filename": file.filename,
            "recognized": False,
            "message": "Image not recognized or prediction uncertain.",
            "confidence": predictions[0]["confidence"],
            "top_predictions": predictions
        }

    return {
        "filename": file.filename,
        "recognized": True,
        "predicted_class": predictions[0]["class"],
        "confidence": predictions[0]["confidence"],
        "top_predictions": predictions
    }


    
    
    
    
    
    
    
    
   