from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
import uvicorn
from pprint import pprint
import re
# from time import time
import mysql.connector as mysql

# def connect():
conn=mysql.connect(
    host='localhost',
    user='root',
    password='varad1901',
    database='cinema_mitra_db'
)
cursor=conn.cursor()
    # return cursor,conn

app=FastAPI()

user_bookings={}
positions=['Left','Right','Middle']
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
    


def give_session_id(output_context):
    session_id=re.findall("\/sessions\/(.*)\/contexts\/",string=output_context[0]['name'])[0]
    return session_id

def show_movies():
    query="Select name from movies;"
    cursor.execute(query)
    movies=""

    for i in cursor.fetchall():
        movies+=i[0]+" ,"

    fulfillmentText=f"We have {movies} streaming today.Which one would you like to ask?"
    return JSONResponse(
        {
            'fulfillmentText':fulfillmentText
        }
    )
     
def new_booking(session_id):
    user_bookings[session_id]={}
    query="Select name from movies;"
    cursor.execute(query)
    movies=""

    for i in cursor.fetchall():
        movies+=i[0]+" ,"
    print(user_bookings)
    fulfillmentText=f"We have {movies} streaming today.Which one would you like to ask?"
    return JSONResponse(
        {
            'fulfillmentText':fulfillmentText
        }
    )

def take_movie(parameters,session_id):
    movie_name=parameters['movie_name']
    print(movie_name)
    user_bookings[session_id]['movie_name']=movie_name
    print(user_bookings)

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
    return JSONResponse(
        {
            'fulfillmentText':fulfillmentText
        }
    )

def take_time(time,session_id):
    print(time)
    movie=user_bookings[session_id]['movie_name']
    # query=f'''
    # select time 
    # from movies join show_times_table
    # on movies.id=show_times_table.movie_id
    # where name='{movie}';
    # '''
    # cursor.execute(query)
    is_present=False
    timings=""
    for i in user_bookings[session_id]['timings']:
        print(i)
        timings+=i[0]+","
        if time==i[0]:
            is_present=True

    print(is_present)
    if not is_present:
        return JSONResponse(
        {
            'fulfillmentText':f"We have no such show time for {movie}..Please select from {timings} "
        }
                            )
    user_bookings[session_id]['show_time']=time
    print(user_bookings)
    fulfillmentText=f"Okkies..Selected {time} for {movie} for you..Please now select the section from normal and balcony"
    return JSONResponse(
        {
            'fulfillmentText':fulfillmentText
        }
    )

def take_section(parameters,session_id):
    if session_id not in user_bookings:
        return JSONResponse(
        {
            'fulfillmentText':"Please start a new booking first..."
        }
    )
    if "movie_name" not in user_bookings[session_id]:
        return JSONResponse(
        {
            'fulfillmentText':"Please select a movie first...For eg Avengers"

        }
    )
    if "show_time" not in user_bookings[session_id]:
        return JSONResponse(
        {
            'fulfillmentText':f"Please select a show time first for {user_bookings[session_id]['movie_name']} from {user_bookings[session_id]['timings']}"

        }
    )
    section=parameters['section']
    print(section)
    user_bookings[session_id]['section']=section
    return JSONResponse(
        {
            'fulfillmentText':f"Selected {user_bookings[session_id]['movie_name']} at {user_bookings[session_id]['show_time']} in section {section}..Please now select the position you would like to sit in from left, middle, right"
        }
    )
    
def take_position(parameters,session_id):
    if session_id not in user_bookings:
        return JSONResponse(
        {
            'fulfillmentText':"Please start a new booking first Eg=>(I want to start a new booking)"
        }
    )
    position=parameters['position']
    if position not in positions:
          return JSONResponse(
        {
            'fulfillmentText':"Please enter a valid postion from left,right or middle.."
        }
    )
    
    user_bookings[session_id]['position']=position
    fulfillmentText=f'''Selected {position} in {user_bookings[session_id]['section']} for {user_bookings[session_id]['movie_name']} at {user_bookings[session_id]["show_time"]}.Now please Enter the number of seats..Max Limit=4'''
    return JSONResponse(
        {
            'fulfillmentText':fulfillmentText
        }
    )
    