import secrets
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import APIKey

security = HTTPBearer()

def generate_key():
    """Generates a random secure key like nova-sk-xxxxx"""
    return f"nova-sk-{secrets.token_urlsafe(32)}"

def get_current_user_from_key(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    
    # Check if key exists in DB
    api_key = db.query(APIKey).filter(APIKey.key == token, APIKey.is_active == True).first()
    
    if not api_key:
        raise HTTPException(
            status_code=403,
            detail="Invalid or revoked NovaMind API Key"
        )
    
    return api_key.user_id