from flask import Blueprint, render_template, session, redirect, request, abort, url_for, jsonify, flash
from flask_login import login_required, current_user
from app.users.forms import UserForm
from flask_mail import Message
from app import mail
from datetime import date, timedelta
import datetime
from datetime import datetime


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()

    return wrapper, url_for, flash
from app.users.forms import EventForm
import app.models as models
from cloudinary.uploader import upload
from app import mysql, IntegrityError
routes = Blueprint('routes', __name__)

@routes.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

@routes.route('/')
def landing_page():
    return render_template("landing_page.html")

# Used for showing the pages in landing page (no events page yet)
# @routes.route('/')
# def landing_page():
#     return render_template("event_description_facilitator.html")

# Used for showing the pages in landing page (no events page yet)
# @routes.route('/')
# def landing_page():
#     return render_template("event_description_facilitator.html")

@routes.route('/home', methods=['POST', 'GET'])
def home():
    switch = request.args.get('switch')

    ongoing_events = models.Events.get_current_events()
    total_ongoing_events = sum(len(event_batch) for event_batch in ongoing_events)


    if request.method == "POST":
        return redirect('/logout')

    try:
        if session["logged_in"] and switch == None:
            if session['is_facilitator']:
                return render_template("home_facilitator.html",
                                       ongoing_events=enumerate(ongoing_events),
                                       total_ongoing_events=total_ongoing_events)
            elif session['is_facilitator'] == None:
                redirect('/')
            else:

                return render_template("index_home2.html",
                                       ongoing_events=enumerate(ongoing_events),
                                       total_ongoing_events=total_ongoing_events)
            
        elif switch == "faci":
            print("Switching to reg...")
            return render_template("index_home2.html",
                                   ongoing_events=enumerate(ongoing_events),
                                   total_ongoing_events=total_ongoing_events)
        elif switch == "reg":
            print("Switching to faci...")
            return render_template("home_facilitator.html", 
                                   ongoing_events=enumerate(ongoing_events),
                                   total_ongoing_events=total_ongoing_events)
    except KeyError:
        return redirect('/')

@routes.route("/logout")
def logout():
    
    session.pop('userID', None)
    session.pop('is_facilitator', None)
    session.clear()
    
    session["is_facilitator"] = None
    return redirect('/')

@routes.route('/about')
def about_page():
    return render_template('about.html')

@routes.route('/aboutf')
def about_page2():
    return render_template('aboutf.html')
    
@routes.route("/profile_facilitator")
def profile_facilitator():
    # Check if the user is logged in
    if 'user_id' in session:
        user_id = session['user_id']
        user_info = models.Users.get_user_info(user_id)  # Fetch user information from the database
        if user_info:
            return render_template('index_profile.html', user_info=user_info)

@routes.route("/edit_profile_facilitator", methods=['GET'])
def edit_facilitator_form():
    # Check if the user is logged in
    if 'user_id' in session:
        user_id = session['user_id']
        user_info = models.Users.get_user_info(user_id, used_for="edit")  # Fetch user information from the database
        
        form = UserForm(obj=user_info)  # Instantiate the form with existing data
        # course_options = models.CollegeCourse.getcourse()
        return render_template('edit_profile.html', form=form, user_info=user_info)

@routes.route("/edit_profile_facilitator", methods=['POST'])
def edit_facilitator():
    if request.method == 'POST':
        user_id = session['user_id']  # Retrieve user ID from the session
        new_college = request.form.get('college')
        new_course = request.form.get('course')
        new_year = request.form.get('year_level')
        
        # Update the user's information in the database
        models.Users.update(user_id, new_college, new_course, new_year)
        
        flash("Profile edited successfully.")

        # Redirect to the profile page
        return redirect(url_for('routes.profile_facilitator'))

@routes.route("/profile_user")
def profile_regular():
    # Check if the user is logged in
    if 'user_id' in session:
        user_id = session['user_id']
        user_info = models.Users.get_user_info(user_id)  # Fetch user information from the database
        if user_info:
            return render_template('index_profile2.html', user_info=user_info)

