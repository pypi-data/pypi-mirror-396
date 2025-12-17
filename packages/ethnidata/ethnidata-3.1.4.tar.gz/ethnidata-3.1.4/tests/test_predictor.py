"""
Unit tests for EthniData predictor
"""

import pytest
from ethnidata import EthniData

# Note: Bu testler veritabanı oluşturulduktan sonra çalışacaktır
# Önce scripts/6_create_database.py çalıştırın

@pytest.fixture
def nbd():
    """EthniData instance fixture"""
    try:
        return EthniData()
    except FileNotFoundError:
        pytest.skip("Database not found. Run scripts/6_create_database.py first")

def test_normalize_name():
    """Test name normalization"""
    assert EthniData.normalize_name("Müller") == "muller"
    assert EthniData.normalize_name("José") == "jose"
    assert EthniData.normalize_name("AHMED") == "ahmed"
    assert EthniData.normalize_name("  Yuki  ") == "yuki"

def test_predict_nationality_turkish(nbd):
    """Test Turkish name prediction"""
    result = nbd.predict_nationality("Ahmet", name_type="first")

    assert result['name'] == "ahmet"
    assert result['country'] is not None
    assert 0 <= result['confidence'] <= 1
    assert len(result['top_countries']) > 0

def test_predict_nationality_japanese(nbd):
    """Test Japanese name prediction"""
    result = nbd.predict_nationality("Tanaka", name_type="last")

    assert result['name'] == "tanaka"
    assert result['country'] is not None

def test_predict_nationality_unknown(nbd):
    """Test unknown name"""
    result = nbd.predict_nationality("XxXUnknownNameXxX", name_type="first")

    assert result['name'] == "xxxunknownnamexxx"
    assert result['country'] is None
    assert result['confidence'] == 0.0
    assert result['top_countries'] == []

def test_predict_full_name(nbd):
    """Test full name prediction"""
    result = nbd.predict_full_name("Mehmet", "Yılmaz")

    assert result['first_name'] == "mehmet"
    assert result['last_name'] == "yilmaz"
    assert result['country'] is not None
    assert 0 <= result['confidence'] <= 1

def test_predict_ethnicity(nbd):
    """Test ethnicity prediction"""
    result = nbd.predict_ethnicity("Muhammad", name_type="first")

    assert result['name'] == "muhammad"
    # Ethnicity may or may not be available
    assert 'ethnicity' in result
    assert 'country' in result

def test_get_stats(nbd):
    """Test database statistics"""
    stats = nbd.get_stats()

    assert 'total_first_names' in stats
    assert 'total_last_names' in stats
    assert 'countries_first' in stats
    assert 'countries_last' in stats

    assert stats['total_first_names'] >= 0
    assert stats['total_last_names'] >= 0

def test_top_n_parameter(nbd):
    """Test top_n parameter"""
    result = nbd.predict_nationality("John", name_type="first", top_n=3)

    assert len(result['top_countries']) <= 3

def test_case_insensitive(nbd):
    """Test case insensitivity"""
    result1 = nbd.predict_nationality("maria", name_type="first")
    result2 = nbd.predict_nationality("MARIA", name_type="first")
    result3 = nbd.predict_nationality("Maria", name_type="first")

    assert result1['name'] == result2['name'] == result3['name']
    assert result1['country'] == result2['country'] == result3['country']

def test_accent_normalization(nbd):
    """Test accent normalization"""
    result1 = nbd.predict_nationality("Jose", name_type="first")
    result2 = nbd.predict_nationality("José", name_type="first")

    assert result1['name'] == result2['name'] == "jose"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
