# 🌍 Climate Risk Analysis Dashboard

> A data engineering + visualization project analyzing global climate risk (2000–2024) using Kaggle data and Streamlit.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-Enabled-ff4b4b?logo=streamlit)
![License](https://img.shields.io/badge/License-Educational-lightgrey)

---

## 📁 Project Structure
```text
climate-risk-analysis-dashboard/
├── .streamlit/                  # UI theme config
├── assets/screenshots/          # Dashboard images
├── etl/
│   ├── data/
│   │   ├── raw/                 # Kaggle dataset
│   │   └── processed/           # Transformed data
│   └── ingest_and_process.py    # ETL pipeline
├── app.py                       # Streamlit dashboard
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup

```bash
git clone https://github.com/<Uvi-12>/climate-risk-analysis-dashboard.git
cd climate-risk-analysis-dashboard
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 🧩 Configure Kaggle API
```bash
mkdir -p ~/.kaggle
mv ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

### 🧮 Run ETL & Launch Dashboard
```bash
python etl/ingest_and_process.py   # downloads + simulates data (2000–2024)
streamlit run app.py
```

---

## 🧠 Overview
- **Data Source:** [Global Climate Risk Index – Kaggle](https://www.kaggle.com/datasets/thedevastator/global-climate-risk-index-and-related-economic-l)  
- **Process:** Automated ETL → Feature Engineering → Yearly Simulation (2000–2024)  
- **Stack:** Python, Pandas, NumPy, Plotly, Streamlit, Kaggle CLI  
- **Output:** `risk_score = 0.5*temp_anomaly_z + 0.3*co2_growth_norm + 0.2*sea_level_z`

---

## 📊 Dashboard Features
| Section | Description |
|----------|--------------|
| **Overview** | Global map & KPIs by year |
| **Trends** | Country-wise multi-year plots |
| **Leaderboard** | Top countries by composite risk |
| **Methods** | ETL + formula reference |

---

## 🚀 Highlights
- Automated **Kaggle data download**
- Simulated **25-year climate trends**
- Fully reproducible **ETL + Streamlit pipeline**

---

## 🧩 Example
```bash
🧮 Simulating yearly variations (2000–2024)...
✅ Wrote processed data to: etl/data/processed/processed_data.csv
```

---

## 📜 License
Educational / Academic use only.  
Dataset © Kaggle (original license applies).

---
