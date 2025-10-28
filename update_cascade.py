from sqlalchemy import text
from app.database import engine

print("🔄 Creating notification-related tables...")

sql_script = """
-- ============= NOTIFICATION PREFERENCES TABLE =============
CREATE TABLE notification_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE,
    email_notifications BOOLEAN DEFAULT TRUE,
    push_notifications BOOLEAN DEFAULT FALSE,
    comment_reactions BOOLEAN DEFAULT TRUE,
    comment_replies BOOLEAN DEFAULT TRUE,
    post_reactions BOOLEAN DEFAULT TRUE,
    new_posts BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_notification_preferences_user_id ON notification_preferences(user_id);

-- ============= NOTIFICATIONS TABLE =============
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    target_type VARCHAR(20),
    target_id INTEGER,
    actor_id INTEGER,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (actor_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);
CREATE INDEX idx_notifications_created_at ON notifications(created_at DESC);
CREATE INDEX idx_notifications_user_read ON notifications(user_id, is_read);

-- ============= COMMUNITY FOLLOWERS TABLE =============
CREATE TABLE community_followers (
    id SERIAL PRIMARY KEY,
    community_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    followed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (community_id) REFERENCES communities(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT unique_community_follower UNIQUE(community_id, user_id)
);

CREATE INDEX idx_community_followers_community_id ON community_followers(community_id);
CREATE INDEX idx_community_followers_user_id ON community_followers(user_id);
CREATE INDEX idx_community_followers_composite ON community_followers(community_id, user_id);
"""

with engine.connect() as conn:
    for statement in sql_script.split(";"):
        stmt = statement.strip()
        if stmt:
            conn.execute(text(stmt))
    conn.commit()

print("✅ All notification tables created successfully!")


