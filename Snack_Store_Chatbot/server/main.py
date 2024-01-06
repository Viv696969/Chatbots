from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
import uvicorn
from pprint import pprint
from db import *
import re
from time import time

app=FastAPI()

user_orders={}


@app.post("/")
async def webhook(request:Request):
    data=await request.json()
    
    intent=data['queryResult']['intent']['displayName']
    
    parameters=data['queryResult']['parameters']
   
    output_context=data['queryResult']['outputContexts']
    session_id=give_session_id(output_context)

    match intent:
        case "give.orderid" :
            return give_order_status(parameters)
        
        case "order.add":
            return add_to_order(parameters,session_id)
        
        case "order.complete":
            return save_order(session_id)
        
        case "order.remove":
            return remove_items(session_id,parameters)

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
def add_to_order(parameters:dict,session_id:str):
    '''
    takes parameters,session_ids as input and extracts food items,numbers

    '''
    # st=time()
    global user_orders
    # print(f"user info at start=====>{user_orders}")
    food_items=parameters['food-item']
    numbers=parameters['number']
    length=len(food_items)
    
    if length != len(numbers): #error condition for add to order
        fulfillmentText="Please specify the items and quantities correctly"
    else:
        ############## session order adding logic ##############
        order_dict=dict(zip(food_items,numbers))
        # print(f"The order dict is === {order_dict}")
        if session_id not in user_orders:
            # when user first time says will create a new entry to remember the past convo
            user_orders[session_id]=order_dict
            # print(f"user info after first order==> {user_orders}")
        else:
            user_orders[session_id].update(order_dict)
            # print(f"user_orders after next order {user_orders}")

        ######printing logic ###########
        text = ",".join(
                [f"{int(j)} {i}" for i,j in user_orders[session_id].items() ]
                )
        
        if length == 1:
            fulfillmentText = f"Okkies added {int(numbers[0])} {food_items[0]} to cart...So far I have  {text} in the total cart...Anything else for you?"
        else:
            
            fulfillmentText = f"Okkies..So far I added {text} to total cart...Anything else for you?"
        ############## printing logic end ###############
    print(user_orders)
    return JSONResponse(
        {
            'fulfillmentText':fulfillmentText
        }
    )


# gives sessionid from the output context and we use re to do it
def give_session_id(output_context):
    session_id=re.findall("\/sessions\/(.*)\/contexts\/",string=output_context[0]['name'])[0]
    return session_id


def save_order(session_id:str):
    '''
    based on session id will create a order and save it
    '''
    print(user_orders)
    if session_id not in user_orders:
        # check if user had put some items in cart
        fulfillmentText=f"No such order created for you please create a new order..Thank you"
    else:
        order=user_orders[session_id]  #take the order 
        status=save_order_to_db(order)  #save to database  
        if status==-1:
            # Some error has occured while creating
            fulfillmentText=f"Error creating order from our side"\
            f"Please try creating a new order"
            del user_orders[session_id]
        else:
            # print("order id is ======>",status)
            total_price=get_total_price(status)  #  get total price
            save_tracking(status,mssg='in progress') # save the status as in progress
            fulfillmentText=f'''
                        Order placed successfully!
                        Your Total price is {total_price}$
                        Pay on delivery
                        Your Order Id is {status}
                        Use order id for tracking
                            '''
            del user_orders[session_id]
            print(user_orders)

    return JSONResponse(
        {
            'fulfillmentText':fulfillmentText
        }
    )

def remove_items(session_id:str,parameters:dict):
    # check if session exists
    if session_id not in user_orders:
        fulfillmentText="You have not added anything to the order...I cant remove anything....You can type 'new order' and proceed further"
    else:
        # some orders are present and we need to remove them
        # check if the item the user wants to remove is present in the orders dict
        food_items=parameters['food-item']
        print(food_items)
        order_items=user_orders[session_id].keys() # take all the food items present in the order
        text=" , ".join(food_items)
        for i in food_items:
            if i not in order_items:  # the item the user wants to remove is not in hsi cart
                
                fulfillmentText=f'OOPs sorry you dont have {text} or either of them  in the cart..You can remove something which already exists'
                print("=========\ntest for unusual item solved\n========================")
                return JSONResponse(
                    {
                        'fulfillmentText':fulfillmentText
                    }
                )
        for i in food_items:
            del user_orders[session_id][i]
        
        print(user_orders[session_id])
        print("Test for items present in order removed solved")

        return JSONResponse(
            {
                'fulfillmentText':f"Done!!.. Removed {text} from your cart"
            }
        )
            