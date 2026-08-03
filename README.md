# Kişiselleştirilmiş Örgü/Tığ Deseni Uygulaması

## Kurulum
    pip install -r requirements.txt

## Yerel test (SQLite ile, DATABASE_URL vermeye gerek yok)
    python seed_demo.py      # demo pattern'i ekler
    streamlit run app.py

## Canlıya alma (PostgreSQL ile)
    export DATABASE_URL=postgresql://kullanici:sifre@host:5432/veritabani
    python seed_demo.py
    streamlit run app.py

## Yeni pattern eklemek
`seed_demo.py`'deki gibi bir `Pattern` satırı oluşturup DB'ye ekle — arayüz
kodunda hiçbir değişiklik gerekmez. Alan/formül formatı için
`pattern-veri-sablonu.md` dosyasına bak.

## Dosyalar
- `models.py`         — veritabanı şeması (patterns, unlocks tablosu)
- `formula_engine.py` — swatch/ölçü → dikiş/sıra hesaplama motoru
- `excel_export.py`   — canlı formüllü, iki sayfalı (Girdiler/Sonuçlar) Excel üretimi
- `app.py`             — Streamlit arayüzü
- `seed_demo.py`       — test amaçlı örnek pattern ekleme scripti

## Etsy alıcılarına dağıtım (hosted model)

Bu uygulama, Etsy'den pattern satıp tek bir uygulama üzerinden herkese
ulaştırmak için **hosted (bulutta barındırılan) bir web app** olarak
çalışacak şekilde tasarlandı — alıcı hiçbir şey kurmuyor, tarayıcıdan bir
linke giriyor.

**Neden hosted:**
- Sen kodu/pattern'i güncelledikçe **herkes anında** güncel halini görür —
  ayrı bir "auto-update" mekanizması kurmana gerek yok.
- Pattern verisi (formüller, talimatlar) hiçbir zaman alıcının cihazına
  inmez, sadece hesaplanan sonuçlar gösterilir — bu yüzden şifrelemeye
  gerek yok.
- Aynı alıcı birden fazla pattern alırsa, hepsine aynı uygulama +
  hesabından erişir; ayrı kurulum gerekmez.

**Nasıl kilit açılıyor:**
- Alıcı e-postasını girer (şifre yok — sadece kimlik/hafıza amaçlı).
- Her `Pattern` satırının kendi `access_key`'i var (Etsy siparişiyle
  birlikte gönderdiğin kod). Doğru key girildiğinde bir `Unlock` satırı
  (email + pattern_id) veritabanına yazılır.
- Bir sonraki ziyarette (başka bir cihazdan bile) aynı e-postayla giriş
  yapınca, önceden açılmış tüm pattern'ler otomatik görünür — tek tek
  tekrar key girmeye gerek yok.
- Link `?email=...` parametresiyle işaretlenir, böylece alıcı sayfayı
  yer imlerine eklerse bir dahaki sefere e-posta girmeden de devam eder.

**Barındırma (senin yapman gerekenler):**
1. Kalıcı bir Postgres veritabanı aç (Render, Railway, Neon gibi
   servislerin ücretsiz/düşük maliyetli planları var) ve `DATABASE_URL`
   ortam değişkenini o bağlantıya ayarla — SQLite'ta bırakırsan her
   deploy'da veritabanı sıfırlanabilir.
2. Uygulamayı Render/Railway/Streamlit Community Cloud gibi bir servise
   deploy et (`streamlit run streamlit_app.py` komutunu çalıştıracak
   şekilde).
3. `python3 seed_demo.py` yerine gerçek pattern'lerini aynı şekilde bir
   script ile veya küçük bir admin arayüzüyle veritabanına ekle.
4. Alıcıya gönderdiğin Etsy dijital indirmesinde, kurulacak bir dosya
   değil, uygulamanın linki + o pattern'e özel `access_key` olsun.
