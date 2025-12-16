"""
Wikipedia Tablo Çekici - Wikipedia sayfalarından tablo verilerini çeken Python kütüphanesi
"""

from .wikipedia_tablo_cek import (
    wikipedia_tablo_cek,
    tablo_kaydet,
    tum_tablolari_goster
)

__version__ = "1.0.0"
__author__ = "Özgür Özen"
__email__ = "oozen760@gmail.com"

__all__ = [
    'wikipedia_tablo_cek',
    'tablo_kaydet',
    'tum_tablolari_goster',
]