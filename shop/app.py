from os import remove
from flask import Flask, render_template, request, send_from_directory, url_for, redirect, flash, session, Blueprint
from flask_login import login_user, login_required, logout_user, current_user
import sqlalchemy
from sqlalchemy.orm import query
from sqlalchemy.sql.functions import user
from sqlalchemy.inspection import inspect
from werkzeug.security import generate_password_hash, check_password_hash # hides password
from .models import User,Product,Cart
from .queries import *
from . import db


# user=current_user  -> links current user to each template
# @login_required -> cant access page unless user logged in

app = Blueprint('app', __name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    
    # list of prodcuts 
    productResult = sortProductBy()

    # if search bar triggered
    # if len(productResult) < 1:
    #     flash('Nothing found for that search. (All words must match.)', category='warning')

    # default items list
    if len(productResult) < 1:
        flash('No items posted yet.', category='warning')


    # have correct things show depending on user
    # if user:
    #     userType = 'user'
    # elif admin:
    #     userType = 'admin'
    return render_template('home.html', user=current_user, productsDict=productResult)
    # return render_template('home.html', user=current_user)


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('EmailAddress')
        password = request.form.get('Password')
        remember  = request.form.get('remember')

        # looks for user in DB
        user = User.query.filter_by(EmailAddress=email).first()

        # if user found checks password
        # if wrong password throw error
        # if user not found throw error
    
        if user:
            if check_password_hash(user.Password, password):
                 flash('You have been successfully logged in.', category='succes')
                 login_user(user, remember=remember)
                 return redirect(url_for('app.index', user=current_user))
            else:
                 flash('Wrong password. Please try again.', category='error')
        else:
            flash('Email does not exist.  Please try again.', category='error')


    return render_template('login.html', user=current_user)

# optional
@app.route('/forgot')
def forgot():
    return render_template('forgot.html')


@app.route('/registration',methods=['GET','POST'])
def registration():
    if request.method == 'POST':
        userType = request.form.get('type')
        
        fname = request.form.get('FirstName')
        midIn = request.form.get('MiddleInitial')
        lname = request.form.get('LastName')

        address = request.form.get('Address')
        city = request.form.get('City')
        state = request.form.get('State')
        zip = request.form.get('Zip')

        email = request.form.get('EmailAddress')
        phone = request.form.get('PhoneNumber')
        password = request.form.get('Password')


        user = User.query.filter_by(EmailAddress=email).first()
       
        if user:
            flash("Email already exits. Try again.", category='error')
        elif len(email) < 5:
            flash('Email must be greater than 5 characters.', category='error')
        elif len(password) != 5:
           flash('Password must be 5 characters.', category='error')
        else:
            newUser = User(
                FirstName = fname,
                MiddleInitial = midIn,
                LastName = lname,
                Address = address,
                City = city,
                State = state,
                ZipCode = zip,
                EmailAddress = email,
                PhoneNumber = phone,
                Password = generate_password_hash(password, method='sha256'))
     
            # to database
            db.session.add(newUser)
            db.session.commit()
            login_user(newUser, remember=True)
            flash('Account created!', category='success')

            return redirect(url_for('app.index'))
            

    return render_template('registration.html', user=current_user)


@app.route('/accountSettings',methods=['GET','POST'])
@login_required
def accountSettings():
    # allows user to change user info

    return render_template('home.html', user=current_user)


@app.route('/logout')
@login_required 
def logOut():
    logout_user()
    return redirect(url_for('app.LoginForm'))


@app.route('/admin')
@login_required
def admin():
    return render_template('Management.html',user=current_user)


@app.route('/itemPost')
@login_required
def itemPost():

    return render_template('itemPost.html',user=current_user)


@app.route('/cart', methods=['GET','POST'])
@login_required
def shoppingCart():
    cartItems = getItemsFromCart(current_user.UserId)

    # upon form completion
    if request.method == 'POST':
        pass



    return render_template('cart.html',user=current_user, productsDict = cartItems)




