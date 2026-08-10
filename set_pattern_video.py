"""
Var olan bir pattern'e video linki bağlar (veya değiştirir).

Video, YouTube/Vimeo'da "unlisted" (liste dışı/gizli link) olarak
yüklenmiş bir link olabilir, ya da doğrudan bir video dosyası URL'i.
Streamlit bunu pattern'in "form" adımında otomatik gömüp oynatıyor
(bkz. views/patterns.py) — o adım zaten sadece pattern açıldıktan
sonra erişilebiliyor, o yüzden video da satın alma arkasında kalıyor.

Kullanım:
    python3 set_pattern_video.py <pattern-slug> <video-url>

Bir pattern'in videosunu kaldırmak istersen:
    python3 set_pattern_video.py <pattern-slug> ""
"""
import sys

from models import SessionLocal, Pattern, init_db


def main():
    if len(sys.argv) != 3:
        print("Kullanım: python3 set_pattern_video.py <pattern-slug> <video-url>")
        sys.exit(1)

    slug, video_url = sys.argv[1], sys.argv[2].strip()

    init_db()
    session = SessionLocal()

    pattern = session.query(Pattern).filter_by(slug=slug).first()
    if not pattern:
        print(f"'{slug}' slug'lı bir pattern bulunamadı.")
        available = [p.slug for p in session.query(Pattern).all()]
        if available:
            print("Mevcut slug'lar:", ", ".join(available))
        session.close()
        sys.exit(1)

    pattern.video_url = video_url or None
    session.commit()

    if video_url:
        print(f"'{pattern.name}' için video bağlandı: {video_url}")
    else:
        print(f"'{pattern.name}' için video kaldırıldı.")

    session.close()


if __name__ == "__main__":
    main()
