"""
EthniData v3.0.1 - ULTRA MASSIVE EXPANSION! Global Demographics Prediction
Predict nationality, ethnicity, gender, region, language AND religion!

🔥 NEW in v3.0.1 - COMPLETE RELIGIOUS COVERAGE:
- 📊 **5.9M+ records** (14x increase from v2.0.0 - 1,326% growth!)
- 🌍 **238 countries** - complete global coverage
- 🗣️  **72 languages**
- 🕌 **ALL 6 MAJOR WORLD RELIGIONS** - Complete coverage:
  - Christianity: 3.9M+ records (65.2%)
  - Buddhism: 1.3M+ records (22.1%)
  - Islam: 504K+ records (8.5%)
  - Judaism: 121K+ records (2.0%) ✡️
  - Hinduism: 90K+ records (1.5%)
  - Sikhism: 24K+ records (0.4%) 🪯 NEW!
- 🌎 **Perfectly balanced regional distribution**:
  - Asia: 33% • Americas: 32% • Africa: 30% • Europe: 3% • Oceania: 0.1%

Features:
- ✅ Nationality prediction (238 countries)
- ✅ Religion prediction (6 major world religions)
- ✅ Gender prediction
- ✅ Region prediction (5 continents)
- ✅ Language prediction (72 languages)
- ✅ Ethnicity prediction
- ✅ Full name analysis

Usage:
    from ethnidata import EthniData

    ed = EthniData()

    # Nationality
    result = ed.predict_nationality("Ahmet")

    # Religion (NOW WITH 6 RELIGIONS!)
    result = ed.predict_religion("Muhammad")  # Islam
    result = ed.predict_religion("Cohen")      # Judaism
    result = ed.predict_religion("Singh")      # Sikhism

    # Gender
    result = ed.predict_gender("Emma")

    # Region
    result = ed.predict_region("Chen")

    # Language
    result = ed.predict_language("José")

    # ALL at once
    result = ed.predict_all("Maria")
    # Returns: nationality, religion, gender, region, language, ethnicity
"""

__version__ = "3.1.0"
__author__ = "Teyfik Oz"
__license__ = "MIT"

from .predictor import EthniData

__all__ = ["EthniData"]
