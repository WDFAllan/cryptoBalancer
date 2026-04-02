# 📈 cryptoBalancer

Une API construite avec FastAPI permettant de gérer et d’analyser un portefeuille de cryptomonnaies.  
Le projet inclut la gestion des cryptos, des wallets, des utilisateurs, du backtesting ainsi que la récupération de données de marché (candles) avec un scheduler automatique.

---

## 🚀 Fonctionnalités

- API REST rapide et moderne avec **FastAPI**
- Gestion des :
  - utilisateurs
  - cryptomonnaies
  - wallets
- Backtesting de stratégies d’investissement
- Récupération des données de marché (candles)
- Scheduler pour mise à jour automatique des données
- Support CORS pour intégration avec un frontend (React, Angular, etc.)

---

## 🧱 Architecture

backend/

├── app/

│ ├── api/v1/

│ │ ├── controllers/ # Routes API

│ │ 

│ ├── core/ # Config, DB, scheduler

│ └── main.py # Point d’entrée FastAPI


---

## 🛠️ Prérequis

- Python 3.10+
- pip 
- (Optionnel) Docker
- Une base de données PostgreSQL
- Un fichier `.env`

---

## 📦 Installation

### 1. Cloner le projet

```bash
git clone https://github.com/WDFAllan/cryptoBalancer.git
cd cryptoBalancer/backend
```

2. Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
.venv\Scripts\activate      # Windows

3. Installer les dépendances
pip install -r requirements.txt

4. Configurer les variables d’environnement

Créer un fichier .env :

SESSION_SECRET_KEY=your_secret_key
DATABASE_URL=postgresql://user:password@localhost:5432/crypto

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
