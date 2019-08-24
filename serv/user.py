import os
from uuid import uuid4

import requests
from bson import ObjectId
from flask import Blueprint, render_template, request, redirect,jsonify
from wtforms import Form
from wtforms.fields import simple
from wtforms import validators
from wtforms import widgets

from settings import MongoDB, REG_PATH, RET, TL_DATA, TL, CHAT_PATH, VOICE, AUDIO_CLIENT

user = Blueprint('users', __name__, template_folder='templates')


# 相当于django中的form组件，用于进行表单和数据验证
class LoginForm(Form):
    # 字段（内部包含正则表达式）
    name = simple.StringField(
        label='用户名',
        validators=[
            # 内部校验器
            validators.DataRequired(message='用户名不能为空.'),
            validators.Length(min=2, max=18, message='用户名长度必须大于%(min)d且小于%(max)d')
        ],
        # 页面的显示插件
        widget=widgets.TextInput(),
        # 给插件添加的属性
        # render_kw={'class': 'form-control'}

    )
    # pwd = html5.EmailField() # 可以使用html5的验证方式
    pwd = simple.PasswordField(
        label='密码',
        validators=[
            validators.DataRequired(message='密码不能为空.'),
            validators.Length(min=2, message='用户名长度必须大于%(min)d'),
        ],
        widget=widgets.PasswordInput(),
        # render_kw={'class': 'form-control'}
    )


class RegisterForm(Form):
    name = simple.StringField(
        label='用户名',
        validators=[
            validators.Length(min=2, max=18, message='用户名长度必须大于%(min)d且小于%(max)d'),
            validators.DataRequired()
        ],
        widget=widgets.TextInput(),
        # 输入框的默认值
        default='alex'
    )

    pwd = simple.PasswordField(
        label='密码',
        validators=[
            validators.Length(min=2, message='用户名长度必须大于%(min)d'),
            validators.DataRequired(message='密码不能为空.')
        ],
        widget=widgets.PasswordInput(),
    )

    pwd_confirm = simple.PasswordField(
        label='重复密码',
        validators=[
            validators.DataRequired(message='重复密码不能为空.'),
            # 内部校验器:与哪一个字段要一直，比django自带的要简单一些，否则还要使用钩子
            validators.EqualTo('pwd', message="两次密码输入不一致")
        ],
        widget=widgets.PasswordInput(),

    )
    file = simple.FileField(
        label='头像上传',
        widget=widgets.FileInput(),
    )

    # 定制钩子函数，使用validate_字段名
    def validate_pwd_confirm(self, field):
        if field.data != self.data['pwd']:
            raise validators.StopValidation("密码不一致")  # 不再继续后续验证
        self.data.pop('pwd_confirm')


@user.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        # data是传入的默认值，表示gender字段默认选中1，来实例化form
        form = RegisterForm()
        return render_template('register.html', form=form)
    else:
        # 使用formdata接收数据
        form = RegisterForm(formdata=request.form)
        if form.validate():
            form.data.pop('pwd_confirm')
            file_name = f'{uuid4()}.jpg'
            file = request.files.get('file')
            dic = request.form.to_dict()
            file.save(f'{REG_PATH}/{file_name}')
            dic['avatar'] = file_name
            dic['chat_list'] = []
            # print(dic)
            # print('用户提交数据通过格式验证，提交的值为：', request.form.to_dict())
            MongoDB.users.insert_one(dic)
            return redirect('/login')

        else:
            print(form.errors)
        return render_template('register.html', form=form)


@user.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        form = LoginForm()
        return render_template('login.html', form=form)
    else:
        form = LoginForm(formdata=request.form)
        if form.validate():
            # print('用户提交数据通过格式验证，提交的值为：', form.data)
            dic = request.form.to_dict()
            user = MongoDB.users.find_one(dic)
            if user:
                return redirect(f"/chat/{user.get('name')}")
            else:
                return redirect('/register')
        else:
            print(form.errors)
        return render_template('login.html', form=form)


@user.route('/chat/<name>', methods=['GET', 'POST'])
def chat(name):
    user = MongoDB.users.find_one({'name': name})
    return render_template('ws.html', user=user)


@user.route('/get_chat/<name>/<username>', methods=['GET'])
def get_chat(name,username):
    friend = MongoDB.users.find_one({'name':name})
    username = MongoDB.users.find_one({'name':username})

    chatx = MongoDB.chats.find_one({'user_list':{'$all':[str(friend['_id']),str(username['_id'])]}})
    print(chatx,str(friend['_id']),str(username['_id']))
    if not chatx:
        ret = {'user_list':[str(friend['_id']),str(username['_id'])]}
        ret['content_list'] = []
        chat = MongoDB.chats.insert_one(ret)
        chat_id = str(chat.inserted_id)

        # 更新数据库
        friend['chat_list'].append(chat_id)
        username['chat_list'].append(chat_id)
        # 更新user
        MongoDB.users.update_one({'_id':ObjectId(username['_id'])},{'$set':username})

         #聊天窗口
        MongoDB.chats.update_one({'_id':ObjectId(friend['_id'])},{'$set':friend})

        friend_info = {
            'img':username['avatar'],
            'chat_id':chat_id,
        }
        RET['code'] = 2
        RET['data'] = friend_info
        return jsonify(RET)
    else:
        user_cont = []
        friend_chat = []
        for cont in chatx['content_list']:
            if cont['name'] == friend['name']:
                friend_chat.append(cont['content'])
            else:
                user_cont.append(cont['content'])

        RET['user_cont'] = user_cont
        RET['friend_chat'] = friend_chat

        friend_info = {
            'img':username['avatar'],
            'chat_id':str(chatx['_id']),
        }
        RET['code'] = 2
        RET['data'] = friend_info
        return jsonify(RET)


def text2audio(text):
    filename = f"{uuid4()}.mp3"
    file_path = os.path.join(CHAT_PATH,filename)
    res = AUDIO_CLIENT.synthesis(text,'zh', 1,VOICE)

    if type(res) == dict:
        pass
    else:
        with open(file_path,'wb') as f:
            f.write(res)

    return filename  # 用于返回生成的文件名


@user.route('/ai_chat/<Q>/<username>',methods=['GET'])
def ai_chat(Q,username):
    TL_DATA['perception']['inputText']['text'] = Q
    TL_DATA['userInfo']['userId'] = username
    res = requests.post(TL, json=TL_DATA)  # 发送字典格式

    res_json = res.json()  # requests对象的反序列化
    start_content = res_json.get("results")[0].get("values").get("text")
    filename = text2audio(start_content)

    ret =  {
        'code':6,
        "from_user": "ai",
        "chat": filename,
    }

    return jsonify(ret)











