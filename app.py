import streamlit as st
import openai
import json

# Page Configuration
st.set_page_config(page_title="B2B Content Scoring Tool", layout="wide")

st.title("🎯 B2B Content Scoring & Feedback Engine")
st.caption("Get instant, actionable editorial, SEO, and GEO analysis with automated competitor tracking.")

# Sidebar for Configuration & API Keys
with st.sidebar:
    st.header("🔑 Configuration")
    openai_api_key = st.text_input("Enter OpenAI API Key", type="password")
    st.info("Your API key is processed securely and never stored permanently.")

# Main Input Form
with st.form("scoring_form"):
    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input("Company Name", placeholder="e.g., Acme Corp")
        target_topic = st.text_input("Target Topic / Focus Keyword", placeholder="e.g., B2B SaaS Churn Reduction")
    with col2:
        company_url = st.text_input("Company Website URL", placeholder="https://www.example.com")
    
    content_draft = st.text_area("Paste Content Draft Here", height=300, placeholder="Paste your full markdown or plain text article here...")
    
    submit_button = st.form_submit_button("Analyze & Score Content")

# Processing and AI Logic
if submit_button:
    if not openai_api_key:
        st.error("Please enter your OpenAI API key in the sidebar to run the analysis.")
    elif not content_draft or not company_name or not target_topic:
        st.error("Please fill out the Company Name, Target Topic, and Content Draft fields.")
    else:
        with st.spinner("Executing deep-dive agency-grade rubric analysis..."):
            try:
                # Initialize OpenAI Client
                client = openai.OpenAI(api_key=openai_api_key)
                
                # THE UPGRADED SYSTEM PROMPT
                system_prompt = """
                You are a ruthless, top-tier B2B Managing Editor and Technical SEO Strategist. 
                Do not provide generic advice like "use active voice" or "add more headings." You must provide granular, receipt-driven feedback.
                
                Start with a perfect score of 25 for each of the 4 pillars, and DEDUCT points for specific infractions.
                
                You MUST return a valid JSON object matching this exact schema:
                {
                    "global_score": 82,
                    "top_3_actions": ["Specific action 1", "Specific action 2", "Specific action 3"],
                    "pillars": {
                        "editorial": {
                            "score": 20,
                            "primary_infraction": "Too much introductory fluff before delivering value.",
                            "quote_from_draft": "[Exact sentence from the user's draft that is failing]",
                            "suggested_rewrite": "[Your ruthless, agency-grade rewrite of that sentence]"
                        },
                        "competitive_info_gain": {
                            "score": 18,
                            "identified_competitors": ["Competitor A", "Competitor B"],
                            "missing_angle": "Identify a specific sub-topic or perspective the competitors cover that this draft missed.",
                            "data_recommendation": "Suggest a specific type of statistic or case study they need to add to win the click."
                        },
                        "seo_structure": {
                            "score": 22,
                            "entity_salience": "Is the target topic clearly defined in the first 100 words? (Yes/No - Explain)",
                            "header_critique": "Critique the specific H2s/H3s used. Are they search-intent aligned?"
                        },
                        "geo_parseability": {
                            "score": 15,
                            "definitional_clarity": "Does this provide a clear, LLM-friendly 'What is X?' definition? If not, write one for them.",
                            "structural_formatting": "Critique their use of bullet points, tables, and bold text for AI scraping."
                        }
                    }
                }
                """
                
                user_prompt = f"""
                Company Name: {company_name}
                Company Website: {company_url}
                Target Topic: {target_topic}
                
                Content Draft to Evaluate:
                {content_draft}
                """
                
                # Call OpenAI API
                response = client.chat.completions.create(
                    model="gpt-4o",
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.2 # Lower temperature for stricter, more analytical output
                )
                
                # Parse JSON Result
                result = json.loads(response.choices[0].message.content)
                
                # --- RENDER THE NEW ROBUST DASHBOARD ---
                st.success("Deep Analysis Complete!")
                
                # Layout columns for Score and Competitors
                score_col, comp_col = st.columns([1, 2])
                
                with score_col:
                    st.header("📊 Evaluation Summary")
                    score = result.get("global_score", 0)
                    if score >= 85:
                        st.balloons()
                        st.metric(label="Publish-Ready Score", value=f"{score}/100", delta="Ready to Publish")
                    elif score >= 70:
                        st.metric(label="Publish-Ready Score", value=f"{score}/100", delta="Needs Minor Edits", delta_color="off")
                    else:
                        st.metric(label="Publish-Ready Score", value=f"{score}/100", delta="- Critical Revisions Needed", delta_color="inverse")
                
                with comp_col:
                    st.header("⚔️ Contextual Competitors Evaluated")
                    pillars = result.get("pillars", {})
                    competitors = pillars.get("competitive_info_gain", {}).get("identified_competitors", [])
                    if competitors:
                        for comp in competitors:
                            st.markdown(f"• **{comp}**")
                    else:
                        st.write("Generic industry baseline used.")
                
                st.divider()
                
                # 2. Top 3 Action Items
                st.subheader("🚀 Top 3 Mandatory Revisions")
                for action in result.get("top_3_actions", []):
                    st.warning(action)
                    
                st.divider()
                
                # 3. Four Pillar Dropdowns
                st.subheader("🔍 The Definitive Grading Rubric")
                
                # Editorial Expander
                with st.expander(f"✍️ Editorial & Brand Voice ({pillars.get('editorial', {}).get('score', 0)}/25)"):
                    ed = pillars.get('editorial', {})
                    st.markdown(f"**Primary Infraction:** {ed.get('primary_infraction')}")
                    st.error(f"**Weak Copy:** \"{ed.get('quote_from_draft')}\"")
                    st.success(f"**Pro Rewrite:** \"{ed.get('suggested_rewrite')}\"")
                
                # Info Gain Expander
                with st.expander(f"⚔️ Information Gain & Competitors ({pillars.get('competitive_info_gain', {}).get('score', 0)}/25)"):
                    ig = pillars.get('competitive_info_gain', {})
                    st.markdown(f"**Missing Angle (How to beat them):** {ig.get('missing_angle')}")
                    st.markdown(f"**Data to Add:** {ig.get('data_recommendation')}")
                
                # SEO Expander
                with st.expander(f"📈 SEO & Intent Match ({pillars.get('seo_structure', {}).get('score', 0)}/25)"):
                    seo = pillars.get('seo_structure', {})
                    st.markdown(f"**Entity Salience (First 100 Words):** {seo.get('entity_salience')}")
                    st.markdown(f"**Header Structure Critique:** {seo.get('header_critique')}")
                
                # GEO Expander
                with st.expander(f"🤖 GEO / AI Parseability ({pillars.get('geo_parseability', {}).get('score', 0)}/25)"):
                    geo = pillars.get('geo_parseability', {})
                    st.markdown(f"**Definitional Clarity:** {geo.get('definitional_clarity')}")
                    st.markdown(f"**Formatting for LLMs:** {geo.get('structural_formatting')}")

            except Exception as e:
                st.error(f"An error occurred during analysis: {str(e)}")
