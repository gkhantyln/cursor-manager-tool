
# Cursor Manager

Cursor Manager, kullanıcıların çeşitli ID'leri değiştirmelerini sağlayan ve güncelleme engelleme/aktif etme işlemleriyle ilgili işlem geçmişi tutan bir masaüstü uygulamasıdır. Uygulama, PySide6 ile geliştirilmiştir ve SQLite veritabanını kullanarak işlem geçmişini kaydeder.

## Özellikler

- **Güncelleme Engelleme ve Aktif Etme:** Uygulama, Cursor güncellemelerini engellemeyi veya tekrar aktifleştirmeyi sağlar. Bu işlem, kullanıcı tarafından başlatıldığında işlem durumu ekranda gösterilir.
- **ID Değiştirme:** Kullanıcılar, çeşitli benzersiz kimlikler (machine ID, mac machine ID, device ID, sqm ID) oluşturabilir. Bu işlemler SQLite veritabanına kaydedilir.
- **İşlem Geçmişi:** Son yapılan işlem ve zaman bilgisi, ekranda kırmızı renk ile gösterilir. ID değişiklikleri ve güncelleme engelleme/aktif etme işlemleri geçmişteki işlemler olarak görüntülenebilir.

## Kullanıcı Arayüzü

Uygulama, kullanıcı dostu bir arayüze sahiptir ve iki ana sekmeye ayrılmıştır:

1. **Güncelleme Kontrolü:** Burada, kullanıcılar güncellemeleri engelleyebilir veya aktifleştirebilir. Son işlem durumu burada görüntülenir.
2. **ID Değiştirme:** Bu sekmede, kullanıcılar rastgele kimlikler oluşturabilir ve daha önce oluşturulan kimlikler gösterilebilir.

## Gereksinimler - Kütüphaneler

- Python 3.x
- PySide6
- SQLite3
- Plyer (Masaüstü bildirimleri için)

## Kurulum

1. Bu repo'yu bilgisayarınıza klonlayın:
   ```bash
   git clone https://github.com/gkhantyln/cursor-manager-tool.git

2. `CursorManager.py` dosyasını çalıştırarak uygulamayı başlatabilirsiniz.

### Katkıda Bulunma
Bu projeye katkıda bulunmak için bir pull request gönderebilir veya sorun bildirebilirsiniz. Yardımcı olmak isterseniz, kodunuzu göndermek için bir issue açın.

### Lisans
Bu proje MIT Lisansı altında lisanslanmıştır.
