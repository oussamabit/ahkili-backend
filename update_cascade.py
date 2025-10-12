from app.database import engine
from sqlalchemy import text

# Connect to the Railway PostgreSQL database
with engine.connect() as conn:
    # Check if the column exists first (safe migration)
    result = conn.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='comments' AND column_name='parent_id';
    """))
    
    if result.fetchone() is None:
        print("🧱 Column 'parent_id' missing — adding it now...")
        conn.execute(text("""
            ALTER TABLE comments
            ADD COLUMN parent_id INTEGER REFERENCES comments(id) ON DELETE CASCADE;
        """))
        conn.commit()
        print("✅ Column 'parent_id' added successfully with CASCADE!")
    else:
        print("⚠️ Column 'parent_id' already exists — no action taken.")

print("🏁 Database update completed.")
