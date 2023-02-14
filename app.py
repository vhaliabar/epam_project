
from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/")
def hello_world():
    name=request.args.get("name", 'world')
    return render_template("index.html", name=name)

@app.route('/about/<name>')
def about(name):
    return f'<h2>Hello, nice to meet you, <a href="">{name}</a> </h2>'

@app.route('/user/<username>')
def profile(username):
    return f'{username}\'s profile'


if __name__ == "__main__":
    app.run(debug=True)