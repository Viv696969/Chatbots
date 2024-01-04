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
