import time
from datetime import datetime
from app import motor_pi, feed_obj
from app.bb_log import bbLog
from app.models import *
from flask_login import current_user


# This continuously captures images to feed the _thread function in BaseCamera.py
def gen(camera):
    try:
        while True:
            frame = camera.get_frame()
            time.sleep(.12)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    except:
        bbLog.info("The camera feed is loading or an error has occurred.")


# Gets the current time and converts it to a string we can do comparison against
def format_time():
    now = datetime.now()
    now_weekday = datetime.now().weekday() + 1
    return now.strftime(str(now_weekday) + " %H %M")


def write_time():
    now = datetime.now()
    return now.strftime("%a %H:%M")


# Writes feed actions to table for the feed log on the viewing page
def db_write_log(uid, fTime, fType):
    addFeed = feedTimes(userID=uid, feed_time=fTime, feed_type=fType)
    db.session.add(addFeed)
    db.session.commit()


# This executes the motor spin script in motor_pi.py
def instant_feed(motor, run):
    try:
        motor.spin(run)
    except Exception as e:
        bbLog.info("An error occurred with the motor.")
        bbLog.info(e)
    else:
        bbLog.info("Motor function was successful.")


# This function is called every minute from a thread started in __init__
def check_feed():
    format_now = format_time()  # Gets the current time and converts it to a string we can do comparison against
    resultQuery = attributes.query.filter_by(scheduleFeed=1).all()
    try:
        bbLog.info("Time now: " + format_now)
        # Query the DB and get days the feeder should run. This will be returned as a string of numbers, w/ 1 being Mon
        # Ex: Feeder is supposed to run M W F. String from DB would be 135
        # i is the position in the string, v is the value in that position
        for query in resultQuery:
            user = users.query.filter_by(id=query.userID).first()
            bbLog.info(str(users.query.filter_by(id=query.userID).first()))
            for i, v in enumerate(str(query.feedDays)):
                # Create string to match above in format Day Hour Minute. Hour and Minute pulled from DB entry directly
                result = v + " " + str(query.feedHour) + " " + str(query.feedMinute)
                # If the current time == the time in the DB run the motor
                if format_now == result:
                    db_write_log(user.username, write_time(), 'scheduled')
                    instant_feed(motor_pi.motor(), run=True)
                else:
                    bbLog.info("    Time Feed: "+result)
    except:
        bbLog.info("An error occurred while checking the scheduled feed.")
    else:
        bbLog.info("Successfully checked the scheduled feed.")


# DB stores feed days as a string of integers, with 1 representing Monday, 2 representing Tuesday and so on
# Monday can't start at 0 because when this gets pulled from the DB Python interprets it as an int and drops leading 0s
# It is easier to pass nums as strings because the datetime function returns day of week as an integer
# See schedule_pi.py for more info
def get_feed_days(mon, tue, wed, thur, fri, sat, sun):
    feed_days = ""
    if mon:
        feed_days = feed_days + "1"
    if tue:
        feed_days = feed_days + "2"
    if wed:
        feed_days = feed_days + "3"
    if thur:
        feed_days = feed_days + "4"
    if fri:
        feed_days = feed_days + "5"
    if sat:
        feed_days = feed_days + "6"
    if sun:
        feed_days = feed_days + "7"
    return feed_days


# Settings Page Conversion Functions #
# These functions are for converting bools to ints for the form to the database, or vice versa for db to python logic
# TODO: Look into moving these inside the classes in models
# def convert_feed_from_form(feed_checkbox):
#     if feed_checkbox:
#         return 1
#     else:
#         return 0
#
#
# def convert_feed_from_db(feed_query):
#     if feed_query == 1:
#         return True
#     else:
#         return False


# Radio buttons return string values
def convert_can_feed_from_form(feed_option):
    # Radio buttons return strings while check boxes return actual booleans
    if feed_option == 'True' or feed_option == True:
        return 1
    else:
        return 0


def convert_can_feed_from_db(can_feed_query):
    if can_feed_query == 1:
        return True
    else:
        return False

# End Settings Conversion Functions #


def get_Feed_Schedule(userID):
# Get every field from the attributes table which has scheduledFeed = 1
    # This amounts to every user who has a feed scheduled
    if userID == 'all':
        all_feeds = attributes.query.filter_by(scheduleFeed=1).all()
    else:
        all_feeds = attributes.query.filter_by(userID=userID).all()
    # Empty list which will be filled by feedTimeObjects
    if all_feeds is not None:
        feed_times = []

        for feed in all_feeds:
            # Create a new empty FeedTimeObject
            this_feed_time = feed_obj.FeedTimeObject()

            usr = users.query.filter_by(id=feed.userID).first()
            # Fill the feed time object
            this_feed_time.set_feed_creator(usr.username)
            this_feed_time.set_feed_days(feed.feedDays)
            this_feed_time.feed_hour = str(feed.feedHour)
            this_feed_time.feed_minute = str(feed.feedMinute)
            this_feed_time.set_feed_time(str(feed.feedHour) + ":" + str(feed.feedMinute))
            # Add the feed time object to the end of a list
            feed_times.append(this_feed_time)

        # Pass the feed_times list of FeedTime Objects to the web page
        return feed_times
    else:
        return None


def get_user_theme():
    attr = attributes.query.filter_by(userID=current_user.get_id()).first()
    return attr.style
