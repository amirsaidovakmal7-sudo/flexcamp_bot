from database import get_db
from database.models import Refresh_token



def create_refresh_token(refresh_token):
    db = next(get_db())
    token = db.query(Refresh_token).filter(Refresh_token.id == 1).first()
    if not token:
        new_token = Refresh_token(refresh_token=refresh_token)
        db.add(new_token)
        db.commit()
        return True
    else:
        return False

def update_refresh_token_bd(refresh_token):
    db = next(get_db())
    bd_refresh_token = db.query(Refresh_token).filter(Refresh_token.id == 1).first()
    if bd_refresh_token:
        bd_refresh_token.refresh_token = refresh_token
        db.commit()
        return True
    else:
        return False


def get_refresh_token_bd():
    db = next(get_db())
    refresh_token = db.query(Refresh_token).filter(Refresh_token.id == 1).first()
    if refresh_token:
        return refresh_token.refresh_token
    else:
        return False
