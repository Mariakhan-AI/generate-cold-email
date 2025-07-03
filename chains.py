import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

class Chain:
    def __init__(self):
        self.llm = ChatGroq(
            temperature=0,
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.1-8b-instant"
        )

    def write_mail(self, job_text, links):
        links_text = "\n".join([f"- [{l['title']}]({l['link']}): {l['description']}" for l in links])
        prompt = PromptTemplate.from_template(
            """
            ### RAW JOB POSTING TEXT:
            {job_text}

            ### INSTRUCTION:
            You are Ahmed, a business development executive at Tech Company (an AI & software consulting company).
            Write a professional cold email describing how Tech Company can fulfill the needs mentioned in the job posting above.
            Include these portfolio projects naturally:
            {links}

            The email should be concise, persuasive, and end with a clear call-to-action.

            ### EMAIL (NO PREAMBLE):
            """
        )
        chain = prompt | self.llm
        res = chain.invoke({
            "job_text": job_text,
            "links": links_text
        })
        return res.content
