from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    # === Create doctor_verifications table ===
    result = conn.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_name = 'doctor_verifications';
    """))
    
    if result.fetchone() is None:
        print("🧱 Table 'doctor_verifications' missing — creating it now...")
        conn.execute(text("""
            CREATE TABLE doctor_verifications (
                id SERIAL PRIMARY KEY,
                user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
                full_name VARCHAR(100) NOT NULL,
                specialization VARCHAR(100) NOT NULL,
                license_number VARCHAR(50) NOT NULL,
                license_document_url TEXT,
                clinic_address TEXT,
                phone_number VARCHAR(20),
                bio TEXT,
                status VARCHAR(20) DEFAULT 'pending',
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
                reviewed_at TIMESTAMP,
                rejection_reason TEXT
            );
        """))
        conn.commit()
        print("✅ Table 'doctor_verifications' created successfully!")
    else:
        print("⚠️ Table 'doctor_verifications' already exists — no action taken.")


    # === Create community_moderators table ===
    result = conn.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_name = 'community_moderators';
    """))
    
    if result.fetchone() is None:
        print("🧱 Table 'community_moderators' missing — creating it now...")
        conn.execute(text("""
            CREATE TABLE community_moderators (
                id SERIAL PRIMARY KEY,
                community_id INTEGER REFERENCES communities(id) ON DELETE CASCADE,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                assigned_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
                assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                permissions VARCHAR(100) DEFAULT 'moderate_posts,delete_comments',
                CONSTRAINT unique_community_moderator UNIQUE (community_id, user_id)
            );
        """))
        conn.commit()
        print("✅ Table 'community_moderators' created successfully!")
    else:
        print("⚠️ Table 'community_moderators' already exists — no action taken.")

print("🏁 Database update completed successfully!")

