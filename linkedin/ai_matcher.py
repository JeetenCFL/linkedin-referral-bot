import os
import json
import pdfplumber
from openai import OpenAI
from dotenv import load_dotenv

class JobMatcher:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self._resume_text = None
        self._my_needs = None
        
    def _load_resume_text(self):
        """Load resume text from PDF, only once."""
        if self._resume_text is None:
            resume_path = os.path.join('config', 'resume.pdf')
            all_text = []
            with pdfplumber.open(resume_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        all_text.append(text)
            self._resume_text = '\n'.join(all_text)
        return self._resume_text
    
    def _load_my_needs(self):
        """Load my_needs from settings, only once."""
        if self._my_needs is None:
            with open(os.path.join('config', 'settings.json'), 'r') as f:
                settings = json.load(f)
                self._my_needs = settings.get('my_needs', '')
        return self._my_needs
    
    def create_matching_prompt(self, job_description):
        """Create the prompt for job matching."""
        resume_text = self._load_resume_text()
        my_needs = self._load_my_needs()
        
        return f"""You are a job matching expert. Analyze the following resume, job description, and candidate's needs to determine the likelihood of the candidate getting this job.

Resume:
{resume_text}

Job Description:
{job_description}

What I'm Looking For:
{my_needs}

Based on the above information, provide a match score from 0-10 where:
- 0 means extremely unlikely to get the job (major mismatches in requirements, experience, or qualifications)
- 10 means extremely likely to get the job (perfect match in skills, experience, and qualifications)

Consider factors like:
- Required skills match with your experience
- Years of experience match with requirements
- Education and qualifications alignment
- Industry experience relevance
- Location and work arrangement preferences
- Overall fit with company culture and role expectations

Respond ONLY with a JSON object containing a single key "match_score" with a number between 0 and 10."""

    def get_match_score(self, job_description):
        """Get match score for a job description."""
        # Create and send prompt
        prompt = self.create_matching_prompt(job_description)
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are a job matching expert that provides match scores in JSON format."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Parse and return the match score
        result = json.loads(response.choices[0].message.content)
        return result.get('match_score', 0) 