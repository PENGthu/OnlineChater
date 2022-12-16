from flask import Flask, request, render_template, redirect, url_for, session, g
from flask_socketio import emit, join_room, leave_room, SocketIO
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from forms import FormLogin, FormRegister, EnterRoom, PersonalForm, GroupForm, GroupInitForm, AddFriendForm, \
    EnterPersonalChat
from SQLdata import RegisteredUser, ChatLog, ChatRoomList, PersonalChatLog, FriendRelationship, Room_User
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, UserMixin
import config
from flask_bootstrap import Bootstrap
from sqlalchemy import or_

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)
migrate = Migrate(app, db)
bootstrap = Bootstrap(app)
socketio = SocketIO()
socketio.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.login_message = 'Access denied.'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    user = RegisteredUser.query.get(user_id)
    return user


# login_manager配置完成



@app.route('/')
def welcome():
    return render_template('dashboard.html')


# @socketio.on(namespace='/login',message='2')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        form = FormLogin(request.form)
        if form.validate():
            username = form.username.data
            password = form.password.data
            user = RegisteredUser.query.filter_by(username=username).first()
            if not user:
                print("该用户不存在")
                error_type = 1
                return render_template('login.html', error_type=error_type)
            if check_password_hash(user.password, password):
                session['user_id'] = user.id
                session['user_username'] = user.username
                print('成功登入,当前登录用户:' + user.username)
                return redirect("/home")
            else:
                error_type = 2
                print("密码输入错误")
                return render_template('login.html', error_type=error_type)
        else:
            error_type = 3
            return render_template('login.html', error_type=error_type)


@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("login"))


