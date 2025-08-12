import os
import json
import pdfplumber
from openai import OpenAI
from dotenv import load_dotenv


# System prompt for the scoring model
SYSTEM_PROMPT = (
    "You are an expert AI/ML hiring screener. Your task is to read a candidate's "
    "resume and a job description, follow the evaluation steps exactly, and output "
    "only the requested JSON object with two scores."
)

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
        """Create the user message content for job scoring using the new template."""
        resume_text = self._load_resume_text()

        return f"""
Resume:
{resume_text}

Job Description:
{job_description}

Candidate facts:
- 2 years professional ML experience
- Specialization: AI/ML with emphasis on NLP
- Relevant focus areas: LLM fine-tuning, Retrieval-Augmented Generation (RAG) pipelines, retrieval systems, embeddings, transformers, classical machine learning

Scoring definitions:
1) match_score (0-100) = likelihood a human recruiter or hiring manager would advance this candidate.
   - Any integer from 0 to 100 is allowed.
   - Anchor points:
     0 = no realistic chance
     25 = weak alignment, several core gaps
     50 = some alignment but notable gaps
     75 = strong alignment, minor gaps
     100 = perfect match on core needs
   - Prioritize core NLP/LLM/RAG/retrieval requirements.
   - Deduct if the role’s primary focus is not in NLP or related AI/ML work, even if tools overlap.
   - Years-of-experience rule:
     * If required years ≤ 4 → no penalty.
     * If required = 5 → apply small deduction (max score ~90 if perfect otherwise).
     * If required = 6 → apply moderate deduction (max score ~70).
     * If required = 7 → apply heavy deduction (max score ~40–50).
     * If required ≥ 8 → match_score = 0 regardless of other factors.
     * If required years are not stated → do not apply penalty.

2) ats_pick_likelihood (0-100) = probability an ATS or keyword filter passes the resume.
   - Any integer from 0 to 100 is allowed.
   - Anchor points:
     0 = almost no keyword overlap
     50 = some relevant keywords present but key ones missing
     100 = all core keywords and phrases present
   - Base only on keyword/phrase overlap: required skills, technologies, and titles.
   - Strong matches include NLP, LLM fine-tuning, transformers, embeddings, vector search, retrieval, RAG, evaluation, classical ML.
   - Ignore years-of-experience for ATS scoring unless the resume explicitly lists a number of years and the JD’s “must have X years” requirement is higher.

Evaluation steps (do internally, do not output):
1) Extract JD core responsibilities, required skills, preferred skills, and years of experience.
2) Score match_score using the above rules, adjusting for domain centrality and years-of-experience curve.
3) Score ats_pick_likelihood using keyword overlap only.
4) Keep the two scores independent.
5) Output final JSON.

Output format:
{{
  "match_score": 0-100,
  "ats_pick_likelihood": 0-100
}}
"""

    def get_scores(self, job_description):
        """Get both match_score and ats_pick_likelihood for a job description (0-100 scale)."""
        from time import perf_counter
        from config.logging_config import log_manager
        logger = log_manager.get_logger(__name__)

        prompt = self.create_matching_prompt(job_description)

        start_time = perf_counter()
        response = self.client.chat.completions.create(
            model="gpt-5",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
        )
        latency_ms = int((perf_counter() - start_time) * 1000)

        result = json.loads(response.choices[0].message.content)
        match_score = result.get("match_score", 0)
        ats_pick_likelihood = result.get("ats_pick_likelihood", 0)

        logger.info(f"LLM scoring latency: {latency_ms} ms")

        return {
            "match_score": match_score,
            "ats_pick_likelihood": ats_pick_likelihood,
        }

    def get_match_score(self, job_description):
        """Backward-compatible helper: returns only match_score (0-100)."""
        scores = self.get_scores(job_description)
        return scores.get("match_score", 0)