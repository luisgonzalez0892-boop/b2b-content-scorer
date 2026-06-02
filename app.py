import streamlit as st
import openai
import json

# Page Configuration
st.set_page_config(page_title="B2B Content Scoring Tool", layout="wide")

st.title("🎯 B2B Content Scoring & Feedback Engine")
st.caption("Get instant, actionable editorial, SEO, and GEO analysis before human review.")

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
        competitor_urls = st.text_area("Competitor URLs (One per line)", placeholder="Optional: Add top 2-3 competitor links for context")
    
    content_draft = st.text_area("Paste Content Draft Here", height=300, placeholder="Paste your full markdown or plain text article here...")
    
    submit_button = st.form_submit_button("Analyze & Score Content")

# Processing and AI Logic
if submit_button:
    if not openai_api_key:
        st.error("Please enter your OpenAI API key in the sidebar to run the analysis.")
    elif not content_draft or not company_name or not target_topic:
        st.error("Please fill out the Company Name, Target Topic, and Content Draft fields.")
    else:
        with st.spinner("Analyzing content depth, competitive stacking, SEO, and GEO patterns..."):
            try:
                # Initialize OpenAI Client
                client = openai.OpenAI(api_key=openai_api_key)
                
                # Formulate the System Prompt (The Rules)
                system_prompt = """
                You are an expert B2B Content Director, SEO Strategist, and Generative Engine Optimization (GEO) specialist. 
                Your task is to analyze a content draft and provide objective, highly actionable feedback.
                
                You must return your analysis strictly as a valid JSON object. Do not include any markdown formatting or commentary outside the JSON.
                The JSON must follow this exact schema:
                {
                    "global_score": 78,
                    "top_3_actions": ["Action 1", "Action 2", "Action 3"],
                    "editorial_score": 20,
                    "editorial_feedback": "Detailed feedback on tone, clarity, and brand alignment.",
                    "competitive_score": 18,
                    "competitive_feedback": "Detailed feedback on information gain and depth vs competitors.",
                    "seo_score": 22,
                    "seo_feedback": "Detailed feedback on keyword intent, structure, and internal linking.",
                    "geo_score": 15,
                    "geo_feedback": "Detailed feedback on LLM-parseability, data density, and clear definitions."
                }
                Each score sub-category must be out of 25 points, combining for a global score out of 100 points.
                """
                
                user_prompt = f"""
                Company Name: {company_name}
                Company Website: {company_url}
                Target Topic: {target_topic}
                Known Competitors: {competitor_urls}
                
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
                    temperature=0.2
                )
                
                # Parse JSON Result
                result = json.loads(response.choices[0].message.content)
                
                # --- RENDER DASHBOARD ---
                st.success("Analysis Complete!")
                
                # 1. Hero Score Section
                st.header("📊 Evaluation Summary")
                score = result.get("global_score", 0)
                
                if score >= 85:
                    st.balloons()
                    st.metric(label="Publish-Ready Score", value=f"{score}/100", delta="Ready to Publish")
                elif score >= 70:
                    st.metric(label="Publish-Ready Score", value=f"{score}/100", delta="Needs Minor Edits", delta_color="off")
                else:
                    st.metric(label="Publish-Ready Score", value=f"{score}/100", delta="- Critical Revisions Needed", delta_color="inverse")
                
                # 2. Top 3 Action Items
                st.subheader("🚀 Top 3 High-Impact Fixes")
                for action in result.get("top_3_actions", []):
                    st.info(action)
                    
                st.divider()
                
                # 3. Four Pillar Dropdowns
                st.subheader("🔍 Detailed Pillar Breakdown")
                
                with st.expander(f"✍️ Editorial & Brand Alignment ({result.get('editorial_score', 0)}/25)"):
                    st.write(result.get("editorial_feedback", "No feedback provided."))
                    
                with st.expander(f"⚔️ Competitive Stacking & Information Gain ({result.get('competitive_score', 0)}/25)"):
                    st.write(result.get("competitive_feedback", "No feedback provided."))
                    
                with st.expander(f"📈 SEO Best Practices ({result.get('seo_score', 0)}/25)"):
                    st.write(result.get("seo_feedback", "No feedback provided."))
                    
                with st.expander(f"🤖 GEO / AI Engine Optimization ({result.get('geo_score', 0)}/25)"):
                    st.write(result.get("geo_feedback", "No feedback provided."))
                    
            except Exception as e:
                st.error(f"An error occurred during analysis: {str(e)}")
