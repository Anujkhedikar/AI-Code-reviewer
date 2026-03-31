import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

load_dotenv()

# Setup API Key and Model
groq_api_key = os.getenv("GROQ_API_KEY")
model = ChatGroq(model_name="llama-3.1-8b-instant", groq_api_key=groq_api_key)

code_string = """
def calculate_sum(a, b):
    result = a + b
    if result > 10:
        print("Greater than 10")
    else:
        print("Less than or equal to 10")
    return result
"""

# The prompt as seen in your screenshot
prompt_template = PromptTemplate(
    input_variables=["code_string"],
    template="""You are an experienced coding teacher, so generate the suggestions based on the given code for
the student. Also, not just give the suggestion but tell that why you are suggesting this for eg. if you are suggesting something
to remove then explain that why to remove.
In the suggestion explain the error the code have like the time complexity, space complexity, and etc.
Also error like naming convention as per pep8 guidelines (for eg: Variables and functions -> snake_case and classes -> PascalCase)
and etc.
Code: {code_string}"""
)

def get_ai_suggestion(code_to_review):
    formatted_prompt = prompt_template.format(code_string=code_to_review)
    result = model.invoke(formatted_prompt)
    return result.content

if __name__ == "__main__":
    get_ai_suggestion(code_string)