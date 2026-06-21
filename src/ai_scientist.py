import sys
import os
from pathlib import Path
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from backend.app.database import SessionLocal
from backend.app.models import Discovery

try:
    import google.generativeai as genai
except ImportError:
    genai = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_synthesis_report():
    logger.info("Starting AI Scientist Synthesis...")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.warning("No GEMINI_API_KEY detected in environment. Using mocked synthesis report for UI.")
        return """## 🧬 The Noetica AI Synthesis Report
*(Mocked Data - Add GEMINI_API_KEY to enable live AI generation)*

**Cross-Disciplinary Convergence:**
Our engine has detected a critical convergence between advanced targeted Oncology trials and emerging quantum computational modeling. The structural folding algorithms mapped in Discovery #1 provide the theoretical framework for the clinical outcomes observed in Discovery #2.

**Humanity Impact Vector:**
This signals an imminent paradigm shift in personalized therapeutics. The fusion of computational topology with in-vivo cancer trials suggests we are within 18 months of highly deterministic, patient-specific molecular interventions."""

    if not genai:
        return "google-generativeai library not installed. Run: pip install google-generativeai"

    genai.configure(api_key=api_key)
    # Using Gemini 1.5 Pro for deep scientific reasoning
    model = genai.GenerativeModel('gemini-1.5-pro')

    db = SessionLocal()
    # Grab the top 3 highest scoring discoveries mathematically ranked by Zig
    top_discoveries = db.query(Discovery).order_by(Discovery.significance_score.desc()).limit(3).all()
    db.close()

    if not top_discoveries:
        return "No discoveries found in database to synthesize."

    prompt = """You are the Noetica AI Scientist, a world-class Polymath and Computational Oncologist.
Analyze the following 3 breakthrough scientific discoveries. 
Write a highly advanced, 3-paragraph Synthesis Report explaining exactly how they might be connected, 
and what their collective impact is on the trajectory of human civilization. Do not use filler words. Be precise.

Discoveries:
"""
    for i, d in enumerate(top_discoveries):
        prompt += f"\n[{i+1}] {d.title}\nDomain: {d.primary_domain}\nAbstract: {d.abstract}\n"

    logger.info("Transmitting to Gemini Neural Net...")
    try:
        response = model.generate_content(prompt)
        report = response.text
        logger.info("AI Synthesis generated successfully.")
        
        with open("latest_synthesis.md", "w", encoding="utf-8") as f:
            f.write(report)
            
        return report
    except Exception as e:
        logger.error(f"AI Generation failed: {e}")
        return f"Synthesis Failed: {str(e)}"

if __name__ == "__main__":
    report = generate_synthesis_report()
    print("\n" + "="*50)
    print(report)
    print("="*50 + "\n")
