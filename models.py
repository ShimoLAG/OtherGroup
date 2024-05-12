from app import mysql
from flask import session, flash
import uuid
from datetime import datetime
import datetime


class Users(object):

    def __init__(self, id=None, email=None, \
        name=None, is_facilitator=None, \
        college=None, course=None, year_level=None):
        self.id = id
        self.email = email
        self.name = name
        self.is_facilitator = is_facilitator
        self.college = college
        self.course = course
        self.year_level = year_level

    def add(self):
        cursor = mysql.connection.cursor()


        sql = f"INSERT INTO User (id, email, name, is_facilitator, \
            college, course, year_level) VALUES ('{self.id}', '{self.email}', '{self.name}', \
            {self.is_facilitator}, '{self.college}', '{self.course}', '{self.year_level}')"
        
        cursor.execute(sql)
        mysql.connection.commit()

    

    @classmethod
    def login_or_signup(cls, login_email):

        cursor = mysql.connection.cursor()

        sql = f"SELECT if(email='{login_email}', True, False) as email FROM User WHERE email='{login_email}'"
        
        cursor.execute(sql)
        result = cursor.fetchone()
        return result

    @classmethod
    def get_id(cls, email):

        cursor = mysql.connection.cursor()

        sql = f"SELECT id, is_facilitator from User WHERE email='{email}';" 

        cursor.execute(sql)
        result = cursor.fetchall()
        return result
    
    @classmethod
    def get_user_data(cls, user_id):
        cursor = mysql.connection.cursor()

        sql = f"SELECT college, course, year_level FROM User WHERE id='{user_id}'"
        cursor.execute(sql)
        result = cursor.fetchone()
        
        if result:
            user_data = {
                "college": result["college"],
                "course": result["course"],
                "year_level": result["year_level"]
            }
            return user_data
        else:
            return None

    @classmethod
    def all(cls):
        cursor = mysql.connection.cursor()

        sql = "SELECT * from User"
        cursor.execute(sql)
        result = cursor.fetchall()
        return result

    @classmethod
    def delete(cls, id):
        try:
            cursor = mysql.connection.cursor()
            sql = f"DELETE from users where id= {id}"
            cursor.execute(sql)
            mysql.connection.commit()
            return True
        except:
            return False
    
    @classmethod
    def update(cls, user_id, new_college, new_course, new_year):
        try:
            with mysql.connection.cursor() as cursor:
                query = "UPDATE User SET college = %s, course = %s, year_level = %s WHERE id = %s"
                print("Executing query:", query)
                print("Parameters:", (new_college, new_course, new_year, user_id))
                cursor.execute(query, (new_college, new_course, new_year, user_id))
                mysql.connection.commit()
                print("User information updated successfully.")
        except Exception as e:
            print("Error updating user:", e)
            mysql.connection.rollback()


    @classmethod
    def get_user_info(cls, user_id, used_for=None):
        cursor = mysql.connection.cursor()
        sql = "SELECT college, course, year_level FROM User WHERE id = %s"
        cursor.execute(sql, (user_id,))
        user_info = cursor.fetchone()
        if used_for == 'edit':
            
            user_info = cls(college=user_info[0], course=user_info[1], year_level=user_info[2])
        cursor.close()
    
        return user_info
    
    

class CollegeCourse(object):
    def __init__(self):
        pass

    @classmethod
    def getcourse(cls):
        cursor = mysql.connection.cursor()

        sql = "SELECT course FROM CollegeCourse"
        cursor.execute(sql)
        result = cursor.fetchall()
        return result
    
    @classmethod
    def courses_from_college(cls, college):
        cursor = mysql.connection.cursor()

        sql = "SELECT course FROM CollegeCourse WHERE college=%s"
        values = (college,)
        cursor.execute(sql, values)
        result = cursor.fetchall()
        return result

