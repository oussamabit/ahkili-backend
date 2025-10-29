from sqlalchemy import text
from app.database import engine

print("🔄 Adding new columns to 'users' table...")

sql_script = """
-- ============= ALTER USERS TABLE =============
ALTER TABLE users ADD COLUMN IF NOT EXISTS bio TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS location VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_picture_url VARCHAR(500);
"""

try:
    with engine.connect() as conn:
        # Split and execute each SQL statement separately
        for statement in sql_script.split(";"):
            stmt = statement.strip()
            if stmt:
                conn.execute(text(stmt))
                conn.commit()
                print("✅ Columns added successfully to 'users' table!")

except Exception as e:
    print(f"❌ Error updating 'users' table: {e}")