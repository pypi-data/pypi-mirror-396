# EthniData - Ethnicity and Nationality Prediction

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/ethnidata.svg)](https://badge.fury.io/py/ethnidata)

Predict **nationality**, **ethnicity**, and **demographics** from names using a comprehensive global database built from multiple authoritative sources.

## 🌟 Features

- **190+ Countries** - Comprehensive coverage from Wikipedia/Wikidata
- **106 Countries** - Enhanced with names-dataset
- **120 Years** of Olympic athlete names
- **Multiple Sources** - Phone directories, census data, public records
- **Fast Predictions** - SQLite-based for instant lookups
- **Normalized Data** - Unicode-aware, case-insensitive matching
- **Ethnicity Support** - Where available in source data
- **Simple API** - Easy to use Python interface

## 📊 Data Sources

1. **Wikipedia/Wikidata** - 190+ countries, biographical data with ethnicity
2. **names-dataset** - 106 countries, curated name lists
3. **Olympics Dataset** - 120 years of athlete names (271,116 records)
4. **Phone Directories** - Public domain name lists from multiple countries
5. **Census Data** - US Census and other government open data

## 🚀 Installation

```bash
pip install ethnidata
```

## 📖 Usage

### Basic Usage

```python
from ethnidata import EthniData

# Initialize
ed = EthniData()

# Predict nationality from first name
result = ed.predict_nationality("Ahmet", name_type="first")
print(result)
# {
#   'name': 'ahmet',
#   'country': 'TUR',
#   'country_name': 'Turkey',
#   'confidence': 0.89,
#   'top_countries': [
#     {'country': 'TUR', 'country_name': 'Turkey', 'probability': 0.89},
#     {'country': 'DEU', 'country_name': 'Germany', 'probability': 0.07},
#     ...
#   ]
# }

# Predict from last name
result = ed.predict_nationality("Tanaka", name_type="last")
print(result['country'])  # 'JPN'

# Predict from full name (combines both)
result = ed.predict_full_name("Wei", "Chen")
print(result['country'])  # 'CHN'

# Predict ethnicity (when available)
result = ed.predict_ethnicity("Muhammad", name_type="first")
print(result)
# {
#   'name': 'muhammad',
#   'ethnicity': 'Arab',
#   'country': 'SAU',
#   'country_name': 'Saudi Arabia'
# }
```

### Advanced Usage

```python
# Get top 10 predictions
result = ed.predict_nationality("Maria", name_type="first", top_n=10)

for country in result['top_countries']:
    print(f"{country['country_name']}: {country['probability']:.2%}")
# Spain: 35.4%
# Italy: 28.2%
# Portugal: 15.1%
# ...

# Database statistics
stats = ed.get_stats()
print(stats)
# {
#   'total_first_names': 123456,
#   'total_last_names': 234567,
#   'countries_first': 195,
#   'countries_last': 198
# }
```

## 🏗️ Project Structure

```
ethnidata/
├── ethnidata/                # Main package
│   ├── __init__.py
│   ├── predictor.py          # Core prediction logic
│   └── ethnidata.db          # SQLite database
├── scripts/                  # Data collection scripts
│   ├── 1_fetch_names_dataset.py
│   ├── 2_fetch_wikipedia.py
│   ├── 3_fetch_olympics.py
│   ├── 4_fetch_phone_directories.py
│   ├── 5_merge_all_data.py
│   └── 6_create_database.py
├── tests/                    # Unit tests
├── examples/                 # Example scripts
├── docs/                     # Documentation
├── setup.py
├── pyproject.toml
└── README.md
```

## 🔬 Accuracy & Methodology

### How it works

1. **Name Normalization**: Names are lowercased and Unicode-normalized (e.g., "José" → "jose")
2. **Database Lookup**: Queries SQLite database for matching names
3. **Frequency-Based Scoring**: Countries are ranked by how often the name appears
4. **Probability Calculation**: Frequencies are converted to probabilities
5. **Full Name Combination**: First name (40%) + last name (60%) weights

### Limitations

- **Bias**: Database reflects historical Olympic participation, Wikipedia coverage
- **Missing Names**: Rare or new names may not be in database
- **Ethnicity**: Only available where source data included it
- **Migration**: Doesn't account for diaspora or modern migration patterns
- **Multiple Origins**: Common names (e.g., "Ali", "Maria") exist in many cultures

## 🛠️ Development

### Build Database from Scratch

```bash
git clone https://github.com/teyfikoz/ethnidata.git
cd ethnidata

# Install dependencies
pip install -r requirements.txt

# Fetch all data (takes 10-30 minutes)
cd scripts
python 1_fetch_names_dataset.py
python 2_fetch_wikipedia.py
python 3_fetch_olympics.py
python 4_fetch_phone_directories.py
python 5_merge_all_data.py
python 6_create_database.py
```

### Run Tests

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📚 Citations

If you use this database in research, please cite:

```bibtex
@software{ethnidata_2024,
  title = {EthniData: Ethnicity and Nationality Prediction from Names},
  author = {Oz, Teyfik},
  year = {2024},
  url = {https://github.com/teyfikoz/ethnidata}
}
```

### Data Source Citations

- **Olympics Data**: Randi Griffin (2018). 120 years of Olympic history. [Kaggle](https://www.kaggle.com/datasets/heesoo37/120-years-of-olympic-history-athletes-and-results)
- **names-dataset**: Philippe Remy (2021). [name-dataset](https://github.com/philipperemy/name-dataset)
- **Wikidata**: Wikimedia Foundation. [Wikidata](https://www.wikidata.org)

## 🔗 Related Projects

- [ethnicolr](https://github.com/appeler/ethnicolr) - Ethnicity prediction using LSTM
- [name-dataset](https://github.com/philipperemy/name-dataset) - Name database (106 countries)
- [gender-guesser](https://github.com/lead-ratings/gender-guesser) - Gender prediction

## 📧 Contact

- GitHub Issues: [Report bugs or request features](https://github.com/teyfikoz/ethnidata/issues)
- GitHub: [@teyfikoz](https://github.com/teyfikoz)

---

**Built with ❤️ using open data**
