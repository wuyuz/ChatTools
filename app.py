from flask import Flask

from serv.content import content
from serv.user import user


app = Flask(__name__)
app.debug = True

app.register_blueprint(user)
app.register_blueprint(content)


if __name__ == '__main__':
    app.run()