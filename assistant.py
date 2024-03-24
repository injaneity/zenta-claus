import os
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
client = OpenAI(api_key=os.getenv("GPT_API"))

'''
ADD KNOWLEDGE FUNCTION
returns file_ids (list)
'''

def add_knowledge():
    
    file_ids = []
    folder_path = "./knowledge"
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        if os.path.isfile(file_path):
            
            response = client.files.create(
                file=open(file_path, "rb"),
                purpose='assistants'
            )
            
            file_ids.append(response["id"])
            
    return file_ids

        
'''
CREATE ASSISTANT FUNCTION
returns assistant object
'''

def create_assistant(instructions, file_ids):
    
    assistant_id = os.getenv("ASSISTANT_ID")

    if assistant_id:
        print(f"Using existing assistant ID: {assistant_id}")
        return client.beta.assistants.retrieve(assistant_id=assistant_id)
    
    else:
        with open("instructions.txt", "r") as file:
            instructions = file.read().strip()

        assistant = client.beta.assistants.create(
            instructions=instructions,
            model="gpt-4-turbo-preview",
            tools=[{"type": "retrieval"}],
            file_ids=file_ids
        )

        with open('.env', 'a') as env_file:
            env_file.write(f"\nASSISTANT_ID={assistant['id']}")

        print("Assistant created with the following files:", file_ids)
        return assistant

'''
DELETE KNOWLEDGE FUNCTION
deletes ALL files attached
'''

def remove_knowledge():
    
    response = client.files.list()
    files = response['data']
    
    for file in files:
        deletion_status = client.files.delete(file_id=file['id'])
        print(f"Deleted file {file['id']}: {deletion_status}")
        
'''
UPDATE KNOWLEDGE FUNCTION
removes all then adds new
'''

def update_knowledge():
    remove_knowledge()
    add_knowledge()


# thread = client.beta.threads.create(
#   messages=[
#     {
#       "role": "user",
#       "content": "Create 3 data visualizations based on the trends in this file.",
#       "file_ids": [file.id]
#     }
#   ]
# )