@routes.route('/edit_profile_regular', methods=['GET', 'POST'])
def edit_regular():
    if request.method == 'POST':
        user_id = session['user_id']  # Retrieve user ID from the session
        new_college = request.form.get('college')
        new_course = request.form.get('course')
        new_year = request.form.get('year_level')
        
        # Update the user's information in the database
        models.Users.update(user_id, new_college, new_course, new_year)
        
        flash("Profile edited successfully.")

        # Redirect to the profile page
        return redirect(url_for('routes.profile_regular'))



    # Fetch user info from the database
    user_info = models.Users.get_user_info(session['user_id'], used_for="edit")
    form = UserForm(obj=user_info)  # Instantiate the form with existing data
    course_options = models.CollegeCourse.getcourse()
    return render_template('edit_profile2.html', form=form, user_info=user_info)








@routes.route('/r_events')
def events_regular():
    all_events = models.Events.get_all_events()
    current_events = models.Events.get_current_events()
    upcoming_events = models.Events.get_upcoming_events()
    past_events = models.Events.get_past_events()

    total_all_events = sum(len(event_batch) for event_batch in all_events)
    total_current_events = sum(len(event_batch) for event_batch in current_events)
    total_upcoming_events = sum(len(event_batch) for event_batch in upcoming_events)
    total_past_events = sum(len(event_batch) for event_batch in past_events)

    return render_template('events_page2.html',
                           all_events=enumerate(all_events),
                           current_events=enumerate(current_events),
                           upcoming_events=enumerate(upcoming_events),
                           past_events=enumerate(past_events),
                           total_all_events=total_all_events,
                           total_current_events=total_current_events,
                           total_upcoming_events=total_upcoming_events,
                           total_past_events=total_past_events)

@routes.route('/f_events')
def events_faci():
    all_events = models.Events.get_all_events()
    current_events = models.Events.get_current_events()
    upcoming_events = models.Events.get_upcoming_events()
    past_events = models.Events.get_past_events()

    total_all_events = sum(len(event_batch) for event_batch in all_events)
    total_current_events = sum(len(event_batch) for event_batch in current_events)
    total_upcoming_events = sum(len(event_batch) for event_batch in upcoming_events)
    total_past_events = sum(len(event_batch) for event_batch in past_events)

    return render_template('events_page.html',
                           all_events=enumerate(all_events),
                           current_events=enumerate(current_events),
                           upcoming_events=enumerate(upcoming_events),
                           past_events=enumerate(past_events),
                           total_all_events=total_all_events,
                           total_current_events=total_current_events,
                           total_upcoming_events=total_upcoming_events,
                           total_past_events=total_past_events)
# Gon
@routes.route('/event/<string:event_id>')
def display_event(event_id):
    event = models.Events.event_description(event_id)
    joined = models.UserEvents.is_joined(session["user_id"], event_id)
    no_of_participants = models.Events.no_of_participants(event_id)
    return render_template('event_description.html', event=event, joined=joined, no_of_participants=no_of_participants)

@routes.route('/eventj/<string:event_id>')
def display_event_j(event_id):
    faci = request.args.get("faci")
    
    event = models.Events.event_description(event_id)
    
    # Check if the user is already a participant
    joined = models.UserEvents.is_joined(session["user_id"], event_id)
    
    if joined:
        flash(f'You are already a participant in "{event.name}".')
        return redirect(url_for('routes.display_event', event_id=event_id))

    join = models.UserEvents.join(event_id, event.participant_limit)
    no_of_participants = models.Events.no_of_participants(event_id)

    if join == "MAX_PARTICIPANTS_REACHED":
        flash("Sorry, the event is already full.")
        return redirect(url_for('routes.display_event', event_id=event_id))

    flash(f'You have joined "{event.name}".')
    owned = models.Events.is_creator(session["user_id"], event_id)
    if faci:
        return render_template('event_description_facilitator.html', joined=joined, join=join, event=event, no_of_participants=no_of_participants, owned=owned)

    return render_template('event_description.html', joined=joined, join=join, event=event, no_of_participants=no_of_participants)

