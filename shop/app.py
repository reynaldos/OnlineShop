from os import remove
from flask import Flask, render_template, request, jsonify, url_for, redirect, flash, Blueprint, Response
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
import json



# user=current_user  -> links current user to each template
# @login_required -> cant access page unless user logged in


adminAccount ={
    'UserID': 1,
    'Email': 'admin@usf.edu'
}

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

    return render_template('home.html', user=current_user, productsDict=productResult, now=datetime.utcnow(), sortby=sortby, search=search,myitems=False)


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

            # gives new user a cart
            userCart = Cart(UserId=current_user.UserId)
            db.session.add(userCart)
            db.session.commit()

            flash('Account created!', category='success')

            return redirect(url_for('app.index'))
            

    return render_template('registration.html', user=current_user)


@app.route('/forgot', methods=['GET','POST'])
def forgot():
    if request.method == 'POST':
        Email_address = request.form.get('email')
    
        # looks for user in DB
        user = User.query.filter_by(Email=Email_address).first()

        # if user found checks password
        # if wrong password throw error
        # if user not found throw error
    
        if user:
            flash('Recovery email sent!', category='warning')
            return redirect(url_for('app.login', user=current_user))
        else:
            flash('Email does not exist.  Please try again.', category='error')


    return render_template('forgot.html',user=current_user)


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
def editPost(PID):
    productFound = Product.query.filter_by(PID=PID).first()

    if not productFound:
        flash('Error Occured when editting.', category='error')
        return redirect(url_for('app.index')) 

    if current_user.UserId not in (productFound.SellerID, adminAccount['UserID']) :
        flash('Access Denied', category='warning')
        return redirect(url_for('app.index'))

    if request.method == 'POST':
        # product info from form
        pName = request.form.get('ProductName')
        pDesc = request.form.get('ProductDescription')
        pPrice = request.form.get('ProductPrice')

        # add img change functionality
        # image info from form
        pPic = request.files['uploadImg']
        filename = secure_filename(pPic.filename)
        mimetype = pPic.mimetype
        
        # update item
        if productFound:
            productFound.Name = pName
            productFound.Description = pDesc
            productFound.Price = pPrice
            # update database
            db.session.commit()
            
            # check if pic added
            if pPic:
                img = Img(
                    ProductId=productFound.PID,
                    img=pPic.read(), 
                    name=filename, 
                    mimetype=mimetype)
                
                # update database
                db.session.add(img)
                db.session.commit()

            flash('Item Updated!', category='success')
            return redirect(url_for('app.index'))
        else:
            flash("Error editing post.", category="error")
            
    return render_template('editPost.html',user=current_user,productFound=productFound,PID=PID)

@app.route('/myitems', methods=['GET', 'POST'])
@app.route('/myitems/<string:sortby>/', methods=['GET', 'POST'])
@app.route('/myitems/<string:sortby>/<string:search>', methods=['GET', 'POST'])
@login_required
def userItems(search='',sortby='newest'):
    
    userID = current_user.UserId

    if request.method == 'POST':
        search = request.form.get('search')
       
    # list of prodcuts sorted
    productResult = list()
    if sortby == "newest":
        productResult = userActiveProducts(userID, search, 'DateAdded', "DESC")
    elif sortby == "priceDesc":
        productResult = userActiveProducts(userID, search, 'Price', "DESC")
    elif sortby == "priceAsc":
        productResult = userActiveProducts(userID, search,'Price', "ASC")
    elif sortby == "alphaAZ":
        productResult = userActiveProducts(userID, search,'Name', "ASC")
    elif sortby == "alphaZA":
        productResult = userActiveProducts(userID, search,'Name', "DESC")
    else:
        flash('Invalid parameter.', category='error')
        # return render_template('home.html', user=current_user, productsDict=productResult, now=datetime.utcnow(), sortby=sortby, search=search)

    # if search bar triggered
    if len(productResult) < 1 and search:
        flash('Nothing found for that search. (All words must match.)', category='warning')

    return render_template('home.html', user=current_user, productsDict=productResult, now=datetime.utcnow(), sortby=sortby, search=search,myitems=True)


