from fastapi import Depends, HTTPException
from jose import jwt

SECRET_KEY = "mco-secret-key"
ALGORITHM = "HS256"


def get_current_user(token: str):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload

    except:
        raise HTTPException(status_code=401, detail="Invalid Token")


def require_role(role):

    def role_checker(user=Depends(get_current_user)):

        if user["role"] != role:
            raise HTTPException(status_code=403, detail="Access Denied")

        return user

    return role_checker