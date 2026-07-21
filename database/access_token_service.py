from database import get_db
from database.models import Access_token



def create_access_token(access_token):
    db = next(get_db())
    token = db.query(Access_token).filter(Access_token.id == 1).first()
    if not token:
        new_token = Access_token(access_token=access_token)
        db.add(new_token)
        db.commit()
        return True
    else:
        return False

def update_access_token_bd(access_token):
    db = next(get_db())
    bd_access_token = db.query(Access_token).filter(Access_token.id == 1).first()
    if bd_access_token:
        bd_access_token.access_token = access_token
        db.commit()
        return True
    else:
        return False


def get_access_token_bd():
    db = next(get_db())
    access_token = db.query(Access_token).filter(Access_token.id == 1).first()
    if access_token:
        return access_token.access_token
    else:
        return False


