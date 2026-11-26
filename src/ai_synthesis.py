"""
Scientific Intelligence Engine - Personalized AI Synthesis
Uses Gemini to generate a tailored executive summary for the user's specific expertise level.
"""

import os
import re
try:
    from google import genai
except ImportError:
    genai = None

try:
    import groq
except ImportError:
    groq = None

_ABSTRACT_CACHE: dict[str, str] = {}


def _build_paper_context(papers: list[dict], limit: int = 5) -> str:
    """Format top discoveries into a compact prompt context."""
    parts = []
    for i, p in enumerate(papers[:limit], 1):
        title = p.get("title", "Untitled")
        domain = p.get("domain", "Unknown")
        abstract = (p.get("abstract") or "")[:500]
        parts.append(f"[{i}] {title}\nDomain: {domain}\nAbstract excerpt: {abstract}...\n")
    return "\n".join(parts)


def _call_gemini(prompt: str) -> str:
    """Call Google GenAI using configured or active Flash model fallbacks."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or not genai:
        return ""
    client = genai.Client(api_key=api_key)
    candidates = [
        m for m in [
            os.environ.get("GEMINI_MODEL", "").strip(),
            "gemini-flash-latest",
            "gemini-2.5-flash",
        ]
        if m
    ]
    last_err = None
    for model_name in candidates:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            text = (getattr(response, "text", None) or "").strip()
            if text:
                return text
        except Exception as e:
            last_err = e
    if last_err:
        print(f"   ⚠️  Gemini call failed ({candidates[-1]}): {last_err}")
    return ""


def _call_groq(prompt: str, system_prompt: str, max_tokens: int = 600) -> str:
    """Call Groq Llama model when configured."""
    api_key_groq = os.environ.get("GROQ_API_KEY")
    if not api_key_groq or not groq:
        return ""
    try:
        client = groq.Groq(api_key=api_key_groq, max_retries=3)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.3,
        )
        return (response.choices[0].message.content or "").strip()
    except Exception as e:
        print(f"   ⚠️  Groq call failed: {e}")
        return ""


def _strip_code_fences(text: str) -> str:
    """Remove wrapping markdown code fences that LLMs sometimes emit around HTML."""
    cleaned = text.strip()
    cleaned = re.sub(r'^```(?:html)?\s*\n?', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\n?```\s*$', '', cleaned)
    return cleaned.strip()


def _clean_structured_html(text: str) -> str:
    """Normalize markdown bold/bullets and newlines into clean email-safe HTML."""
    text = _strip_code_fences(text)
    text = text.replace("\\r\\n", "\n").replace("\r\n", "\n").replace("\\n", "\n")
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'<br\s*/?>', '<br>', text, flags=re.IGNORECASE)
    text = re.sub(
        r'(?:<br>\s*|\n)[ \t]*(?:[-*][ \t]+|[-*](?=<(?:b|i|strong|em)>))',
        '<br>&nbsp;&nbsp;&bull; ',
        text,
    )
    text = text.replace("\n", " ")
    text = re.sub(r'(<br>)?\s*(<b>\s*[23]\.)', lambda m: (m.group(1) or '<br><br>') + m.group(2), text)
    return re.sub(r' {2,}', ' ', text).strip()


def format_abstract_pointwise(abstract: str) -> str:
    """
    Format a raw abstract into a structured, easily understandable 3-point format.
    """
    if not abstract:
        return ""
    if abstract in _ABSTRACT_CACHE:
        return _ABSTRACT_CACHE[abstract]

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
    text = _call_gemini(prompt)
    if not text:
        text = _call_groq(
            prompt,
            "You are a concise science communicator. Output only clean HTML using <b> and <br> tags.",
            max_tokens=350,
        )
    if text:
        _ABSTRACT_CACHE[abstract] = _clean_structured_html(text)
        return _ABSTRACT_CACHE[abstract]
    return abstract


def _clean_synthesis_html(text: str) -> str:
    """Normalize markdown bold, fences, and paragraph breaks for executive synthesis HTML."""
    text = _strip_code_fences(text)
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    if "<br>" not in text.lower() and "<p>" not in text.lower():
        text = text.replace("\n\n", "<br><br>").replace("\n", " ")
    return text


def generate_personalized_synthesis(papers: list[dict], expertise: str, interests: str) -> str:
    """
    Generate a personalized 2-paragraph synthesis of the top papers
    calibrated to the user's expertise level.
    """
    if not papers:
        return ""

    paper_context = _build_paper_context(papers, limit=5)
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
    system_msg = (
        "You are the Noetica AI Intelligence Director. You MUST format your response using "
        "standard HTML <p> tags for every paragraph to ensure readability. Never output a single "
        "massive wall of text. Write exactly 2 distinct paragraphs."
    )
    text = _call_groq(prompt, system_msg, max_tokens=600)
    if not text:
        text = _call_gemini(prompt)
    if not text:
        return ""
    return _clean_synthesis_html(text)


def _generate_personalized_synthesis_gemini(papers: list[dict], expertise: str, interests: str) -> str:
    """Backward-compatible wrapper for Gemini synthesis."""
    if not papers:
        return ""
    paper_context = _build_paper_context(papers, limit=5)
    prompt = (
        f"Synthesize these scientific discoveries in 2 HTML <p> paragraphs for an {expertise} "
        f"reader interested in {interests}:\n\n{paper_context}"
    )
    text = _call_gemini(prompt)
    return _clean_synthesis_html(text) if text else ""