@routes.route('/eventl/<string:event_id>')
def display_event_l(event_id):
    faci = request.args.get("faci")
    event = models.Events.event_description(event_id)
    leave = models.UserEvents.un_join(event_id, event.participant_limit)

    no_of_participants = models.Events.no_of_participants(event_id)

    joined = models.UserEvents.is_joined(session["user_id"], event_id)
    flash(f'You have left "{event.name}".')

    owned = models.Events.is_creator(session["user_id"], event_id)
    if faci:
        return render_template('event_description_facilitator.html', joined=joined, leave=leave, event=event, no_of_participants=no_of_participants, owned=owned)

    return render_template('event_description.html', joined=joined, leave=leave, event=event, no_of_participants=no_of_participants)

@routes.route('/faci_event/<string:event_id>')
def delete_event(event_id):
    event = models.Events.event_description(event_id)
    delete = models.Events.delete_event(event_id)
    
    flash(f'Event "{event.name}" is deleted.')
    
    return redirect(url_for('routes.events_faci'))

@routes.route('/faci_event_postponed/<string:event_id>', methods = ['POST', 'GET'])
def postpone_event(event_id):
    event = models.Events.event_description(event_id)
    event.postpone_event(event_id)
    
    flash(f'Event "{event.name}" is postponed.')
    owned = models.Events.is_creator(session["user_id"], event_id)

    users = models.Events.get_participants(event_id)
    recipient_emails = [user[0] for user in users]

    event_url = f"http://127.0.0.1:5555/eventj/{event_id}"

    with mail.connect() as connection:
        for recipient_email in recipient_emails:
            message = Message (
                subject = "EVENT POSTPONED",
                recipients = [recipient_email],
                sender = ('MyEvents', 'myiitevents@mailtrap.com'),
                #body = 'This event has been postponed, Please wait for further notice.'
                html = render_template('postpone_notif_email.html', eventname=event.name, event_url = event_url)
                )
            connection.send(message)
    #return render_template('event_description_facilitator.html', event=event, owned=owned)
    return redirect(url_for('routes.display_event_faci', event_id = event_id, owned = owned))

@routes.route('/notify_participants/<string:event_id>', methods = ['POST', 'GET'])
def notify(event_id):
    event = models.Events.event_description(event_id)

    flash(f'All participants has been notified.')
    owned = models.Events.is_creator(session["user_id"], event_id)
    users = models.Events.get_participants(event_id)
    recipient_emails = [user[0] for user in users]

    current_time = datetime.now()

    # Event start and end times as strings
    event_start_time_str = event.DateTimeStart 
    event_end_time_str = event.DateTimeEnd  

    # Parse the event start and end times to datetime objects
    event_start_time = datetime.strptime(event_start_time_str, "%B %d, %Y %I:%M %p")
    event_end_time = datetime.strptime(event_end_time_str, "%B %d, %Y %I:%M %p")
    time_remaining = event_start_time - current_time

    print(current_time)
    print(event_start_time)
    print(event_end_time)
    print(time_remaining)
    
    event_url = f"http://127.0.0.1:5555/eventj/{event_id}"



    with mail.connect() as connection:
        for recipient_email in recipient_emails:
            time_remaining = event_start_time - current_time
            hours, seconds = divmod(int(time_remaining.total_seconds()), 3600)
            minutes = seconds // 60

            # Format the remaining hours and minutes as a string
            countdown = f"{hours} hours and {minutes} minutes."
            if event_start_time > datetime.now():
                message = Message (
                    subject = "EVENT REMINDER",
                    recipients = [recipient_email],
                    sender = ('MyEvents', 'myiitevents@mailtrap.com'),
                    #body = 'Good day, event name starts in somethinghours '
                    html = render_template('notifemail.html', eventname=event.name, countdown=countdown, event_url = event_url)
                    )
                connection.send(message)
            elif (event_start_time == datetime.now() or event_start_time < datetime.now()) and event_end_time > datetime.now():
                message = Message (
                    subject = "EVENT REMINDER",
                    recipients = [recipient_email],
                    sender = ('MyEvents', 'myiitevents@mailtrap.com'),
                    #body = 'Good day, event name starts in somethinghours '
                    html = render_template('ongoing_notif.html', eventname=event.name, countdown=countdown, event_url = event_url)
                    )
                connection.send(message)
            elif event_end_time < datetime.now():
                message = Message (
                    subject = "EVENT REMINDER",
                    recipients = [recipient_email],
                    sender = ('MyEvents', 'myiitevents@mailtrap.com'),
                    #body = 'Good day, event name starts in somethinghours '
                    html = render_template('ended_notif.html', eventname=event.name, countdown=countdown, event_url = event_url)
                    )
                connection.send(message)
            else:
                message = Message (
                    subject = "EVENT REMINDER",
                    recipients = [recipient_email],
                    sender = ('MyEvents', 'myiitevents@mailtrap.com'),
                    #body = 'Good day, event name starts in somethinghours '
                    html = render_template('notifemail.html', eventname=event.name, countdown=countdown, event_url = event_url)
                    )
                connection.send(message)

    #return render_template('event_description_facilitator.html', event=event, owned=owned)
    return redirect(url_for('routes.display_event_faci', event_id = event_id, owned = owned))
    


