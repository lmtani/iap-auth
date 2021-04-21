from datetime import datetime


def is_token_valid(expires_at: float):
    print(expires_at)
    print(datetime.now().timestamp())
    if expires_at and expires_at > datetime.now().timestamp():
        return True
    return False