@app.route('/home')
def home():
    if not g.user:
        # ('未登录，返回登录界面')
        return redirect(url_for("login"))
    username_now = session['user_username']
    friends = FriendRelationship.query.filter_by(friend1=username_now)
    rooms = ChatRoomList.query.filter_by()

    rooms_final = ''
    friends_final = ''
    for friend in friends:
        friends_final += '【'
        friends_final += friend.friend2
        friends_final += '】 '
    for room in rooms:
        rooms_final += '【'
        rooms_final += room.roomname
        rooms_final += '：成员数量'
        num = Room_User.query.filter_by(room=room.roomname).count()
        rooms_final += str(num)
        rooms_final += '人,最大成员数量'
        rooms_final += str(room.max_users)
        rooms_final += '人】 '
    return render_template('home.html', username_now=username_now, friends=friends_final, rooms=rooms_final)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        form = FormRegister(request.form)
        if form.validate():
            username = form.username.data
            password = form.password.data
            user = RegisteredUser(username=username, password=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            return redirect("/login")
        else:
            # print(form.errors)
            return render_template("register.html", register_error=1)


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@socketio.on(namespace='/groupchat', message='1')
@app.route('/groupchat', methods=['GET', 'POST'])
def groupchat():
    if not g.user:
        print('未登录，返回登录界面')
        return redirect(url_for("login"))
    username_now = session['user_username']
    datas = Room_User.query.filter_by(room=session.get('room'))
    userlist = ''
    for data in datas:
        userlist += data.user
        userlist += ' 、'
    if request.method == 'GET':
        user_nickname = session.get('user_nickname', '')
        room = session.get('room', '')
        form = GroupForm(request.form)
        groupchat_history = ChatLog.query.filter_by(send_by_chatroom=room).all()
        history_show = '聊天记录:\n'
        for g_his in groupchat_history:
            history_show += '--' + str(g_his.send_time) + '-- ' + g_his.send_by_nickname + ':' + g_his.text + '\n'

        return render_template('groupchat.html', user_nickname=user_nickname, room=room, form=form,
                               history_show=history_show, username_now=username_now, userlist=userlist)
    else:
        user_nickname = session.get('user_nickname', '')
        room = session.get('room', '')
        if user_nickname == '' or room == '':
            return redirect(url_for('home'))
        form = GroupForm(request.form)
        if form.validate():
            print("表单验证成功")
            text = form.text.data
            chatlog = ChatLog(text=text, send_by_user_id=username_now, send_by_chatroom=room,
                              send_by_nickname=user_nickname)
            db.session.add(chatlog)
            db.session.commit()

            groupchat_history = ChatLog.query.filter_by(send_by_chatroom=room).all()
            history_show = '聊天记录:\n'
            for g_his in groupchat_history:
                history_show += '--' + str(g_his.send_time) + '-- ' + g_his.send_by_nickname + ':' + g_his.text + '\n'
            return render_template('groupchat.html', user_nickname=user_nickname, room=room, form=form,
                                   history_show=history_show, username_now=username_now, userlist=userlist)
        else:
            # 说明前面的表单有误
            groupchat_history = ChatLog.query.filter_by(send_by_chatroom=room).all()
            history_show = '聊天记录:\n'
            for g_his in groupchat_history:
                history_show += '--' + str(g_his.send_time) + '-- ' + g_his.send_by_nickname + ':' + g_his.text + '\n'
            return render_template('groupchat.html', user_nickname=user_nickname, room=room, form=form,
                                   history_show=history_show, username_now=username_now, userlist=userlist)


@app.route('/group_init', methods=['GET', 'POST'])
def group_init():
    if not g.user:
        return redirect(url_for("login"))
    if request.method == 'GET':
        return render_template('group_init.html')
    form = GroupInitForm(request.form)
    if form.validate():
        room_name = form.room_name.data
        max_users = form.max_users.data
        room = ChatRoomList(roomname=room_name, max_users=max_users)
        db.session.add(room)
        db.session.commit()
        return redirect("/home")
    return render_template("group_init.html")



@app.route('/personalchat', methods=['GET', 'POST'])
def personalchat():
    if not g.user:
        print('未登录，返回登录界面')
        return redirect(url_for("login"))
    form = PersonalForm(request.form)
    user_nickname = session.get('user_nickname', '')
    receiver = session.get('receiver', '')
    if form.validate():
        text = form.text.data
        personalchatlog = PersonalChatLog(text=text, send_by_user_id=g.user.username, receiver=receiver)

        # print(g.user)
        db.session.add(personalchatlog)
        db.session.commit()
        per_history = PersonalChatLog.query.filter(
            or_(PersonalChatLog.send_by_user_id == receiver, PersonalChatLog.send_by_user_id == g.user.username)
        ).all()
        history_show = '聊天记录:\n'
        for per in per_history:
            history_show += ('--' + str(per.send_time) + '-- ' + per.send_by_user_id + ':' + per.text + '\n')

        return render_template('personalchat.html', form=form, user_nickname=user_nickname, receiver=receiver,
                               history_show=history_show)
    else:
        # print(form.errors)
        per_history = PersonalChatLog.query.filter(
            or_(PersonalChatLog.send_by_user_id == receiver, PersonalChatLog.send_by_user_id == g.user.username)
        ).all()
        history_show = '聊天记录:\n'
        for per in per_history:
            history_show += ('--' + str(per.send_time) + '-- ' + per.send_by_user_id + ':' + per.text + '\n')
        return render_template('personalchat.html', form=form, user_nickname=user_nickname, receiver=receiver,
                               history_show=history_show)


@app.route('/personalchat_exit')
def personalchat_exit():
    if not g.user:
        print('未登录，返回登录界面')
        return redirect(url_for("login"))
    chatlog = PersonalChatLog(text='昵称为"' + session.get('user_nickname') + '"的用户退出了私聊。',
                              send_by_user_id=g.user.username,
                              receiver=session.get('receiver'))
    db.session.add(chatlog)
    db.session.commit()
    return render_template('personalchat_exit.html')


# 一定要记得在render_template里给html文件传参！
@socketio.on
@app.route('/groupchat_enter', methods=['GET', 'POST'])
def groupchat_enter():
    if not g.user:
        # print('未登录，返回登录界面')
        return redirect(url_for(("login")))
    form = EnterRoom(request.form)
    username_now = session['user_username']
    if form.validate():
        session['user_nickname'] = form.user_nickname.data
        session['room'] = form.room.data
        a = ChatRoomList.query.filter_by(roomname=form.room.data).first()
        if a is not None:
            num = Room_User.query.filter_by(room=form.room.data).count()
            room_to_query = ChatRoomList.query.filter_by(roomname=form.room.data).first()
            limit = room_to_query.max_users
            if Room_User.query.filter(Room_User.user == g.user.username,
                                      Room_User.room == form.room.data).first() is None:
                if num < limit:
                    chatlog = ChatLog(text='昵称为"' + session.get('user_nickname') + '"的用户进入了房间。',
                                      send_by_user_id=username_now,
                                      send_by_chatroom=session.get('room'),
                                      send_by_nickname=session.get('user_nickname'))
                    db.session.add(chatlog)
                    room_user = Room_User(user=g.user.username, room=form.room.data)

                    db.session.add(room_user)
                    db.session.commit()
                    return redirect(url_for('groupchat'))
                else:
                    return render_template('groupchat_enter.html', errorcode=2, form=form, username_now=username_now)
            else:
                chatlog = ChatLog(text='昵称为"' + session.get('user_nickname') + '"的用户进入了房间。',
                                  send_by_user_id=username_now,
                                  send_by_chatroom=session.get('room'),
                                  send_by_nickname=session.get('user_nickname'))
                db.session.add(chatlog)
                db.session.commit()
                return redirect(url_for('groupchat'))
        else:
            return render_template('groupchat_enter.html', errorcode=1, form=form, username_now=username_now)

    return render_template('groupchat_enter.html', form=form, username_now=username_now)


@app.route('/personalchat_enter', methods=['GET', 'POST'])
def personalchat_enter():
    if not g.user:
        return redirect(url_for("login"))
    form = EnterPersonalChat(request.form)
    if form.validate():
        session['user_nickname'] = form.user_nickname.data
        session['receiver'] = form.friend.data

        chatlog = PersonalChatLog(text='昵称为"' + session.get('user_nickname') + '"的用户进入了私聊。',
                                  send_by_user_id=g.user.username, receiver=form.friend.data)
        check_relation = FriendRelationship.query.filter_by(friend1=g.user.username, friend2=form.friend.data).first()
        if check_relation:
            db.session.add(chatlog)
            db.session.commit()
            return redirect(url_for('personalchat'))
        else:
            return render_template('personalchat_enter.html', form=form, errorcode=1)
    return render_template('personalchat_enter.html', form=form)


@app.route('/add_friend', methods=['GET', 'POST'])
def add_friend():
    if not g.user:
        return redirect(url_for("login"))
    if request.method == 'GET':
        return render_template('add_friend.html')
    form = AddFriendForm(request.form)
    if form.validate():
        friend1 = form.friend_name.data
        friend2 = g.user.username
        relation1 = FriendRelationship(friend1=friend1, friend2=friend2)
        db.session.add(relation1)
        relation2 = FriendRelationship(friend1=friend2, friend2=friend1)
        db.session.add(relation2)
        db.session.commit()

    return render_template('add_friend.html')

@app.before_request
def request_before():
    user_id = session.get("user_id")
    if user_id:
        user = RegisteredUser.query.get(user_id)
        setattr(g, "user", user)
    else:
        setattr(g, "user", None)

@app.route('/savelog')
def savelog():
    log1 = ChatLog.query.all()
    data = '-------下面是群聊的聊天记录-------\n'
    for log in log1:
        data += '聊天室:' + log.send_by_chatroom + ' 时间:' + str(log.send_time) + \
                ' 用户名:' + log.send_by_user_id + '(昵称)' + log.send_by_nickname + ' 内容:' + log.text + '\n'
    log2=PersonalChatLog.query.all()
    data+='-------下面是私聊的聊天记录-------\n'
    for log in log2:
        data+='时间:' + str(log.send_time)+' 发送人:'+log.send_by_user_id+' 接收人:'+log.receiver+' 内容:'+log.text+'\n'
    file = open('log.txt', 'w', encoding="utf-8")
    file.write(data)
    return render_template('savelog.html')


@app.route('/groupchat_exit')
def groupchat_exit():
    chatlog = ChatLog(text='昵称为"' + session.get('user_nickname') + '"的用户退出了房间。',
                      send_by_user_id=g.user.username,
                      send_by_chatroom=session.get('room'),
                      send_by_nickname=session.get('user_nickname'))
    db.session.add(chatlog)
    db.session.commit()
    return render_template('groupchat_exit.html')


@app.context_processor
def processor_context():
    return {"user": g.user}


# 下面是socketio的配置

@socketio.on('joined', namespace='/groupchat')
def joined(message):
    room = session.get('room')
    join_room(room)
    username_now = g.user.username

    # emit('status', {'msg': session.get('user_nickname') + '进入了房间。'}, room=room)
    chatlog = ChatLog(text=session.get('user_nickname') + '进入了房间。', send_by_user_id=username_now,
                      send_by_chatroom=room,
                      send_by_nickname=session.get('user_nickname'))
    db.session.add(chatlog)
    db.session.commit()


@socketio.on('text', namespace='/groupchat')
def text(message):
    room = session.get('room')
    emit('message', {'msg': session.get('user_nickname') + ':' + message['msg']}, room=room)


@socketio.on('left', namespace='/groupchat')
def left(message):
    room = session.get('room')
    leave_room(room)
    emit('status', {'msg': session.get('user_nickname') + '退出了房间。'}, room=room)


if __name__ == '__main__':
    socketio.run(app, allow_unsafe_werkzeug=True, port=5001,host='127.0.1.3')