@routes.route('/faci_event_canceled/<string:event_id>', methods = ['POST', 'GET'])
def cancel_event(event_id):
    event = models.Events.event_description(event_id)
    event.cancel_event(event_id)
    
    flash(f'Event "{event.name}" is canceled.')
    owned = models.Events.is_creator(session["user_id"], event_id)
    users = models.Events.get_participants(event_id)
    recipient_emails = [user[0] for user in users]

    event_url = f"http://127.0.0.1:5555/eventj/{event_id}"

    with mail.connect() as connection:
        for recipient_email in recipient_emails:
            message = Message (
                subject = "EVENT CANCELLED",
                recipients = [recipient_email],
                sender = ('MyEvents', 'myiitevents@mailtrap.com'),
                #body = 'This event has been cancelled and will no longer be resumed.'
                html = render_template('cancel_notif_email.html', eventname=event.name, event_url = event_url)
                )
            connection.send(message)
    #return render_template('event_description_facilitator.html', event=event, owned=owned)
    return redirect(url_for('routes.display_event_faci', event_id = event_id, owned = owned))

# Gon
@routes.route('/event_f/<string:event_id>', methods = ['POST', 'GET'])
def display_event_faci(event_id):
    event = models.Events.event_description(event_id)  
    print(event)
    owned = models.Events.is_creator(session["user_id"], event_id)
    no_of_participants = models.Events.no_of_participants(event_id)
    return render_template('event_description_facilitator.html', event=event, owned=owned, no_of_participants=no_of_participants)



# Gon additions for JS ajax

@routes.route("/course_dropdown")
def course_dropdown():
    college = request.args['college']
    
    
    # since you have the college value, use it in models.py to get all courses belonging in that college

    courses = models.CollegeCourse.courses_from_college(college)
    course_list = []

    for course in courses:
        courseObj = {}
        courseObj['name'] = course
        course_list.append(courseObj)

    return jsonify({'courses': course_list})

@routes.route('/CreateEvent', methods=['POST', 'GET'])
def create_event():
    form = EventForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            img_url = None
            if form.image.data:
                f = request.files[form.image.name].read()
                response = upload(f, folder="Events Image")
                img_url = response['url']
            else:
                img_url = "https://placehold.jp/300x300.png"

            # Validate hashtags
            hashtags = form.hashtags.data
            if not validate_hashtags(hashtags):
                flash('Event tags must start with "#" and you can add up to 5 tags only.', 'danger')
                return render_template('create_event.html', form=form)

            event = models.Events(
                name=form.eventname.data,
                description=form.description.data,
                location=form.location.data,
                DateTimeStart=form.DateTimeStart.data,
                DateTimeEnd=form.DateTimeEnd.data,
                img_url=img_url,
                participant_limit=form.participant_limit.data,
                hashtags=hashtags
            )

            try:
                event.addevent()
                flash('Event created successfully.')
                return redirect(url_for('routes.events_faci'))
            except IntegrityError as e:
                if "UNIQUE constraint failed" in str(e.args):
                    flash('Error: Event with this ID already exists.', 'danger')
                else:
                    flash('Error: Failed to add event.', 'danger')
        else:
            flash('Error: All fields are required.', 'danger')
    return render_template('create_event.html', form=form)


def validate_hashtags(hashtags):
    # Split hashtags by space and filter out empty strings
    tags = [tag for tag in hashtags.split() if tag.strip()]
    if len(tags) > 5:
        return False
    for tag in tags:
        if not tag.startswith("#"):
            return False
    return True


