"""Idempotent demo data seeder — safe to run on every container start."""
from app.auth import hash_password
from app.database import SessionLocal
from app.embeddings import chunk_text, embed_texts
from app.models import Organization, User, Document, DocumentChunk, Role

SAMPLE_DOCS = [
    (
        "Shipping & Returns FAQ",
        "Orders ship within 2 business days. Standard shipping takes 5-7 business "
        "days; express shipping takes 1-2 business days. You can return any item "
        "within 30 days of delivery for a full refund, as long as it is unused and "
        "in its original packaging. To start a return, go to Orders > Return Item "
        "in your account, or contact support with your order number. Refunds are "
        "issued to the original payment method within 5-10 business days after we "
        "receive the returned item.",
    ),
    (
        "Billing & Subscription FAQ",
        "Subscriptions renew automatically each month on the date you first "
        "subscribed. You can cancel anytime from Account > Billing > Cancel "
        "Subscription; cancelling stops future charges but does not refund the "
        "current billing period. We accept Visa, Mastercard, Amex, and PayPal. "
        "If a payment fails, we retry it three times over five days before "
        "pausing your account. You can update your card at Account > Billing > "
        "Payment Methods.",
    ),
]


def seed():
    db = SessionLocal()
    try:
        org = db.query(Organization).filter(Organization.slug == "acme").first()
        if not org:
            org = Organization(name="Acme Inc", slug="acme")
            db.add(org)
            db.flush()

            db.add(
                User(
                    organization_id=org.id,
                    email="admin@acme.com",
                    full_name="Ava Admin",
                    hashed_password=hash_password("password123"),
                    role=Role.owner,
                )
            )
            db.add(
                User(
                    organization_id=org.id,
                    email="agent@acme.com",
                    full_name="Alex Agent",
                    hashed_password=hash_password("password123"),
                    role=Role.agent,
                )
            )
            db.flush()

            for title, content in SAMPLE_DOCS:
                doc = Document(organization_id=org.id, title=title, source_type="faq")
                db.add(doc)
                db.flush()

                pieces = chunk_text(content)
                vectors = embed_texts(pieces)
                for idx, (piece, vector) in enumerate(zip(pieces, vectors)):
                    db.add(
                        DocumentChunk(
                            document_id=doc.id,
                            organization_id=org.id,
                            content=piece,
                            chunk_index=idx,
                            embedding=vector,
                        )
                    )

            db.commit()
            print("Seeded demo org 'acme' with admin/agent users and 2 FAQ documents.")
        else:
            print("Demo org 'acme' already exists — skipping seed.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
