from datetime import datetime
from extensions import db


class RegisteredUser(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(1000), nullable=False)
    register_time = db.Column(db.DateTime, default=datetime.now)


class ChatLog(db.Model):
    __tablename__ = 'chatlog'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    # send_by_user_id = db.Column(db.String(100), db.ForeignKey("user.id"), nullable=False)# 外键
    send_by_user_id = db.Column(db.String(100), nullable=False)
    send_by_nickname = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    send_time = db.Column(db.DateTime, default=datetime.now)
    send_by_chatroom = db.Column(db.String(100), nullable=False)


class ChatRoomList(db.Model):
    __tablename__ = 'chatroom'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    roomname = db.Column(db.String(100), nullable=False)
    max_users = db.Column(db.Integer, nullable=False)


class PersonalChatLog(db.Model):
    __tablename__ = 'personalchatlog'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    # send_by_user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)  # 外键
    send_by_user_id = db.Column(db.String(100), nullable=False)
    receiver=db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    send_time = db.Column(db.DateTime, default=datetime.now)


class FriendRelationship(db.Model):
    __tablename__ = 'friendrelationship'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    friend1 = db.Column(db.String(100), nullable=False)
    friend2 = db.Column(db.String(100), nullable=False)


class Room_User(db.Model):
    __tablename__ = 'room-user'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user=db.Column(db.String(100), nullable=False)
    room=db.Column(db.String(100), nullable=False)
