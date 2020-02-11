from app import app
from flask import render_template, flash, redirect, url_for, request, Response, Flask, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import forms, db, camera_pi, base_camera, route_logic, motor_pi, schedule_pi
from app.forms import register
from app.models import users
from app.models import *
from app import feed_obj


# Global variables to control the camera filter
# and whether the thread needs to be restarted
global filter
filter = 'none'
global check
check = False


# The default page which will be rendered
@app.route('/')
def startPage():
    id = None
    if current_user.is_authenticated:
        id = current_user.get_id()
    return render_template('start.html', id=id)


# The page rendered for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    # if a logged in user tries to view the login page, send them home
    if current_user.is_authenticated:
        return redirect(url_for('startPage'))

    login = forms.signIn()
    # Only run this when the form is submitted, not on page load
    if login.validate_on_submit():
        # Query DB to get user
        usr = users.query.filter_by(username=login.username.data).first()
        if usr is None or not usr.check_password(login.password.data):
            flash("Incorrect Username or Password")
            # Refresh page to show the flashed message
            return redirect(url_for('login'))
        login_user(usr, remember=login.remember.data)
        next_page = request.args.get('next')
        # 'next' will take the user to the last page they tried to visit before logging in
        # if that page required login and kicked them back to this page
        # .netloc ensures that the URL actually exists in the app and hasn't been injected
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('startPage')
        return redirect(next_page)
    return render_template('login.html', form=login)


# The page rendered after the user logs out
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('startPage'))


# The page rendered when the user registers
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('startPage'))

    registrationForm = forms.register()
    if registrationForm.validate_on_submit():
        uname = registrationForm.username.data
        email = registrationForm.email.data
        usr = users(username=uname, email=email)
        usr.set_password(registrationForm.password.data)
        db.session.add(usr)
        db.session.commit()
        committedUser = users.query.filter_by(username=uname).first()
        uid = committedUser.id
        attr = attributes(userID=uid, canFeed=1, isAdmin=1, style='light')
        db.session.add(attr)
        db.session.commit()
        flash("User Registered")
        return redirect(url_for('login'))
    return render_template('register.html', form=registrationForm)


# The page rendered when the registered user clicks the view bird option
@app.route('/view/<username>', methods=['GET', 'POST'])
@login_required
def birdView(username):
    usr = users.query.filter_by(id=current_user.get_id()).first_or_404()
    attr = attributes.query.filter_by(userID=current_user.get_id()).first_or_404()
    # Convert the ints from the DB to bools
    can_feed = route_logic.convert_can_feed_from_db(attr.canFeed)
    if request.method == "GET":
        # Allows authenticated user to view the stream
        return render_template('birdView.html', user=usr, can_feed=can_feed)
    if request.method == "POST":
        # Apply the selected filter and restart the stream
        global filter  # Indicates we are referring the the global filter
        filter = 'negative'
        global check  # Indicated we are referring the the global check
        check = True
        return render_template('birdView.html', user=usr, can_feed=can_feed)


@app.route('/birdstream')
def birdstream():
    # Handles the live stream to the img element on the live stream page
    return Response(route_logic.gen(camera_pi.Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


# Handles the jquery when pressing 'Feed' link/button on birdView.html
@app.route('/_feed')
def toFeed():
    # Call route logic to execute the motor spinning script
    route_logic.instant_feed(motor_pi.motor(), run=True)
    return ()


@login_required
@app.route('/settings', methods=['GET', 'POST'])
def adminSettings():
    # TODO: Auto populate form based on current settings
    feed_settings = forms.feedSettings()
    theme_settings = forms.themeSettings()
    # If the form passes validation and is submitted
    if feed_settings.validate_on_submit():
        # Get the current user's ID and load the attributes table for that user (userID is FK with ID in users table)
        uid = current_user.get_id()
        attr = attributes.query.filter_by(userID=uid).first()

        # Set the attributes in the attributes table to the values in the form
        # Since SQLite does not have bools, some of this is passed to separate functions to convert bool to int
        attr.canFeed = route_logic.convert_can_feed_from_form(feed_settings.canFeed.data)
        attr.scheduleFeed = route_logic.convert_feed_from_form(feed_settings.scheduledFeed.data)
        attr.feedDays = route_logic.get_feed_days(
            feed_settings.feedDay_Monday.data, feed_settings.feedDay_Tuesday.data, feed_settings.feedDay_Wednesday.data,
            feed_settings.feedDay_Thursday.data, feed_settings.feedDay_Friday.data, feed_settings.feedDay_Saturday.data,
            feed_settings.feedDay_Sunday.data
        )
        attr.feedHour = feed_settings.feedHour.data
        attr.feedMinute = feed_settings.feedMinute.data

        # write changes to DB and flash a message to users
        db.session.commit()
        flash("Feed Settings updated")
        return render_template('settings.html', feed_settings=feed_settings, theme_settings=theme_settings)

    if theme_settings.validate_on_submit():
        uid = current_user.get_id()
        attr = attributes.query.filter_by(userID=uid).first()
        attr.style = theme_settings.themes.data
        db.session.commit()
        flash('Theme Updated')

    return render_template('settings.html', feed_settings=feed_settings, theme_settings=theme_settings)

@login_required
@app.route('/schedule')
def schedule():
    # Get every field from the attributes table which has scheduledFeed = 1
    # This amounts to every user who has a feed scheduled
    all_feeds = attributes.query.filter_by(scheduleFeed=1).all()
    # Empty list which will be filled by feedTimeObjects
    feed_times = []

    for feed in all_feeds:
        # Create a new empty FeedTimeObject
        this_feed_time = feed_obj.FeedTimeObject()

        usr = users.query.filter_by(id=feed.userID).first()
        # Fill the feed time object
        this_feed_time.set_feed_creator(usr.username)
        this_feed_time.set_feed_days(feed.feedDays)
        this_feed_time.set_feed_time(str(feed.feedHour) + ":" + str(feed.feedMinute))
        # Add the feed time object to the end of a list
        feed_times.append(this_feed_time)

    # Pass the feed_times list of FeedTime Objects to the web page
    return render_template('feedSchedule.html', feed_times=feed_times)
