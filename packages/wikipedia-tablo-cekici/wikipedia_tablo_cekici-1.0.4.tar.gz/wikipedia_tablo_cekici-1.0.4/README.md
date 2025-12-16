# Wikipedia Tablo Çekici

Wikipedia sayfalarından tablo verilerini çeken Python kütüphanesi.

## Kurulum
```bash
pip install wikipedia-tablo-cekici
```

## Kullanım

### Temel Kullanım
```python
from wikipedia_tablo_cekici import wikipedia_tablo_cek, tablo_kaydet

url = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)"
df = wikipedia_tablo_cek(url, tablo_index=0)
tablo_kaydet(df, 'veriler', 'csv')
```

### Tüm Tabloları Görüntüleme
```python
from wikipedia_tablo_cekici import tum_tablolari_goster

url = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)"
tum_tablolari_goster(url)
```

### Farklı Formatlarda Kaydetme
```python
# CSV
tablo_kaydet(df, 'veriler', 'csv')

# Excel
tablo_kaydet(df, 'veriler', 'excel')

# JSON
tablo_kaydet(df, 'veriler', 'json')
```

## Özellikler

- Wikipedia tablolarını Pandas DataFrame'e dönüştürme
- CSV, Excel ve JSON formatlarında kaydetme
- Basit ve kullanımı kolay API

## Gereksinimler

- Python 3.7+
- requests
- beautifulsoup4
- pandas
- lxml
- openpyxl

## Lisans

MIT

## Yazar

Özgür Özen

## GitHub

https://github.com/ozgurrozennn/my_project