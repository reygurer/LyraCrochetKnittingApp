"""
Etsy'den yeni bir sipariş geldiğinde çalıştır — alıcının email'ini o
pattern için yetkilendirir.

Bu kayıt olmadan, doğru access_key girilse bile pattern açılmaz
(bkz. views/patterns.py — Verify artık hem doğru key hem de burada
bir yetki kaydı istiyor).

Kullanım:
    python3 add_order.py <pattern-slug> <alici@email.com>

Pattern'in slug'ını seed_demo.py'deki gibi Pattern satırından görebilirsin.
"""
import sys

from sqlalchemy.exc import IntegrityError

from models import SessionLocal, Pattern, PurchaseAuthorization, init_db


def main():
    if len(sys.argv) != 3:
        print("Kullanım: python3 add_order.py <pattern-slug> <alici@email.com>")
        sys.exit(1)

    slug, email = sys.argv[1], sys.argv[2].strip().lower()

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

    try:
        session.add(PurchaseAuthorization(email=email, pattern_id=pattern.id))
        session.commit()
        print(f"Kaydedildi: {email} artık '{pattern.name}' için access_key girip açabilir.")
    except IntegrityError:
        session.rollback()
        print(f"{email} zaten '{pattern.name}' için yetkiliydi, tekrar eklemeye gerek yok.")

    session.close()


if __name__ == "__main__":
    main()
