from sqlalchemy import text
from app.database import engine

print("🔄 Creating community_members table...")

sql_script = """
-- ============= COMMUNITY MEMBERS TABLE =============
CREATE TABLE IF NOT EXISTS community_members (
    id SERIAL PRIMARY KEY,
    community_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (community_id) REFERENCES communities(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT unique_community_member UNIQUE(community_id, user_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_community_members_community_id ON community_members(community_id);
CREATE INDEX IF NOT EXISTS idx_community_members_user_id ON community_members(user_id);
CREATE INDEX IF NOT EXISTS idx_community_members_composite ON community_members(community_id, user_id);
"""

try:
    with engine.connect() as conn:
        # Split the script and execute each statement
        for statement in sql_script.split(";"):
            stmt = statement.strip()
            if stmt:
                conn.execute(text(stmt))
        conn.commit()
    print("✅ community_members table created successfully!")
    
except Exception as e:
    print(f"❌ Error creating community_members table: {e}")