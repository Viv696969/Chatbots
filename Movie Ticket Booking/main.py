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
    timings=""
    for i in cursor.fetchall():
        timings+=i[0]+","
    
    fulfillmentText=f"Selected {movie_name} successfully.The available show times are {timings}.Please select any one from that"
    return JSONResponse(
        {
            'fulfillmentText':fulfillmentText
        }
    )

def take_time(time,session_id):
    movie=user_bookings[session_id]['movie_name']
    query=f'''
    select time 
    from movies join show_times_table
    on movies.id=show_times_table.movie_id
    where name='{movie}';
    '''
    cursor.execute(query)
    is_present=False
    timings=""
    for i in cursor.fetchall():
        print(i)
        timings+=i[0]+","
        if "time"==i[0]:
            is_present=True

    print(is_present)
    if not is_present:
        return JSONResponse(
        {
            'fulfillmentText':f"We have no such show time for {movie}..Please select from {timings} "
        }
                            )
    user_bookings[session_id]['show_time']=time
    fulfillmentText=f"Okkies..Selected {time} for {movie} for you..Please now select the section from normal and balcony"
    return JSONResponse(
        {
            'fulfillmentText':fulfillmentText
        }
    )
    

    