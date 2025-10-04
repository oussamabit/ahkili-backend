from app.database import SessionLocal
from app.models import User, Community, Post
from datetime import datetime

db = SessionLocal()

# Create test user
user = User(
    firebase_uid="test_user_123",
    username="test_user",
    email="test@example.com"
)
db.add(user)
db.commit()

# Create communities
communities = [
    Community(name="Anxiety Support", description="Support for anxiety", created_by=user.id),
    Community(name="Depression Support", description="Support for depression", created_by=user.id),
    Community(name="Mindfulness", description="Meditation and mindfulness", created_by=user.id),
]

for community in communities:
    db.add(community)
db.commit()

# Create some posts
posts = [
    Post(
        title="Welcome to Ahkili",
        content="This is a safe space for mental health support. Feel free to share your thoughts and experiences.",
        user_id=user.id,
        community_id=communities[0].id
    ),
    Post(
        title="Small victories",
        content="Today I managed to get out of bed and take a shower. It might seem small but it's a big step for me.",
        user_id=user.id,
        community_id=communities[0].id
    ),
]

for post in posts:
    db.add(post)
db.commit()

print("✅ Seed data created successfully!")
db.close()