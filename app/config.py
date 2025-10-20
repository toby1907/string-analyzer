from os import access
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv



class Settings(BaseSettings):  
   database_hostname: str 
   database_port: str  
   database_password: str 
   database_name: str 
   database_username: str 
   secret_key: str   # Change this to your actual secret key
   algorithm: str
   access_token_expire_minutes: int 
   database_url: str 
    
   
   class Config:
       env_file = ".env"
     

settings = Settings() 