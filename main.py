from flask import Flask, render_template, redirect, url_for,request ,flash
from flask_login import login_user, LoginManager, login_required, UserMixin , current_user , logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from werkzeug.security import check_password_hash , generate_password_hash
from sqlalchemy.exc import IntegrityError



app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'


# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)

class Users(UserMixin,db.Model):
    id: Mapped[int] = mapped_column(Integer , primary_key=True)
    username : Mapped[str] = mapped_column(String(50),nullable=True)
    email : Mapped[str] = mapped_column(String(30),nullable=True,unique=True)
    password : Mapped[str] = mapped_column(String,nullable=True)




with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Users, int(user_id))  # SQLAlchemy 2.0+ syntax




@app.route('/')
def get_all_posts():
    # TODO: Query the database for all the posts. Convert the data to a python list.
    posts = []
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts)



# TODO: Add a route so that you can click on individual posts.
@app.route('/post/<int:post_id>')
@login_required
def show_post(post_id):
    # TODO: Retrieve a BlogPost from the database based on the post_id
    requested_post = db.get_or_404(BlogPost,post_id)
    return render_template("post.html", post=requested_post)


# TODO: add_new_post() to create a new blog post
@app.route("/new-post",methods=["GET","POST"])
@login_required
def add_new_post():
    if request.method == "POST":
        title = request.form.get("title")
        subtitle=request.form.get("subtitle")
        body=request.form.get("body")
        author = request.form.get("author")
        img_url = request.form.get("img_url")
        date = request.form.get("date")

        new_post = BlogPost(
            title = title,
            subtitle = subtitle,
            body = body,
            author = author,
            img_url = img_url,
            date = date,

    )
        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for("get_all_posts"))

    return render_template("make-post.html")


# TODO: edit_post() to change an existing blog post
@app.route("/edit-post/<int:post_id>",methods=["GET","POST"])
@login_required
def edit_post(post_id):
    post = db.get_or_404(BlogPost,post_id)

    if request.method == "POST":
        post.title = request.form.get("title")
        post.subtitle= request.form.get("subtitle")
        post.body = request.form.get("body")
        post.author = request.form.get("author")
        post.img_url = request.form.get("img_url")
        post.date = request.form.get("date")

        db.session.commit()

        return redirect(url_for("show_post",post_id = post_id))


    return render_template("make-post.html",post=post,is_edit=True)




# TODO: delete_post() to remove a blog post from the database

@app.route("/delete/<int:post_id>",methods=["POST"])
@login_required
def delete_post(post_id):
    if request.method == "GET":
        post_to_delete = db.get_or_404(BlogPost,post_id)
        db.session.delete(post_to_delete)
        db.session.commit()

    return redirect(url_for("get_all_posts"))

# Below is the code from previous lessons. No changes needed.
@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/register",methods=["GET","POST"])
def register():
    if request.method == "POST":

        hashed_password = generate_password_hash(
            password=request.form.get("password"),
            method = "pbkdf2:sha256",
            salt_length=8
        )

        new_user = Users(
        username = request.form.get("username"),
        email = request.form.get("email"),
        password = hashed_password

        )
        try:
            db.session.add(new_user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            print("flash triggered")
            flash("Email address already exist. Please try again with different email id")
            return redirect(url_for("register"))


        login_user(new_user)
        return redirect(url_for("add_new_post"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("get_all_posts"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        result = db.session.execute(db.select(Users).where(Users.email == email))
        user = result.scalar()

        if not user:
            flash("User not found. Please register.")
        elif not check_password_hash(user.password, password):
            flash("Incorrect password. Try again.")
        else:
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("get_all_posts"))

    # ✅ Always return the login form for GET requests and if login failed
    return render_template("login.html")

@app.route("/logout")
def logout():
    logout_user()

    return redirect(url_for("get_all_posts"))








if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)
