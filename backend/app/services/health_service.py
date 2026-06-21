from sqlalchemy import text
from sqlalchemy.orm import Session


def check_database_connection(db: Session) -> bool:
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        return False

    return True
