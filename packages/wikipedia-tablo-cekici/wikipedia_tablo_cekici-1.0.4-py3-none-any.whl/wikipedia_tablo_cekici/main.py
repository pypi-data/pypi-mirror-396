import requests
from bs4 import BeautifulSoup
import pandas as pd
import os


def wikipedia_tablo_cek(url, tablo_index=0):
    """
    Wikipedia sayfasindan belirtilen indexteki tabloyu ceker
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Önce wikitable class'ını dene
    tablolar = soup.find_all('table', {'class': 'wikitable'})
    
    # Bulunamazsa tüm tabloları al
    if not tablolar:
        print("⚠ wikitable bulunamadı, tüm tabloları arıyorum...")
        tablolar = soup.find_all('table')
    
    if not tablolar:
        raise ValueError("Sayfada tablo bulunamadi!")
    
    print(f"✓ Toplam {len(tablolar)} tablo bulundu")
    
    if tablo_index >= len(tablolar):
        raise ValueError(f"Gecersiz tablo indexi! Sayfada {len(tablolar)} tablo var.")
    
    tablo = tablolar[tablo_index]
    df = pd.read_html(str(tablo))[0]
    
    print(f"✓ Tablo {tablo_index} çekildi: {df.shape[0]} satır x {df.shape[1]} sütun")
    
    return df


def tablo_kaydet(df, klasor_adi='veriler', dosya_formati='csv'):
    """
    DataFrame'i belirtilen formatta kaydeder
    """
    os.makedirs(klasor_adi, exist_ok=True)
    
    dosya_adi = f"tablo.{dosya_formati}"
    dosya_yolu = os.path.join(klasor_adi, dosya_adi)
    
    if dosya_formati == 'csv':
        df.to_csv(dosya_yolu, index=False, encoding='utf-8-sig')
    elif dosya_formati == 'excel':
        df.to_excel(dosya_yolu, index=False)
    elif dosya_formati == 'json':
        df.to_json(dosya_yolu, orient='records', force_ascii=False)
    else:
        raise ValueError("Gecersiz format! 'csv', 'excel' veya 'json' olmali.")
    
    print(f"✓ Tablo '{dosya_yolu}' olarak kaydedildi.")


def tum_tablolari_goster(url):
    """
    Sayfadaki tum tablolari gosterir
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    tablolar = soup.find_all('table', {'class': 'wikitable'})
    
    if not tablolar:
        tablolar = soup.find_all('table')
    
    print(f"Bu sayfada {len(tablolar)} tablo bulundu:\n")
    
    for i, tablo in enumerate(tablolar):
        print(f"Tablo {i}:")
        df = pd.read_html(str(tablo))[0]
        print(f"  Boyut: {df.shape[0]} satır x {df.shape[1]} sütun")
        print(f"  Sütunlar: {list(df.columns)[:5]}")
        print(df.head(3))
        print("\n" + "="*50 + "\n")