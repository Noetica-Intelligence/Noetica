"""
Scientific Intelligence Engine - Personalized AI Synthesis
Uses Gemini to generate a tailored executive summary for the user's specific expertise level.
"""

import os
try:
    from google import genai
except ImportError:
    genai = None

try:
    import groq
except ImportError:
    groq = None

def format_abstract_pointwise(abstract: str) -> str:
    """
    Format a raw abstract into a structured, easily understandable 3-point format.
    """
    if not abstract:
        return ""
        
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or not genai:
        return abstract

    try:
        client = genai.Client(api_key=api_key)
        # 1.5 Flash is highly generous on the free tier
        
        prompt = f"""You are an expert science communicator.
Your task is to rewrite this scientific abstract into a highly accessible, easy-to-understand 3-point format.
Do NOT just copy-paste the text. Use AI to synthesize and explain the concepts simply so anyone can understand them.

FORMAT REQUIREMENT (Use exactly these bold headers, using HTML <b> tags):
<b>1. Abstract Overview:</b> (Maximum 4 lines, simple summary of what this is about)<br><br>
<b>2. Research Details:</b> (Topic, Workflow, Material, and Methods used)<br><br>
<b>3. Key Findings & Future Directions:</b> (Maximum 3 lines, why this matters)

Do not use Markdown formatting (like **, ##, etc). Use raw HTML tags (<b>, <i>, <br>) for formatting. 

ORIGINAL ABSTRACT:
{abstract}
"""
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        text = response.text.strip()
        
        # Convert markdown bold to HTML bold just in case the AI ignored instructions
        import re
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        
        # We always return the generated text, as the AI likely structured it somehow.
        return text.replace("\\n", " ")
    except Exception as e:
        print(f"   ⚠️  Gemini Abstract Formatting failed: {e}")
        return abstract

def generate_personalized_synthesis(papers: list[dict], expertise: str, interests: str) -> str:
    """
    Generate a personalized 2-paragraph synthesis of the top papers 
    calibrated to the user's expertise level.
    """
    if not papers:
        return ""
        
    api_key_groq = os.environ.get("GROQ_API_KEY")
    if not api_key_groq or not groq:
        # Fallback to Gemini if Groq is missing
        return _generate_personalized_synthesis_gemini(papers, expertise, interests)

    try:
        client = groq.Groq(api_key=api_key_groq, max_retries=5)
        
        
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

        # Dynamic Expertise Router
        exp_lower = expertise.lower()
        if "advanced" in exp_lower or "research" in exp_lower or "industry" in exp_lower:
            target_model = "gpt-oss-120b"
            print(f"      ↳ Routing to Deep Reasoning Model ({target_model})")
        else:
            target_model = "llama-3.3-70b-versatile"
            print(f"      ↳ Routing to Versatile Synthesis Model ({target_model})")

        response = client.chat.completions.create(
            model=target_model,
            messages=[
                {"role": "system", "content": "You are the Noetica AI Intelligence Director. You MUST format your response using standard HTML <p> tags for every paragraph to ensure readability. Never output a single massive wall of text. Write exactly 2 distinct paragraphs."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.3
        )
        text = response.choices[0].message.content.strip()
        
        # Convert newlines to HTML breaks if they didn't use HTML
        if "<br>" not in text and "<p>" not in text:
            text = text.replace("\n\n", "<br><br>").replace("\n", " ")
            
        return text
    except Exception as e:
        print(f"   ⚠️  Groq (Llama 3) Synthesis failed: {e}")
        # Try falling back to Gemini if Groq hits a hard limit
        return _generate_personalized_synthesis_gemini(papers, expertise, interests)

def _generate_personalized_synthesis_gemini(papers: list[dict], expertise: str, interests: str) -> str:
    """Fallback using Gemini if Groq fails or isn't configured."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or not genai:
        return ""
    try:
        client = genai.Client(api_key=api_key)
        paper_context = ""
        for i, p in enumerate(papers[:5]):
            title = p.get("title", "Untitled")
            domain = p.get("domain", "Unknown")
            abstract = p.get("abstract", "")[:500]
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
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        text = response.text.strip()
        if "<br>" not in text and "<p>" not in text:
            text = text.replace("\n\n", "<br><br>").replace("\n", " ")
        return text
    except Exception as e:
        print(f"   ⚠️  Gemini Fallback Synthesis failed: {e}")
        return ""
