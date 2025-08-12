import os
import json
import time
from datetime import datetime
from .ai_matcher import JobMatcher
from config.logging_config import log_manager

class JobScorer:
    def __init__(self):
        self.job_matcher = JobMatcher()
        self.scored_jobs = {}
        self.logger = log_manager.get_logger(__name__)
    
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
                self.logger.info("No job description files found")
                return
        
        self.logger.info(f"Processing jobs from: {jobs_file}")
        
        try:
            with open(jobs_file, 'r') as f:
                jobs = json.load(f)
        except FileNotFoundError:
            self.logger.error(f"No jobs file found at {jobs_file}")
            return
        
        # Create new scored jobs file
        scored_file = self._get_scored_filename(jobs_file)
        self.logger.info(f"Scored jobs will be saved to: {scored_file}")
        
        for job_id, job_data in jobs.items():
            self.logger.info(f"Scoring job: {job_data['job_title']} at {job_data['company_name']}")
            try:
                # Get both scores
                start_api = time.perf_counter()
                scores = self.job_matcher.get_scores(job_data['job_description'])
                api_latency_ms = int((time.perf_counter() - start_api) * 1000)
                match_score = scores.get('match_score', 0)
                ats_pick_likelihood = scores.get('ats_pick_likelihood', 0)

                # Add scores and timestamp to job data
                scored_job = {
                    **job_data,
                    'match_score': match_score,
                    'ats_pick_likelihood': ats_pick_likelihood,
                    'scored_at': datetime.now().isoformat()
                }
                
                # Update scored jobs
                self.scored_jobs[job_id] = scored_job
                
                # Save after each successful scoring
                with open(scored_file, 'w') as f:
                    json.dump(self.scored_jobs, f, indent=2)
                
                self.logger.info(
                    f"Scores — job_id={job_id} match: {match_score}/100, ats: {ats_pick_likelihood}/100 (latency: {api_latency_ms} ms)"
                )
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                self.logger.error(f"Error scoring job {job_id}: {str(e)}")
                continue
        
        self.logger.info(f"Finished scoring jobs. Results saved to {scored_file}")