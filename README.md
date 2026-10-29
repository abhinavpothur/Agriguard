# 🌿 AgriGuard AI — Smart Crop Health & Treatment System

> Upload a photo of a sick leaf → AI identifies the disease → get the exact pesticides and fertilizers to use, with doses calculated for your farm size → an agronomist verifies it before you order.

![Status](https://img.shields.io/badge/status-hackathon%20prototype-orange)
![Hardware](https://img.shields.io/badge/hardware-ESP32-blue)
![Crops](https://img.shields.io/badge/crops-7-green)
![Disease classes](https://img.shields.io/badge/disease%20classes-20-brightgreen)

---

## 📖 What does it do?

AgriGuard AI is a web-based crop-health assistant made of two apps: a **Farmer dashboard** and an **Agronomist console**.

1. **Detects disease automatically.** The farmer uploads a leaf image; a trained image-classification model returns the disease class.
2. **Prescribes the treatment.** The class is matched to a treatment database of pesticides and fertilizers with per-acre rates.
3. **Calculates the dose.** The farmer enters total and infected acres; AgriGuard computes the quantity of every product.
4. **Gets expert approval.** The plan goes to an agronomist who sees the image, diagnosis, sensor data and doses, then approves or rejects.
5. **Unlocks delivery.** Ordering stays locked until the agronomist approves.
6. **Reads the field live.** An ESP32 streams soil moisture, humidity, temperature, rain and light readings into the dashboard.

> Nothing is prescribed until a disease has actually been detected. There is no default or guessed treatment.

## 🚜 What problem does it solve?

| Problem for farmers | How AgriGuard helps |
|---|---|
| Diseases are hard to identify early and accurately | AI detects the disease from a single leaf photo |
| Unsure which pesticide or fertilizer treats it | Built-in treatment table for 20 disease classes |
| Wrong quantities waste money and harm soil and crops | Doses are calculated from the infected acreage |
| No quick access to an expert for a second opinion | Agronomist approval loop with one-tap approve/reject |
| No field data to guide spraying decisions | Live ESP32 readings (e.g. rain detected → delay spray) |

## 🌾 Supported crops

| Crop | Disease classes |
|---|---|
| rice | `Bacterial leaf blight`, `Sheath_Blight`, `Narrow_Brown_Spot` |
| wheat | `YellowRust`, `Septoria`, `Mildew` |
| tomato | `Tomato__Late_blight`, `Tomato__Tomato_Yellow_Leaf_Curl_Virus`, `Tomato__Bacterial_spot` |
| suargcane | `smut`, `BrownRust`, `Grassy shoot` |
| spinach | `Downy-Mildew`, `Anthracnose`, `Bacterial-Spot` |
| lemon | `Citrus_Canker`, `Algal_Leaf_Spot`, `Citrus_Scab` |
| Kalanchoe pinata | `Kalanchoe_Web_Blight`, `Kalanchoe_Yellow_Blight` |

Names match the labels used to train the backend model exactly. Vector-control insecticides and sugarcane sett-soak are handled.

## 📐 How the dose is calculated

```
quantity = per-acre rate × infected acres
```

Example: Mancozeb 75% WP at `600–800 g/acre` over 2.5 infected acres gives `1.50–2.00 kg`. Units auto-convert (`1500 g → 1.50 kg`).

## 🛠️ Tech stack

Flow: **ESP32 + leaf image → Farmer dashboard → trained model API → treatment DB → dose calculator → agronomist approval.**

| Layer | Technology |
|---|---|
| Frontend | HTML5, JavaScript (ES6), Tailwind CSS, Font Awesome |
| Hardware | ESP32 with DHT (temp/humidity), soil moisture, rain droplet and LDR sensors |
| AI backend | Any image-classification API (e.g. FastAPI / Flask serving a trained CNN) |
| Sync | localStorage, BroadcastChannel, optional Firebase Realtime Database |
| Build | None. Each page is a single self-contained HTML file |

## 📁 Project structure

```
AgriGuard_Project/
├── AgriGuard_Farmer.html        # Sensors, vision, calculation, review, delivery
├── AgriGuard_Agronomist.html    # Receives cases, approves / rejects
├── README.md
└── README_DETAILED.md           # Full documentation
```

## 🚀 Quick start

```bash
cd AgriGuard_Project
python -m http.server 5500
```

1. Open `http://localhost:5500/AgriGuard_Farmer.html` and click **Open Live Dashboard**.
2. Open `http://localhost:5500/AgriGuard_Agronomist.html` in a second tab.
3. Upload a leaf image, enter farm and infected acres, then submit for review.

**Connect your model:** edit the `BACKEND` block at the top of the script in `AgriGuard_Farmer.html` (`url`, `fileField`). Your API returns e.g. `{"class": "Sheath_Blight", "confidence": 0.97}` and must allow CORS.

**Connect the ESP32:** enter its IP and click *Connect ESP32*. It polls `http://<ip>/data` for `{"soil":42,"humidity":68,"temp":29.4,"rain":false,"ldrRaw":1850}`.

## ⚠️ Limitations & disclaimer

- This is a **hackathon prototype**. Dealer stock, the priority queue and delivery times are simulated demo data.
- The trained model is **not included**; the frontend expects an HTTP prediction endpoint.
- Doses are reference rates. Have them **verified by a qualified agronomist** and always follow the product label and safety guidance.

## 📌 Roadmap

Separate plan for `Kalanchoe_Yellow_Blight` · soil-health and weather data · real dealer integration · automatic infected-area estimation.

## 📄 License

Add a `LICENSE` file (e.g. MIT).
