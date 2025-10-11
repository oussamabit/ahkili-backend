from app.database import engine
from sqlalchemy import text

# Drop and recreate tables with proper cascade
with engine.connect() as conn:
    # Backup data first (optional but recommended)
    
    # Drop constraints
    conn.execute(text("ALTER TABLE comments DROP CONSTRAINT IF EXISTS comments_post_id_fkey"))
    conn.execute(text("ALTER TABLE post_reactions DROP CONSTRAINT IF EXISTS post_reactions_post_id_fkey"))
    
    # Recreate with CASCADE
    conn.execute(text("ALTER TABLE comments ADD CONSTRAINT comments_post_id_fkey FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE"))
    conn.execute(text("ALTER TABLE post_reactions ADD CONSTRAINT post_reactions_post_id_fkey FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE"))
    
    conn.commit()
    
print("✅ Database updated with CASCADE constraints!")