from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
import uvicorn
import re
import mysql.connector as mysql
import smtplib
from mangum import Mangum

app=FastAPI()
handler=Mangum(app)

def connect():
    conn=mysql.connect(
        host='myfirstrds.c5eeiea4ujq1.ap-south-1.rds.amazonaws.com',
        user='admin',
        password='admin1234',
        database='chatbot_db'
    )
    cursor=conn.cursor()
    return conn,cursor

s = smtplib.SMTP('smtp.gmail.com', 587)
s.starttls()
s.login("vivek.211215.co@mhssce.ac.in", "varad1901")


def give_seat_nos(seats,section,position):
    seat_nums=""
    if section=="Balcony":
        for i in range(seats):
            seat_nums+=f"H{i+1} , "
    else:
        for i in range(seats):
            seat_nums+=f"C{i+1},"
    return seat_nums

def send_mail(reciever,mssg):
    
    s.sendmail("vivek.211215.co@mhssce.ac.in", reciever, mssg)




user_bookings={}
positions=['Left','Right','Middle']

@app.get("/test_url")
async def test():
    return {"Message":"Test"}

@app.post("/")
async def webhook(request:Request):
    data=await request.json()
    
    intent=data['queryResult']['intent']['displayName']
    
    parameters=data['queryResult']['parameters']
   
    output_context=data['queryResult']['outputContexts']
    session_id=give_session_id(output_context)
    print(session_id)
    print(parameters)
    print(intent)

    match intent:
        case "new_booking":
            return new_booking(session_id)
        case "show-movies":
            return show_movies()
        
        case "take_movie":
            return take_movie(parameters,session_id)
        
        case "take_show_time":
            return take_time(data['queryResult']["queryText"],session_id)
        
        case "take_section":
            return take_section(parameters,session_id)
        
        case "take_position":
            return  take_position(parameters,session_id)
        
        case "take_no_of_seats":
            return take_no_of_seats(parameters,session_id)
        
        case "book_ticket":
            return book_ticket(session_id)
        
        case "take_gmail":
            return take_email(parameters,session_id)
        
        case "take_id_showing_ticket":
            return show_ticket(parameters)
    


def give_session_id(output_context):
    session_id=re.findall("\/sessions\/(.*)\/contexts\/",string=output_context[0]['name'])[0]
    return session_id

def show_movies():
    conn,cursor=connect()
    query="Select name from movies;"
    cursor.execute(query)
    movies=""

    for i in cursor.fetchall():
        movies+=i[0]+" ,"

    fulfillmentText=f"We have {movies} streaming today.Which one would you like to ask?"
    cursor.close()
    conn.close()
    return create_response(fulfillmentText)
     
def new_booking(session_id):
    user_bookings[session_id]={}
    query="Select name from movies;"
    conn,cursor=connect()
    cursor.execute(query)
    movies=""

    for i in cursor.fetchall():
        movies+=i[0]+" ,"
    print(user_bookings)
    fulfillmentText=f"We have {movies} streaming today.Which one would you like to ask?"
    cursor.close()
    conn.close()
    return create_response(fulfillmentText)

def take_movie(parameters,session_id):
    movie_name=parameters['movie_name']
    user_bookings[session_id]['movie_name']=movie_name
    conn,cursor=connect()
    query=f'''
    select time 
    from movies join show_times_table
    on movies.id=show_times_table.movie_id
    where name='{movie_name}';
    '''
    cursor.execute(query)
    timing_list=cursor.fetchall()
    timings=""
    for i in timing_list:
        timings+=i[0]+","
    user_bookings[session_id]['timings']=timing_list
    fulfillmentText=f"Selected {movie_name} successfully.The available show times are {timings}.Please select any one from that"
    cursor.close()
    conn.close()
    return create_response(fulfillmentText)

def take_time(time,session_id):
    movie=user_bookings[session_id]['movie_name']
    is_present=False
    timings=""
    for i in user_bookings[session_id]['timings']:
        print(i)
        timings+=i[0]+","
        if time==i[0]:
            is_present=True

    if not is_present:
        return create_response(f"We have no such show time for {movie}..Please select from {timings} ")
    user_bookings[session_id]['show_time']=time
    print(user_bookings)
    fulfillmentText=f"Okkies..Selected {time} for {movie} for you..Please now select the section from normal and balcony"
    return create_response(fulfillmentText)

