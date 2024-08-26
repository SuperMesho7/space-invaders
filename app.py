from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    login_user,
    UserMixin,
    LoginManager,
    login_required,
    current_user,
    logout_user,
)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todos.db"
app.config["SECRET_KEY"] = "secret"
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    todos = db.relationship("Todos", backref="users")


class Todos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(900))
    check = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))


with app.app_context():
    db.create_all()


@login_manager.user_loader
def loader_user(user_id):
    return Users.query.get(user_id)


@app.route("/", methods=["POST", "GET"])
def index():
    if not current_user.is_authenticated:
        new_user = Users()
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
    if request.form.get("todo"):
        todo = Todos(
            text=request.form.get("todo"), check=False, user_id=current_user.id
        )
        db.session.add(todo)
        db.session.commit()
        todos = current_user.todos
        return render_template("index.html", todos=todos)
    else:
        todos = current_user.todos
        return render_template("index.html", todos=todos)


@app.route("/change-check", methods=["POST", "GET"])
def change_check():
    new_check = request.form.get("check")
    todo_id = request.form.get("todo_id")
    if type(new_check) == type(None):
        new_check = False
    else:
        new_check = True
    print(new_check)
    db.session.query(Todos).get(todo_id).check = new_check
    db.session.commit()
    return redirect("/")


@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
