import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 

from app.service.db_service import drop_all_tables
from schema.file import FileSystem 
from schema.conversation import Conversation
from schema.user import User
from service.role_service import RoleService
from service.conversation_service import ConversationService
from service.message_service import MessageService
from service.file_service import FileService
from service.user_service import UserService  
from api.chat_api import start_api 
 
def seed_role_data(): 
    RoleService.create_table_if_not_exists()
    RoleService.initialize_default_roles() 

def seed_user_data(): 
    UserService.create_table_if_not_exists()
    UserService.create(user=User(username="admin", password="123456", role="admin"))  
    UserService.create(user=User(username="humanresource", password="123456", role="hr"))  
    UserService.create(user=User(username="sales", password="123456", role="sales"))  
    UserService.create(user=User(username="marketing", password="123456", role="marketing"))  
    UserService.create(user=User(username="legal", password="123456", role="legal"))  
    UserService.create(user=User(username="finance", password="123456", role="finance"))  
    UserService.create(user=User(username="it", password="123456", role="it"))  

def seed_conversation_data(): 
    ConversationService.create_table_if_not_exists() 

def seed_message_data(): 
    MessageService.create_table_if_not_exists() 

def seed_file_data(): 
    FileService.create_table_if_not_exists()
    # FileService.create(file=FileSystem(name="abds232s-2324.pdf", orginal_name="ke hoach 2025", extension="pdf", username="admin"))
    # FileService.create(file=FileSystem(name="rwrvvsd-23sb.docx", orginal_name="Docker introduction", extension="docx", username="admin"))
    # FileService.create(file=FileSystem(name="bpsdfs2-bc04.txt", orginal_name="Project proposal", extension="txt", username="admin"))
    # FileService.create(file=FileSystem(name="serfsfs-aa35.excel", orginal_name="My project.excel", extension="excel", username="humanresource"))
    # FileService.create(file=FileSystem(name="serfsfs-abce.pdf", orginal_name="IT Report.pdf", extension="pdf", username="it"))
    # FileService.create(file=FileSystem(name="abpopei-bc00.excel", orginal_name="Sales Report.excel", extension="excel", username="sales"))
    # FileService.create(file=FileSystem(name="abpopei-3132.txt", orginal_name="Legal Report.txt", extension="txt", username="legal"))
    # FileService.create(file=FileSystem(name="abccsdd-httt.excel", orginal_name="Marketing Report.excel", extension="excel", username="marketing"))
    # FileService.create(file=FileSystem(name="tet4t44-sfad.pptx", orginal_name="Finance Report.pptx", extension="pptx", username="finance"))
     
def seed_data():    
    drop_all_tables()
    seed_role_data()
    seed_user_data()
    seed_conversation_data()
    seed_message_data()
    seed_file_data()

if __name__ == "__main__":
    seed_data()
    start_api() 
