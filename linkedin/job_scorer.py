import os
import json
import time
from datetime import datetime
from .ai_matcher import JobMatcher

class JobScorer:
    def __init__(self):
        self.job_matcher = JobMatcher()
        self.scored_jobs = {}
    
    def _get_latest_jobs_file(self):
        """Get the most recent jobs file."""
        job_files = [f for f in os.listdir('.') if f.startswith('job_descriptions_') and f.endswith('.json')]
        if not job_files:
            return None
        return max(job_files)  # This works because of the timestamp format YYYYMMDD_HHMMSS
    
    def _get_scored_filename(self, jobs_file):
        """Generate scored filename based on jobs file."""
        # Extract timestamp from jobs file
        timestamp = jobs_file.replace('job_descriptions_', '').replace('.json', '')
        return f"job_descriptions_scored_{timestamp}.json"
    
    def process_new_jobs(self, jobs_file=None):
        """Process new jobs from the jobs file and update scored jobs.
        
        Args:
            jobs_file (str, optional): Specific jobs file to process. If None, uses most recent.
        """
        # If no specific file provided, use the most recent one
        if jobs_file is None:
            jobs_file = self._get_latest_jobs_file()
            if jobs_file is None:
                print("No job description files found")
                return
        
        print(f"\nProcessing jobs from: {jobs_file}")
        
        try:
            with open(jobs_file, 'r') as f:
                jobs = json.load(f)
        except FileNotFoundError:
            print(f"No jobs file found at {jobs_file}")
            return
        
        # Create new scored jobs file
        scored_file = self._get_scored_filename(jobs_file)
        print(f"Scored jobs will be saved to: {scored_file}")
        
        for job_id, job_data in jobs.items():
            print(f"\nScoring job: {job_data['job_title']} at {job_data['company_name']}")
            try:
                # Get match score
                match_score = self.job_matcher.get_match_score(job_data['job_description'])
                
                # Add score and timestamp to job data
                scored_job = {
                    **job_data,
                    'match_score': match_score,
                    'scored_at': datetime.now().isoformat()
                }
                
                # Update scored jobs
                self.scored_jobs[job_id] = scored_job
                
                # Save after each successful scoring
                with open(scored_file, 'w') as f:
                    json.dump(self.scored_jobs, f, indent=2)
                
                print(f"Score: {match_score}/10")
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"Error scoring job {job_id}: {str(e)}")
                continue
        
        print(f"\nFinished scoring jobs. Results saved to {scored_file}") 