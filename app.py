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
        with st.spinner("Executing high-density agency-grade rubric analysis..."):
            try:
                client = openai.OpenAI(api_key=openai_api_key)
                
                # THE HIGH-DENSITY SYSTEM PROMPT
                system_prompt = """
                You are a ruthless, top-tier B2B Managing Editor and Technical SEO Strategist. 
                Your feedback must be incredibly dense, highly specific, and comprehensive. Do not be brief.
                
                Start with a perfect score of 25 for each of the 4 pillars, and DEDUCT points for specific infractions.
                
                You MUST return a valid JSON object matching this exact schema:
                {
                    "global_score": 82,
                    "top_3_actions": [
                        "A dense, 2-sentence explanation of the first major structural fix required.", 
                        "A dense, 2-sentence explanation of the second fix.", 
                        "A dense, 2-sentence explanation of the third fix."
                    ],
                    "pillars": {
                        "editorial": {
                            "score": 20,
                            "comprehensive_analysis": "Write a dense, 3-4 sentence paragraph explaining the overall tone, flow, and structural flaws of the piece.",
                            "line_edits": [
                                {"quote": "[Exact weak sentence 1]", "rewrite": "[Pro rewrite]", "reason": "Why this change matters."},
                                {"quote": "[Exact weak sentence 2]", "rewrite": "[Pro rewrite]", "reason": "Why this change matters."}
                            ]
                        },
                        "competitive_info_gain": {
                            "score": 18,
                            "identified_competitors": ["Competitor A", "Competitor B"],
                            "gap_analysis": "Write a comprehensive 3-4 sentence paragraph explaining exactly what angles or themes the competitors covered that this draft missed entirely.",
                            "recommended_additions": [
                                "Highly specific section to add (e.g., 'Pricing Breakdown') and what it should include.",
                                "Highly specific case study, metric, or data point needed to win the click."
                            ]
                        },
                        "seo_structure": {
                            "score": 22,
                            "entity_salience": "A detailed 2-3 sentence explanation of whether the target topic and related LSI keywords are clearly defined early in the text.",
                            "header_optimizations": [
                                {"current_h2": "[Quote current weak H2/H3]", "suggested_h2": "[Optimized H2/H3]", "reasoning": "Intent match improvement."}
                            ]
                        },
                        "geo_parseability": {
                            "score": 15,
                            "definitional_clarity": "Provide a complete, copy-pasteable 2-3 sentence 'What is X?' definition optimized specifically for LLM extraction that they can insert into their draft.",
                            "suggested_table": "Describe a specific data table the writer should insert. Tell them exactly what the column headers and row data should represent to make the piece more AI-parseable.",
                            "structural_formatting": "A detailed paragraph critiquing their lack of bullet points, bold text, or scanning elements."
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
                
                response = client.chat.completions.create(
                    model="gpt-4o",
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.3 # Slightly higher to allow for more robust paragraph generation
                )
                
                result = json.loads(response.choices[0].message.content)
                
                # --- RENDER THE NEW DENSE DASHBOARD ---
                st.success("Deep Analysis Complete!")
                
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
                
                st.subheader("🚀 Top 3 Mandatory Revisions")
                for action in result.get("top_3_actions", []):
                    st.warning(action)
                    
                st.divider()
                
                st.subheader("🔍 The Definitive Grading Rubric")
                
                # Editorial Expander
                with st.expander(f"✍️ Editorial & Brand Voice ({pillars.get('editorial', {}).get('score', 0)}/25)"):
                    ed = pillars.get('editorial', {})
                    st.markdown(f"**Comprehensive Analysis:**<br>{ed.get('comprehensive_analysis')}", unsafe_allow_html=True)
                    st.markdown("---")
                    st.markdown("**Surgical Line Edits:**")
                    for edit in ed.get('line_edits', []):
                        st.error(f"**Weak Copy:** \"{edit.get('quote')}\"")
                        st.success(f"**Pro Rewrite:** \"{edit.get('rewrite')}\"")
                        st.caption(f"**Reasoning:** {edit.get('reason')}")
                        st.write("")
                
                # Info Gain Expander
                with st.expander(f"⚔️ Information Gain & Competitors ({pillars.get('competitive_info_gain', {}).get('score', 0)}/25)"):
                    ig = pillars.get('competitive_info_gain', {})
                    st.markdown(f"**Competitive Gap Analysis:**<br>{ig.get('gap_analysis')}", unsafe_allow_html=True)
                    st.markdown("---")
                    st.markdown("**Required Additions to Win the Click:**")
                    for addition in ig.get('recommended_additions', []):
                        st.markdown(f"• {addition}")
                
                # SEO Expander
                with st.expander(f"📈 SEO & Intent Match ({pillars.get('seo_structure', {}).get('score', 0)}/25)"):
                    seo = pillars.get('seo_structure', {})
                    st.markdown(f"**Entity Salience (First 100 Words):**<br>{seo.get('entity_salience')}", unsafe_allow_html=True)
                    st.markdown("---")
                    st.markdown("**Header Optimizations:**")
                    for header in seo.get('header_optimizations', []):
                        st.warning(f"**Current:** {header.get('current_h2')}")
                        st.success(f"**Optimized:** {header.get('suggested_h2')}")
                        st.caption(f"**Reasoning:** {header.get('reasoning')}")
                        st.write("")
                
                # GEO Expander
                with st.expander(f"🤖 GEO / AI Parseability ({pillars.get('geo_parseability', {}).get('score', 0)}/25)"):
                    geo = pillars.get('geo_parseability', {})
                    st.markdown(f"**Definitional Clarity (Copy-Paste Insert):**<br>*{geo.get('definitional_clarity')}*", unsafe_allow_html=True)
                    st.markdown("---")
                    st.markdown(f"**Suggested Data Table:**<br>{geo.get('suggested_table')}", unsafe_allow_html=True)
                    st.markdown("---")
                    st.markdown(f"**Formatting for LLMs:**<br>{geo.get('structural_formatting')}", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"An error occurred during analysis: {str(e)}")
