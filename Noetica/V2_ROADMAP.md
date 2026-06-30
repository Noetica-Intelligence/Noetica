# 🗺️ Noetica Version 2.0: The Precision Update (Roadmap)

While Version 1.0 successfully laid the foundation for autonomous intelligence and zero-cost scaling, Version 2.0 focuses entirely on Academic Quality of Life (QoL), hyper-precision targeting, and structural readability. 

These are the 6 core features planned for the post-beta development sprint:

---

### 1. Guaranteed Domain Representation (The "No-Starvation" Algorithm)
*   **The Problem:** If a massive AI breakthrough happens on Monday, the Zig scoring engine might accidentally fill an entire email with AI papers, ignoring the user's other selected fields (e.g., Biotech).
*   **The V2 Solution:** The engine will enforce a strict "Domain Quota." If a user selects 3 distinct domains, Noetica will guarantee that the final email contains *at least one* top-scoring breakthrough from every single chosen domain to prevent topic starvation.

### 2. Sub-Domain Precision Targeting
*   **The Problem:** Major paradigms like "Medicine" or "Physics" are too broad.
*   **The V2 Solution:** Users will be able to input specific keywords, MeSH terms, or sub-domains (e.g., "CRISPR in liver cells", "Graph Neural Networks"). The Python fetchers will aggressively pre-filter global databases using these precise strings before scoring even begins.

### 3. One-Click Citation Export
*   **The Problem:** Academics waste hours manually formatting citations for papers they discover.
*   **The V2 Solution:** Directly beneath every discovery in the email, Noetica will inject one-click citation buttons (`[Copy APA]` | `[Copy BibTeX]`). Clicking them will instantly copy the perfectly formatted citation to the user's clipboard.

### 4. Structured Pointwise Synthesis
*   **The Problem:** Dense paragraphs take too long to read. 
*   **The V2 Solution:** We will update the Gemini AI prompt to completely reformat the "Executive Summary" into a strictly structured, highly scannable bullet-point layout:
    *   **Context (3-4 lines):** Why does this matter?
    *   **Methodology:** What was the actual workflow or material used?
    *   **Key Findings & Future Directions (3-4 lines):** What is the paradigm shift?

### 5. Seamless Compliance (One-Click Unsubscribe)
*   **The Problem:** Users need an easy way to opt-out or pause their intelligence briefs.
*   **The V2 Solution:** A secure, one-click `Unsubscribe / Manage Preferences` footer will be added to every email, ensuring Noetica complies with global anti-spam laws (CAN-SPAM) and builds maximum trust with beta testers.

### 6. Direct "Read Full PDF" Injection
*   **The Problem:** Navigating through publisher websites to find the actual PDF is tedious.
*   **The V2 Solution:** We will integrate the free *Unpaywall API*. If an open-access PDF exists for a highly-scored paper, Noetica will bypass the abstract page and inject a direct link straight to the PDF file inside the email.
