from os import remove
from flask import Flask, render_template, request, send_from_directory, url_for, redirect, flash, Blueprint, Response
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy.orm import query
from sqlalchemy.sql.expression import null
from sqlalchemy.sql.functions import user
from sqlalchemy.inspection import inspect
from werkzeug.security import generate_password_hash, check_password_hash # hides password
from werkzeug.utils import secure_filename
from .models import User,Product,Cart, Img
from datetime import datetime
from .queries import *
from . import db


# user=current_user  -> links current user to each template
# @login_required -> cant access page unless user logged in

app = Blueprint('app', __name__)
@app.route('/', methods=['GET', 'POST'])
@app.route('/<string:sortby>/', methods=['GET', 'POST'])
@app.route('/<string:sortby>/<string:search>', methods=['GET', 'POST'])
def index(search='',sortby='newest'):
    
    if request.method == 'POST':
        search = request.form.get('search')
       
    # list of prodcuts sorted
    productResult = list()
    if sortby == "newest":
        productResult = sortProductBy(search, 'DateAdded', "DESC")
    elif sortby == "priceDesc":
        productResult = sortProductBy(search, 'Price', "DESC")
    elif sortby == "priceAsc":
        productResult = sortProductBy(search,'Price', "ASC")
    elif sortby == "alphaAZ":
        productResult = sortProductBy(search,'Name', "ASC")
    elif sortby == "alphaZA":
        productResult = sortProductBy(search,'Name', "DESC")
    else:
        flash('Invalid parameter.', category='error')
        # return render_template('home.html', user=current_user, productsDict=productResult, now=datetime.utcnow(), sortby=sortby, search=search)

    # if search bar triggered
    if len(productResult) < 1 and search:
        flash('Nothing found for that search. (All words must match.)', category='warning')

    return render_template('home.html', user=current_user, productsDict=productResult, now=datetime.utcnow(), sortby=sortby, search=search)


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        Email_address = request.form.get('email_address')
        password = request.form.get('password')

        # looks for user in DB
        user = User.query.filter_by(Email=Email_address).first()

        # if user found checks password
        # if wrong password throw error
        # if user not found throw error
    
        if user:
            if check_password_hash(user.Password, password):
                 flash('You have been successfully logged in.', category='success')
                 login_user(user)
                 return redirect(url_for('app.index', user=current_user))
            else:
                 flash('Wrong password. Please try again.', category='error')
        else:
            flash('Email does not exist.  Please try again.', category='error')


    return render_template('login.html', user=current_user)


@app.route('/registration',methods=['GET','POST'])
def registration():
    if request.method == 'POST':
        userType = request.form.get('type')
        
        fname = request.form.get('first_name')
        midIn = request.form.get('middle_initial')
        lname = request.form.get('last_name')

        address = request.form.get('address')
        city = request.form.get('city')
        state = request.form.get('state')
        zip = request.form.get('zipcode')

        email = request.form.get('email')
        phone = request.form.get('phone_number')
        password = request.form.get('password')

        user = User.query.filter_by(Email=email).first()
       
        if user:
            flash("Email already exits. Try again.", category='error')
            return redirect('base.html')
        elif len(email) < 5:
            flash('Email must be greater than 5 characters.', category='error')
        elif len(password) != 5:
           flash('Password must be 5 characters.', category='error')
        else:
            newUser = User(
                Fname = fname,
                MiddleIn = midIn,
                Lname = lname,
                Address = address,
                City = city,
                State = state,
                ZipCode = zip,
                Email = email,
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
    return redirect(url_for('app.login'))


@app.route('/itemPost', methods=['GET','POST'])
@login_required
def itemPost():
    if request.method == 'POST':
        # product info from form
        pName = request.form.get('ProductName')
        pDesc = request.form.get('ProductDescription')
        pPrice = request.form.get('ProductPrice')

        # image info from form
        pPic = request.files['uploadImg']
        filename = secure_filename(pPic.filename)
        mimetype = pPic.mimetype
    
        if not pPic:
          flash('Image required to submit item.', category='error')
        else:
            newProduct = Product(
                SellerID = current_user.UserId,
                Name = pName,
                Description = pDesc,
                Price = pPrice)

             # product to database
            db.session.add(newProduct)
            db.session.commit()

            dbNewProduct = Product.query.filter_by(Name=pName, SellerID=current_user.UserId).first()
            img = Img(
                ProductId=dbNewProduct.PID,
                img=pPic.read(), 
                name=filename, 
                mimetype=mimetype)
            
            # img to database
            db.session.add(img)
            db.session.commit()

            flash('Item Posted!', category='success')
            return redirect(url_for('app.index'))

    return render_template('itemPost.html',user=current_user)


@app.route('/editPost/<int:PID>', methods=['GET','POST'])
@login_required
def EditPost(PID):
    productFound = query.filter_by(PID=PID).first()

    if request.method == 'POST' and productFound.SellerId in (current_user.UserId, 1):
        # product info from form
        pName = request.form.get('ProductName')
        pDesc = request.form.get('ProductDescription')
        pPrice = request.form.get('ProductPrice')

        # image info from form
        # pPic = request.files['uploadImg']
        # filename = secure_filename(pPic.filename)
        # mimetype = pPic.mimetype
    
        # if not pPic:
        #   flash('Image required to submit item.', category='error')
        # else:
       
        if productFound:
            productFound.Name = pName
            productFound.Description = pDesc
            productFound.Price = pPrice
            # update database
            db.session.commit()
            flash('Item Updated!', category='success')
            return redirect(url_for('app.index'))
        else:
            flash("Error editing post.", category="error")
                
            # dbNewProduct = Product.query.filter_by(Name=pName, SellerID=current_user.UserId).first()
            # img = Img(
            #     ProductId=dbNewProduct.PID,
            #     img=pPic.read(), 
            #     name=filename, 
            #     mimetype=mimetype)
            
            # update database
            # db.session.add(img)
            
    return render_template('itemPost.html',user=current_user,PID=PID)

# have log required to view cart once registration/log in functionality complete
@app.route('/cart', methods=['GET','POST'])
@login_required
def shoppingCart():
    # uncoment upon registration completion
    # cartItems = getItemsFromCart(current_user.UserId)
    cartItems = list()

    # calculate check out total cost
    checkOutSum = 0
    for product in cartItems:
        checkOutSum += product[5]

    # upon form completion
    if request.method == 'POST':
        for product in cartItems:
            product.isSold =True
            db.session.commit()

        flash('Check Out Success! Shipping information sent to email!', category='warning')
        return redirect(url_for('app.index')) 

    return render_template('cart.html',user=current_user, productsDict = cartItems, checkOutSum=checkOutSum)


@app.route('/<int:id>/')
def get_img(id):
    img = Img.query.filter_by(id=id).first()
    
    if img:
        return Response(img.img, mimetype=img.mimetype)
    else:
        return null

# TODO:
# //////////////////////

@app.route('/admin')
@login_required
def admin():
    return render_template('admin.html',user=current_user)


# optional
@app.route('/forgot')
def forgot():
    return render_template('forgot.html')
