pip install wikipedia-tablo-cekici 
Yukarıdakini Kopyalayın ve kurun 
Basit Kullanım için aşağıdakini yapın
#Aşağıdakini kopyalayın ve aşağıdaki kodu girip çalıştırın veriyi csv formatında kaydedecektir.
from wikipedia_tablo_cekici import wikipedia_tablo_cek, tablo_kaydet
url = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)"
df = wikipedia_tablo_cek(url, tablo_index=0)
tablo_kaydet(df, 'veriler', 'csv')

