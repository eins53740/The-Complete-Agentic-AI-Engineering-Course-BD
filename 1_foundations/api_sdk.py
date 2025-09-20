# Start with imports - ask ChatGPT to explain any package that you don't know
import os
import json
from dotenv import load_dotenv

from anthropic import Anthropic
from IPython.display import Markdown, display

# Always remember to do this!
load_dotenv(override=True)
openai_api_key = os.getenv('OPENAI_API_KEY')
anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
google_api_key = os.getenv('GOOGLE_API_KEY')
deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
groq_api_key = os.getenv('GROQ_API_KEY')

request = "Please come up with a challenging, nuanced question that I can ask a number of LLMs to evaluate their intelligence. "
request += "Answer only with the question, no explanation."
messages = [{"role": "user", "content": request}]



from openai import OpenAI
model_name = "gpt-4o-mini"
openai = OpenAI()
response = openai.chat.completions.create(model=model_name, messages=messages)
answer = response.choices[0].message.content

#from openai import OpenAI
model_name = "gemini-2.0-flash"
gemini = OpenAI(api_key=google_api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
response = gemini.chat.completions.create(model=model_name, messages=messages)
answer = response.choices[0].message.content

model_name = "llama-3.3-70b-versatile"
groq = OpenAI(api_key=groq_api_key, base_url="https://api.groq.com/openai/v1")
response = groq.chat.completions.create(model=model_name, messages=messages)
answer = response.choices[0].message.content



from strands import Agent
from strands_tools import calculator
agent = Agent(tools=[calculator])
agent("What is the square root of 1764")

### pip install strands-agents
### python -u agent.py
from strands import Agent
# Create an agent with default settings
agent = Agent()
# Ask the agent a question
response = agent("Tell me about agentic AI")
print(response)