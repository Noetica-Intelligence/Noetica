import requests
from datetime import datetime, timedelta
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CLINICAL_TRIALS_API_URL = "https://clinicaltrials.gov/api/v2/studies"

def fetch_recent_oncology_trials(days_back=7):
    """Fetches recent clinical trials related to Oncology/Cancer."""
    logger.info(f"Fetching oncology clinical trials from the last {days_back} days...")
    
    date_from = (datetime.utcnow() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    
    # Using the ClinicalTrials.gov API v2
    params = {
        "query.cond": "cancer OR oncology OR tumor",
        "filter.advanced": f"AREA[StudyFirstPostDate]RANGE[{date_from},MAX]",
        "pageSize": 20,
        "format": "json"
    }
    
    try:
        response = requests.get(CLINICAL_TRIALS_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        trials = []
        for study in data.get('studies', []):
            protocol = study.get('protocolSection', {})
            id_module = protocol.get('identificationModule', {})
            status_module = protocol.get('statusModule', {})
            desc_module = protocol.get('descriptionModule', {})
            
            nct_id = id_module.get('nctId')
            title = id_module.get('briefTitle', 'Unknown Title')
            status = status_module.get('overallStatus', 'Unknown')
            abstract = desc_module.get('briefSummary', '')
            
            trials.append({
                "id": f"nct_{nct_id}",
                "source": "ClinicalTrials.gov",
                "title": f"[Clinical Trial] {title}",
                "status": status,
                "abstract": abstract,
                "url": f"https://clinicaltrials.gov/study/{nct_id}",
                "domain": "Clinical Oncology"
            })
            
        logger.info(f"Successfully fetched {len(trials)} clinical trials.")
        return trials
        
    except Exception as e:
        logger.error(f"Failed to fetch clinical trials: {e}")
        return []

if __name__ == "__main__":
    trials = fetch_recent_oncology_trials()
    for t in trials[:3]:
        print(f"{t['nct_id']}: {t['title']} ({t['status']})")
