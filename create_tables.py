from database import Base, engine
from models import User, Game, Role, UserInGame

# This will create all tables that inherit from Base
Base.metadata.create_all(bind=engine)

print("Tables created!")
