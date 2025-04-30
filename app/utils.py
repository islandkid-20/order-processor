
from uuid import uuid4

def generate_order_id():
    while True:
        order_id = uuid4().hex[:6].upper()
        if order_id[0].isalpha():
            return order_id