class Events(object):
    def __init__(self, id = None, event_id=None, name=None, description=None, location=None, DateTimeStart=None, DateTimeEnd = None, img_url = None, status = None, participant_limit = None, hashtags = None):
        self.id = id
        self.event_id = event_id
        self.name = name
        self.description = description
        self.location = location
        self.DateTimeStart = DateTimeStart
        self.DateTimeEnd = DateTimeEnd        
        self.img_url = img_url
        self.status = status
        self.participant_limit = participant_limit
        self.hashtags = hashtags

    @classmethod
    def no_of_participants(cls, event_id):
        cursor = mysql.connection.cursor()
        sql = "SELECT COUNT(*) FROM user_events WHERE event_id=%s"
        values = (event_id,)
        cursor.execute(sql, values)
        result = cursor.fetchone()
        print("THIS IS RESULT", result)
        return result[0]

    def addevent(self):
        cursor = mysql.connection.cursor()
        ape = session['user_id']
        ayde = str(uuid.uuid4())

        print("Generated UUID:", ayde)

        sql = "INSERT INTO event (id, f_id, name, location, DateTimeStart, DateTimeEnd, description, img_url, participant_limit, hashtags) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (ayde, ape, self.name, self.location, self.DateTimeStart, self.DateTimeEnd, self.description, self.img_url, int(self.participant_limit), self.hashtags)
        print(values)
        
        cursor.execute(sql, values)

        mysql.connection.commit()

    @classmethod
    def get_all_events(cls):
        cursor = mysql.connection.cursor()
        sql = "SELECT * FROM event"
        cursor.execute(sql)
        results = cursor.fetchall()
        events = []
        templist = []
        
        for result in results:
            event = cls(event_id=result[0], name=result[2], description=result[6],
                        location=result[3], DateTimeStart=result[4].strftime('%B %d, %Y %I:%M %p'), DateTimeEnd=result[5].strftime('%B %d, %Y %I:%M %p'),
                        img_url=result[7])
            templist.append(event)
            if len(templist) == 3:
                events.append(templist)
                templist = []

        # Append any remaining events in templist
        if templist:
            events.append(templist)

        return events
    
    @classmethod
    def get_current_events(cls):
        ''' Updated sql query for ongoing current events to display '''
        cursor = mysql.connection.cursor()
        sql = "SELECT img_url, name, description, location, DateTimeStart, DateTimeEnd, id FROM event WHERE DateTimeStart <= NOW() AND DateTimeEnd >= NOW();"
        cursor.execute(sql)
        results = cursor.fetchall()

        events = []
        templist = []
        
        for result in results:
            event = cls(name=result[1], description=result[2],
                        location=result[3], DateTimeStart=result[4].strftime('%B %d, %Y %I:%M %p'),
                        img_url=result[0], event_id=result[6], DateTimeEnd=result[5].strftime('%B %d, %Y %I:%M %p'))
            templist.append(event)
            if len(templist) == 3:
                events.append(templist)
                templist = []

        # Append any remaining events in templist
        if templist:
            events.append(templist)

        return events
    
    @classmethod
    def get_upcoming_events(cls):
        cursor = mysql.connection.cursor()
        sql = "SELECT img_url, name, description, location, DateTimeStart, DateTimeEnd, id FROM event WHERE DateTimeStart > NOW() AND DateTimeStart <= DateTimeEnd;"
        cursor.execute(sql)
        results = cursor.fetchall()

        events = []
        templist = []
        
        for result in results:
            event = cls(name=result[1], description=result[2],
                        location=result[3], DateTimeStart=result[4].strftime('%B %d, %Y %I:%M %p'),
                        img_url=result[0], event_id=result[6], DateTimeEnd=result[5].strftime('%B %d, %Y %I:%M %p'))
            templist.append(event)
            if len(templist) == 3:
                events.append(templist)
                templist = []

        # Append any remaining events in templist
        if templist:
            events.append(templist)

        return events
    
    @classmethod
    def get_past_events(cls):
        cursor = mysql.connection.cursor()
        sql = "SELECT img_url, name, description, location, DateTimeStart, DateTimeEnd, id FROM event WHERE DateTimeEnd < NOW();"
        cursor.execute(sql)
        results = cursor.fetchall()

        events = []
        templist = []
        
        for result in results:
            event = cls(name=result[1], description=result[2],
                        location=result[3], DateTimeStart=result[4].strftime('%B %d, %Y %I:%M %p'),
                        img_url=result[0], event_id=result[6], DateTimeEnd=result[5].strftime('%B %d, %Y %I:%M %p'))
            templist.append(event)
            if len(templist) == 3:
                events.append(templist)
                templist = []

        # Append any remaining events in templist
        if templist:
            events.append(templist)

        return events

    @classmethod
    def get_participants(cls, event_id):
        cursor = mysql.connection.cursor()

        sql = "SELECT u.email FROM user AS u INNER JOIN user_events AS ue ON u.id = ue.user_id WHERE ue.event_id = %s;"

        cursor.execute(sql, (event_id,))
        
        pariticpants = cursor.fetchall()
        
        print(pariticpants)
    
        return pariticpants
    




    # Bob
    def get_event(self):
        cursor = mysql.connection.cursor()
        ape = session['user_id']

        sql = "SELECT id, img_url, name, description, location, DATE_FORMAT(DateTimeStart, '%M %d, %Y %h:%i %p'), hashtags FROM event WHERE f_id = %s"
    
        # Execute the query with the parameter
        cursor.execute(sql, (ape,))
        events = cursor.fetchall()
    

        cursor.close()
        return events
    
    def get_eventreg(self):
        cursor = mysql.connection.cursor()
        ape = session['user_id']

        sql = "SELECT e.id, e.img_url, e.name, e.description, e.location, DATE_FORMAT(e.DateTimeStart, '%M %d, %Y %h:%i %p'), e.hashtags FROM event e INNER JOIN user_events ue WHERE ue.event_id = e.id AND ue.user_id = %s"
    
        # Execute the query with the parameter
        cursor.execute(sql, (ape,))
        regevents = cursor.fetchall()
    

        cursor.close()
        return regevents
    
    def get_past(self):
        cursor = mysql.connection.cursor()
        ape = session['user_id']

        sql = "SELECT id, img_url, name, description, location, DATE_FORMAT(DateTimeStart, '%M %d, %Y %h:%i %p'), hashtags FROM event WHERE f_id = %s AND DateTimeEnd < NOW();"
        cursor.execute(sql, (ape,))
        past_events = cursor.fetchall()

        cursor.close()
        return past_events
    
    def get_pastreg(self):
        cursor = mysql.connection.cursor()
        ape = session['user_id']

        sql = "SELECT e.id, e.img_url, e.name, e.description, e.location, DATE_FORMAT(e.DateTimeStart, '%M %d, %Y %h:%i %p'), e.hashtags FROM event e INNER JOIN user_events ue WHERE ue.event_id = e.id AND ue.user_id = %s AND DateTimeEnd < NOW();"
        cursor.execute(sql, (ape,))
        reg_past_events = cursor.fetchall()

        cursor.close()
        return reg_past_events

    def get_current(self):
        cursor = mysql.connection.cursor()
        ape = session['user_id']

        sql = "SELECT id, img_url, name, description, location, DATE_FORMAT(DateTimeStart, '%M %d, %Y %h:%i %p'), hashtags FROM event WHERE f_id = %s AND DateTimeStart <= NOW() AND DateTimeEnd >= NOW();"
        cursor.execute(sql, (ape,))
        curr_events = cursor.fetchall()

        cursor.close()
        return curr_events
    
    def get_currentreg(self):
        cursor = mysql.connection.cursor()
        ape = session['user_id']

        sql = "SELECT e.id, e.img_url, e.name, e.description, e.location, DATE_FORMAT(e.DateTimeStart, '%M %d, %Y %h:%i %p'), e.hashtags FROM event e INNER JOIN user_events ue WHERE ue.event_id = e.id AND ue.user_id = %s AND DateTimeStart <= NOW() AND DateTimeEnd >= NOW();"
        cursor.execute(sql, (ape,))
        reg_curr_events = cursor.fetchall()

        cursor.close()
        return reg_curr_events
    
    def get_future(self):
        cursor = mysql.connection.cursor()
        ape = session['user_id']

        
        sql = "SELECT id, img_url, name, description, location, DATE_FORMAT(DateTimeStart, '%M %d, %Y %h:%i %p'), hashtags FROM event WHERE f_id = %s AND DateTimeStart > NOW() AND DateTimeStart <= DateTimeEnd;"

        # Execute the query with the parameter
        cursor.execute(sql, (ape,))
        fut_events = cursor.fetchall()

        cursor.close()

        return fut_events
    
    def get_futurereg(self):
        cursor = mysql.connection.cursor()
        ape = session['user_id']

        sql = "SELECT e.id, e.img_url, e.name, e.description, e.location, DATE_FORMAT(e.DateTimeStart, '%M %d, %Y %h:%i %p'), e.hashtags FROM event e INNER JOIN user_events ue WHERE ue.event_id = e.id AND ue.user_id = %s AND DateTimeEnd > NOW() + INTERVAL 1 DAY AND DateTimeStart > NOW() + INTERVAL 1 DAY;"

        # Execute the query with the parameter
        cursor.execute(sql, (ape,))
        reg_fut_events = cursor.fetchall()


        cursor.close()

        return reg_fut_events

    @classmethod
    def event_description(cls, event_id):
        cursor = mysql.connection.cursor()

        sql = "SELECT * FROM event WHERE id = %s"

        # Execute the query with the parameter
        cursor.execute(sql, (event_id,))
        result = cursor.fetchone()
        
        event = cls(event_id=result[0], name=result[2], description=result[6],
                        location=result[3], DateTimeStart=result[4].strftime('%B %d, %Y %I:%M %p'), DateTimeEnd=result[5].strftime('%B %d, %Y %I:%M %p'),
                        img_url=result[7], status = result[8], participant_limit = result[9], hashtags = result[10])
        print(event.status)
        return event

    @classmethod
    def is_creator(cls, faci_id, event_id):
        cursor = mysql.connection.cursor()

        sql = "SELECT COUNT(*) FROM event WHERE f_id = %s AND id = %s"
        values = (faci_id, event_id)
        cursor.execute(sql, values)

        result = cursor.fetchone()[0]
        if result == 0:
            return False
        else:
            return True

    @classmethod
    def get_edit_event(cls, event_id):
        cursor = mysql.connection.cursor()
        sql = "SELECT * FROM event WHERE id = %s"
        values = (event_id,)
 
        cursor.execute(sql, values)
        result = cursor.fetchone()
        event = cls(event_id=result[0], name=result[2], description=result[6],
                        location=result[3], DateTimeStart=result[4], DateTimeEnd=result[5],
                        img_url=result[7], participant_limit = result[9], hashtags = result[10])
        event.eventname = event.name
        
        return event
    
    
    def update_event(self, event_id):
        try:
            cursor = mysql.connection.cursor()
            ape = session['user_id']
            self.status = 'default'

            sql = "UPDATE event SET img_url = %s, name = %s, location =%s,description = %s, DateTimeStart = %s, DateTimeEnd = %s, status = %s, participant_limit = %s, hashtags = %s WHERE id = %s"
            values = (self.img_url, self.name, self.location, self.description, self.DateTimeStart, self.DateTimeEnd,self.status, self.participant_limit, self.hashtags, event_id)
    
            cursor.execute(sql, values)

            mysql.connection.commit()
            
            return True
            
        except:
            
            return False
    
    def postpone_event(self, event_id):
        try:
            cursor = mysql.connection.cursor()

            sql = "UPDATE event SET status = 'postpone' WHERE id = %s"
            values = (event_id,)

            cursor.execute(sql, values)

            mysql.connection.commit()

            return True
        except:

            return False
        
    def cancel_event(self, event_id):
        try:
            cursor = mysql.connection.cursor()

            sql = "UPDATE event SET status = 'cancel' WHERE id = %s"
            values = (event_id,)

            cursor.execute(sql, values)

            mysql.connection.commit()

            return True
        except:

            return False
        
    @classmethod
    def delete_event(cls, event_id):
        try:
            cursor = mysql.connection.cursor()
            
            sql = "DELETE FROM event WHERE id = %s"
            values = (event_id,)
    
            cursor.execute(sql, values)

            mysql.connection.commit()
            return True
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
        
    def search_events(self, searchText):
        cursor = mysql.connection.cursor()

        sql = f"SELECT DISTINCT id, img_url, name,  description, location, DATE_FORMAT(DateTimeStart, '%M %d, %Y %h:%i %p'), DATE_FORMAT(DateTimeEnd, '%M %d, %Y %h:%i %p'), hashtags  FROM event WHERE name LIKE '%{searchText}%' OR hashtags LIKE '%{searchText}%' OR location LIKE '%{searchText}%';"

        # Execute the query with the parameter
        cursor.execute(sql)
        results = cursor.fetchall()
        
  

        return results


    
