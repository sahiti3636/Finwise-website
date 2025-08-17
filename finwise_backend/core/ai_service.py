import os
import json
import google.generativeai as genai
from typing import Dict, List, Optional, Any
import logging
import re

logger = logging.getLogger(__name__)

class GeminiAIService:
    """AI service using Google Gemini for financial recommendations"""
    
    def __init__(self):
        # Get Gemini API key
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize Gemini model
        try:
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("Gemini AI service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            raise
    
    def generate_chat_response(self, user_message: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a conversational response for the chatbot"""
        try:
            # Create context-aware prompt
            prompt = self._create_chat_prompt(user_message, user_profile)
            
            # Generate response using Gemini
            logger.info(f"Generating chat response with Gemini")
            response = self.model.generate_content(prompt)
            
            # Extract the generated text
            generated_text = response.text.strip()
            logger.info(f"Generated text: {generated_text[:200]}...")
            
            # Clean up the response
            cleaned_response = self._clean_response(generated_text)
            
            # Parse structured response if available
            parsed_response = self._parse_chat_response(cleaned_response)
            
            return {
                "response": parsed_response.get("formatted_response", cleaned_response),
                "suggestions": self._generate_suggestions(user_message),
                "confidence": 0.9,
                "structured_data": parsed_response
            }
            
        except Exception as e:
            logger.error(f"Error generating chat response: {e}")
            return self._get_fallback_chat_response(user_message, user_profile)
    
    def generate_tax_recommendations(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate tax savings recommendations"""
        try:
            # Create tax-specific prompt
            prompt = self._create_tax_prompt(user_profile)
            
            # Generate response using Gemini
            logger.info(f"Generating tax recommendations with Gemini")
            response = self.model.generate_content(prompt)
            
            generated_text = response.text.strip()
            cleaned_response = self._clean_response(generated_text)
            
            # Parse the response into structured format
            parsed_response = self._parse_tax_response(cleaned_response, user_profile)
            logger.info(f"Parsed tax response: {parsed_response}")
            return parsed_response
            
        except Exception as e:
            logger.error(f"Error generating tax recommendations: {e}")
            return self._get_fallback_tax_recommendations(user_profile)
    
    def generate_benefits_recommendations(self, user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate government benefits recommendations"""
        try:
            # Create benefits-specific prompt
            prompt = self._create_benefits_prompt(user_profile)
            
            # Generate response using Gemini
            logger.info(f"Generating benefits recommendations with Gemini")
            response = self.model.generate_content(prompt)
            
            generated_text = response.text.strip()
            cleaned_response = self._clean_response(generated_text)
            
            # Parse the response into structured format
            return self._parse_benefits_response(cleaned_response, user_profile)
            
        except Exception as e:
            logger.error(f"Error generating benefits recommendations: {e}")
            return self._get_fallback_benefits(user_profile)
    
    def _create_chat_prompt(self, user_message: str, user_profile: Dict[str, Any]) -> str:
        """Create a context-aware prompt for chat"""
        income = user_profile.get('income', 0)
        age = user_profile.get('age', 30)
        investment_amount = user_profile.get('investment_amount', 0)
        dependents = user_profile.get('dependents', 0)
        occupation = user_profile.get('occupation', '')
        city = user_profile.get('city', '')
        monthly_savings = user_profile.get('monthly_savings', 0)
        emergency_fund = user_profile.get('emergency_fund', 0)
        retirement_savings = user_profile.get('retirement_savings', 0)
        
        prompt = f"""You are an expert financial advisor with 20+ years of experience specializing in Indian financial markets. You provide clear, actionable, and professional financial advice.

User Profile:
- Income: ₹{income:,} per year (₹{income//12:,}/month)
- Age: {age} years old
- Investment Amount: ₹{investment_amount:,}
- Dependents: {dependents}
- Occupation: {occupation}
- Location: {city}
- Monthly Savings: ₹{monthly_savings:,}
- Emergency Fund: ₹{emergency_fund:,}
- Retirement Savings: ₹{retirement_savings:,}

User Question: {user_message}

Provide comprehensive, professional financial advice in this EXACT format:

**Main Advice:** [Provide 2-3 complete sentences with your primary recommendation. Be specific about what they should do and why it's important for their financial situation.]

**Specific Numbers:** [Give exact amounts, percentages, calculations, or specific figures in ₹. Include at least 2-3 specific numbers relevant to their question. If asking about investments, provide expected returns. If about savings, give target amounts.]

**Action Steps:** [List 3-4 specific, actionable steps they can take immediately. Each step should be clear and implementable. Number them 1, 2, 3, 4.]

**Timeline:** [Provide specific timeline for implementation. Include short-term (1-3 months), medium-term (3-12 months), and long-term (1+ years) actions if applicable.]

**Risks & Considerations:** [List 2-3 important risks, limitations, or factors they should consider. Include how to mitigate these risks.]

IMPORTANT REQUIREMENTS:
1. Fill ALL sections completely - no empty or incomplete responses
2. Use specific numbers and amounts in Indian Rupees (₹)
3. Make advice actionable and implementable
4. Consider their exact financial profile
5. Reference Indian financial products and tax laws when relevant
6. Be professional, clear, and comprehensive
7. Each section must have substantial, useful content

Focus on Indian financial context:
- Indian tax laws (80C, 80D, 80CCD deductions)
- Indian investment products (ELSS, PPF, NPS, mutual funds)
- Indian government schemes (PM-KISAN, Ayushman Bharat, etc.)
- Indian banking and insurance products
- Indian real estate and gold investment options

Example of good response:
**Main Advice:** Based on your ₹{income:,} annual income, you should prioritize building an emergency fund equivalent to 6 months of expenses. This provides financial security and prevents debt during unexpected situations.

**Specific Numbers:** Target emergency fund: ₹{max(300000, income//12*6):,}. Current gap: ₹{max(0, max(300000, income//12*6) - emergency_fund):,}. Monthly contribution needed: ₹{max(0, (max(300000, income//12*6) - emergency_fund)//12):,}.

**Action Steps:** 1. Open a high-yield savings account with 4-6% interest rate. 2. Set up automatic monthly transfers of ₹{max(10000, monthly_savings//2):,}. 3. Reduce non-essential expenses by 15-20%. 4. Consider liquid mutual funds for better returns.

**Timeline:** Start emergency fund building immediately. Achieve 3-month target in 6 months, 6-month target in 12-18 months. Review and adjust monthly contributions quarterly.

**Risks & Considerations:** 1. Don't invest emergency funds in volatile assets. 2. Ensure easy liquidity within 24-48 hours. 3. Consider inflation impact on purchasing power over time.

Now provide your response following this exact format and quality standard."""
        return prompt
    
    def _create_tax_prompt(self, user_profile: Dict[str, Any]) -> str:
        """Create a prompt for tax recommendations"""
        income = user_profile.get('income', 0)
        age = user_profile.get('age', 30)
        dependents = user_profile.get('dependents', 0)
        investment_amount = user_profile.get('investment_amount', 0)
        occupation = user_profile.get('occupation', '')
        marital_status = user_profile.get('marital_status', '')
        
        prompt = f"""As a tax expert specializing in Indian tax laws, provide 5-7 specific tax savings recommendations for:

Profile:
- Income: ₹{income:,} per year
- Age: {age} years old
- Dependents: {dependents}
- Current Investments: ₹{investment_amount:,}
- Occupation: {occupation}
- Marital Status: {marital_status}

Provide detailed tax-saving strategies in this EXACT format:

**Strategy:** [Strategy Name]
**Amount:** [Investment amount in ₹]
**Savings:** [Tax savings in ₹ - calculate based on {income//100000}% tax bracket]
**Implementation:** [Step-by-step implementation]
**Priority:** [High/Medium/Low]
**Risk Level:** [Low/Medium/High]
**Lock-in Period:** [Duration]

Focus on Indian tax laws and products like:
- ELSS mutual funds (80C) - ₹1.5 lakh limit
- PPF (Public Provident Fund) - ₹1.5 lakh limit
- NPS (National Pension System) - ₹2 lakh limit
- Health insurance premiums (80D) - ₹25,000 limit
- Home loan interest (80C) - ₹2 lakh limit
- Education loan interest (80E) - No limit
- HRA exemptions
- Standard deduction of ₹50,000
- Professional tax deductions

Calculate actual savings based on their {income//100000}% tax bracket. Provide at least 5 specific recommendations with exact amounts in Indian Rupees.

IMPORTANT: Use the exact format above with **bold labels** for each section. Make sure each strategy is clearly separated."""
        return prompt
    
    def _create_benefits_prompt(self, user_profile: Dict[str, Any]) -> str:
        """Create a prompt for benefits recommendations"""
        income = user_profile.get('income', 0)
        age = user_profile.get('age', 30)
        occupation = user_profile.get('occupation', '')
        city = user_profile.get('city', '')
        state = user_profile.get('state', '')
        dependents = user_profile.get('dependents', 0)
        education = user_profile.get('education', '')
        
        prompt = f"""As a government benefits expert specializing in Indian government schemes, recommend 5-7 specific available programs for:

Profile:
- Income: ₹{income:,} per year
- Age: {age} years old
- Occupation: {occupation}
- Location: {city}, {state}
- Dependents: {dependents}
- Education: {education}

Provide detailed Indian government benefits in this EXACT format:

**Program:** [Program Name]
**Category:** [Category - Health/Insurance/Savings/etc.]
**Eligibility:** [Specific eligibility criteria]
**Amount:** [Benefit amount in ₹]
**Application:** [Step-by-step application process]
**Timeline:** [Approval and disbursement timeline]
**Documents:** [Required documents]

Focus on Indian government schemes like:
- PM-KISAN: ₹6,000/year for farmers
- Ayushman Bharat: ₹5 lakh health insurance
- PMAY (Pradhan Mantri Awas Yojana): Housing subsidy
- Mudra Loan: Micro business loans
- PMJJBY: ₹2 lakh life insurance for ₹330/year
- PMSBY: ₹2 lakh accident insurance for ₹12/year
- Atal Pension Yojana: Guaranteed pension
- Sukanya Samriddhi Yojana: Girl child savings
- PM Fasal Bima Yojana: Crop insurance
- PM Ujjwala Yojana: LPG connection
- PM Garib Kalyan Yojana: Free food grains
- State-specific schemes for {state}

Recommend programs they likely qualify for based on their profile. Provide at least 5 specific benefits with exact amounts and application steps.

IMPORTANT: Use the exact format above with **bold labels** for each section. Make sure each program is clearly separated."""
        return prompt
    
    def _clean_response(self, generated_text: str) -> str:
        """Clean up the generated response"""
        if not generated_text:
            return "I'm sorry, I couldn't generate a response at this time. Please try again."
        
        # Clean up any artifacts
        response = generated_text.strip()
        response = response.replace('\n\n', '\n').strip()
        
        # Remove any incomplete sentences at the end
        if response and response[-1] not in '.!?':
            # Find the last complete sentence
            sentences = response.split('.')
            if len(sentences) > 1:
                response = '.'.join(sentences[:-1]) + '.'
        
        return response
    
    def _parse_tax_response(self, response: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Parse tax response into structured format"""
        try:
            # Try to extract JSON from the response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                data = json.loads(json_str)
                return data
        except:
            pass
        
        # If no JSON found, create structured recommendations from the text
        income = user_profile.get('income', 0)
        tax_bracket = min(30, max(5, income // 100000))  # 5% to 30% tax bracket
        
        # Create multiple recommendations by parsing the AI response
        recommendations = []
        
        # Split response into sections and parse each recommendation
        sections = response.split('**Strategy:**')
        
        for section in sections[1:]:  # Skip first empty section
            lines = section.strip().split('\n')
            if not lines:
                continue
                
            # Extract strategy name
            strategy_name = lines[0].strip()
            
            # Parse the section for details
            amount = 0
            description = ""
            priority = "medium"
            category = "Tax Optimization"
            action = "Review Options"
            risk = "Low"
            returns = "Tax Savings"
            lock_in = "1 year"
            
            for line in lines:
                line = line.strip()
                if '**Amount:**' in line:
                    # Extract amount information
                    amount_text = line.replace('**Amount:**', '').strip()
                    # Try to extract numeric value
                    amount_match = re.search(r'₹([\d,]+)', amount_text)
                    if amount_match:
                        amount = int(amount_match.group(1).replace(',', ''))
                elif '**Savings:**' in line:
                    # Extract savings information
                    savings_text = line.replace('**Savings:**', '').strip()
                    savings_match = re.search(r'₹([\d,]+)', savings_text)
                    if savings_match:
                        amount = int(savings_match.group(1).replace(',', ''))
                elif '**Priority:**' in line:
                    priority = line.replace('**Priority:**', '').strip().lower()
                elif '**Risk Level:**' in line:
                    risk = line.replace('**Risk Level:**', '').strip()
                elif '**Lock-in Period:**' in line:
                    lock_in = line.replace('**Lock-in Period:**', '').strip()
                elif line and not line.startswith('**'):
                    description += line + " "
            
            # Clean up description
            description = description.strip()
            if not description:
                description = f"Tax optimization strategy: {strategy_name}"
            
            # Calculate potential savings if not found
            if amount == 0:
                # Estimate based on strategy type
                if '80C' in strategy_name or 'ELSS' in strategy_name or 'PPF' in strategy_name:
                    amount = 150000 * tax_bracket // 100
                elif '80D' in strategy_name or 'health' in strategy_name.lower():
                    amount = 25000 * tax_bracket // 100
                elif 'NPS' in strategy_name or '80CCD' in strategy_name:
                    amount = 50000 * tax_bracket // 100
                elif 'HRA' in strategy_name or 'rent' in strategy_name.lower():
                    amount = 50000 * tax_bracket // 100
                else:
                    amount = 10000 * tax_bracket // 100
            
            recommendations.append({
                "title": strategy_name,
                "description": description,
                "potential_saving": amount,
                "priority": priority,
                "category": category,
                "action": action,
                "risk": risk,
                "returns": returns,
                "lock_in": lock_in
            })
        
        # If we couldn't parse any recommendations, create fallback ones
        if not recommendations:
            recommendations = self._create_fallback_tax_recommendations(user_profile)
        
        # Calculate total potential savings
        total_savings = sum(r.get("potential_saving", 0) for r in recommendations)
        
        return {
            "recommendations": recommendations,
            "summary": {
                "total_potential_savings": total_savings,
                "optimization_score": min(90, 60 + (len(recommendations) * 5)),
                "current_tax_saved": 0,
                "tax_bracket": f"{tax_bracket}%"
            }
        }
    
    def _create_fallback_tax_recommendations(self, user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create comprehensive fallback tax recommendations"""
        income = user_profile.get('income', 0)
        age = user_profile.get('age', 30)
        dependents = user_profile.get('dependents', 0)
        tax_bracket = min(30, max(5, income // 100000))
        
        recommendations = []
        
        # 80C deductions
        if income > 500000:
            recommendations.append({
                "title": "ELSS Mutual Funds (Section 80C)",
                "description": f"Invest in Equity Linked Savings Scheme for tax deduction up to ₹1.5 lakh. With your {tax_bracket}% tax bracket, this can save you ₹{150000 * tax_bracket // 100:,} annually.",
                "potential_saving": 150000 * tax_bracket // 100,
                "priority": "high",
                "category": "Section 80C",
                "action": "Open ELSS account",
                "risk": "Medium",
                "returns": "12-15%",
                "lock_in": "3 years"
            })
            
            recommendations.append({
                "title": "Public Provident Fund (PPF)",
                "description": f"Contribute to PPF for tax-free returns. With {tax_bracket}% tax bracket, this can save you ₹{150000 * tax_bracket // 100:,} annually plus earn 7-8% interest.",
                "potential_saving": 150000 * tax_bracket // 100,
                "priority": "high",
                "category": "Section 80C",
                "action": "Open PPF account",
                "risk": "Low",
                "returns": "7-8%",
                "lock_in": "15 years"
            })
        
        # 80D health insurance
        if dependents > 0:
            recommendations.append({
                "title": "Health Insurance Premium (Section 80D)",
                "description": f"Get health insurance for family. With {tax_bracket}% tax bracket, this can save you ₹{25000 * tax_bracket // 100:,} annually on ₹25,000 premium.",
                "potential_saving": 25000 * tax_bracket // 100,
                "priority": "high",
                "category": "Section 80D",
                "action": "Purchase health insurance",
                "risk": "Low",
                "returns": "Tax Benefit + Coverage",
                "lock_in": "1 year"
            })
        
        # NPS for additional deduction
        if age < 60:
            recommendations.append({
                "title": "National Pension System (Section 80CCD)",
                "description": f"Invest in NPS for additional ₹50,000 deduction. With {tax_bracket}% tax bracket, this can save you ₹{50000 * tax_bracket // 100:,} annually.",
                "potential_saving": 50000 * tax_bracket // 100,
                "priority": "medium",
                "category": "Section 80CCD",
                "action": "Open NPS account",
                "risk": "Medium",
                "returns": "8-10%",
                "lock_in": "Till 60"
            })
        
        # HRA exemption if applicable
        if income > 800000:
            recommendations.append({
                "title": "HRA Exemption",
                "description": f"Claim HRA exemption if you pay rent. With {tax_bracket}% tax bracket, this can save you ₹{50000 * tax_bracket // 100:,} annually on ₹50,000 HRA.",
                "potential_saving": 50000 * tax_bracket // 100,
                "priority": "medium",
                "category": "HRA Exemption",
                "action": "Submit rent receipts",
                "risk": "Low",
                "returns": "Tax Benefit",
                "lock_in": "1 year"
            })
        
        return recommendations
    
    def _parse_benefits_response(self, response: str, user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse benefits response into structured format"""
        try:
            # Try to extract JSON array from the response
            start = response.find('[')
            end = response.rfind(']') + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                data = json.loads(json_str)
                return data
        except:
            pass
        
        # If no JSON found, create structured benefits from the text
        benefits = []
        
        # Split response into sections and parse each benefit
        sections = response.split('**Program:**')
        
        for section in sections[1:]:  # Skip first empty section
            lines = section.strip().split('\n')
            if not lines:
                continue
                
            # Extract program name
            program_name = lines[0].strip()
            
            # Parse the section for details
            category = "Government Scheme"
            eligibility = "Based on your profile"
            amount = "₹500-1000"
            application = "Visit government portal"
            timeline = "15-30 days"
            documents = "ID proof, income certificate"
            
            for line in lines:
                line = line.strip()
                if '**Category:**' in line:
                    category = line.replace('**Category:**', '').strip()
                elif '**Eligibility:**' in line:
                    eligibility = line.replace('**Eligibility:**', '').strip()
                elif '**Amount:**' in line:
                    amount = line.replace('**Amount:**', '').strip()
                elif '**Application:**' in line:
                    application = line.replace('**Application:**', '').strip()
                elif '**Timeline:**' in line:
                    timeline = line.replace('**Timeline:**', '').strip()
                elif '**Documents:**' in line:
                    documents = line.replace('**Documents:**', '').strip()
                elif line and not line.startswith('**'):
                    # This is additional description
                    pass
            
            # Clean up and create benefit object
            description = f"{program_name} - {category}. {eligibility}. {application}. Timeline: {timeline}. Required: {documents}."
            
            benefits.append({
                "name": program_name,
                "description": description,
                "eligibility_reason": eligibility,
                "link": "https://www.india.gov.in/topics/benefits",
                "amount": amount,
                "category": category,
                "estimatedTime": timeline
            })
        
        # If we couldn't parse any benefits, create fallback ones
        if not benefits:
            benefits = self._create_fallback_benefits(user_profile)
        
        return benefits
    
    def _create_fallback_benefits(self, user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create comprehensive fallback benefits recommendations"""
        income = user_profile.get('income', 0)
        age = user_profile.get('age', 30)
        dependents = user_profile.get('dependents', 0)
        city = user_profile.get('city', '')
        state = user_profile.get('state', '')
        
        benefits = []
        
        # Universal benefits
        benefits.append({
            "name": "Pradhan Mantri Jeevan Jyoti Bima Yojana (PMJJBY)",
            "description": "₹2 lakh life insurance coverage for just ₹330/year. Available to all savings account holders aged 18-50.",
            "eligibility_reason": "Age 18-50 with savings account",
            "link": "https://www.jansuraksha.gov.in",
            "amount": "₹2 lakh coverage",
            "category": "Life Insurance",
            "estimatedTime": "Instant"
        })
        
        benefits.append({
            "name": "Pradhan Mantri Suraksha Bima Yojana (PMSBY)",
            "description": "₹2 lakh accident insurance coverage for just ₹12/year. Available to all savings account holders aged 18-70.",
            "eligibility_reason": "Age 18-70 with savings account",
            "link": "https://www.jansuraksha.gov.in",
            "amount": "₹2 lakh coverage",
            "category": "Accident Insurance",
            "estimatedTime": "Instant"
        })
        
        # Income-based benefits
        if income < 1200000:
            benefits.append({
                "name": "PM-KISAN",
                "description": "₹6,000/year income support for eligible farmers. Helps with agricultural expenses and family support.",
                "eligibility_reason": "Income below ₹12 lakh, farmer",
                "link": "https://pmkisan.gov.in",
                "amount": "₹6,000/year",
                "category": "Agriculture",
                "estimatedTime": "15-30 days"
            })
        
        if income < 500000:
            benefits.append({
                "name": "Ayushman Bharat",
                "description": "₹5 lakh health insurance coverage for low-income families. Covers hospitalization and medical expenses.",
                "eligibility_reason": "Income below ₹5 lakh",
                "link": "https://pmjay.gov.in",
                "amount": "₹5 lakh/year",
                "category": "Health",
                "estimatedTime": "Instant"
            })
        
        # Age-based benefits
        if age >= 18 and age <= 40:
            benefits.append({
                "name": "Atal Pension Yojana (APY)",
                "description": "Guaranteed pension scheme for unorganized sector workers. Provides ₹1,000-5,000 monthly pension after 60.",
                "eligibility_reason": "Age 18-40, unorganized sector",
                "link": "https://npscra.nsdl.co.in",
                "amount": "₹1,000-5,000/month",
                "category": "Pension",
                "estimatedTime": "15-30 days"
            })
        
        if age >= 60:
            benefits.append({
                "name": "Senior Citizen Savings Scheme (SCSS)",
                "description": "High interest savings scheme for seniors with 8.2% interest rate. Maximum investment ₹30 lakh.",
                "eligibility_reason": "Age 60 or above",
                "link": "https://www.nsiindia.gov.in",
                "amount": "8.2% interest",
                "category": "Savings",
                "estimatedTime": "7-15 days"
            })
        
        # Location-based benefits
        if state and state.lower() in ['maharashtra', 'gujarat', 'karnataka', 'tamil nadu']:
            benefits.append({
                "name": f"{state} State Benefits",
                "description": f"Various state-specific schemes available in {state}. Visit state government portal for details.",
                "eligibility_reason": f"Resident of {state}",
                "link": f"https://{state.lower().replace(' ', '')}.gov.in",
                "amount": "Varies by scheme",
                "category": "State Schemes",
                "estimatedTime": "15-45 days"
            })
        
        return benefits
    
    def _generate_suggestions(self, user_message: str) -> List[str]:
        """Generate follow-up suggestions based on user message"""
        message_lower = user_message.lower()
        
        if 'investment' in message_lower:
            suggestions = [
                "What's the best investment strategy for my age?",
                "How much should I invest monthly?",
                "What are the risks of this investment?",
                "Show me low-risk investment options",
                "Which tax-saving investments are best for me?",
                "How do I diversify my portfolio?"
            ]
        elif 'saving' in message_lower or 'budget' in message_lower:
            suggestions = [
                "How much should I save each month?",
                "What's the best way to budget my income?",
                "How do I build an emergency fund?",
                "What are good savings goals?",
                "How can I automate my savings?",
                "What's the 50/30/20 rule?"
            ]
        elif 'tax' in message_lower:
            suggestions = [
                "What tax deductions can I claim?",
                "How can I reduce my tax bill?",
                "What are the best tax-saving investments?",
                "When should I file my taxes?",
                "How much can I save with 80C deductions?",
                "What's the difference between 80C and 80CCD?"
            ]
        elif 'debt' in message_lower or 'loan' in message_lower:
            suggestions = [
                "How do I pay off debt faster?",
                "What's the best debt payoff strategy?",
                "Should I consolidate my loans?",
                "How much debt is too much?",
                "What's the debt avalanche method?",
                "How do I prioritize debt payments?"
            ]
        elif 'retirement' in message_lower:
            suggestions = [
                "How much should I save for retirement?",
                "What's the best retirement account?",
                "When should I start retirement planning?",
                "How do I calculate retirement needs?",
                "What's the difference between EPF and NPS?",
                "How do I maximize retirement savings?"
            ]
        elif 'emergency' in message_lower or 'fund' in message_lower:
            suggestions = [
                "How much should I have in emergency fund?",
                "Where should I keep my emergency fund?",
                "How do I build an emergency fund quickly?",
                "What counts as an emergency expense?",
                "Should I invest my emergency fund?",
                "How often should I review my emergency fund?"
            ]
        elif 'insurance' in message_lower:
            suggestions = [
                "How much life insurance do I need?",
                "What's the best health insurance plan?",
                "Should I get term or whole life insurance?",
                "How do I choose the right insurance?",
                "What are government insurance schemes?",
                "How much should I pay for insurance?"
            ]
        else:
            suggestions = [
                "Tell me more about this",
                "How can I implement this?",
                "What are the risks?",
                "Show me alternatives",
                "Give me specific numbers",
                "What's the next step?"
            ]
        
        return suggestions
    
    def _get_fallback_chat_response(self, user_message: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Provide a fallback response when AI service fails"""
        income = user_profile.get('income', 0)
        age = user_profile.get('age', 30)
        monthly_savings = user_profile.get('monthly_savings', 0)
        
        # Analyze user message for common financial topics
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ['tax', 'taxes', 'itr', 'deduction']):
            response = f"""**Main Advice:**
Based on your ₹{income:,} annual income, you should focus on maximizing tax deductions through Section 80C investments and other eligible expenses to reduce your tax liability.

**Specific Numbers:**
Section 80C limit: ₹1.5 lakh (potential tax saving: ₹{income//100000*150000//100:,})
Health insurance (80D): ₹25,000 (potential tax saving: ₹{income//100000*25000//100:,})
Standard deduction: ₹50,000 (automatic)

**Action Steps:**
1. Invest in ELSS mutual funds or PPF to utilize 80C limit
2. Purchase health insurance for family members
3. Claim HRA if you're paying rent
4. Consider NPS for additional ₹50,000 deduction

**Timeline:**
Start tax planning immediately. Complete 80C investments by March 31st. File ITR by July 31st.

**Risks & Considerations:**
1. Don't invest just for tax savings - choose suitable products
2. Keep proper documentation for all deductions
3. Consider lock-in periods of tax-saving instruments"""

        elif any(word in message_lower for word in ['invest', 'investment', 'mutual fund', 'stock']):
            response = f"""**Main Advice:**
Given your ₹{income:,} income and ₹{monthly_savings:,} monthly savings, you should adopt a systematic investment approach focusing on long-term wealth creation through diversified investments.

**Specific Numbers:**
Monthly investment capacity: ₹{monthly_savings:,}
Recommended equity allocation: ₹{monthly_savings*70//100:,} (70% for growth)
Debt allocation: ₹{monthly_savings*30//100:,} (30% for stability)
Expected long-term returns: 12-15% annually

**Action Steps:**
1. Start SIP in diversified equity mutual funds
2. Allocate 20% to large-cap, 30% to mid-cap, 20% to small-cap
3. Consider index funds for lower costs
4. Maintain emergency fund before investing

**Timeline:**
Begin SIP immediately. Review portfolio quarterly. Rebalance annually based on market conditions.

**Risks & Considerations:**
1. Equity investments are subject to market volatility
2. Don't invest money needed within 3-5 years
3. Diversify across sectors and market caps"""

        elif any(word in message_lower for word in ['save', 'saving', 'emergency', 'fund']):
            response = f"""**Main Advice:**
Building a robust emergency fund should be your top priority. With ₹{income:,} annual income, you need 6-12 months of expenses saved for financial security.

**Specific Numbers:**
Target emergency fund: ₹{max(300000, income//12*6):,}
Current gap: ₹{max(0, max(300000, income//12*6) - user_profile.get('emergency_fund', 0)):,}
Monthly contribution needed: ₹{max(10000, monthly_savings//2):,}
Recommended savings rate: 20-30% of income

**Action Steps:**
1. Open high-yield savings account (4-6% interest)
2. Set up automatic monthly transfers
3. Cut non-essential expenses by 15-20%
4. Consider liquid mutual funds for better returns

**Timeline:**
Achieve 3-month target in 6 months, 6-month target in 12-18 months. Review monthly.

**Risks & Considerations:**
1. Don't invest emergency funds in volatile assets
2. Ensure 24-48 hour liquidity
3. Consider inflation impact on purchasing power"""

        else:
            response = f"""**Main Advice:**
Based on your ₹{income:,} income and financial profile, I recommend creating a comprehensive financial plan that balances short-term needs with long-term goals.

**Specific Numbers:**
Monthly savings potential: ₹{monthly_savings:,}
Emergency fund target: ₹{max(300000, income//12*6):,}
Investment allocation: ₹{monthly_savings*80//100:,} monthly
Insurance coverage needed: ₹{income*10:,} (10x annual income)

**Action Steps:**
1. Build emergency fund equivalent to 6 months of expenses
2. Start systematic investment plan (SIP) in mutual funds
3. Purchase adequate life and health insurance
4. Create a budget and track expenses regularly

**Timeline:**
Emergency fund: 6-12 months. Investment portfolio: Start immediately, review quarterly. Insurance: Purchase within 1 month.

**Risks & Considerations:**
1. Don't delay insurance - health issues can arise anytime
2. Maintain adequate emergency fund before aggressive investing
3. Consider inflation and tax implications in long-term planning"""

        return {
            "response": response,
            "suggestions": self._generate_suggestions(user_message),
            "confidence": 0.8,
            "structured_data": {
                "formatted_response": response,
                "sections": {},
                "original_response": response
            }
        }
    
    def _get_fallback_tax_recommendations(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback tax recommendations"""
        income = user_profile.get('income', 0)
        
        recommendations = []
        if income > 1000000:
            recommendations.append({
                "category": "High-Income Tax Strategies",
                "description": "Consider tax-loss harvesting, charitable giving, and retirement account maximization.",
                "estimated_savings": 50000,
                "priority": "High"
            })
        elif income > 500000:
            recommendations.append({
                "category": "Tax-Efficient Investing",
                "description": "Focus on tax-advantaged accounts and government securities.",
                "estimated_savings": 30000,
                "priority": "Medium"
            })
        else:
            recommendations.append({
                "category": "Standard Deductions",
                "description": "Maximize standard deductions and consider ELSS mutual funds.",
                "estimated_savings": 10000,
                "priority": "High"
            })
        
        return {
            "recommendations": recommendations,
            "total_estimated_savings": sum(r["estimated_savings"] for r in recommendations)
        }
    
    def _get_fallback_benefits(self, user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fallback benefits recommendations"""
        return [
            {
                "name": "General Government Benefits",
                "description": "Based on your profile, you may be eligible for various Indian government programs. Visit india.gov.in for a comprehensive assessment.",
                "eligibility_reason": "General eligibility based on income and location",
                "link": "https://www.india.gov.in/topics/benefits",
                "amount": "Varies",
                "category": "General",
                "estimatedTime": "15-30 days"
            }
        ]

    def _parse_chat_response(self, response: str) -> Dict[str, Any]:
        """Parse structured chat response with bold labels"""
        try:
            # Try to extract structured sections
            sections = {}
            
            # Look for main advice
            if '**Main Advice:**' in response:
                main_advice_start = response.find('**Main Advice:**') + len('**Main Advice:**')
                main_advice_end = response.find('**', main_advice_start)
                if main_advice_end == -1:
                    main_advice_end = len(response)
                main_advice = response[main_advice_start:main_advice_end].strip()
                if main_advice and not main_advice.startswith('*'):
                    sections['main_advice'] = main_advice
                else:
                    sections['main_advice'] = "Based on your financial profile, I recommend focusing on building a strong financial foundation through systematic savings and smart investments."
            
            # Look for specific numbers
            if '**Specific Numbers:**' in response:
                numbers_start = response.find('**Specific Numbers:**') + len('**Specific Numbers:**')
                numbers_end = response.find('**', numbers_start)
                if numbers_end == -1:
                    numbers_end = len(response)
                specific_numbers = response[numbers_start:numbers_end].strip()
                if specific_numbers and not specific_numbers.startswith('*'):
                    sections['specific_numbers'] = specific_numbers
                else:
                    sections['specific_numbers'] = "Consider setting aside 20-30% of your monthly income for savings and investments. Emergency fund target: 6 months of expenses."
            
            # Look for action steps
            if '**Action Steps:**' in response:
                steps_start = response.find('**Action Steps:**') + len('**Action Steps:**')
                steps_end = response.find('**', steps_start)
                if steps_end == -1:
                    steps_end = len(response)
                action_steps = response[steps_start:steps_end].strip()
                if action_steps and not action_steps.startswith('*'):
                    sections['action_steps'] = action_steps
                else:
                    sections['action_steps'] = "1. Review your current expenses and identify areas to cut back. 2. Set up automatic savings transfers. 3. Research investment options suitable for your risk profile. 4. Consult with a financial advisor for personalized guidance."
            
            # Look for timeline
            if '**Timeline:**' in response:
                timeline_start = response.find('**Timeline:**') + len('**Timeline:**')
                timeline_end = response.find('**', timeline_start)
                if timeline_end == -1:
                    timeline_end = len(response)
                timeline = response[timeline_start:timeline_end].strip()
                if timeline and not timeline.startswith('*'):
                    sections['timeline'] = timeline
                else:
                    sections['timeline'] = "Start implementing these steps immediately. Review progress monthly and adjust strategies quarterly. Set quarterly milestones to track your financial goals."
            
            # Look for risks
            if '**Risks & Considerations:**' in response:
                risks_start = response.find('**Risks & Considerations:**') + len('**Risks & Considerations:**')
                risks_end = response.find('**', risks_start)
                if risks_end == -1:
                    risks_end = len(response)
                risks = response[risks_start:risks_end].strip()
                if risks and not risks.startswith('*'):
                    sections['risks'] = risks
                else:
                    sections['risks'] = "1. Market volatility can affect investment returns. 2. Inflation may reduce purchasing power over time. 3. Ensure adequate insurance coverage for unexpected events."
            
            # Create formatted response with emojis and better structure
            if sections:
                formatted_parts = []
                if 'main_advice' in sections:
                    formatted_parts.append(f"**Main Advice:**\n{sections['main_advice']}")
                if 'specific_numbers' in sections:
                    formatted_parts.append(f"**Specific Numbers:**\n{sections['specific_numbers']}")
                if 'action_steps' in sections:
                    formatted_parts.append(f"**Action Steps:**\n{sections['action_steps']}")
                if 'timeline' in sections:
                    formatted_parts.append(f"**Timeline:**\n{sections['timeline']}")
                if 'risks' in sections:
                    formatted_parts.append(f"**Risks & Considerations:**\n{sections['risks']}")
                
                formatted_response = "\n\n".join(formatted_parts)
            else:
                # If no structured sections found, format the original response
                formatted_response = response.replace('**', '**').replace('\n\n', '\n')
            
            return {
                "formatted_response": formatted_response,
                "sections": sections,
                "original_response": response
            }
            
        except Exception as e:
            logger.error(f"Error parsing chat response: {e}")
            return {
                "formatted_response": response,
                "sections": {},
                "original_response": response
            }

# Global instance
ai_service = GeminiAIService() 