"""
Komut satırından kullanım için modül
"""
import sys
from .wikipedia_tablo_cek import wikipedia_tablo_cek, tablo_kaydet, tum_tablolari_goster


def main():
    if len(sys.argv) < 2:
        print("Kullanım Örnekleri:")
        print("-" * 50)
        print("1. Tüm tabloları listele:")
        print("   python -m wikipedia_tablo_cekici <URL> --liste")
        print()
        print("2. Belirli bir tabloyu çek:")
        print("   python -m wikipedia_tablo_cekici <URL> [tablo_no] [format]")
        print()
        print("Formatlar: csv, json, excel (varsayılan: csv)")
        print()
        print("Örnek:")
        print("   python -m wikipedia_tablo_cekici https://tr.wikipedia.org/wiki/Türkiye 0 csv")
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


if __name__ == "__main__":
    main()