@app.route('/cart', methods=['GET','POST'])
@login_required
def shoppingCart():
    # uncoment upon registration completion
    userCart = userCart = Cart.query.filter_by(UserId=current_user.UserId).first()

    # calculate check out total cost
    checkOutSum = 0
    # cartItems = list()
    for product in userCart.Products:
        checkOutSum += product.Price

    # upon form completion
    if request.method == 'POST':
        for product in userCart.Products:
            userCart.Products.remove(product)
            product.isSold =True
            db.session.commit()

        flash('Check out success! Shipping information sent to email!', category='success')
        return redirect(url_for('app.index')) 

    return render_template('cart.html',user=current_user, cartItems = userCart.Products, checkOutSum=checkOutSum)


@app.route('/<int:id>/')
def get_img(id):
    img = Img.query.filter_by(id=id).first()
    
    if img:
        return Response(img.img, mimetype=img.mimetype)
    else:
        return null

@app.route('/add-item', methods=['POST'])
@login_required
def addCartItem():
    # finds user cart
    userCart = Cart.query.filter_by(UserId=current_user.UserId).first()
    

    # gets PID from request
    form = json.loads(request.data)
    foundPID = form['PID']

    # gets product and adds user cart
    item  = Product.query.filter_by(PID=foundPID).first()
    if item:
        if not userCart:
            flash('Log in to add item to cart!', category='warning')

        elif item in userCart.Products:
            flash('Item already in cart!', category='warning')

        elif userCart.UserId == current_user.UserId:
            userCart.Products.append(item)
            db.session.commit()
            flash('Item added to cart!', category='success')
        else:
            return 404

    return jsonify({})


@app.route('/remove-item', methods=['POST'])
@login_required
def removeCartItem():
    # finds user cart
    userCart = Cart.query.filter_by(UserId=current_user.UserId).first()

    # gets PID from request
    form = json.loads(request.data)
    foundPID = form['PID']

    # gets product and removes from user cart
    item  = Product.query.filter_by(PID=foundPID).first()
    if item:
        if userCart.UserId == current_user.UserId:
            userCart.Products.remove(item)
            db.session.commit()

    return jsonify({})


@app.route('/delete-item', methods=['POST'])
@login_required
def deleteProduct():
    
    # gets PID from request
    form = json.loads(request.data)
    foundPID = form['PID']

    # gets product and removes from DB
    item  = Product.query.get(foundPID)

    print(item.PID)

    if item:
        img = Img.query.filter_by(ProductId=item.PID).first()

        if current_user.UserId in (item.SellerID, adminAccount['UserID']):
            db.session.delete(img)
            db.session.delete(item)
            db.session.commit()
            flash('Item deleted.', category='warning')

    return jsonify({})



# TODO:
# //////////////////////

@app.route('/admin')
@login_required
def admin():
    
    rows = getUserIds()
    product_list = sortProductBy("", "SellerID", "ASC")

    if current_user.Email != adminAccount['Email'] or current_user.UserId != adminAccount['UserID']:
        flash('Access Denied.', category='error')
        return redirect(url_for('app.index')) 
        
    # return render_template('admin.html',user=current_user,)

    return render_template('admin.html',user=current_user, rows=rows, products=product_list)


@app.route('/accountSettings',methods=['GET','POST'])
@login_required
def accountSettings():
    if request.method == 'POST':
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

        user = User.query.filter_by(UserId=current_user.UserId).first()

        if user:
            user.Fname = fname
            user.MiddleIn = midIn
            user.Lname = lname
            user.Address = address
            user.City = city
            user.State = state
            user.ZipCode = zip
            user.Email = email
            user.PhoneNumber = phone
            user.Password = generate_password_hash(password, method='sha256')

            # to database
            db.session.commit()
            flash('Account Updated!', category='success')
            return redirect(url_for('app.index'))
        else:
            flash('Account not found.', category='error')
            
    return render_template('accountSettings.html', user=current_user)



   


from shop import create_app
myapp = create_app()

if __name__ == '__main__':
    myapp.run(debug=True)
