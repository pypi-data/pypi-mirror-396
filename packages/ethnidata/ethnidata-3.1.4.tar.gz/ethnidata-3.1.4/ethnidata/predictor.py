"""
EthniData Predictor v2.0 - Gelişmiş özelliklerle
Yeni özellikler:
- Gender prediction (Cinsiyet tahmini)
- Region prediction (Bölge: Europe, Asia, Americas, Africa, Oceania)
- Language prediction (Yaygın dil tahmini)
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Literal
from unidecode import unidecode
import pycountry

class EthniData:
    """Ethnicity, Nationality, Gender, Region and Language predictor"""

    def __init__(self, db_path: Optional[str] = None, use_v3: bool = False):
        """
        Initialize EthniData predictor

        Args:
            db_path: Path to SQLite database. If None, uses default location.
            use_v3: If True, attempts to use v3.0.0 database (5.8M records).
                   If False, uses v2.0.0 database (415K records, included in package).
        """
        if db_path is None:
            package_dir = Path(__file__).parent

            if use_v3:
                # Try to use v3 database
                v3_path = package_dir / "ethnidata_v3.db"
                if v3_path.exists():
                    db_path = v3_path
                else:
                    print(f"\n💡 EthniData v3.0.0 (5.8M records) is not installed.")
                    print(f"   To download: from ethnidata.downloader import download_v3_database")
                    print(f"   download_v3_database()")
                    print(f"\n   Using v2.0.0 (415K records) for now...")
                    db_path = package_dir / "ethnidata.db"
            else:
                db_path = package_dir / "ethnidata.db"

        self.db_path = Path(db_path)

        if not self.db_path.exists():
            raise FileNotFoundError(
                f"Database not found: {self.db_path}\n"
                f"Please reinstall: pip install --upgrade --force-reinstall ethnidata"
            )

        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def __del__(self):
        """Close database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()

    @staticmethod
    def normalize_name(name: str) -> str:
        """Normalize name (lowercase, remove accents)"""
        return unidecode(name.strip().lower())

    def predict_nationality(
        self,
        name: str,
        name_type: Literal["first", "last"] = "first",
        top_n: int = 5
    ) -> Dict:
        """
        Predict nationality from name

        Args:
            name: First or last name
            name_type: "first" or "last"
            top_n: Number of top predictions

        Returns:
            {
                'name': str,
                'country': str (ISO 3166-1 alpha-3),
                'country_name': str,
                'confidence': float (0-1),
                'region': str,  # NEW
                'language': str,  # NEW
                'top_countries': [...]
            }
        """

        normalized = self.normalize_name(name)

        query = """
            SELECT country_code, region, language, COUNT(*) as frequency
            FROM names
            WHERE name = ? AND name_type = ?
            GROUP BY country_code, region, language
            ORDER BY frequency DESC
            LIMIT ?
        """

        cursor = self.conn.cursor()
        cursor.execute(query, (normalized, name_type, top_n))
        results = cursor.fetchall()

        if not results:
            return {
                'name': normalized,
                'country': None,
                'country_name': None,
                'confidence': 0.0,
                'region': None,
                'language': None,
                'top_countries': []
            }

        # Calculate probabilities
        total_freq = sum(row['frequency'] for row in results)

        top_countries = []
        for row in results:
            prob = row['frequency'] / total_freq

            try:
                country = pycountry.countries.get(alpha_3=row['country_code'])
                country_name = country.name if country else row['country_code']
            except:
                country_name = row['country_code']

            top_countries.append({
                'country': row['country_code'],
                'country_name': country_name,
                'region': row['region'],
                'language': row['language'],
                'probability': round(prob, 4),
                'frequency': row['frequency']
            })

        top = top_countries[0]

        return {
            'name': normalized,
            'country': top['country'],
            'country_name': top['country_name'],
            'confidence': top['probability'],
            'region': top['region'],  # NEW
            'language': top['language'],  # NEW
            'top_countries': top_countries
        }

    def predict_gender(
        self,
        name: str
    ) -> Dict:
        """
        Predict gender from first name

        Args:
            name: First name

        Returns:
            {
                'name': str,
                'gender': str ('M' or 'F' or None),
                'confidence': float,
                'distribution': {'M': prob, 'F': prob, None: prob}
            }
        """

        normalized = self.normalize_name(name)

        query = """
            SELECT gender, COUNT(*) as count
            FROM names
            WHERE name = ? AND name_type = 'first'
            GROUP BY gender
        """

        cursor = self.conn.cursor()
        cursor.execute(query, (normalized,))
        results = cursor.fetchall()

        if not results:
            return {
                'name': normalized,
                'gender': None,
                'confidence': 0.0,
                'distribution': {}
            }

        # Count by gender
        gender_counts = {}
        total = 0

        for row in results:
            gender = row['gender']
            count = row['count']
            gender_counts[gender] = count
            total += count

        # Calculate probabilities
        distribution = {g: round(c / total, 4) for g, c in gender_counts.items()}

        # Top gender
        top_gender = max(gender_counts.items(), key=lambda x: x[1])[0]
        confidence = gender_counts[top_gender] / total

        return {
            'name': normalized,
            'gender': top_gender,
            'confidence': round(confidence, 4),
            'distribution': distribution
        }

    def predict_region(
        self,
        name: str,
        name_type: Literal["first", "last"] = "first"
    ) -> Dict:
        """
        Predict geographic region from name

        Args:
            name: First or last name
            name_type: "first" or "last"

        Returns:
            {
                'name': str,
                'region': str (Europe, Asia, Americas, Africa, Oceania, Other),
                'confidence': float,
                'distribution': {region: probability, ...}
            }
        """

        normalized = self.normalize_name(name)

        query = """
            SELECT region, COUNT(*) as total_freq
            FROM names
            WHERE name = ? AND name_type = ?
            GROUP BY region
            ORDER BY total_freq DESC
        """

        cursor = self.conn.cursor()
        cursor.execute(query, (normalized, name_type))
        results = cursor.fetchall()

        if not results:
            return {
                'name': normalized,
                'region': None,
                'confidence': 0.0,
                'distribution': {}
            }

        total = sum(row['total_freq'] for row in results)

        distribution = {}
        for row in results:
            region = row['region']
            prob = row['total_freq'] / total
            distribution[region] = round(prob, 4)

        top_region = results[0]['region']
        confidence = results[0]['total_freq'] / total

        return {
            'name': normalized,
            'region': top_region,
            'confidence': round(confidence, 4),
            'distribution': distribution
        }

    def predict_language(
        self,
        name: str,
        name_type: Literal["first", "last"] = "first",
        top_n: int = 5
    ) -> Dict:
        """
        Predict most likely language from name

        Args:
            name: First or last name
            name_type: "first" or "last"
            top_n: Number of top predictions

        Returns:
            {
                'name': str,
                'language': str,
                'confidence': float,
                'top_languages': [{language, probability}, ...]
            }
        """

        normalized = self.normalize_name(name)

        query = """
            SELECT language, COUNT(*) as total_freq
            FROM names
            WHERE name = ? AND name_type = ? AND language IS NOT NULL
            GROUP BY language
            ORDER BY total_freq DESC
            LIMIT ?
        """

        cursor = self.conn.cursor()
        cursor.execute(query, (normalized, name_type, top_n))
        results = cursor.fetchall()

        if not results:
            return {
                'name': normalized,
                'language': None,
                'confidence': 0.0,
                'top_languages': []
            }

        total = sum(row['total_freq'] for row in results)

        top_languages = []
        for row in results:
            lang = row['language']
            prob = row['total_freq'] / total
            top_languages.append({
                'language': lang,
                'probability': round(prob, 4)
            })

        return {
            'name': normalized,
            'language': top_languages[0]['language'],
            'confidence': top_languages[0]['probability'],
            'top_languages': top_languages
        }

    def predict_religion(
        self,
        name: str,
        name_type: Literal["first", "last"] = "first",
        top_n: int = 5
    ) -> Dict:
        """
        Predict religion from name - NEW in v1.3.0!

        Args:
            name: First or last name
            name_type: "first" or "last"
            top_n: Number of top predictions

        Returns:
            {
                'name': str,
                'religion': str (Christianity, Islam, Hinduism, Buddhism, Judaism),
                'confidence': float,
                'top_religions': [{religion, probability}, ...]
            }
        """

        normalized = self.normalize_name(name)

        query = """
            SELECT religion, COUNT(*) as total_freq
            FROM names
            WHERE name = ? AND name_type = ? AND religion IS NOT NULL
            GROUP BY religion
            ORDER BY total_freq DESC
            LIMIT ?
        """

        cursor = self.conn.cursor()
        cursor.execute(query, (normalized, name_type, top_n))
        results = cursor.fetchall()

        if not results:
            return {
                'name': normalized,
                'religion': None,
                'confidence': 0.0,
                'top_religions': []
            }

        total = sum(row['total_freq'] for row in results)

        top_religions = []
        for row in results:
            religion = row['religion']
            prob = row['total_freq'] / total
            top_religions.append({
                'religion': religion,
                'probability': round(prob, 4)
            })

        return {
            'name': normalized,
            'religion': top_religions[0]['religion'],
            'confidence': top_religions[0]['probability'],
            'top_religions': top_religions
        }

    def predict_ethnicity(
        self,
        name: str,
        name_type: Literal["first", "last"] = "first"
    ) -> Dict:
        """Predict ethnicity from name (uses nationality as proxy)"""

        # Use nationality as ethnicity proxy since we don't have separate ethnicity data
        nationality = self.predict_nationality(name, name_type, top_n=1)

        return {
            'name': nationality['name'],
            'ethnicity': nationality['country_name'],  # Use country as ethnicity
            'country': nationality['country'],
            'country_name': nationality['country_name'],
            'region': nationality.get('region'),
            'language': nationality.get('language'),
            'confidence': nationality['confidence']
        }

    def predict_full_name(
        self,
        first_name: str,
        last_name: str,
        top_n: int = 5
    ) -> Dict:
        """
        Predict from full name (first + last) - ENHANCED

        Returns nationality, region, language
        """

        first_pred = self.predict_nationality(first_name, "first", top_n=top_n)
        last_pred = self.predict_nationality(last_name, "last", top_n=top_n)

        # Combine scores
        combined_scores = {}

        for item in first_pred['top_countries']:
            combined_scores[item['country']] = {
                'score': item['probability'] * 0.4,
                'region': item['region'],
                'language': item['language']
            }

        for item in last_pred['top_countries']:
            if item['country'] in combined_scores:
                combined_scores[item['country']]['score'] += item['probability'] * 0.6
            else:
                combined_scores[item['country']] = {
                    'score': item['probability'] * 0.6,
                    'region': item['region'],
                    'language': item['language']
                }

        # Sort
        sorted_countries = sorted(
            combined_scores.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )[:top_n]

        # Format
        top_countries = []
        for country_code, data in sorted_countries:
            try:
                country = pycountry.countries.get(alpha_3=country_code)
                country_name = country.name if country else country_code
            except:
                country_name = country_code

            top_countries.append({
                'country': country_code,
                'country_name': country_name,
                'region': data['region'],
                'language': data['language'],
                'probability': round(data['score'], 4)
            })

        top = top_countries[0] if top_countries else {}

        return {
            'first_name': self.normalize_name(first_name),
            'last_name': self.normalize_name(last_name),
            'country': top.get('country'),
            'country_name': top.get('country_name'),
            'region': top.get('region'),  # NEW
            'language': top.get('language'),  # NEW
            'confidence': top.get('probability', 0.0),
            'top_countries': top_countries
        }

    def predict_all(
        self,
        name: str,
        name_type: Literal["first", "last"] = "first"
    ) -> Dict:
        """
        Predict ALL attributes at once - UPDATED v1.3.0
        Now includes: nationality, gender, region, language, religion, ethnicity

        Args:
            name: First or last name
            name_type: "first" or "last"

        Returns:
            {
                'name': str,
                'nationality': {...},
                'gender': {...},  # Only for first names
                'region': {...},
                'language': {...},
                'religion': {...},  # NEW in v1.3.0!
                'ethnicity': {...}
            }
        """

        normalized = self.normalize_name(name)

        result = {
            'name': normalized,
            'nationality': self.predict_nationality(name, name_type),
            'region': self.predict_region(name, name_type),
            'language': self.predict_language(name, name_type),
            'religion': self.predict_religion(name, name_type),  # NEW!
            'ethnicity': self.predict_ethnicity(name, name_type)
        }

        # Gender only for first names
        if name_type == "first":
            result['gender'] = self.predict_gender(name)

        return result

    def get_stats(self) -> Dict:
        """Get database statistics"""

        cursor = self.conn.cursor()

        stats = {}

        cursor.execute("SELECT COUNT(*) as count FROM names WHERE name_type = 'first'")
        stats['total_first_names'] = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM names WHERE name_type = 'last'")
        stats['total_last_names'] = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(DISTINCT country_code) as count FROM names")
        stats['countries'] = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(DISTINCT region) as count FROM names WHERE region IS NOT NULL")
        stats['regions'] = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(DISTINCT language) as count FROM names WHERE language IS NOT NULL")
        stats['languages'] = cursor.fetchone()['count']

        return stats
