from datetime import datetime

def current_time() -> str:
    return datetime.now().strftime('%B %d, %Y at %H:%M:%S')

def unix_to_date(time_stamp) -> str:
    d = datetime.fromtimestamp(time_stamp)
    return d.strftime("%d-%b-%Y")

def divide_chunks(l, n) -> list: 
    for i in range(0, len(l), n):  
        yield l[i:i + n] 