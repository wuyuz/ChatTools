import json

from flask import Flask,request,render_template,jsonify
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket.server import WSGIServer
from geventwebsocket.websocket import WebSocket

from settings import MongoDB

ws = Flask(__name__)
socket_list = {}
chating = set()

@ws.route("/ws/<user>")
def my_ws(user):
    ws_socket = request.environ.get("wsgi.websocket")#type:WebSocket   #获取长链接对象
    socket_list[user] = ws_socket
    # print(socket_list,len(socket_list))

    while 1:
        user_msg = ws_socket.receive()
        user_msg_dict = json.loads(user_msg)
        user_msg_dict['count'] = len(socket_list)
        user_msg_dict['users'] = list(socket_list.keys())
        to_user = user_msg_dict.get('to_user')
        code = user_msg_dict.get('status')
        #code为0表示初始化table

        if code == 3:
            from_user = user_msg_dict.get('from_user')
            chating.remove(to_user)
            chating.remove(from_user)

        elif code == 4:
            for key, item in socket_list.items():
                print(key)
                if key != user_msg_dict.get('from_user'):
                    item.send(json.dumps(user_msg_dict))
            else:
                continue

        elif code:
            chating.add(to_user)

        user_msg_dict['chating'] = list(chating)
        reveiver = socket_list.get(to_user)
        print(user_msg_dict)
        reveiver.send(json.dumps(user_msg_dict))


if __name__ == '__main__':
    http_serv = WSGIServer(("0.0.0.0",9528),ws,handler_class=WebSocketHandler)
    http_serv.serve_forever()
