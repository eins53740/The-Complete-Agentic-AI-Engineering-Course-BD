import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic
from IPython.display import Markdown, display

# Always remember to do this!
load_dotenv(override=True)

# Print the key prefixes to help with any debugging

openai_api_key = os.getenv('OPENAI_API_KEY')
anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
google_api_key = os.getenv('GOOGLE_API_KEY')
deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
groq_api_key = os.getenv('GROQ_API_KEY')

history = ""

request_gemini = f"You are a 40 years old portuguese man sending messages to a match girl in the Tinder apk. Please continue the conversation with the girl. The following is the conversation history: {history}"
message_gemini = [{"role": "user", "content": request_gemini}]

model_name_gemini = "gemini-2.0-flash"
gemini = OpenAI(api_key=google_api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
response_gemini = gemini.chat.completions.create(model=model_name_gemini, messages=message_gemini)
answer_gemini = response_gemini.choices[0].message.content
history += f"User: MAN\nConversation: {answer_gemini}\n"

request_groq = f"You are a 35 years old portuguese girln sending messages, to a match boy you started a conversation in the Tinder apk. Please continue the conversation with the girl. The following is the conversation history: {history}"   
message_groq = [{"role": "user", "content": request_groq}]

model_name_groq = "llama-3.3-70b-versatile"
groq = OpenAI(api_key=groq_api_key, base_url="https://api.groq.com/openai/v1")
response_groq = groq.chat.completions.create(model=model_name_groq, messages=message_groq)
answer_groq = response_groq.choices[0].message.content
history += f"User: GIRL\nConversation: {answer_groq}\n"

model_name_gemini = "gemini-2.0-flash"
gemini = OpenAI(api_key=google_api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
response_gemini = gemini.chat.completions.create(model=model_name_gemini, messages=message_gemini)
answer_gemini = response_gemini.choices[0].message.content
history += f"User: MAN\nConversation: {answer_gemini}\n"

request_groq = f"You are a 35 years old portuguese girln sending messages, to a match boy you started a conversation in the Tinder apk. Please continue the conversation with the girl. The following is the conversation history: {history}"   
message_groq = [{"role": "user", "content": request_groq}]

model_name_groq = "llama-3.3-70b-versatile"
groq = OpenAI(api_key=groq_api_key, base_url="https://api.groq.com/openai/v1")
response_groq = groq.chat.completions.create(model=model_name_groq, messages=message_groq)
answer_groq = response_groq.choices[0].message.content
history += f"User: GIRL\nConversation: {answer_groq}\n"


model_name_gemini = "gemini-2.5-flash"
gemini = OpenAI(api_key=google_api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
response_gemini = gemini.chat.completions.create(model=model_name_gemini, messages=message_gemini)
answer_gemini = response_gemini.choices[0].message.content
history += f"User: MAN\nConversation: {answer_gemini}\n"



request_groq = f"You are a 35 years old portuguese girln sending messages, to a match boy you started a conversation in the Tinder apk. Please continue the conversation with the girl. The following is the conversation history: {history}"   
message_groq = [{"role": "user", "content": request_groq}]

model_name_groq = "llama-3.3-70b-versatile"
groq = OpenAI(api_key=groq_api_key, base_url="https://api.groq.com/openai/v1")
response_groq = groq.chat.completions.create(model=model_name_groq, messages=message_groq)
answer_groq = response_groq.choices[0].message.content
history += f"User: GIRL\nConversation: {answer_groq}\n"


print(history)

