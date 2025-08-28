import streamlit as st
import openai
import json
import time
from typing import Dict, Any, Optional
import os

# Page configuration
st.set_page_config(
    page_title="JD Extraction Prompt Tester",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .prompt-box {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .result-box {
        background-color: #e8f5e8;
        border: 1px solid #28a745;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #dc3545;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'openai_key' not in st.session_state:
        st.session_state.openai_key = ""
    if 'company_context' not in st.session_state:
        st.session_state.company_context = {
            'name': '',
            'industry': '',
            'company_size': '',
            'headquarters': ''
        }
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 1

def validate_openai_key(api_key: str) -> bool:
    """Validate OpenAI API key by making a test call"""
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        return True
    except Exception as e:
        st.error(f"Invalid OpenAI API key: {str(e)}")
        return False

def show_step1_text_enhancement(model: str, temperature: float, max_tokens: int):
    """Step 1: Text Enhancement"""
    st.markdown('<h2 class="section-header">📝 Step 1: Text Enhancement</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    This step enhances raw job description text into readable, formatted text.
    You can modify the prompt below to improve the enhancement quality.
    """)
    
    # Input area
    st.markdown("### 📥 Input Job Description")
    jd_text = st.text_area(
        "Paste your job description text here:",
        height=200,
        placeholder="Paste your job description text here..."
    )
    
    # Prompt customization
    st.markdown("### ✏️ Prompt Customization")
    
    # Company context section
    company_context_section = f"""
# MINIMAL COMPANY CONTEXT (FOR ROLE ANALYSIS ONLY):
Company Information Available (for context only - DO NOT include in output):
- Name: {st.session_state.company_context['name'] or 'Not specified'}
- Industry: {st.session_state.company_context['industry'] or 'Not specified'}
- Size: {st.session_state.company_context['company_size'] or 'Not specified'}
- Location: {st.session_state.company_context['headquarters'] or 'Not specified'}

CONTEXT APPLICATION RULES:
1. USE FOR ROLE ANALYSIS ONLY: Use company context only to understand the role better
2. DO NOT INCLUDE COMPANY INFO: Do not display company information in the enhanced output
3. FOCUS ON JOB CONTENT: Prioritize and enhance the actual job description content
4. ROLE-SPECIFIC ENHANCEMENT: Enhance based on what the role actually requires, not company details
"""
    
    # Main prompt
    main_prompt = f"""You are a professional job description writer and enhancer with expertise in talent acquisition and HR. 
Extract and significantly enhance the following job description to create a comprehensive, compelling, and precise document.

Your task is to transform this job description into a well-formatted, enhanced text document that covers all the important fields that would typically be in a structured job description. The output should be in PLAIN TEXT format for display in a simple text box.

{company_context_section}

# ENHANCEMENT REQUIREMENTS:

## Format the output as readable plain text covering these sections:
1. Job Title and Basic Information - Include job title, job code (if any), department, job level, job function, and seniority level
2. Industry Classification - List the most relevant industries this position belongs to
3. Experience Requirements - Detail the experience range and qualifications needed
4. Job Summary - A comprehensive overview of the position
5. Key Responsibilities - Detailed list of what the person will do
6. Required Qualifications - Education, experience, and mandatory requirements including college/university preferences
7. Preferred Qualifications - Nice-to-have qualifications, postgraduate degrees, and field of study preferences
8. Skills Required - Technical, domain, and soft skills with proficiency levels
9. Languages and Certifications - Required languages and certifications (if any). If no specific language is mentioned, automatically detect the language of the input text and list it as a required language with "Fluent" proficiency
10. Work Environment and Arrangements:
    - Employment type (full-time, part-time, contract)
    - Workplace type (remote, hybrid, onsite)
    - Location information
    - Travel requirements and shift types
11. Compensation and Benefits (if specified):
    - Base salary and salary ranges
    - Benefits package and perks
    - Relocation assistance and visa sponsorship details
12. Interview Process (if specified):
    - Number of interview rounds
    - Reporting structure and team dynamics
13. Key Performance Indicators - Success metrics for the role

# DETAILED ENHANCEMENT INSTRUCTIONS:

## IMPORTANT: FOCUS ON JOB CONTENT ONLY
- DO NOT include company information sections
- Focus entirely on the job description content and requirements
- Enhance and structure the actual job-related information
- Make the output clean, professional, and focused on the role itself

## For ALL fields:
- Transform vague or generic descriptions into specific, detailed, and meaningful content
- Use professional, industry-standard terminology and clear language
- Ensure all content is actionable, measurable, and relevant for candidate evaluation
- For any fields with no information available, mention "Not specified" or skip the section
- Remove redundant language and filler content that doesn't add value
- **CRITICAL: PRESERVE ALL INFORMATION** - Ensure no information from the original job description is lost or omitted. Every detail, requirement, qualification, responsibility, and specification must be included in the enhanced output

## EXCLUSIVE GUIDELINE -
- Use every single field provided as context or input.
- Establish a user-based relationship by leveraging all available context.
- When generating or enhancing the job description, identify and incorporate all context in a logical, coherent flow.
- Ensure the flow of information justifies the creation or enhancement of the job description.
- The enhanced job description must contribute to the relevance and accuracy of future candidate searches.
- Prioritize sub-industry and company context provided by the user for industry tagging. If additional relevant industries are found, add them; if any are missing, note as such.

## JOB TITLE GENERATION (MOST CRITICAL - COMPREHENSIVE ANALYSIS ACROSS ALL PARAMETERS):
- Generate exactly 4-5 OPTIMAL job titles through COMPREHENSIVE PARAMETER ANALYSIS
- Analyze ALL parameters: responsibilities, skills, experience level, company industry, company size, company stage, qualifications, and role scope
- These titles MUST be optimized for LinkedIn matching and cover different ways this role might be advertised across ALL industries
- Base titles on COMPLETE analysis of job content, company context, and market standards

## IMPORTANT OUTPUT FORMAT:
- Return ONLY formatted text paragraphs, NOT JSON
- Use clear section headers with proper formatting
- Make the text readable and professional with good spacing
- Include all relevant information in a structured, easy-to-read format
- Do NOT include any JSON formatting, brackets, or technical syntax
- The output should be human-readable text suitable for display in a text box
- For skills: Use format "Skill Name (Proficiency Level)" - NOT JSON objects
- For all sections: Use bullet points or numbered lists with plain text, not structured data
- **SPACING**: Add extra line breaks between sections for better readability
- **SECTION SEPARATION**: Use clear visual separation between major sections
- **FORMATTING**: Use consistent formatting with proper indentation and spacing

Enhanced Job Description Text:
{jd_text}

Return only the enhanced job description text in a readable, formatted paragraph structure without any JSON formatting. Focus on the job content, requirements, and responsibilities - do not include company information sections."""

    # Display the prompt
    with st.expander("🔍 View/Edit Prompt", expanded=False):
        st.text_area(
            "Prompt (you can edit this):",
            value=main_prompt,
            height=400,
            key="step1_prompt"
        )
        
        # Save button for the prompt
        if st.button("💾 Save Prompt Changes", key="save_step1_prompt"):
            # Get the current value from the text area
            current_prompt = st.session_state.get("step1_prompt", main_prompt)
            st.session_state.saved_step1_prompt = current_prompt
            st.success("✅ Prompt saved successfully!")
        
        # Use saved prompt if available, otherwise use default
        prompt_to_use = st.session_state.get('saved_step1_prompt', main_prompt)
    
    # Execute button
    if st.button("🚀 Execute Text Enhancement", type="primary", use_container_width=True):
        if not jd_text.strip():
            st.error("Please enter job description text first.")
            return
        
        with st.spinner("Enhancing job description..."):
            try:
                client = openai.OpenAI(api_key=st.session_state.openai_key)
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a world-class job description enhancement specialist with deep expertise in HR, recruiting, and talent acquisition. Your job is to transform basic job descriptions into comprehensive, precise, and compelling documents focused on the job content itself. DO NOT include company information sections. Focus on enhancing and structuring the actual job requirements, responsibilities, and qualifications. For industry classification, use ONLY actual business sector industries (not job functions) from standard categories. Return only formatted text paragraphs, not JSON. For skills, use format 'Skill Name (Proficiency Level)' not JSON objects."},
                        {"role": "user", "content": prompt_to_use}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                enhanced_text = response.choices[0].message.content
                
                # Store in session state for step 2
                st.session_state.enhanced_text = enhanced_text
                
                # Display result
                st.markdown('<h3 class="section-header">✅ Enhanced Job Description</h3>', unsafe_allow_html=True)
                st.markdown('<div class="result-box">', unsafe_allow_html=True)
                st.text_area(
                    "Enhanced Text:",
                    value=enhanced_text,
                    height=400,
                    disabled=True
                )
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Copy button
                st.button("📋 Copy to Clipboard", on_click=lambda: st.write("Copied!"))
                
            except Exception as e:
                st.error(f"Error during enhancement: {str(e)}")

def show_step2_structured_extraction(model: str, temperature: float, max_tokens: int):
    """Step 2: Structured Extraction"""
    st.markdown('<h2 class="section-header">🔧 Step 2: Structured Extraction</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    This step converts enhanced text into structured JSON format.
    You can modify the prompts below to improve extraction quality.
    """)
    
    # Check if we have enhanced text from step 1
    if 'enhanced_text' not in st.session_state or not st.session_state.enhanced_text:
        st.warning("⚠️ Please complete Step 1 first to get enhanced text.")
        return
    
    # Display the enhanced text
    st.markdown("### 📝 Enhanced Text (from Step 1)")
    st.text_area(
        "Enhanced Text:",
        value=st.session_state.enhanced_text,
        height=200,
        disabled=True
    )
    
    # Skills extraction prompt
    st.markdown("### 🎯 Skills Extraction Prompt")
    skills_prompt = f"""You are a skill extraction expert. ALWAYS prioritize the job role over company context. Extract skills appropriate for the specific role, not the company's main business. Return ONLY a JSON array.

Job Title: [Extract from text]
Industry: [Extract from text]
Experience Level: [Extract from text]
Company Info: {st.session_state.company_context}

CRITICAL ROLE-BASED SKILL SELECTION RULES:
1. **MANDATORY ROLE-FIRST APPROACH**: Extract skills appropriate for THIS SPECIFIC ROLE, NOT the company's main business
2. **FOR UNRELATED ROLES**: Use ONLY standard industry skills for that role, ignore company-specific technologies
3. **ONLY for DIRECTLY RELATED ROLES**: Integrate relevant company-specific technologies
4. **VALIDATION**: If role is NOT related to company's main business, company-specific tech skills should NOT appear
5. **CRITICAL**: Do NOT include advertising, marketing, or tech skills unless the role is directly related to those functions

**EXPLICIT UNRELATED ROLE INSTRUCTIONS - CRITICAL FOR SKILLS GENERATION:**
- **IF THE ROLE IS UNRELATED TO COMPANY'S MAIN BUSINESS**: 
  - DO NOT use any company-specific technologies, tools, or platforms mentioned in company context
  - DO NOT use company's industry-specific skills unless they directly apply to the role
  - DO NOT use company's proprietary systems or internal tools
  - DO NOT use company's specific methodologies or frameworks unless they are industry-standard for the role
  - DO NOT use company's business domain knowledge unless it's directly relevant to the role
  - **ONLY use standard, industry-appropriate skills for the specific role type**
  - **IGNORE company context completely for skill selection**

**EXAMPLES OF UNRELATED ROLES:**
- If company is a tech company but hiring an HR Manager → Use HR skills, NOT tech skills
- If company is a healthcare company but hiring an Accountant → Use accounting skills, NOT healthcare skills  
- If company is a finance company but hiring a Marketing Specialist → Use marketing skills, NOT finance skills
- If company is a manufacturing company but hiring a Sales Representative → Use sales skills, NOT manufacturing skills

**EXAMPLES OF RELATED ROLES:**
- If company is a tech company hiring a Software Engineer → Use tech skills + company-specific technologies
- If company is a healthcare company hiring a Nurse → Use healthcare skills + company-specific medical systems
- If company is a finance company hiring a Financial Analyst → Use finance skills + company-specific financial tools

DOMAIN-SPECIFIC SKILLS (60-70% of skills):
- Focus on skills that are specific to the role's domain and industry
- Select skills that professionals in this exact role would list on LinkedIn
- Avoid generic skills that don't match the role's specific domain
- Use industry-standard skills for the role's domain

TECHNICAL SKILLS (if relevant, 20-30%):
- Use standard tool/platform names relevant to the role's domain
- Use standard methodologies appropriate for the role's industry
- Use standard technologies that professionals in this role would use

SOFT SKILLS (10-20% maximum):
- Use common LinkedIn terms appropriate for the role's seniority level
- Focus on leadership, communication, and management skills relevant to the role

Format:
   - Return ONLY a JSON array of skill objects
   - Each object: {{"skill_name": "skill", "skill_type": "technical/domain/soft", "proficiency_level": "Beginner/Intermediate/Advanced/Expert"}}
   - Order by importance: domain skills first, then technical, soft skills last
   - No repetition or compound skills
   - Extract EXACTLY 8-10 skills - no more, no less

Remember: Skills must match what successful professionals in this exact role/industry list on LinkedIn.

Enhanced Job Description Text:
{st.session_state.enhanced_text}"""

    # Responsibilities extraction prompt
    st.markdown("### 📋 Responsibilities Extraction Prompt")
    responsibilities_prompt = f"""You are a LinkedIn talent sourcing expert. Extract EXACTLY 6 responsibilities that match how real professionals describe their work on LinkedIn.

Job Title: [Extract from text]
Job Description:
{st.session_state.enhanced_text[:4000]}

CRITICAL RULES FOR LINKEDIN OPTIMIZATION:
1. Think about the ACTUAL day-to-day work:
   - For technical roles: Focus on technical tasks, tools used, and team interactions
   - For business roles: Focus on business impact, client/stakeholder interaction, and deliverables
   - For manual/operational roles: Focus on physical tasks, equipment operated, and procedures followed

2. Format each responsibility:
   - Use 3-6 words, action-oriented
   - Start with strong verbs (e.g., "Lead", "Develop", "Manage", "Implement")
   - Include measurable outcomes where possible
   - Use industry-standard terminology

3. AVOID:
   - Generic responsibilities that could apply to any job
   - Company-specific jargon or acronyms
   - Overly detailed or technical descriptions
   - Responsibilities that don't match the seniority level

4. Structure:
   - Return ONLY a JSON array of 6 strings
   - Order by importance (most critical first)
   - No repetition
   - Each responsibility should be distinct

Example for a Senior Software Engineer:
[
    "Lead backend development team",
    "Architect cloud infrastructure solutions",
    "Implement CI/CD automation pipelines",
    "Mentor junior developers",
    "Design system architecture",
    "Optimize application performance"
]

Example for a Warehouse Operator:
[
    "Operate forklift equipment safely",
    "Manage inventory tracking system",
    "Load/unload delivery trucks",
    "Maintain warehouse organization",
    "Process shipping documentation",
    "Perform equipment maintenance checks"
]

Remember: These responsibilities should match what successful professionals in similar roles list on their LinkedIn profiles."""

    # Base info extraction prompt (NEW - matches original system)
    st.markdown("### 🎯 Base Info Extraction Prompt")
    base_info_prompt = f"""Extract ONLY these fields from the job description. Return ONLY JSON.

CRITICAL RULES:
1. Return ONLY a JSON object with these fields: job_title, job_code, job_level, department, job_function, jd_industry, experience_range, job_summary, required_qualifications, seniority_level, location
2. Use null for missing fields
3. PROCESS ORDER: First extract experience range, then use that to determine seniority level
4. For job titles: 4-5 LinkedIn-optimized titles
5. For jd_industry: CRITICAL ROLE-BASED CLASSIFICATION - Use ONLY industry names from standard categories:
   **MANDATORY RULE**: Classify based on the ROLE'S industry, NOT the company's industry
   **VALIDATION**: If role is NOT related to company's main business, the company industry should NOT appear in jd_industry
   **EXAMPLES OF PROPER INDUSTRIES**: "Software Development", "IT Services and IT Consulting", "Financial Services", "Healthcare", "Manufacturing", "Retail", "Education", "Consulting"
   **EXAMPLES OF WHAT NOT TO USE**: "Quality Assurance", "Testing", "Development", "Sales", "Marketing" (these are job functions, not industries)

6. For experience: {{min: X, max: Y}} - CRITICAL RULES:
   - Extract the EXACT minimum years from the job description
   - If job says "11 years experience" = min: 11, max: 11 (NOT min: 8, max: 11)
   - If job says "8-11 years experience" = min: 8, max: 11
   - If job says "5+ years experience" = min: 5, max: based on seniority level
   - Set MAXIMUM based on seniority level (don't set both min and max to the same value unless job specifies exact years):
     * Internship: max 1 year
     * Entry Level: max 3 years
     * Junior: max 5 years
     * Junior to Mid: max 7 years
     * Mid Level: max 10 years
     * Mid - Senior: max 12 years
     * Senior Level: max 15 years
     * CXO: max 20 years

7. For seniority_level: Use EXACTLY these values: Internship/Entry Level/Junior/Junior to Mid/Mid Level/Mid - Senior/Senior Level/CXO
   - Determine from experience range and job requirements
   - If experience is 0-1 years: Internship
   - If experience is 1-3 years: Entry Level
   - If experience is 3-5 years: Junior
   - If experience is 5-7 years: Junior to Mid
   - If experience is 7-10 years: Mid Level
   - If experience is 10-12 years: Mid - Senior
   - If experience is 12+ years: Senior Level
   - If job title contains C-level terms (CEO, CTO, CFO, etc.): CXO

8. For location: Extract ONLY the physical location, not remote/hybrid status
   - Examples: "San Francisco, CA", "New York, NY", "London, UK"
   - Do NOT include: "Remote", "Hybrid", "On-site" in location field

Enhanced Job Description Text:
{st.session_state.enhanced_text}

Return ONLY a valid JSON object with the specified fields."""

    # Display prompts
    with st.expander("🔍 View/Edit Skills Prompt", expanded=False):
        st.text_area(
            "Skills Extraction Prompt:",
            value=skills_prompt,
            height=300,
            key="skills_prompt"
        )
        
        # Save button for the skills prompt
        if st.button("💾 Save Skills Prompt", key="save_skills_prompt"):
            # Get the current value from the text area
            current_skills_prompt = st.session_state.get("skills_prompt", skills_prompt)
            st.session_state.saved_skills_prompt = current_skills_prompt
            st.success("✅ Skills prompt saved successfully!")
        
        # Use saved prompt if available, otherwise use default
        skills_prompt_to_use = st.session_state.get('saved_skills_prompt', skills_prompt)
    
    with st.expander("🔍 View/Edit Responsibilities Prompt", expanded=False):
        st.text_area(
            "Responsibilities Extraction Prompt:",
            value=responsibilities_prompt,
            height=300,
            key="responsibilities_prompt"
        )
        
        # Save button for the responsibilities prompt
        if st.button("💾 Save Responsibilities Prompt", key="save_responsibilities_prompt"):
            # Get the current value from the text area
            current_responsibilities_prompt = st.session_state.get("responsibilities_prompt", responsibilities_prompt)
            st.session_state.saved_responsibilities_prompt = current_responsibilities_prompt
            st.success("✅ Responsibilities prompt saved successfully!")
        
        # Use saved prompt if available, otherwise use default
        responsibilities_prompt_to_use = st.session_state.get('saved_responsibilities_prompt', responsibilities_prompt)
    
    with st.expander("🔍 View/Edit Base Info Prompt", expanded=False):
        st.text_area(
            "Base Info Extraction Prompt:",
            value=base_info_prompt,
            height=300,
            key="base_info_prompt"
        )
        
        # Save button for the base info prompt
        if st.button("💾 Save Base Info Prompt", key="save_base_info_prompt"):
            # Get the current value from the text area
            current_base_info_prompt = st.session_state.get("base_info_prompt", base_info_prompt)
            st.session_state.saved_base_info_prompt = current_base_info_prompt
            st.success("✅ Base info prompt saved successfully!")
        
        # Use saved prompt if available, otherwise use default
        base_info_prompt_to_use = st.session_state.get('saved_base_info_prompt', base_info_prompt)
    
    # Execute button
    if st.button("🚀 Execute Structured Extraction", type="primary", use_container_width=True):
        with st.spinner("Extracting structured data..."):
            try:
                client = openai.OpenAI(api_key=st.session_state.openai_key)
                
                # Extract base info
                base_info_response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a base info extraction expert. Return ONLY a valid JSON object."},
                        {"role": "user", "content": base_info_prompt_to_use}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                # Extract skills
                skills_response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a skill extraction expert. ALWAYS prioritize the job role over company context. Extract skills appropriate for the specific role, not the company's main business. Return ONLY a JSON array."},
                        {"role": "user", "content": skills_prompt_to_use}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                # Extract responsibilities
                responsibilities_response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a responsibility extraction expert. Return ONLY a JSON array."},
                        {"role": "user", "content": responsibilities_prompt_to_use}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                # Parse responses
                base_info_text = base_info_response.choices[0].message.content
                skills_text = skills_response.choices[0].message.content
                responsibilities_text = responsibilities_response.choices[0].message.content
                
                # Store results
                st.session_state.extraction_results = {
                    'base_info': base_info_text,
                    'skills': skills_text,
                    'responsibilities': responsibilities_text
                }
                
                # Display results
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("### 🎯 Extracted Base Info")
                    st.markdown('<div class="result-box">', unsafe_allow_html=True)
                    st.text_area(
                        "Base Info:",
                        value=base_info_text,
                        height=200,
                        disabled=True
                    )
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown("### 🎯 Extracted Skills")
                    st.markdown('<div class="result-box">', unsafe_allow_html=True)
                    st.text_area(
                        "Skills:",
                        value=skills_text,
                        height=200,
                        disabled=True
                    )
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col3:
                    st.markdown("### 📋 Extracted Responsibilities")
                    st.markdown('<div class="result-box">', unsafe_allow_html=True)
                    st.text_area(
                        "Responsibilities:",
                        value=responsibilities_text,
                        height=200,
                        disabled=True
                    )
                    st.markdown('</div>', unsafe_allow_html=True)
                
                st.success("✅ Structured extraction completed successfully!")
                
            except Exception as e:
                st.error(f"Error during extraction: {str(e)}")

def show_step3_results_comparison():
    """Step 3: Results Comparison"""
    st.markdown('<h2 class="section-header">📊 Step 3: Results Comparison</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    Compare and analyze the results from previous steps.
    """)
    
    if 'enhanced_text' not in st.session_state:
        st.warning("⚠️ Please complete Step 1 first.")
        return
    
    if 'extraction_results' not in st.session_state:
        st.warning("⚠️ Please complete Step 2 first.")
        return
    
    # Display all results
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📝 Enhanced Text (Step 1)")
        st.text_area(
            "Enhanced Text:",
            value=st.session_state.enhanced_text,
            height=300,
            disabled=True
        )
    
    with col2:
        st.markdown("### 🔧 Structured Data (Step 2)")
        st.markdown("**Base Info:**")
        st.code(st.session_state.extraction_results['base_info'])
        st.markdown("**Skills:**")
        st.code(st.session_state.extraction_results['skills'])
        st.markdown("**Responsibilities:**")
        st.code(st.session_state.extraction_results['responsibilities'])
    
    # Export functionality
    st.markdown("### 📤 Export Results")
    
    if st.button("💾 Export as JSON", use_container_width=True):
        export_data = {
            'enhanced_text': st.session_state.enhanced_text,
            'extraction_results': st.session_state.extraction_results,
            'company_context': st.session_state.company_context,
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        st.download_button(
            label="📥 Download JSON",
            data=json.dumps(export_data, indent=2),
            file_name=f"jd_extraction_results_{time.strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

def main():
    st.markdown('<h1 class="main-header">🔍 JD Extraction Prompt Tester</h1>', unsafe_allow_html=True)
    
    # Initialize session state
    initialize_session_state()
    
    # Sidebar for configuration
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        
        # OpenAI API Key
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=st.session_state.openai_key,
            help="Enter your OpenAI API key to test the prompts"
        )
        
        if api_key != st.session_state.openai_key:
            st.session_state.openai_key = api_key
            if api_key and validate_openai_key(api_key):
                st.success("✅ API key validated successfully!")
            elif api_key:
                st.error("❌ Invalid API key")
        
        # Company Context
        st.markdown("### 🏢 Company Context")
        st.session_state.company_context['name'] = st.text_input(
            "Company Name",
            value=st.session_state.company_context['name'],
            placeholder="e.g., TechCorp Inc."
        )
        
        st.session_state.company_context['industry'] = st.text_input(
            "Company Industry",
            value=st.session_state.company_context['industry'],
            placeholder="e.g., Software Development"
        )
        
        st.session_state.company_context['company_size'] = st.text_input(
            "Company Size",
            value=st.session_state.company_context['company_size'],
            placeholder="e.g., 100-500 employees"
        )
        
        st.session_state.company_context['headquarters'] = st.text_input(
            "Headquarters",
            value=st.session_state.company_context['headquarters'],
            placeholder="e.g., San Francisco, CA"
        )
        
        # Model Selection
        st.markdown("### 🤖 Model Selection")
        model = st.selectbox(
            "OpenAI Model",
            ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
            index=0
        )
        
        # Temperature
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.4,
            step=0.1,
            help="Lower values = more deterministic, Higher values = more creative"
        )
        
        # Max Tokens
        max_tokens = st.number_input(
            "Max Tokens",
            min_value=100,
            max_value=4000,
            value=2000,
            step=100
        )
    
    # Main content area
    if not st.session_state.openai_key:
        st.warning("⚠️ Please enter your OpenAI API key in the sidebar to continue.")
        return
    
    # Step navigation
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📝 Step 1: Text Enhancement", use_container_width=True):
            st.session_state.current_step = 1
    with col2:
        if st.button("🔧 Step 2: Structured Extraction", use_container_width=True):
            st.session_state.current_step = 2
    with col3:
        if st.button("📊 Step 3: Results Comparison", use_container_width=True):
            st.session_state.current_step = 3
    
    # Step content
    if st.session_state.current_step == 1:
        show_step1_text_enhancement(model, temperature, max_tokens)
    elif st.session_state.current_step == 2:
        show_step2_structured_extraction(model, temperature, max_tokens)
    elif st.session_state.current_step == 3:
        show_step3_results_comparison()

if __name__ == "__main__":
    main()
