import requests
import time
import uuid

thread_id = uuid.uuid4()
thread_id_Str = str(thread_id)
print(thread_id_Str)

while True:
    #input
    query = {
        "query": input("\n prompt: " ),
        "thread_id": thread_id_Str
        }
    
    if query["query"] == "exit":
        break

    # POST to Janus
    response = requests.post(url="http://127.0.0.1:8001/route", json=query, stream=True)
    for chunk in response.iter_content(decode_unicode=True, chunk_size=None):
        if chunk:
            print(chunk, end="", flush=True)
            time.sleep(0.03)  # 20ms delay between chunks for natural feel
    
        
            
    
#parse response
#final_response = response.json()["answer"]
#no .json(). It's raw text chunks now.
    #print answer
    
#iter_lines() returns bytes by default.

    
