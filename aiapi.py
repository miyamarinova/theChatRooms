
from openai import OpenAI
import config 
client = OpenAI(api_key = config.DevelopmentConfig.OPENAI_KEY)

messages = []
messages.append({"role": "system", "content": "You are a mental health specialist."})

def generate_chat_response(prompt):
    question = {}
    question['role'] = 'user'
    question['content'] = prompt
    messages.append(question)
    
    response = client.chat.completions.create(model="gpt-3.5-turbo",messages=messages)
    
 
    try:
        answer = response.choices[0].message.content
    except:
        answer = 'Oops, sorry! Try a different question. If the problem still occures, please come back later!'
    

    return answer