from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base

from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    games = relationship("UserInGame", back_populates="user")


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    users = relationship("UserInGame", back_populates="game", cascade="all, delete-orphan")


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    user_in_games = relationship("UserInGame", back_populates="role")


class UserInGame(Base):
    __tablename__ = "user_in_games"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="games")
    game = relationship("Game", back_populates="users")
    role = relationship("Role", back_populates="user_in_games", uselist=False)
