from flask import Flask, render_template, request, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float

app = Flask(__name__)
app.config['SECRET_KEY'] = 'f0cb505df6b8286e'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///new-books-collection.db"
Bootstrap5(app)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

class Book(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    author: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    rating: Mapped[float] = mapped_column(Float, unique=False, nullable=False)  # Corrected unique constraint

with app.app_context():
    db.create_all()

class MyForm(FlaskForm):
    name = StringField('Book Name', validators=[DataRequired()])
    author = StringField('Book Author', validators=[DataRequired()])
    rating = FloatField('Rating', validators=[DataRequired()])
    submit = SubmitField('Submit')

class EditRatingForm(FlaskForm):
    rating = FloatField('Rating', validators=[DataRequired()])
    submit = SubmitField('Update Rating')

@app.route('/')
def home():
    all_books = Book.query.all()
    return render_template("index.html", all_books=all_books)

@app.route("/add", methods=["GET", "POST"])
def add():
    form = MyForm()
    if form.validate_on_submit():
        new_book = Book(
            name=form.name.data,
            author=form.author.data,
            rating=float(form.rating.data)
        )
        db.session.add(new_book)
        db.session.commit()        
        return redirect(url_for('home'))
    return render_template("add.html", form=form)

@app.route("/delete/<int:book_id>", methods=["GET", "POST"])
def delete(book_id):
    book_to_delete = Book.query.get_or_404(book_id)
    
    try:
        db.session.delete(book_to_delete)
        db.session.commit()
        flash('Book deleted successfully', 'success')
    except:
        db.session.rollback()
        flash('Error deleting book', 'error')
    
    return redirect(url_for('home'))

@app.route("/edit_rating/<int:book_id>", methods=["GET", "POST"])
def edit_rating(book_id):
    book_to_edit_rating = Book.query.get_or_404(book_id)
    form = EditRatingForm()

    if form.validate_on_submit():
        book_to_edit_rating.rating = form.rating.data  # Correctly update the rating attribute
    
        try:
            db.session.commit()
            flash('Book rating edited successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error editing book rating: {str(e)}', 'error')
    
        return redirect(url_for('home'))
    
    return render_template('edit_rating.html', form=form, book=book_to_edit_rating)

if __name__ == "__main__":
    app.run(debug=True)
