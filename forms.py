import wtforms
from wtforms.validators import Length, EqualTo, DataRequired



class FormRegister(wtforms.Form):
    username = wtforms.StringField(validators=[Length(min=2, max=10, message='用户名长度有误')])
    password = wtforms.StringField(validators=[Length(min=6, max=10, message='密码长度有误')])
    password_2 = wtforms.StringField(validators=[EqualTo("password", message='用户两次输入密码不一致')])


class FormLogin(wtforms.Form):
    username = wtforms.StringField(validators=[Length(min=2, max=10, message='用户名长度有误')])
    password = wtforms.StringField(validators=[Length(min=6, max=10, message='密码长度有误')])


class EnterRoom(wtforms.Form):
    user_nickname = wtforms.StringField('您想使用的昵称', validators=[DataRequired()])
    room = wtforms.StringField('聊天室编号', validators=[DataRequired()])
    submit = wtforms.SubmitField('进入聊天室')


class PersonalForm(wtforms.Form):
    text = wtforms.StringField('在这里输入你的聊天内容',validators=[DataRequired()])
    submit = wtforms.SubmitField('发送!')


class GroupForm(wtforms.Form):
    text = wtforms.StringField('在这里输入你的聊天内容',validators=[DataRequired()])
    submit = wtforms.SubmitField('发送!')


class GroupInitForm(wtforms.Form):
    room_name = wtforms.StringField('期望创建的聊天室名称', validators=[DataRequired()])
    max_users = wtforms.IntegerField('最大用户数量', validators=[DataRequired()])


class AddFriendForm(wtforms.Form):
    # 假定好友为双向关系
    friend_name = wtforms.StringField(validators=[DataRequired()])


class EnterPersonalChat(wtforms.Form):
    user_nickname = wtforms.StringField('您想使用的昵称', validators=[DataRequired()])
    friend = wtforms.StringField('私聊对象(必须在您的好友列表中)', validators=[DataRequired()])
    submit = wtforms.SubmitField('进入私聊')
