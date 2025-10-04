from app.database import engine, Base
from app.models import User, Community, Post, Comment, Hotline

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Database tables created successfully!")