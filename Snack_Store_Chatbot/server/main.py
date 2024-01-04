from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
import uvicorn
from pprint import pprint
from db import *
app=FastAPI()


@app.post("/")
async def webhook(request:Request):
    data=await request.json()
    
    intent=data['queryResult']['intent']['displayName']
    
    parameters=data['queryResult']['parameters']
   
    output_context=data['queryResult']['outputContexts']
   

    match intent:
        case "give.orderid" :
            return give_order_status(parameters)

    
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


