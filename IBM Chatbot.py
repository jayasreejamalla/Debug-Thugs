import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import random
from typing import Dict, List, Tuple
import re

# Configure Streamlit page
st.set_page_config(
    page_title="Personal Finance Assistant",
    page_icon="💰",
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
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .bot-message {
        background-color: #f5f5f5;
        border-left: 4px solid #4caf50;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .insight-card {
        background: #fff3e0;
        border: 1px solid #ffb74d;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

class PersonalFinanceChatbot:
    def __init__(self):
        self.user_profiles = {
            "student": {
                "tone": "casual and encouraging",
                "complexity": "simple",
                "focus": ["budgeting", "savings", "student_loans", "part_time_income"]
            },
            "professional": {
                "tone": "formal and analytical",
                "complexity": "detailed",
                "focus": ["investments", "retirement", "tax_optimization", "career_growth"]
            },
            "young_adult": {
                "tone": "friendly and motivational",
                "complexity": "moderate",
                "focus": ["emergency_fund", "debt_management", "first_home", "career_building"]
            }
        }
        
        self.financial_tips = {
            "budgeting": [
                "Follow the 50/30/20 rule: 50% needs, 30% wants, 20% savings",
                "Track every expense for at least a month to understand spending patterns",
                "Use budgeting apps or spreadsheets to monitor your finances",
                "Review and adjust your budget monthly"
            ],
            "savings": [
                "Pay yourself first - save before spending",
                "Automate your savings to make it effortless",
                "Build an emergency fund of 3-6 months of expenses",
                "Take advantage of high-yield savings accounts"
            ],
            "investments": [
                "Start investing early to benefit from compound interest",
                "Diversify your portfolio across different asset classes",
                "Consider low-cost index funds for beginners",
                "Don't try to time the market - invest consistently"
            ],
            "debt": [
                "Pay more than the minimum on high-interest debt",
                "Consider the debt avalanche or snowball method",
                "Avoid taking on new debt while paying off existing debt",
                "Look into debt consolidation if it lowers your interest rate"
            ]
        }

    def get_user_profile_advice(self, user_type: str, topic: str) -> str:
        profile = self.user_profiles.get(user_type, self.user_profiles["young_adult"])
        
        if user_type == "student":
            if topic.lower() in ["budget", "budgeting"]:
                return "Hey! As a student, budgeting is super important. Start simple: track your income (from jobs, parents, financial aid) and your expenses. Try the envelope method - allocate money for essentials like food, textbooks, and rent first, then see what's left for fun stuff!"
            elif topic.lower() in ["save", "saving", "savings"]:
                return "Even saving small amounts as a student makes a huge difference! Try to save 10% of any income you get. Look for student discounts everywhere, buy used textbooks, and consider cooking instead of eating out. Every dollar counts!"
        
        elif user_type == "professional":
            if topic.lower() in ["investment", "investing"]:
                return "As a professional, you should consider diversifying your investment portfolio. Focus on tax-advantaged accounts like 401(k) and IRA first. Consider low-cost index funds, and if your employer offers 401(k) matching, contribute at least enough to get the full match - it's free money."
            elif topic.lower() in ["retirement"]:
                return "Retirement planning should be a priority. Aim to save 10-15% of your income for retirement. Max out your 401(k) contributions if possible, especially if you're in a high tax bracket. Consider Roth IRA for tax diversification in retirement."
        
        return f"Based on your profile, here's some tailored advice about {topic}..."

    def analyze_spending_data(self, transactions: List[Dict]) -> Dict:
        if not transactions:
            return {"error": "No transaction data provided"}
        
        df = pd.DataFrame(transactions)
        
        # Calculate totals by category
        category_totals = df.groupby('category')['amount'].sum().to_dict()
        total_spent = df['amount'].sum()
        
        # Calculate insights
        largest_category = max(category_totals, key=category_totals.get)
        largest_amount = category_totals[largest_category]
        
        insights = {
            "total_spent": total_spent,
            "category_breakdown": category_totals,
            "largest_category": largest_category,
            "largest_amount": largest_amount,
            "transaction_count": len(transactions),
            "average_transaction": total_spent / len(transactions) if transactions else 0
        }
        
        return insights

    def generate_budget_summary(self, income: float, expenses: Dict) -> str:
        total_expenses = sum(expenses.values())
        remaining = income - total_expenses
        savings_rate = (remaining / income * 100) if income > 0 else 0
        
        summary = f"""
        💰 **Monthly Budget Summary**
        
        **Income:** ${income:,.2f}
        **Total Expenses:** ${total_expenses:,.2f}
        **Remaining:** ${remaining:,.2f}
        **Savings Rate:** {savings_rate:.1f}%
        
        **Expense Breakdown:**
        """
        
        for category, amount in expenses.items():
            percentage = (amount / total_expenses * 100) if total_expenses > 0 else 0
            summary += f"\n- {category}: ${amount:,.2f} ({percentage:.1f}%)"
        
        # Add recommendations
        if savings_rate < 20:
            summary += f"\n\n⚠️ **Recommendation:** Try to increase your savings rate to at least 20%. Consider reducing expenses in your largest categories."
        else:
            summary += f"\n\n✅ **Great job!** You're saving {savings_rate:.1f}% of your income. Keep up the good work!"
        
        return summary

    def get_financial_advice(self, query: str, user_type: str) -> str:
        query_lower = query.lower()
        
        # Simple keyword matching for demo purposes
        if any(word in query_lower for word in ["budget", "budgeting"]):
            return self.get_user_profile_advice(user_type, "budget")
        elif any(word in query_lower for word in ["save", "saving", "savings"]):
            return self.get_user_profile_advice(user_type, "savings")
        elif any(word in query_lower for word in ["invest", "investment", "investing"]):
            return self.get_user_profile_advice(user_type, "investment")
        elif any(word in query_lower for word in ["debt", "loan", "credit"]):
            return "Managing debt is crucial for financial health. Focus on paying off high-interest debt first, make more than minimum payments when possible, and avoid taking on new debt. Consider debt consolidation if it reduces your interest rate."
        elif any(word in query_lower for word in ["retirement"]):
            return self.get_user_profile_advice(user_type, "retirement")
        elif any(word in query_lower for word in ["emergency", "emergency fund"]):
            return "An emergency fund is essential! Aim to save 3-6 months of living expenses in a high-yield savings account. Start small - even $500 can help with minor emergencies. Automate transfers to build this fund gradually."
        else:
            return f"I understand you're asking about: '{query}'. While I'd love to provide more specific advice, here are some general financial principles that apply to most situations: spend less than you earn, save consistently, invest for the long term, and always have an emergency fund. Could you be more specific about what financial topic you'd like help with?"

def main():
    st.markdown('<h1 class="main-header">💰 Personal Finance Assistant</h1>', unsafe_allow_html=True)
    
    # Initialize chatbot
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = PersonalFinanceChatbot()
    
    # Initialize chat history
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Initialize user data
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {
            'profile_type': 'young_adult',
            'income': 0,
            'expenses': {},
            'transactions': []
        }
    
    # Sidebar for user profile and data input
    with st.sidebar:
        st.header("👤 User Profile")
        
        # User type selection
        user_type = st.selectbox(
            "Select your profile:",
            ["student", "young_adult", "professional"],
            index=["student", "young_adult", "professional"].index(st.session_state.user_data['profile_type'])
        )
        st.session_state.user_data['profile_type'] = user_type
        
        st.header("💵 Financial Information")
        
        # Income input
        monthly_income = st.number_input(
            "Monthly Income ($):",
            min_value=0.0,
            value=float(st.session_state.user_data['income']),
            step=100.0
        )
        st.session_state.user_data['income'] = monthly_income
        
        # Expense categories
        st.subheader("Monthly Expenses")
        expense_categories = ["Housing", "Food", "Transportation", "Entertainment", "Healthcare", "Other"]
        
        expenses = {}
        for category in expense_categories:
            amount = st.number_input(
                f"{category} ($):",
                min_value=0.0,
                value=float(st.session_state.user_data['expenses'].get(category, 0)),
                step=50.0,
                key=f"expense_{category}"
            )
            if amount > 0:
                expenses[category] = amount
        
        st.session_state.user_data['expenses'] = expenses
        
        # Quick transaction input
        st.subheader("Add Quick Transaction")
        with st.form("transaction_form"):
            trans_amount = st.number_input("Amount ($):", min_value=0.0, step=1.0)
            trans_category = st.selectbox("Category:", expense_categories)
            trans_description = st.text_input("Description (optional):")
            
            if st.form_submit_button("Add Transaction"):
                transaction = {
                    'amount': trans_amount,
                    'category': trans_category,
                    'description': trans_description,
                    'date': datetime.now().strftime('%Y-%m-%d')
                }
                st.session_state.user_data['transactions'].append(transaction)
                st.success("Transaction added!")
    
    # Main content area with tabs
    tab1, tab2, tab3 = st.tabs(["💬 Chat Assistant", "📊 Budget Overview", "📈 Spending Analysis"])
    
    with tab1:
        st.header("Chat with your Financial Assistant")
        
        # Display chat messages
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f'<div class="chat-message user-message">**You:** {message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message bot-message">**Assistant:** {message["content"]}</div>', unsafe_allow_html=True)
        
        # Chat input
        user_input = st.chat_input("Ask me anything about personal finance...")
        
        if user_input:
            # Add user message
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Generate response
            response = st.session_state.chatbot.get_financial_advice(
                user_input, 
                st.session_state.user_data['profile_type']
            )
            
            # Add assistant response
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Rerun to display new messages
            st.rerun()
        
        # Quick action buttons
        st.subheader("Quick Questions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💡 Budgeting Tips"):
                tips = "\n".join([f"• {tip}" for tip in st.session_state.chatbot.financial_tips["budgeting"]])
                st.session_state.messages.append({"role": "user", "content": "Give me budgeting tips"})
                st.session_state.messages.append({"role": "assistant", "content": f"Here are some budgeting tips:\n\n{tips}"})
                st.rerun()
        
        with col2:
            if st.button("💰 Saving Strategies"):
                tips = "\n".join([f"• {tip}" for tip in st.session_state.chatbot.financial_tips["savings"]])
                st.session_state.messages.append({"role": "user", "content": "How can I save more money?"})
                st.session_state.messages.append({"role": "assistant", "content": f"Here are some saving strategies:\n\n{tips}"})
                st.rerun()
        
        with col3:
            if st.button("📈 Investment Advice"):
                tips = "\n".join([f"• {tip}" for tip in st.session_state.chatbot.financial_tips["investments"]])
                st.session_state.messages.append({"role": "user", "content": "Tell me about investing"})
                st.session_state.messages.append({"role": "assistant", "content": f"Here's some investment advice:\n\n{tips}"})
                st.rerun()
    
    with tab2:
        st.header("📊 Budget Overview")
        
        if monthly_income > 0 or expenses:
            # Generate budget summary
            budget_summary = st.session_state.chatbot.generate_budget_summary(monthly_income, expenses)
            st.markdown(budget_summary)
            
            # Create visualizations
            if expenses:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Expense breakdown pie chart
                    fig_pie = px.pie(
                        values=list(expenses.values()),
                        names=list(expenses.keys()),
                        title="Expense Breakdown"
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                with col2:
                    # Income vs Expenses bar chart
                    total_expenses = sum(expenses.values())
                    remaining = monthly_income - total_expenses
                    
                    fig_bar = go.Figure(data=[
                        go.Bar(name='Income', x=['Monthly'], y=[monthly_income], marker_color='green'),
                        go.Bar(name='Expenses', x=['Monthly'], y=[total_expenses], marker_color='red'),
                        go.Bar(name='Remaining', x=['Monthly'], y=[remaining], marker_color='blue')
                    ])
                    fig_bar.update_layout(title='Income vs Expenses', barmode='group')
                    st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Please enter your income and expenses in the sidebar to see your budget overview.")
    
    with tab3:
        st.header("📈 Spending Analysis")
        
        if st.session_state.user_data['transactions']:
            # Analyze spending data
            insights = st.session_state.chatbot.analyze_spending_data(st.session_state.user_data['transactions'])
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f'''
                <div class="metric-card">
                    <h3>${insights["total_spent"]:.2f}</h3>
                    <p>Total Spent</p>
                </div>
                ''', unsafe_allow_html=True)
            
            with col2:
                st.markdown(f'''
                <div class="metric-card">
                    <h3>{insights["transaction_count"]}</h3>
                    <p>Transactions</p>
                </div>
                ''', unsafe_allow_html=True)
            
            with col3:
                st.markdown(f'''
                <div class="metric-card">
                    <h3>${insights["average_transaction"]:.2f}</h3>
                    <p>Avg Transaction</p>
                </div>
                ''', unsafe_allow_html=True)
            
            with col4:
                st.markdown(f'''
                <div class="metric-card">
                    <h3>{insights["largest_category"]}</h3>
                    <p>Top Category</p>
                </div>
                ''', unsafe_allow_html=True)
            
            # Transaction history
            st.subheader("Recent Transactions")
            df_transactions = pd.DataFrame(st.session_state.user_data['transactions'])
            st.dataframe(df_transactions, use_container_width=True)
            
            # Spending by category
            if len(st.session_state.user_data['transactions']) > 0:
                category_chart = px.bar(
                    x=list(insights["category_breakdown"].keys()),
                    y=list(insights["category_breakdown"].values()),
                    title="Spending by Category"
                )
                st.plotly_chart(category_chart, use_container_width=True)
        else:
            st.info("No transactions recorded yet. Add some transactions in the sidebar to see your spending analysis.")
    
    # Footer
    st.markdown("---")
    st.markdown("*This is a demo Personal Finance Chatbot. For real financial advice, please consult with a qualified financial advisor.*")

if __name__ == "__main__":
    main()
