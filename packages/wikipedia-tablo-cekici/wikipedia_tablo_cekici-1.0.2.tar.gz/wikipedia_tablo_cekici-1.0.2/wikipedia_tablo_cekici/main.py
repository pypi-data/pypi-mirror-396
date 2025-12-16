import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

# Bu satırı SİLİN:
# from .wikipedia_tablo_cek import wikipedia_tablo_cek, tablo_kaydet, tum_tablolari_goster

def wikipedia_tablo_cek(url, tablo_index=0):
    """
    Wikipedia sayfasından belirtilen indexteki tabloyu çeker
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    tablolar = soup.find_all('table', {'class': 'wikitable'})
    
    if not tablolar:
        raise ValueError("Sayfada tablo bulunamadı!")
    
    if tablo_index >= len(tablolar):
        raise ValueError(f"Geçersiz tablo indexi! Sayfada {len(tablolar)} tablo var.")
    
    tablo = tablolar[tablo_index]
    df = pd.read_html(str(tablo))[0]
    
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
        raise ValueError("Geçersiz format! 'csv', 'excel' veya 'json' olmalı.")
    
    print(f"✅ Tablo '{dosya_yolu}' olarak kaydedildi.")

def tum_tablolari_goster(url):
    """
    Sayfadaki tüm tabloları gösterir
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    tablolar = soup.find_all('table', {'class': 'wikitable'})
    
    print(f"Bu sayfada {len(tablolar)} tablo bulundu:\n")
    
    for i, tablo in enumerate(tablolar):
        print(f"Tablo {i}:")
        df = pd.read_html(str(tablo))[0]
        print(df.head())
        print("\n" + "="*50 + "\n")