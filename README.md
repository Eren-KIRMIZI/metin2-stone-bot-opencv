# Metin2 Bot - Python OpenCV Template Matching

Bu proje, Python ve OpenCV kullanarak Metin2 oyununda otomatik taş (metin) tespit ve saldırı işlemi gerçekleştiren bir bot denemesidir.

---

## Uyari

Bu bot ve benzeri otomasyon araclari oyun kurallarina aykiridir. Kullanimi hesabinizin kalici olarak banlanmasina yol acabilir. Proje yalnizca egitim ve arastirma amacli gelistirilmistir. Cok sayida eksigi ve hatasi vardir, production ortaminda kullanilmasi onerilmez. Kullanimdan dogan her turlu sorumluluk kullaniciya aittir.

---

https://github.com/user-attachments/assets/825f6ecd-838e-488a-8376-0d9873bf9e69

## Gereksinimler

- Python 3.11
- Windows 10/11

### Kutuphaneler
```
pip install opencv-python numpy pywin32 mss pynput keyboard
```

---

## Dosya Yapisi
```
jak/
├── main.py
├── windowcapture.py
├── char.jpg
├── metin.JPG
├── headers.txt
└── stones.txt
```

---

## Dosyalarin Hazirlanmasi

### char.jpg

Karakterinizin uzerindeki isim etiketinin ekran goruntusunu alin. Oyun acikken Windows Ekran Alintisi Araci (Win + Shift + S) ile karakterinizin isminin oldugu alani kucuk bir dikdortgen olarak kirpin ve `char.jpg` olarak kaydedin.

Ornek: Karakter isminiz `oloOErenOolo` ise bu ismin ekranda gorunduğu kismi kirpin.

### metin.JPG

Oyunda bir Savas Metini tasinin yaninda dururken, tasin uzerinde cikan `Savas Metini` yazi etiketini kirpin ve `metin.JPG` olarak kaydedin. Yazinin etrafinda cok fazla bosluk birakmamaya calisin.

### headers.txt

Oyun penceresinin baslik cubugu yazisini bu dosyaya yazin. Her satira bir baslik gelin.

Ornek:
```
www.saltanatmt2.com.tr
```

Pencere basligini bulmak icin su scripti calistirabilirsiniz:
```python
import win32gui

def listWindows():
    def handler(hwnd, ctx):
        if win32gui.IsWindowVisible(hwnd):
            print(win32gui.GetWindowText(hwnd))
    win32gui.EnumWindows(handler, None)

listWindows()
```

### stones.txt

Aramak istediginiz tas gorsel dosyasinin adini yazin. Her satira bir dosya adi.

Ornek:
```
metin.JPG
```

---

## Calistirma

Botu yonetici yetkisiyle calistirmaniz gerekmektedir. Aksi halde fare tiklamalari oyuna ulasmayabilir.

1. Baslat menusu arama cubuguna `cmd` yazin
2. Komut Istemi uzerine sag tiklayin, `Yonetici olarak calistir` secin
3. Asagidaki komutlari calistirin:
```
cd C:\Users\KullaniciAdi\Desktop\jak
python main.py
```

4. Bot basladiktan sonra oyun penceresine gecin
5. Bot otomatik olarak tasi arayip saldiracaktir

---

## Kontroller

| Tus | Islem |
|-----|-------|
| F12 | Botu duraklat / devam ettir |
| END | Botu tamamen kapat |

---

## Nasil Calisir

1. Bot baslarken `headers.txt` dosyasindaki pencere adlarini tek tek dener, oyun penceresini bulur
2. `stones.txt` dosyasindaki gorsel dosyalarini tarayarak ekranda eslesen tasi arar
3. Tas bulunursa en yakin tasa saldirmaya baslar
4. Tas vurulup kayboldugunda kilitli koordinata vurmaya devam eder, bir sure sonra yeni tas arar
5. Etrafta hic tas yoksa WASD tuslariyla gezinir ve kamerayi dondurup yeni tas arar

---

## Bilinen Eksikler ve Sorunlar

- Template matching yontemi kullandigi icin ayni tasin farkli acilarda veya mesafelerde gorunumunu taniyamazsa basarisiz olabilir
- Kamera acisi degistiginde tasin gorunumu degistigi icin tespit kaybedilebilir
- Baska oyuncular veya objeler tasin onunu kapatirsa bot kaybeder
- Harita sinirlarini tanimaz, sinira sikilabilir
- VSCode terminali yerine yonetici CMD kullanilmalidir, aksi halde fare inputlari engellenir
- Oyunun pencere modu ve tam ekran arasinda koordinat farkliliklari olusabilir
- Anti-cheat sistemleri botu tespit edebilir

---

## Teknik Detaylar

- Ekran goruntuleri `mss` kutuphanesi ile alinir, oyun arka planda olsa bile calisir
- Fare tiklamalari Windows `SendInput` API'si ile gonderilir
- Klavye dinleme `pynput` ile global olarak yapilir, oyun on planda olsa bile F12/END calisir
- Pencere koordinatlari `ClientToScreen` ile dogru hesaplanir, pencere modu ve tam ekranda otomatik guncellenir
- Template matching icin `cv2.TM_CCOEFF_NORMED` yontemi kullanilir, esik degeri 0.50
