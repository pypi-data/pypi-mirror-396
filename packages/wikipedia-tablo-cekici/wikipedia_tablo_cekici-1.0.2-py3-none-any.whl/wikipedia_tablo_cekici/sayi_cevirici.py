import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import sys


def wikipedia_tablo_cek(url, tablo_index=0, format='csv'):
    """
    Wikipedia sayfasından tablo verisi çeker

    Args:
        url: Wikipedia sayfa URL'i
        tablo_index: Kaçıncı tabloyu çekmek istediğiniz (0'dan başlar)
        format: Çıktı formatı ('csv', 'json', 'excel')

    Returns:
        DataFrame: Pandas DataFrame olarak tablo verisi
    """
    try:
        # Wikipedia sayfasını indir
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # HTML'i parse et
        soup = BeautifulSoup(response.content, 'html.parser')

        # Tüm tabloları bul
        tables = soup.find_all('table', {'class': 'wikitable'})

        if not tables:
            print("Hata: Sayfada wikitable bulunamadı!")
            print("Diğer tablo tiplerini arıyorum...")
            tables = soup.find_all('table')
            if not tables:
                print("Hata: Sayfada hiç tablo bulunamadı!")
                return None

        print(f"✓ Toplam {len(tables)} adet tablo bulundu")

        # İstenen tabloyu kontrol et
        if tablo_index >= len(tables):
            print(f"Hata: Tablo index {tablo_index} çok büyük! Maksimum: {len(tables) - 1}")
            return None

        # Pandas ile tabloyu oku
        df = pd.read_html(str(tables[tablo_index]))[0]

        print(f"\n✓ Tablo {tablo_index} başarıyla çekildi!")
        print(f"  Satır sayısı: {len(df)}")
        print(f"  Sütun sayısı: {len(df.columns)}")
        print(f"\n  Sütunlar: {list(df.columns)}")

        return df

    except requests.exceptions.RequestException as e:
        print(f"Hata: URL'e erişilemedi - {e}")
        return None
    except Exception as e:
        print(f"Hata: {str(e)}")
        return None


def tablo_kaydet(df, dosya_adi, format='csv'):
    """
    DataFrame'i belirtilen formatta kaydeder

    Args:
        df: Pandas DataFrame
        dosya_adi: Kaydedilecek dosya adı (uzantısız)
        format: Dosya formatı ('csv', 'json', 'excel')
    """
    try:
        if format == 'csv':
            df.to_csv(f'{dosya_adi}.csv', index=False, encoding='utf-8-sig')
            print(f"\n✓ CSV dosyası kaydedildi: {dosya_adi}.csv")

        elif format == 'json':
            df.to_json(f'{dosya_adi}.json', orient='records', force_ascii=False, indent=2)
            print(f"\n✓ JSON dosyası kaydedildi: {dosya_adi}.json")

        elif format == 'excel':
            df.to_excel(f'{dosya_adi}.xlsx', index=False, engine='openpyxl')
            print(f"\n✓ Excel dosyası kaydedildi: {dosya_adi}.xlsx")

        else:
            print(f"Hata: Desteklenmeyen format '{format}'")

    except Exception as e:
        print(f"Hata: Dosya kaydedilemedi - {e}")


def tum_tablolari_goster(url):
    """
    Sayfadaki tüm tabloların önizlemesini gösterir
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        tables = soup.find_all('table', {'class': 'wikitable'})

        if not tables:
            tables = soup.find_all('table')

        print(f"\n{'=' * 60}")
        print(f"Toplam {len(tables)} adet tablo bulundu:")
        print(f"{'=' * 60}\n")

        for i, table in enumerate(tables):
            df = pd.read_html(str(table))[0]
            print(f"Tablo {i}:")
            print(f"  Boyut: {df.shape[0]} satır x {df.shape[1]} sütun")
            print(f"  Sütunlar: {list(df.columns)[:5]}{'...' if len(df.columns) > 5 else ''}")
            print(f"  İlk satır: {df.iloc[0].tolist()[:3] if len(df) > 0 else 'Boş'}")
            print()

    except Exception as e:
        print(f"Hata: {str(e)}")


# Komut satırından kullanım
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Kullanım Örnekleri:")
        print("-" * 50)
        print("1. Tüm tabloları listele:")
        print("   python wikipedia_tablo_cek.py <URL> --liste")
        print()
        print("2. Belirli bir tabloyu çek:")
        print("   python wikipedia_tablo_cek.py <URL> [tablo_no] [format]")
        print()
        print("Formatlar: csv, json, excel (varsayılan: csv)")
        print()
        print("Örnek:")
        print("   python wikipedia_tablo_cek.py https://tr.wikipedia.org/wiki/Türkiye 0 csv")
        sys.exit(1)

    url = sys.argv[1]

    # Tüm tabloları listele
    if len(sys.argv) > 2 and sys.argv[2] == '--liste':
        tum_tablolari_goster(url)
    else:
        # Belirli tabloyu çek
        tablo_index = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        format = sys.argv[3] if len(sys.argv) > 3 else 'csv'

        df = wikipedia_tablo_cek(url, tablo_index, format)

        if df is not None:
            # İlk 5 satırı göster
            print("\nİlk 5 satır:")
            print(df.head())

            # Dosyaya kaydet
            tablo_kaydet(df, 'wikipedia_tablo', format)