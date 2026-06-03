import streamlit as st
import openai
import json

# Page Configuration
st.set_page_config(page_title="B2B Content Scoring Tool", layout="wide")

st.title("🎯 B2B Content Scoring & Feedback Engine")
st.caption("Paragraph-by-paragraph editorial, SEO, and GEO analysis.")

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
        with st.spinner("Executing paragraph-by-paragraph rubric analysis..."):
            try:
                client = openai.OpenAI(api_key=openai_api_key)
                
                system_prompt = """
                You are a ruthless, top-tier B2B Managing Editor and Technical SEO Strategist. 
                Your core task is to provide a linear, PARAGRAPH-BY-PARAGRAPH analysis of the submitted draft.
                
                You MUST return a valid JSON object matching this exact schema:
                {
                    "global_score": 82,
                    "top_3_actions": [
                        "Actionable fix 1", 
                        "Actionable fix 2", 
                        "Actionable fix 3"
                    ],
                    "block_by_block_analysis": [
                        {
                            "original_block_excerpt": "The first 5-7 words of the paragraph being analyzed...",
                            "primary_issue": "e.g., Fluff / Lacks Info Gain / Poor SEO / Missed GEO Format / Solid (No changes)",
                            "critique": "Dense 2-sentence explanation of what is wrong with this specific paragraph.",
                            "pro_rewrite": "A fully rewritten, optimized version of the paragraph."
                        }
                    ],
                    "macro_pillars": {
                        "competitive_info_gain": {
                            "identified_competitors": ["Competitor A", "Competitor B"],
                            "gap_analysis": "3-4 sentences explaining what themes competitors covered that this draft missed.",
                            "recommended_additions": ["Specific section to add", "Specific data point to add"]
                        },
                        "seo_structure": {
                            "entity_salience": "Are the target topic and LSI keywords defined early?",
                            "header_optimizations": [
                                {"current_h2": "Weak H2", "suggested_h2": "Optimized H2", "reasoning": "Intent match"}
                            ]
                        },
                        "geo_parseability": {
                            "definitional_clarity": "Provide a copy-pasteable 2-3 sentence 'What is X?' definition.",
                            "suggested_table": "Describe a specific data table the writer should insert.",
                            "structural_formatting": "Critique their lack of bullet points or bold text."
                        }
                    }
                }
                
                Iterate chronologically through the draft. Include at least 3-5 blocks in your block_by_block_analysis array, focusing on the weakest paragraphs that need the most intervention.
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
                    temperature=0.2 
                )
                
                result = json.loads(response.choices[0].message.content)
                
                # RENDER DASHBOARD
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
                    macro = result.get("macro_pillars", {})
                    competitors = macro.get("competitive_info_gain", {}).get("identified_competitors", [])
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
                
                # BLOCK BY BLOCK ANALYSIS
                st.subheader("🔍 Paragraph-by-Paragraph Breakdown")
                blocks = result.get("block_by_block_analysis", [])
                
                for index, block in enumerate(blocks):
                    with st.expander(f"Block {index + 1}: \"{block.get('original_block_excerpt')}...\" - [{block.get('primary_issue')}]"):
                        st.markdown(f"**Critique:** {block.get('critique')}")
                        st.success(f"**Pro Rewrite:** \"{block.get('pro_rewrite')}\"")
                
                st.divider()
                
                # MACRO PILLARS
                st.subheader("🌐 Macro Strategy")
                
                # Info Gain
                with st.expander("⚔️ Information Gain & Competitors"):
                    ig = macro.get('competitive_info_gain', {})
                    st.markdown(f"**Competitive Gap Analysis:**<br>{ig.get('gap_analysis')}", unsafe_allow_html=True)
                    st.markdown("---")
                    st.markdown("**Required Additions:**")
                    for addition in ig.get('recommended_additions', []):
                        st.markdown(f"• {addition}")
                
                # SEO
                with st.expander("📈 SEO & Intent Match"):
                    seo = macro.get('seo_structure', {})
                    st.markdown(f"**Entity Salience:**<br>{seo.get('entity_salience')}", unsafe_allow_html=True)
                    st.markdown("---")
                    st.markdown("**Header Optimizations:**")
                    for header in seo.get('header_optimizations', []):
                        st.warning(f"**Current:** {header.get('current_h2')}")
                        st.success(f"**Optimized:** {header.get('suggested_h2')}")
                        st.caption(f"**Reasoning:** {header.get('reasoning')}")
                        st.write("")
                
                # GEO
                with st.expander("🤖 GEO / AI Parseability"):
                    geo = macro.get('geo_parseability', {})
                    st.markdown(f"**Definitional Clarity:**<br>*{geo.get('definitional_clarity')}*", unsafe_allow_html=True)
                    st.markdown("---")
                    st.markdown(f"**Suggested Data Table:**<br>{geo.get('suggested_table')}", unsafe_allow_html=True)
                    st.markdown("---")
                    st.markdown(f"**Formatting for LLMs:**<br>{geo.get('structural_formatting')}", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"An error occurred during analysis: {str(e)}")
