import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import logging

load_dotenv()

class Chain:
    def __init__(self):
        """Initialize the Chain with ChatGroq LLM"""
        try:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY not found in environment variables")
            
            self.llm = ChatGroq(
                temperature=0,
                groq_api_key=api_key,
                model_name="llama-3.1-8b-instant",
                max_tokens=2000  # Ensure we don't hit token limits
            )
            
        except Exception as e:
            logging.error(f"Failed to initialize ChatGroq: {e}")
            raise
    
    def extract_job_requirements(self, job_text):
        """Extract key requirements from job posting"""
        extract_prompt = PromptTemplate.from_template(
            """
            Analyze this job posting and extract the key requirements, skills, and company needs:
            
            {job_text}
            
            Return a JSON-like structure with:
            - company_name: Name of the hiring company
            - job_title: Position title
            - key_requirements: List of main technical requirements
            - soft_skills: List of soft skills needed
            - company_type: Type of company (startup, enterprise, etc.)
            - industry: Industry sector
            
            Keep it concise and focused on the most important elements.
            """
        )
        
        chain = extract_prompt | self.llm
        try:
            result = chain.invoke({"job_text": job_text})
            return result.content
        except Exception as e:
            logging.error(f"Error extracting job requirements: {e}")
            return None
    
    def write_mail(self, job_text, links):
        """Generate a professional cold email based on job posting and portfolio links"""
        
        # Handle empty or None links
        if not links:
            links_text = "While we don't have specific portfolio examples to share right now, we have extensive experience in similar projects."
        else:
            # Format links properly - handle both dict and string formats
            formatted_links = []
            for link in links:
                if isinstance(link, dict):
                    title = link.get('title', 'Project')
                    url = link.get('link', '#')
                    description = link.get('description', 'Relevant project experience')
                    formatted_links.append(f"• [{title}]({url}): {description}")
                else:
                    # Handle string links
                    formatted_links.append(f"• {link}")
            
            links_text = "\n".join(formatted_links)
        
        prompt = PromptTemplate.from_template(
            """
            You are Ahmed, a business development executive at TechFlow Solutions - an AI & software consulting company that helps businesses leverage cutting-edge technology to solve complex problems and drive growth.
            
            ### JOB POSTING:
            {job_text}
            
            ### RELEVANT PORTFOLIO PROJECTS:
            {links}
            
            ### INSTRUCTIONS:
            Write a professional cold email that:
            1. Shows you understand their specific needs from the job posting
            2. Briefly explains how TechFlow Solutions can help
            3. Naturally mentions 2-3 relevant portfolio projects as proof of capability
            4. Keeps the tone professional but personable
            5. Ends with a clear, specific call-to-action
            6. Is concise (under 200 words)
            
            ### WRITING GUIDELINES:
            - Address the hiring manager professionally
            - Don't oversell or use too much jargon
            - Focus on value proposition and results
            - Make it feel personalized, not templated
            - Include your contact information
            - Use proper email formatting
            
            ### EMAIL:
            """
        )
        
        chain = prompt | self.llm
        
        try:
            res = chain.invoke({
                "job_text": job_text,
                "links": links_text
            })
            
            # Post-process the email to ensure proper formatting
            email_content = res.content
            
            # Add signature if not present
            if "Ahmed" not in email_content.split('\n')[-3:]:
                email_content += "\n\nBest regards,\nAhmed\nBusiness Development Executive\nTechFlow Solutions\nahmed@techflowsolutions.com\n+1 (555) 123-4567"
            
            return email_content
            
        except Exception as e:
            logging.error(f"Error generating email: {e}")
            return f"Error generating email: {str(e)}"
    
    def refine_email(self, email_content, feedback):
        """Refine the generated email based on user feedback"""
        refine_prompt = PromptTemplate.from_template(
            """
            Here's a cold email that was generated:
            
            {email_content}
            
            Please refine it based on this feedback:
            {feedback}
            
            Return the improved version while maintaining the professional tone and structure.
            """
        )
        
        chain = refine_prompt | self.llm
        
        try:
            res = chain.invoke({
                "email_content": email_content,
                "feedback": feedback
            })
            return res.content
        except Exception as e:
            logging.error(f"Error refining email: {e}")
            return email_content  # Return original if refinement fails
    
    def generate_subject_line(self, job_text):
        """Generate compelling subject lines for the email"""
        subject_prompt = PromptTemplate.from_template(
            """
            Based on this job posting, generate 3 compelling email subject lines that would make a hiring manager want to open the email:
            
            {job_text}
            
            Guidelines:
            - Keep them under 50 characters
            - Make them specific and relevant
            - Avoid spam words
            - Show value proposition
            
            Return only the 3 subject lines, one per line.
            """
        )
        
        chain = subject_prompt | self.llm
        
        try:
            res = chain.invoke({"job_text": job_text})
            return res.content.strip().split('\n')
        except Exception as e:
            logging.error(f"Error generating subject lines: {e}")
            return [
                "Partnership Opportunity - AI & Software Solutions",
                "Solving Your Technical Challenges",
                "Your Next Technology Partner"
            ]
    
    def test_connection(self):
        """Test if the LLM connection is working"""
        try:
            test_prompt = PromptTemplate.from_template("Say 'Connection successful' if you can read this.")
            chain = test_prompt | self.llm
            result = chain.invoke({})
            return "Connection successful" in result.content
        except Exception as e:
            logging.error(f"Connection test failed: {e}")
            return False
