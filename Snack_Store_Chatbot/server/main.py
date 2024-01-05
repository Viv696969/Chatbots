from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
import uvicorn
from pprint import pprint
from db import *
import re

app=FastAPI()


@app.post("/")
async def webhook(request:Request):
    data=await request.json()
    
    intent=data['queryResult']['intent']['displayName']
    
    parameters=data['queryResult']['parameters']
   
    output_context=data['queryResult']['outputContexts']
    print(re.findall("\/sessions\/(.*)\/contexts\/",string=output_context[0]['name']))

    match intent:
        case "give.orderid" :
            return give_order_status(parameters)
        
        case "order.add":
            return add_to_order(parameters)

# gives order status by getting the connecting to db
def give_order_status(parameters:dict):
    
    order_id=int(parameters['order_id'])
    
    result = get_order_status(order_id)
    if result=='not available':
        response=JSONResponse(
                content={
                    'fulfillmentText':f"Your order id {order_id} does not exist..please enter correct order id"
                    }
                    )
    else:
        response=JSONResponse(
                content={
                    'fulfillmentText':f"Your order id {order_id} and the status is {result}"
                    }
                    )
    return response

# performs adding to cart functionality...takes the parameters and retrieve the 
# food and numbers
def add_to_order(parameters:dict):
    '''
    takes parameters as input and extracts food items,numbers

    '''
    food_items=parameters['food-item']
    numbers=parameters['number']
    print(food_items,"\n",numbers)
    
    if len(food_items) != len(numbers):
        fulfillmentText="Please specify the items and quantities correctly"
    else:
        fulfillmentText=f"Okkies added {food_items} and {numbers } to cart"

    return JSONResponse(
        {
            'fulfillmentText':fulfillmentText
        }
    )


# gives sessionid from the output context and we use re to do it
def give_session_id(output_context):
    session_id=re.findall("\/sessions\/(.*)\/contexts\/",string=output_context[0]['name'])[0]
    return session_id