# Attendance Page

@routes.route("/attendance_page/<string:event_id>", methods = ['POST','GET'])
def attendance_page(event_id):
    event = models.Events.event_description(event_id)

    day = request.args.get('day')

    hold1 = datetime.strptime(event.DateTimeStart, '%B %d, %Y %I:%M %p')
    hold2 = datetime.strptime(event.DateTimeEnd, '%B %d, %Y %I:%M %p')
    event.DateTimeStart = hold1.strftime("%Y-%m-%d")
    event.DateTimeEnd = hold2.strftime("%Y-%m-%d")

    event.DateTimeStart = datetime.strptime(event.DateTimeStart, "%Y-%m-%d").date()
    event.DateTimeEnd = datetime.strptime(event.DateTimeEnd, "%Y-%m-%d").date()

    # date of that specific attendance page
    
    
    attendance_date = event.DateTimeStart + timedelta(days=int(day)-1)

    day_interval = event.DateTimeEnd - event.DateTimeStart
    day_interval = day_interval.days + 1 # + 1 so that the last day will be included

    print("yahoo")
    print(event.DateTimeStart)
    print(day_interval)

    attendance_list = models.Attendance.by_date(event_id, attendance_date)
    
    curr_date = date.today()
    curr_date = curr_date.strftime("%Y-%m-%d")
    
    attendance_list = models.Attendance.by_date(event_id, attendance_date)

    curr_date = date.today()
    curr_date = curr_date.strftime("%Y-%m-%d")

    return render_template("attendance_page.html", attendance_list=attendance_list, event = event, day=int(day), day_interval=day_interval, attendance_date = attendance_date.strftime('%B %d, %Y'))

@routes.route("/attendance_page_facilitator/<string:event_id>", methods=['POST', 'GET'])
def attendance_page_facilitator(event_id):
    event = models.Events.event_description(event_id) 
    
    day = request.args.get('day')
    print("day is the :", day)

    hold1 = datetime.strptime(event.DateTimeStart, '%B %d, %Y %I:%M %p')
    hold2 = datetime.strptime(event.DateTimeEnd, '%B %d, %Y %I:%M %p')
    event.DateTimeStart = hold1.strftime("%Y-%m-%d")
    event.DateTimeEnd = hold2.strftime("%Y-%m-%d")

    event.DateTimeStart = datetime.strptime(event.DateTimeStart, "%Y-%m-%d").date()
    event.DateTimeEnd = datetime.strptime(event.DateTimeEnd, "%Y-%m-%d").date()

    # date of that specific attendance page
    aw = timedelta(days=int(day)-1)
    print(type(event.DateTimeStart), "+", type(aw))
    attendance_date = event.DateTimeStart + timedelta(days=int(day)-1)

    day_interval = event.DateTimeEnd - event.DateTimeStart
    day_interval = day_interval.days + 1 # + 1 so that the last day will be included

    print("yahoo")
    print(event.DateTimeStart)
    print(day_interval)

    attendance_list = models.Attendance.by_date(event_id, attendance_date)
    
    curr_date = date.today()
    curr_date = curr_date.strftime("%Y-%m-%d")

    disableAdd = False
    print(attendance_date, "attendance date and currdate", curr_date)
    if str(attendance_date) != str(curr_date):
        disableAdd = True
    
    return render_template("attendance_page_facilitator.html", disableAdd=disableAdd, attendance_list=attendance_list, event = event, day=int(day), day_interval=day_interval, attendance_date = attendance_date.strftime('%B %d, %Y'))


@routes.route("/add_attendance/<string:event_id>", methods=['POST', 'GET'])
def add_attendance(event_id):
    event = models.Events.event_description(event_id) 
    student_id = request.args['studentId']

    day = request.args.get('day')
    converted = datetime.strptime(event.DateTimeStart, '%B %d, %Y %I:%M %p')
    
    event.DateTimeStart = converted.date()
    
    attendance_date = event.DateTimeStart + timedelta(days=int(day)-1)

    if student_id == '':
        attendance_list = models.Attendance.by_date(event_id, attendance_date)
    else:
        print(student_id, "is the student ID")
        try:
            catch = models.Attendance.add(student_id, event_id)
            print(catch)
            attendance_list = models.Attendance.by_date(event_id, attendance_date)

            if catch == "not_joined" or catch == "in_attendance":
                return catch
            
            
        except:
            return event_id
    return render_template('attendance_table_gen.html', attendance_list=attendance_list, event = event)

