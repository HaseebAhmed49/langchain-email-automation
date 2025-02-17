from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()
app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# Pydantic models
class EmailRequest(BaseModel):
    sender: str
    subject: str
    body: str


class EmailResponse(BaseModel):
    category: str
    response: str
    urgency: str


# LangChain setup
template = """You are an email automation assistant. Analyze this email and:
1. Categorize it (urgent, general inquiry, spam, complaint)
2. Generate appropriate response
3. Determine urgency (high, medium, low)

Email from {sender}:
Subject: {subject}
Body: {body}

Respond in this format:
Category: [category]
Urgency: [urgency]
Response: [response]"""

prompt = PromptTemplate(
    input_variables=["sender", "subject", "body"],
    template=template
)

llm = ChatOpenAI(temperature=0.3, model="gpt-3.5-turbo", api_key=OPENAI_API_KEY)
chain = LLMChain(llm=llm, prompt=prompt)

@app.post("/process-email", response_model=EmailResponse)
async def process_email(email: EmailRequest):
    try:
        result = chain.run({
            "sender": email.sender,
            "subject": email.subject,
            "body": email.body
        })

        # Parse the LLM response
        response_dict = {}
        for line in result.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                response_dict[key.strip().lower()] = value.strip()

        return EmailResponse(
            category=response_dict.get("category", "general inquiry"),
            response=response_dict.get("response", "Thank you for your email."),
            urgency=response_dict.get("urgency", "medium")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)