class UserEvents(object):
    def __init__(self, user_id = None, event_id = None):
        self.user_id = user_id
        self.event_id = event_id
    
    @classmethod
    def is_joined(cls, user_id, event_id):
        cursor = mysql.connection.cursor()

        sql = "SELECT COUNT(*) FROM user_events WHERE user_id = %s AND event_id = %s"
        values = (user_id, event_id)
        cursor.execute(sql, values)

        result = cursor.fetchone()[0]
        if result == 0:
            return False
        else:
            return True
        
    @classmethod
    def join(cls, event_id, participant_limit):
        cursor = mysql.connection.cursor()
        user_id = session['user_id']

        # Check first if no of participants is more than the limit
        sql = "SELECT COUNT(*) FROM user_events WHERE event_id=%s"
        values = (event_id,)
        cursor.execute(sql, values)
        no_of_participants = cursor.fetchone()[0]

        if no_of_participants >= participant_limit:
            if participant_limit == 0:
                pass
            else:
                return "MAX_PARTICIPANTS_REACHED"

        sql = "INSERT INTO user_events (user_id, event_id) VALUES (%s, %s)"
        values = (user_id, event_id)
        
        cursor.execute(sql, values)

        mysql.connection.commit()

    @classmethod
    def un_join(cls, event_id, participant_limit):
        cursor = mysql.connection.cursor()
        ape = session['user_id']



        sql = "DELETE FROM user_events WHERE user_id = %s AND event_id = %s"
        values = (ape, event_id)
        
        
        cursor.execute(sql, values)

        mysql.connection.commit()
        
      

