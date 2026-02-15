from datetime import datetime
import random
import string

ALPHABET = string.ascii_uppercase + string.digits

def generate_usercode():
    now = datetime.now()
    time_part = now.strftime("%y%m%d%H%M%S")
    rand_part = ''.join(random.choices(ALPHABET, k=4))
    return (time_part + rand_part)[-8:]