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
            
            file = client.files.create(
                    file=open(file_path, "rb"),
                    purpose='assistants'
                    )
            
            print(f"added file {file.filename}")
            file_ids.append(file.id)
            
    return file_ids

        
'''
CREATE ASSISTANT FUNCTION
returns assistant object
'''

def create_assistant(instructions, file_ids):
    
    print(file_ids)
    
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
            env_file.write(f"\nASSISTANT_ID={assistant.id}")

        print("Assistant created with the following files:", file_ids)
        return assistant

'''
DELETE KNOWLEDGE FUNCTION
deletes ALL files attached
'''

def remove_knowledge():
    
    response = client.files.list()
    files = response.data
    
    for file in files:
        deletion_status = client.files.delete(file_id=file.id)
        print(f"Deleted file {file.filename}: {deletion_status}")
        
'''
UPDATE KNOWLEDGE FUNCTION
removes all then adds new
'''

def update_knowledge():
    remove_knowledge()
    return add_knowledge()

'''
SETUP GPT ASSISTANT FUNCTION
assistant id stored in .env
'''

import time
import datetime

def setup():
    files = add_knowledge()
    create_assistant("instructions.txt", files)
    
def simulate_user_interaction_and_log(query):
    # Create a thread for a new conversation
    thread = client.beta.threads.create()
    
    # Add a user message to the thread
    user_message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=query
    )
    
    with open("instructions.txt", "r") as file:
            instructions = file.read().strip()
            
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=os.getenv("ASSISTANT_ID"),
        instructions=instructions
    )
    
    # Poll the run status until completion
    while run.status in ['queued', 'in_progress', 'cancelling']:
        time.sleep(1)  # Wait for 1 second before polling again
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
    
    # Once the run completes, retrieve messages added by the assistant
    if run.status == 'completed':
        messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )
        
        content = messages.data[0].content[0].text.value
        # Log the interaction
        log_interaction(thread.id, query, content)
    else:
        print(f"Run did not complete successfully: {run.status}")

def log_interaction(thread_id, user_query, gpt_response):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Log the interaction to a file
    with open("interaction_logs.txt", "a") as log_file:
        log_entry = f"Timestamp: {timestamp}\nThread ID: {thread_id}\nUser Query: {user_query}\nGPT Response: {gpt_response}\n\n"
        log_file.write(log_entry)

# Example usage
with open("prompt.txt", "r") as file:
            prompt = file.read().strip()
simulate_user_interaction_and_log(prompt)

