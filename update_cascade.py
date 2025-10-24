from sqlalchemy import text
from app.database import engine

print("🔄 Updating NULL is_anonymous values to FALSE...")
with engine.connect() as conn:
    conn.execute(text("UPDATE posts SET is_anonymous = FALSE WHERE is_anonymous IS NULL;"))
    conn.commit()

print("🔍 Fetching latest posts to verify...")
with engine.connect() as conn:
    result = conn.execute(text(
        "SELECT id, title, user_id, is_anonymous FROM posts ORDER BY id DESC LIMIT 10;"
    ))
    rows = result.fetchall()
    for row in rows:
        print(row)

print("✨ Update complete!")

