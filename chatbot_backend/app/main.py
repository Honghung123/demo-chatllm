import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 

from app.service.db_service import drop_all_tables, ensure_db_file_exists 
from schema.user import User
from service.role_service import RoleName, RoleService
from service.conversation_service import ConversationService
from service.message_service import MessageService 
from service.user_service import UserService  
from api.chat_api import start_api 
from utils.file_utils import get_root_path
 
def seed_role_data(): 
    RoleService.create_table_if_not_exists()
    RoleService.initialize_default_roles() 

def seed_user_data(): 
    UserService.create_table_if_not_exists()
    UserService.create(user=User(username="admin", password="123456", role=RoleName.ADMIN.split("|")[0]))  
    UserService.create(user=User(username="humanresource", password="123456", role=RoleName.HR.split("|")[0]))  
    UserService.create(user=User(username="sales", password="123456", role=RoleName.SALES.split("|")[0]))     
    UserService.create(user=User(username="marketing", password="123456", role=RoleName.MARKETING.split("|")[0]))  
    UserService.create(user=User(username="legal", password="123456", role=RoleName.LEGAL.split("|")[0]))  
    UserService.create(user=User(username="finance", password="123456", role=RoleName.FINANCE.split("|")[0]))  
    UserService.create(user=User(username="it", password="123456", role=RoleName.IT.split("|")[0]))  

def seed_conversation_data(): 
    ConversationService.create_table_if_not_exists() 

def seed_message_data(): 
    MessageService.create_table_if_not_exists() 

def seed_file_data():  
    # FileService.create(file=FileSystem(name="abds232s-2324.pdf", orginal_name="ke hoach 2025", extension="pdf", username="admin"), roles=["admin", "hr", "sales", "marketing"])
    pass
     
def seed_data():    
    ensure_db_file_exists()
    drop_all_tables()
    seed_role_data()
    seed_user_data()
    seed_conversation_data()
    seed_message_data()
    seed_file_data()

def create_dirs():
    documents_dir = f"{get_root_path()}/data/files"
    # Create directory if it doesn't exist
    os.makedirs(documents_dir, exist_ok=True)

if __name__ == "__main__":
    create_dirs()
    seed_data()
    start_api() 
