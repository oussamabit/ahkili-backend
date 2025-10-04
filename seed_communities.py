from app.database import SessionLocal
from app.models import Community
from app import crud

db = SessionLocal()

# Get or create a default user
user = db.query(crud.models.User).first()
if not user:
    print("❌ No users found. Please create a user first!")
    exit()

communities_data = [
    {
        "name": "Anxiety Support",
        "description": "A safe space for people dealing with anxiety. Share experiences, coping strategies, and support each other."
    },
    {
        "name": "Depression Support",
        "description": "Connect with others who understand depression. You are not alone in this journey."
    },
    {
        "name": "Mindfulness & Meditation",
        "description": "Practice mindfulness together. Share meditation techniques and peaceful living tips."
    },
    {
        "name": "PTSD Recovery",
        "description": "Support group for PTSD survivors. A judgment-free zone for healing and recovery."
    },
    {
        "name": "Self-Care & Wellness",
        "description": "Focus on self-care routines, healthy habits, and overall mental wellness."
    },
    {
        "name": "Stress Management",
        "description": "Learn and share stress management techniques. Build resilience together."
    },
]

for comm_data in communities_data:
    # Check if community already exists
    existing = db.query(Community).filter(Community.name == comm_data["name"]).first()
    if not existing:
        community = Community(
            name=comm_data["name"],
            description=comm_data["description"],
            created_by=user.id
        )
        db.add(community)
        print(f"✅ Created community: {comm_data['name']}")
    else:
        print(f"⏭️  Community already exists: {comm_data['name']}")

db.commit()
db.close()
print("\n✅ Communities seeded successfully!")