def take_section(parameters,session_id):
    if session_id not in user_bookings:
        return create_response("Please start a new booking first...")
    if "movie_name" not in user_bookings[session_id]:
        return create_response("Please select a movie first...For eg Avengers")
    if "show_time" not in user_bookings[session_id]:
        return create_response(f"Please select a show time first for {user_bookings[session_id]['movie_name']} from {user_bookings[session_id]['timings']}")
    section=parameters['section']
    user_bookings[session_id]['section']=section
    fulfillmentText=f"Selected {user_bookings[session_id]['movie_name']} at {user_bookings[session_id]['show_time']} in section {section}..Please now select the position you would like to sit in from left, middle, right"
    return create_response(fulfillmentText)
    
def take_position(parameters,session_id):
    if session_id not in user_bookings:
        return create_response("Please start a new booking first Eg=>(I want to start a new booking)")
    position=parameters['position']
    if position not in positions:
          return create_response("Please enter a valid postion from left,right or middle..")
    
    user_bookings[session_id]['position']=position
    fulfillmentText=f'''Selected {position} in {user_bookings[session_id]['section']} for {user_bookings[session_id]['movie_name']} at {user_bookings[session_id]["show_time"]}.Now please Enter the number of seats..Max Limit=4'''
    return create_response(fulfillmentText)
    
def take_no_of_seats(parameters,session_id):
    if session_id not in user_bookings:

        return create_response("Please start a new booking first...")
    seats=int(parameters['number'])

    if seats>4 or seats<0:
        return create_response("Please enter valid number of seats from 1,2,3,4")
    
    user_bookings[session_id]['no_of_seats']=seats
    fulfillmentText=f'''Selected {seats} seats for {user_bookings[session_id]['movie_name']} at {user_bookings[session_id]['show_time']} in section {user_bookings[session_id]['section']} and position {user_bookings[session_id]['position']} Successfully...Should i confirm your booking ?'''
    return create_response(fulfillmentText)

def book_ticket(session_id):
    print(user_bookings[session_id])
    user_bookings[session_id]['confirmed']=True
    fulfillmentText="Please Enter your gmail to finalize your booking...eg=>abcd@gmail.com"
    return create_response(fulfillmentText)
    
def take_email(parameters,session_id):
    conn,cursor=connect()
    email=parameters['email']
    user=user_bookings[session_id]
    seats=user["no_of_seats"]
    section=user['section']
    position=user['position']
    seat_nums=give_seat_nos(seats,section,position)
    movie=user['movie_name']
    showtime=user['show_time']
    query="select max(ticket_id) from bookings;"
    cursor.execute(query)
    id=cursor.fetchone()[0]
    print(id)
    ticket_id=id+1
    email_mssg=f'''
    Thank you for booking {movie} at {showtime}
    Section : {section}
    Seat numbers : {seat_nums}
    Number of tickets : {seats}
    Your Ticket id is {ticket_id}
    '''
    
    query=f'''
    insert into bookings values(
    {ticket_id},
    "{email}",
    "{movie}",
    "{section}",
    "{position}",
    {seats},
    "{seat_nums}",
    "{showtime}",
    "url_demo",
    "{email_mssg}"
    );
    '''
    cursor.execute(query)
    conn.commit()
    s.sendmail("vivek.211215.co@mhssce.ac.in", email, email_mssg)
    fulfillmentText=f"{email} thank you for booking {movie} with us..Your ticket id is {ticket_id}..Incase you forget your ticket id check you mail once..Enjoy"
    cursor.close()
    conn.close()
    return create_response(fulfillmentText)

def create_response(fulfillmentText):
    return JSONResponse({'fulfillmentText': fulfillmentText})

def show_ticket(parameters):
    id=int(parameters['number'])
    print(id)
    conn,cursor=connect()
    query=f'''
    select ticket_text from bookings where ticket_id={id}
    '''
    cursor.execute(query)
    text=cursor.fetchone()
    cursor.close()
    conn.close()
    if text is None:
        return create_response(f"No such id like {id}...Please try with the correct id")
    else:
        return create_response(f"Your ticket is {text[0][26:]}")


