"""
EthniData Predictor - Ana tahmin modülü
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Literal
from unidecode import unidecode
import pycountry

class EthniData:
    """Ethnicity and Nationality Data predictor"""

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize EthniData predictor

        Args:
            db_path: Path to SQLite database. If None, uses default location.
        """
        if db_path is None:
            db_path = Path(__file__).parent / "ethnidata.db"

        self.db_path = Path(db_path)

        if not self.db_path.exists():
            raise FileNotFoundError(
                f"Database not found: {self.db_path}\n"
                f"Please run scripts/6_create_database.py first"
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
            top_n: Number of top predictions to return

        Returns:
            {
                'name': normalized name,
                'country': top country code (ISO 3166-1 alpha-3),
                'confidence': confidence score (0-1),
                'top_countries': [{country, probability, frequency}, ...]
            }
        """

        normalized = self.normalize_name(name)

        table = "first_names" if name_type == "first" else "last_names"

        # Query database
        query = f"""
            SELECT country_code, frequency
            FROM {table}
            WHERE name = ?
            ORDER BY frequency DESC
            LIMIT ?
        """

        cursor = self.conn.cursor()
        cursor.execute(query, (normalized, top_n))

        results = cursor.fetchall()

        if not results:
            return {
                'name': normalized,
                'country': None,
                'confidence': 0.0,
                'top_countries': []
            }

        # Calculate probabilities
        total_frequency = sum(row['frequency'] for row in results)

        top_countries = []
        for row in results:
            prob = row['frequency'] / total_frequency

            # Country name lookup
            try:
                country = pycountry.countries.get(alpha_3=row['country_code'])
                country_name = country.name if country else row['country_code']
            except:
                country_name = row['country_code']

            top_countries.append({
                'country': row['country_code'],
                'country_name': country_name,
                'probability': round(prob, 4),
                'frequency': row['frequency']
            })

        # Top prediction
        top = top_countries[0]

        return {
            'name': normalized,
            'country': top['country'],
            'country_name': top['country_name'],
            'confidence': top['probability'],
            'top_countries': top_countries
        }

    def predict_ethnicity(
        self,
        name: str,
        name_type: Literal["first", "last"] = "first"
    ) -> Dict:
        """
        Predict ethnicity from name

        Args:
            name: First or last name
            name_type: "first" or "last"

        Returns:
            {
                'name': normalized name,
                'ethnicity': predicted ethnicity,
                'country': most likely country,
                'confidence': confidence score
            }
        """

        normalized = self.normalize_name(name)

        table = "first_names" if name_type == "first" else "last_names"

        # Query with ethnicity
        query = f"""
            SELECT country_code, ethnicity, frequency
            FROM {table}
            WHERE name = ? AND ethnicity IS NOT NULL
            ORDER BY frequency DESC
            LIMIT 1
        """

        cursor = self.conn.cursor()
        cursor.execute(query, (normalized,))

        result = cursor.fetchone()

        if result:
            # Country name
            try:
                country = pycountry.countries.get(alpha_3=result['country_code'])
                country_name = country.name if country else result['country_code']
            except:
                country_name = result['country_code']

            return {
                'name': normalized,
                'ethnicity': result['ethnicity'],
                'country': result['country_code'],
                'country_name': country_name,
                'frequency': result['frequency']
            }

        # Fallback to nationality prediction
        nationality = self.predict_nationality(name, name_type, top_n=1)

        return {
            'name': normalized,
            'ethnicity': None,
            'country': nationality['country'],
            'country_name': nationality.get('country_name'),
            'confidence': nationality['confidence']
        }

    def predict_full_name(
        self,
        first_name: str,
        last_name: str,
        top_n: int = 5
    ) -> Dict:
        """
        Predict nationality from full name (first + last)

        Combines predictions from both first and last names

        Args:
            first_name: First name
            last_name: Last name
            top_n: Number of top predictions

        Returns:
            Combined prediction with country probabilities
        """

        first_pred = self.predict_nationality(first_name, "first", top_n=top_n)
        last_pred = self.predict_nationality(last_name, "last", top_n=top_n)

        # Combine probabilities
        combined_scores = {}

        for item in first_pred['top_countries']:
            combined_scores[item['country']] = item['probability'] * 0.4

        for item in last_pred['top_countries']:
            if item['country'] in combined_scores:
                combined_scores[item['country']] += item['probability'] * 0.6
            else:
                combined_scores[item['country']] = item['probability'] * 0.6

        # Sort by combined score
        sorted_countries = sorted(
            combined_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_n]

        # Format results
        top_countries = []
        for country_code, score in sorted_countries:
            try:
                country = pycountry.countries.get(alpha_3=country_code)
                country_name = country.name if country else country_code
            except:
                country_name = country_code

            top_countries.append({
                'country': country_code,
                'country_name': country_name,
                'probability': round(score, 4)
            })

        return {
            'first_name': self.normalize_name(first_name),
            'last_name': self.normalize_name(last_name),
            'country': top_countries[0]['country'] if top_countries else None,
            'country_name': top_countries[0]['country_name'] if top_countries else None,
            'confidence': top_countries[0]['probability'] if top_countries else 0.0,
            'top_countries': top_countries
        }

    def get_stats(self) -> Dict:
        """Get database statistics"""

        cursor = self.conn.cursor()

        stats = {}

        cursor.execute("SELECT COUNT(*) as count FROM first_names")
        stats['total_first_names'] = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM last_names")
        stats['total_last_names'] = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(DISTINCT country_code) as count FROM first_names")
        stats['countries_first'] = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(DISTINCT country_code) as count FROM last_names")
        stats['countries_last'] = cursor.fetchone()['count']

        return stats