@routes.route("/search_attendance/<string:event_id>", methods=['POST', 'GET'])
def search_attendance(event_id):
    event = models.Events.event_description(event_id)
    searchText = request.args['searchText']

    day = request.args.get('day')

    # date of that specific attendance page
    converted = datetime.strptime(event.DateTimeStart, '%B %d, %Y %I:%M %p')
    
    event.DateTimeStart = converted.date()
    attendance_date = event.DateTimeStart + timedelta(days=int(day)-1)
    
    if searchText == '':
        attendance_list = models.Attendance.by_date(event_id, attendance_date)
    else:
        
        attendance_list = models.Attendance.search(searchText, event_id, attendance_date)
    return render_template('attendance_table_gen.html', attendance_list=attendance_list, event = event)

# List Of Events

@routes.route("/listofevents", methods = ['POST', 'GET'])
def Levents():
    card = models.Events()
    cards = []
    try:
        events = card.get_eventreg()
    except:
        events = []

    for event in events:
        description = event[3] if len(event[2]) <= 69 else event[2][:66] + "..."
        cards.append({
            "event_id": event[0],
            "image_src": event[1],
            "title": event[2],
            "description": description,
            "Location": event[4],
            "DateStart": event[5],
        })

    return render_template("index_ListofEvents.html", cards = cards)

@routes.route("/listofeventsregfilter", methods=['POST', 'GET'])
def LeventsFilter():
    filter_type = request.args.get('filter_type', 'all')
    card = models.Events()
    cards = []

    if filter_type == 'regular_all':
        try:
            events = card.get_eventreg()  # Modify this function to fetch all events
        except:
            events = []
    elif filter_type == 'regular_past':
        try:
            events = card.get_pastreg()  # Modify this function to fetch past events
        except:
            events = []
    elif filter_type == 'regular_current':
        try:
            events = card.get_currentreg()  # Modify this function to fetch past events
        except:
            events = []
    elif filter_type == 'regular_upcoming':
        try:
            events = card.get_futurereg()  # Modify this function to fetch upcoming events
        except:
            events = []
    else:
        try:
            print('No events Found')
        except:
            events = []

    for event in events:
        description = event[3] if len(event[2]) <= 69 else event[2][:66] + "..."
        cards.append({
            "event_id": event[0],
            "image_src": event[1],
            "title": event[2],
            "description": description,
            "Location": event[4],
            "DateStart": event[5],
        })
    
    return render_template("index_ListofEvents.html", cards=cards)

@routes.route("/listofeventsf", methods = ['POST', 'GET'])
def Levents2():
    id = session['user_id']
    card = models.Events()
    cards = []
    try:
        events = card.get_event()
    except:
        events = []

    for event in events:
        description = event[3] if len(event[2]) <= 20 else event[2][:20] + "..."
        cards.append({
            "event_id": event[0],
            "image_src": event[1],
            "title": event[2],
            "description": description,
            "Location": event[4],
            "DateStart": event[5],
        })
    
    return render_template("index_ListofEventsF.html", cards=cards)

@routes.route("/listofeventsfilter", methods=['POST', 'GET'])
def Levents2Filter():
    filter_type = request.args.get('filter_type', 'all')
    card = models.Events()
    cards = []
    

    if filter_type == 'all':
        try:
            events = card.get_event()  # Modify this function to fetch all events
        except:
            events = []
    elif filter_type == 'past':
        try:
            events = card.get_past()  # Modify this function to fetch past events
        except:
            events = []
    elif filter_type == 'current':
        try:
            events = card.get_current()  # Modify this function to fetch past events
        except:
            events = []
    elif filter_type == 'upcoming':
        try:
            events = card.get_future()  # Modify this function to fetch upcoming events
        except:
            events = []
    else:
        try:
            print('No events Found')
        except:
            events = []

    for event in events:
        description = event[3] if len(event[2]) <= 69 else event[2][:66] + "..."
        cards.append({
            "event_id": event[0],
            "image_src": event[1],
            "title": event[2],
            "description": description,
            "Location": event[4],
            "DateStart": event[5],
        })
    return render_template("index_ListofEventsF.html", cards=cards)


