from sqlalchemy import text
from app.database import engine

print("🔄 Updating ...")
with engine.connect() as conn:
    conn.execute(text("ALTER TABLE posts ADD COLUMN video_url VARCHAR;"))
    conn.commit()

print("✨ Update complete!")

