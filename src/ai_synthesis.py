"""
Scientific Intelligence Engine - Personalized AI Synthesis
Uses Gemini to generate a tailored executive summary for the user's specific expertise level.
"""

import os
try:
    import google.generativeai as genai
except ImportError:
    genai = None

def generate_personalized_synthesis(papers: list[dict], expertise: str, interests: str) -> str:
    """
    Generate a personalized 2-paragraph synthesis of the top papers 
    calibrated to the user's expertise level.
    """
    if not papers:
        return ""
        
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or not genai:
        return ""

    try:
        genai.configure(api_key=api_key)
        # 1.5 Pro is explicitly designed for complex reasoning and deep scientific synthesis
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Build the context
        paper_context = ""
        for i, p in enumerate(papers[:5]): # Max 5 papers for context to keep token count low
            title = p.get("title", "Untitled")
            domain = p.get("domain", "Unknown")
            abstract = p.get("abstract", "")[:500] # Truncate abstract
            paper_context += f"[{i+1}] {title}\nDomain: {domain}\nAbstract excerpt: {abstract}...\n\n"
            
        prompt = f"""You are the Noetica AI Intelligence Director.
Your task is to write a highly personalized, 2-paragraph Executive Synthesis of the day's top scientific discoveries for a specific subscriber.

SUBSCRIBER PROFILE:
- Expertise Level: "{expertise}" 
- Core Interests: "{interests}"

INSTRUCTIONS FOR EXPERTISE LEVEL:
- If Beginner: Use simple analogies, plain language, and explain *why* it matters to humanity. No jargon.
- If Intermediate: You can use some technical terms, but provide brief context.
- If Advanced/Researcher/Industry: Use highly precise, technical, and academic language. Focus on methodology, theoretical implications, and paradigm shifts.

Write exactly 2 paragraphs. The first paragraph should synthesize the most important overarching theme or convergence among these top discoveries. The second paragraph should directly explain why this matters to someone with their specific interests.
Do not use Markdown (no **, no ##). Use raw HTML tags (<b>, <i>, <br>) if you need formatting, but keep it minimal.
Do not include greetings. Just the synthesis.

TOP DISCOVERIES TODAY:
{paper_context}
"""

        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Convert newlines to HTML breaks if they didn't use HTML
        if "<br>" not in text and "<p>" not in text:
            text = text.replace("\n\n", "<br><br>").replace("\n", " ")
            
        return text
    except Exception as e:
        print(f"   ⚠️  Gemini AI Synthesis failed: {e}")
        return ""