class Attendance(object):
    def __init__():
        pass

    @classmethod
    def by_date(cls, event_id, date):
        date = date.strftime("%Y-%m-%d")

        cursor = mysql.connection.cursor()

        sql = "SELECT student_id, user.name, TIME_FORMAT(time_attended, '%h:%\i %p') AS time_attended, attendance.college, attendance.course, attendance.year_level FROM Attendance INNER JOIN User ON attendance.student_id=user.id  WHERE event_id = %s AND date = %s"
        values = (event_id, date)
        cursor.execute(sql, values)
        result = cursor.fetchall()
        print(result, event_id, date)
        return result
    
    @classmethod
    def add(cls, student_id, event_id):
        cursor = mysql.connection.cursor()

        # Checks if user joined the said event
        sql = "SELECT EXISTS(SELECT * FROM user_events WHERE user_id=%s AND event_id=%s)"
        values = (student_id, event_id)
        cursor.execute(sql, values)
        result = cursor.fetchone()
        
        if result[0] == 0:
            return "not_joined"

        # Checks if user is already in the attendance in that day

        date_now = datetime.date.today()
        date_now = date_now.strftime("%Y-%m-%d")

        sql = "SELECT EXISTS(SELECT * FROM Attendance WHERE student_id = %s AND event_id = %s AND date = %s)"
        values = (student_id, event_id, date_now)
        cursor.execute(sql, values)
        result = cursor.fetchone()
        if result[0] == 1:
            return "in_attendance"

        sql = "SELECT college, course, year_level FROM User WHERE id=%s"
        values = student_id
        cursor.execute(sql, (values,))
        result = cursor.fetchone()
        
        if result == None:
            flash("ERROR No student with this id.")
        college, course, year_level = result
        
        #We now have studentid, eventid, college, course, yearlevel
        time_now = datetime.datetime.now()
        time_attended = time_now.strftime("%H%M%S")
        # We also have time attended now
        
        sql = "INSERT INTO Attendance (event_id, date, time_attended, student_id, college, course, year_level)\
                VALUES (%s, %s, %s, %s, %s, %s, %s)"
        values = (event_id, date_now, time_attended, student_id, college, course, year_level)
        cursor.execute(sql, values)
        mysql.connection.commit()
        return
    
    @classmethod
    def search(cls, searchText, event_id, date):
        cursor = mysql.connection.cursor()
        date = date.strftime("%Y-%m-%d")
        print(date, "DSATE", searchText, type(date))

        sql = f"SELECT DISTINCT u.id, u.name, TIME_FORMAT(t.time_attended, '%h:%\i %p'), u.college, u.course, u.year_level FROM user AS u JOIN attendance AS t ON u.id = t.student_id AND t.event_id = '{event_id}' WHERE date = '{date}' AND (u.id LIKE '{searchText}%' OR u.name LIKE '%{searchText}%' OR u.college LIKE '{searchText}%' OR u.course LIKE '{searchText}%' OR u.year_level LIKE '{searchText}%');"

        
        cursor.execute(sql)
        result = cursor.fetchall()
        print(result)
        return result