@routes.route('/edit_event/<string:event_id>', methods =['POST', 'GET'])
def edit_evs(event_id):
    event = models.Events.get_edit_event(event_id)
    form = EventForm(obj=event)

    if request.method == 'POST':
        img_url = event.img_url  # Default to existing image URL

        if form.image.data:
            f = request.files[form.image.name].read()
            response = upload(f, folder="Events Image")
            img_url = response['url']

        event.name = form.eventname.data
        event.description = form.description.data
        event.location = form.location.data
        event.DateTimeStart = form.DateTimeStart.data
        event.DateTimeEnd = form.DateTimeEnd.data
        event.img_url = img_url
        event.participant_limit = form.participant_limit.data
        event.hashtags = form.hashtags.data
        event.event_id

        # Validate hashtags
        hashtags = form.hashtags.data
        if not validate_hashtags(hashtags):
            flash('Event tags must start with "#" and you can add up to 5 tags only.', 'danger')
            return render_template('edit_event_faci.html', form=form, event=event)

        try:
            event.update_event(event_id)
            flash('Event updated successfully.')
            owned = models.Events.is_creator(session["user_id"], event_id)
            return redirect(url_for('routes.display_event_faci', event_id=event_id, owned=owned))
        except Exception as e:
            flash('Error: Failed to update event. Please input valid data.', 'danger')

    return render_template('edit_event_faci.html', form=form, event=event)



@routes.route('/event_search_results', methods=['GET', 'POST'])
def search_results():
    card = models.Events()
    cards = []

    searchText = request.args.get('searchText')  # Get the search text from query parameters
    filterField = request.args.get('filterField')  

    try:
        events = card.search_events(searchText)
    except:
        events = []

    for event in events:
        description = event[3] if len(event[2]) <= 69 else event[2][:66] + "..."
        cards.append({
            "event_id": event[0],
            "image_src": event[1],
            "title": event[2],
            "description": description,
            "Location": event[4],
            "DateStart": event[5],
            "hashtags": event[7]
        })

    filtered_cards = []

    for event in cards:
        if filterField == 'title' and searchText.lower() in event['title'].lower():
            filtered_cards.append(event)
        elif filterField == 'hashtags' and searchText.lower() in event['hashtags'].lower():
            filtered_cards.append(event)
        elif filterField == 'location' and searchText.lower() in event['Location'].lower():
            filtered_cards.append(event)
        
    if not filtered_cards:
        truncated_searchText = searchText[:30] + '...' if len(searchText) > 30 else searchText
        flash(f"No events found for '{truncated_searchText}' in the selected category.", "error")

    return render_template("search_ev_faci.html", cards=filtered_cards, searchText=searchText)


@routes.route('/search_resultsss', methods=['GET', 'POST'])
def search_results_reg():
    card = models.Events()
    cards = []

    searchText = request.args.get('searchText')  # Get the search text from query parameters
    filterField = request.args.get('filterField')  

    try:
        events = card.search_events(searchText)
    except:
        events = []

    for event in events:
        description = event[3] if len(event[2]) <= 69 else event[2][:66] + "..."
        cards.append({
            "event_id": event[0],
            "image_src": event[1],
            "title": event[2],
            "description": description,
            "Location": event[4],
            "DateStart": event[5],
            "hashtags": event[7]
        })

    filtered_cards = []

    for event in cards:
        if filterField == 'title' and searchText.lower() in event['title'].lower():
            filtered_cards.append(event)
        elif filterField == 'hashtags' and searchText.lower() in event['hashtags'].lower():
            filtered_cards.append(event)
        elif filterField == 'location' and searchText.lower() in event['Location'].lower():
            filtered_cards.append(event)
        
    
    if not filtered_cards:
        truncated_searchText = searchText[:30] + '...' if len(searchText) > 30 else searchText
        flash(f"No events found for '{truncated_searchText}' in the selected category.", "error")

    return render_template("search_ev_reg.html", cards=filtered_cards, searchText=searchText)
