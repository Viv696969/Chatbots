from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
import uvicorn
from pprint import pprint

app=FastAPI()


@app.post("/")
async def webhook(request:Request):
    data=await request.json()
    # print(data)
    intent=data['queryResult']['intent']['displayName']
    print("Intent is  ",intent)
    parameters=data['queryResult']['parameters']
    pprint(parameters,depth=2)
    output_context=data['queryResult']['outputContexts']
    print(output_context)

    if intent=='give.orderid':
        return JSONResponse(
            content={
                'fulfillmentText':f"Ok! recieved order id as {int(parameters['order_id'])}"
                }
                            )
    
def give_order_status(parameters):
    order_id=int(parameters['order_id'])
    response=JSONResponse(
            content={
                'fulfillmentText':f"Ok! recieved order id as {order_id}"
                }
                )


