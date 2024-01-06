import mysql.connector as mysql

def connect():
    conn=mysql.connect(
        host='localhost',
        user='root',
        password='varad1901',
        database='pandeyji_eatery'
    )
    cursor=conn.cursor()
    return cursor,conn




def get_order_status(order_id:int):
    cursor,conn=connect()
    query=f'''select status from order_tracking where order_id={order_id}'''
    cursor.execute(query)
    result=cursor.fetchone()
    print(result)
    conn.close()
    cursor.close()
    
    return result[0] if result is not None else "not available"

def save_order_to_db(order:dict):
    # first find the max order present
    cursor,conn=connect()
    query="select max(order_id) from orders"
    cursor.execute(query)
    max_order_id=cursor.fetchone()[0]
    if max_order_id is None:
        order_id=1
    else:
        order_id=max_order_id+1
    
    # print(order_id)

    # save each item to db
    for item,quantity in order.items():
        status=save_to_db(item,quantity,order_id,cursor,conn)
        if status==1:
            print("order item saved successfull")
        else:
            print("problem putting in db")
            # print(order_id)
            return -1
    
    conn.commit()
    print("Order commited")
    conn.close()
    cursor.close()
    # print(order_id)
    return order_id
    
def save_to_db(item,quantity,order_id,cursor,conn):
    try:
        cursor.callproc('insert_order_item',(item,quantity,order_id))
        return 1
    except:
        conn.rollback()
        return -1
    

save_order_to_db(
    {'pav bhaji':2}
)

def get_total_price(status):
    cursor,conn=connect()
    query=f'select get_total_order_price({status});'
    cursor.execute(query)
    return cursor.fetchone()[0]

def save_tracking(order_id,mssg):
    '''
    saves order status on basis of order id
    '''
    cursor,conn=connect()
    query=f'insert into order_tracking values ({order_id},"{mssg}")'
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()
    

