import streamlit as st
import pickle
from pymongo import MongoClient
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import plotly.express as px
import pandas as pd


#  DATABASE 

client = MongoClient("mongodb://localhost:27017/")
db = client["employee_db"]

employees_collection = db["employees"]
users_collection = db["users"]
feedback_collection = db["feedback"]
#  MODEL

with open("model_metadata.pkl", "rb") as f:
    metadata = pickle.load(f)

model = metadata["model"]
feature_names = metadata["feature_names"]
#st.write(feature_names)
analyzer = SentimentIntensityAnalyzer()
def generate_suggestions(prediction, inputs):

    suggestions = []
    reasons = []

    work_life_balance = inputs["WorkLifeBalance"]
    years_since_promotion = inputs["YearsSinceLastPromotion"]
    distance = inputs["DistanceFromHome"]
    years_company = inputs["YearsAtCompany"]
    age = inputs["Age"]

    if prediction == 1:

        suggestions.append("🚨 High Attrition Risk Detected")

        if work_life_balance <= 2:
            reasons.append(
                "Poor work-life balance may cause burnout."
            )

            suggestions.append(
                "⚖️ Introduce flexible work schedules."
            )

            suggestions.append(
                "🧘 Provide wellness programs."
            )

        if years_since_promotion >= 3:

            reasons.append(
                "Employee has not received promotion recently."
            )

            suggestions.append(
                "📈 Consider promotion opportunities."
            )

            suggestions.append(
                "🎯 Create a career growth plan."
            )

        if distance >= 20:

            reasons.append(
                "Long commuting distance may reduce satisfaction."
            )

            suggestions.append(
                "🏠 Offer hybrid or remote work."
            )

            suggestions.append(
                "🚌 Provide transport support."
            )

        if years_company >= 10:

            reasons.append(
                "Long-tenure employees may seek new challenges."
            )

            suggestions.append(
                "🔄 Offer role rotation opportunities."
            )

        if age < 30:

            reasons.append(
                "Young employees often explore better opportunities."
            )

            suggestions.append(
                "💰 Offer performance incentives."
            )

            suggestions.append(
                "📚 Provide upskilling programs."
            )

    else:

        reasons.append(
            "Employee profile indicates low attrition risk."
        )

        suggestions.append(
            "✅ Employee appears engaged and stable."
        )

        suggestions.append(
            "📚 Continue learning opportunities."
        )

        suggestions.append(
            "🏆 Recognize achievements regularly."
        )

    return reasons, suggestions
#  PAGE 

st.set_page_config(
    page_title="AI HR Analytics Platform",
    layout="wide"
)
st.markdown("""
<style>

/* Main Background */
.stApp {
    background-color: #f5f7fa;
}

/* Title */
h1 {
    color: #1f4e79;
    text-align: center;
    font-weight: bold;
}

/* Headers */
h2, h3 {
    color: #2c3e50;
}

/* Buttons */
.stButton > button {
    background-color: #1f77b4;
    color: white;
    border-radius: 10px;
    border: none;
    padding: 10px 20px;
    font-weight: bold;
}

.stButton > button:hover {
    background-color: #0d5ea6;
}

/* Input Boxes */
.stTextInput input,
.stNumberInput input {
    border-radius: 8px;
}

/* Metrics */
[data-testid="metric-container"] {
    background-color: white;
    border-radius: 15px;
    padding: 15px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #1f2937;
}

section[data-testid="stSidebar"] * {
    color: white;
    font-size: 22px !important;
    font-weight: 600;
}
/* Make all field labels bigger */
.stTextInput label,
.stNumberInput label,
.stSelectbox label,
.stTextArea label,
.stSlider label {
    font-size: 22px !important;
    font-weight: bold !important;
}

/* Force all labels */
label p {
    font-size: 24px !important;
    font-weight: bold !important;
}

</style>
""", unsafe_allow_html=True)

# SESSION 

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "company" not in st.session_state:
    st.session_state.company = ""

# TITLE

st.title("🤖 AI HR Analytics Platform")

# LOGIN / SIGNUP

if not st.session_state.logged_in:

    st.subheader("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        user = users_collection.find_one({
            "username": username,
            "password": password
        })

        if user:

            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.company = user.get(
                "company_name",
                ""
            )

            st.rerun()

        else:
            st.error("Invalid Credentials")

    st.subheader("📝 Sign Up")

    new_user = st.text_input("New Username")
    new_pass = st.text_input(
        "New Password",
        type="password"
    )

    company_name = st.text_input(
        "Company Name"
    )

    if st.button("Register"):

        existing = users_collection.find_one({
            "username": new_user
        })

        if existing:

            st.warning(
                "Username already exists"
            )

        else:

            users_collection.insert_one({
                "username": new_user,
                "password": new_pass,
                "company_name": company_name
            })

            st.success(
                "Account Created Successfully"
            )

    st.stop()

# USER INFO

st.write(
    f"👤 Logged in as: {st.session_state.username}"
)

st.write(
    f"🏢 Company: {st.session_state.company}"
)

if st.button("🚪 Logout"):

    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.company = ""

    st.rerun()


# SIDEBAR

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Attrition Prediction",
        "Layoff Risk",
        "Work-Life Balance",
        "Sentiment Analysis",
        "Employee Records",
        "Chatbot"
    ]
)

# DASHBOARD

if page == "Dashboard":

    st.markdown("""
    <div style="
    padding:25px;
    border-radius:15px;
    background:linear-gradient(90deg,#1f77b4,#4facfe);
    color:white;
    text-align:center;
    margin-bottom:20px;
    ">

    <h1 style="color:white;">
    🤖 AI HR Analytics Platform
    </h1>

    <h4 style="color:white;">
    Predict • Analyze • Retain Talent
    </h4>

    </div>
    """, unsafe_allow_html=True)

    total_employees = employees_collection.count_documents({
        "hr_user": st.session_state.username
    })

    at_risk = employees_collection.count_documents({
        "hr_user": st.session_state.username,
        "Prediction": "Employee Might Leave The Job"
    })

    safe = employees_collection.count_documents({
        "hr_user": st.session_state.username,
        "Prediction": "Employee Might Not Leave The Job"
    })

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "👥 Total Employees",
            total_employees
        )

    with col2:
        st.metric(
            "⚠️ At Risk",
            at_risk
        )

    with col3:
        st.metric(
            "✅ Safe",
            safe
        )

    with col4:
        retention_rate = 0
        if total_employees > 0:
            retention_rate = (
                safe / total_employees
            ) * 100

        st.metric(
            "📈 Retention Rate",
            f"{retention_rate:.1f}%"
        )
    chart_data = pd.DataFrame({
        "Category": ["At Risk", "Safe"],
        "Count": [at_risk, safe]
    })

    fig = px.pie(
        chart_data,
        names="Category",
        values="Count",
        title="Employee Attrition Distribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ATTRITION PREDICTION

elif page == "Attrition Prediction":

    st.header(
        "🤖 Employee Attrition Prediction"
    )

    employee_id = st.text_input(
        "Employee ID"
    )

    name = st.text_input(
        "Employee Name"
    )

    age = st.number_input(
        "Age",
        18,
        65,
        30
    )

    business_travel = st.selectbox(
        "Business Travel",
        [
            "Travel_Rarely",
            "Travel_Frequently",
            "Non-Travel"
        ]
    )

    daily_rate = st.number_input(
        "Daily Rate",
        value=800
    )

    distance = st.number_input(
        "Distance From Home",
        value=10
    )

    education_map = {
    "Below College": 1,
    "College Diploma": 2,
    "Bachelor Degree (BE/BTech/BSc)": 3,
    "Master Degree (ME/MTech/MSc/MBA)": 4
}

    education_label = st.selectbox(
    "Education",
    list(education_map.keys())
)

    education = education_map[education_label]

    department = st.selectbox(
        "Department",
        [
            "Sales",
            "HR",
            "Research & Development"
        ]
    )

    years_company = st.number_input(
        "Years At Company",
        value=5
    )

    wlb_options = {
            "Poor (1)": 1,
            "Average (2)": 2,
            "Good (3)": 3,
            "Excellent (4)": 4
            }

    wlb_label = st.selectbox(
                "Work Life Balance",
                list(wlb_options.keys())
            )

    wlb = wlb_options[wlb_label]

    years_promo = st.number_input(
        "Years Since Last Promotion",
        value=1
    )

    if st.button("Predict Attrition"):

        inputs = {
            "Age": age,
            "BusinessTravel": business_travel,
            "DailyRate": daily_rate,
            "DistanceFromHome": distance,
            "Education": education,
            "Department": department,
            "YearsAtCompany": years_company,
            "WorkLifeBalance": wlb,
            "YearsSinceLastPromotion": years_promo
        }

        df = pd.DataFrame([inputs])

        df = pd.get_dummies(
            df,
            columns=[
                "BusinessTravel",
                "Department"
            ],
            drop_first=True
        )

        for col in feature_names:
            if col not in df.columns:
                df[col] = 0

        df = df[feature_names]

        prediction = model.predict(df)
        probability = model.predict_proba(df)[0][1]

        result = (
            "Employee Might Leave The Job"
            if prediction[0] == 1
            else "Employee Might Not Leave The Job"
        )

        employees_collection.insert_one({
            "hr_user": st.session_state.username,
            "company": st.session_state.company,
            "EmployeeID": employee_id,
            "Name": name,
            "Age": age,
            "Department": department,
            "Prediction": result
        })

        st.metric(
            "Attrition Risk",
            f"{probability*100:.1f}%"
        )
        if prediction[0] == 1:
            st.error(
                "🚨 Employee Might Leave The Job"
                )
        else:
            st.success(
                "✅ Employee Might Not Leave The Job"
                )
        reasons, suggestions = generate_suggestions(
            prediction[0],
            inputs
        )

        st.subheader(
            "🔍 Prediction Reasoning"
        )

        for reason in reasons:
            st.write(
                "•", reason
            )

        st.subheader(
            "💡 Recommendations"
        )

        for suggestion in suggestions:
            st.write(
                "•", suggestion
            )

# EMPLOYEE RECORDS

elif page == "Employee Records":

    st.header("📋 Employee Records")

    records = list(
        employees_collection.find(
            {
                "hr_user": st.session_state.username
            }
        )
    )

    if len(records) == 0:

        st.warning(
            "No employee records found"
        )

    else:

        df_records = pd.DataFrame(
            records
        )

        if "_id" in df_records.columns:
            df_records.drop(
                columns=["_id"],
                inplace=True
            )

        st.dataframe(
            df_records,
            use_container_width=True
        )

# PLACEHOLDERS

elif page == "Layoff Risk":

    st.header("📉 Layoff Risk Prediction")

    employee_name = st.text_input(
        "Employee Name",
        key="layoff_name"
    )

    performance = st.slider(
        "Performance Rating",
        1, 5, 3
    )

    skill_level = st.slider(
        "Skill Level",
        1, 5, 3
    )

    experience = st.number_input(
        "Years of Experience",
        min_value=0,
        value=3
    )

    salary = st.number_input(
        "Monthly Salary",
        min_value=5000,
        value=25000
    )

    department = st.selectbox(
        "Department",
        ["Sales", "HR", "Research & Development"],
        key="layoff_dept"
    )

    productivity = st.slider(
        "Productivity Score",
        1, 100, 70
    )

    if st.button("Calculate Layoff Risk"):

        risk_score = 0

        # Performance
        if performance <= 2:
            risk_score += 30
        elif performance == 3:
            risk_score += 15

        # Skill
        if skill_level <= 2:
            risk_score += 25
        elif skill_level == 3:
            risk_score += 10

        # Productivity
        if productivity < 50:
            risk_score += 25
        elif productivity < 70:
            risk_score += 10

        # Experience
        if experience < 2:
            risk_score += 15

        # Salary
        if salary > 80000:
            risk_score += 10

        risk_score = min(risk_score, 100)

        st.metric(
            "Layoff Risk Score",
            f"{risk_score}%"
        )

        if risk_score >= 70:
            st.error("🔴 High Layoff Risk")

        elif risk_score >= 40:
            st.warning("🟡 Medium Layoff Risk")

        else:
            st.success("🟢 Low Layoff Risk")

        st.subheader("💡 Recommendations")

        if risk_score >= 70:
            st.write("• Improve performance metrics")
            st.write("• Upskill through training programs")
            st.write("• Increase productivity levels")

        elif risk_score >= 40:
            st.write("• Continue skill development")
            st.write("• Improve performance consistency")

        else:
            st.write("• Employee appears stable")
            st.write("• Continue growth opportunities")
elif page == "Work-Life Balance":

    st.header("⚖️ Work-Life Balance Calculator")

    work_hours = st.slider(
        "Working Hours Per Day",
        4, 16, 8
    )

    overtime = st.slider(
        "Overtime Hours Per Week",
        0, 30, 5
    )

    stress_level = st.slider(
        "Stress Level",
        1, 10, 5
    )

    vacation_days = st.number_input(
        "Vacation Days Taken This Year",
        min_value=0,
        max_value=50,
        value=10
    )
    job_satisfaction = st.slider(
    "Job Satisfaction",
    1, 5, 3
)

    manager_support = st.selectbox(
    "Manager Support",
    [
        "Poor",
        "Average",
        "Good",
        "Excellent"
    ]
)

    sleep_hours = st.slider(
    "Sleep Hours Per Night",
    3, 12, 7
)

    weekend_work = st.selectbox(
    "Weekend Work Frequency",
    [
        "Never",
        "Sometimes",
        "Often",
        "Always"
    ]
)

    if st.button("Calculate Work-Life Balance"):

        score = 100

        # Working Hours
        if work_hours > 8:
            score -= (work_hours - 8) * 8

        # Overtime
        score -= overtime * 1.5

        # Stress
        score -= stress_level * 4

        # Vacation
        score += vacation_days * 0.5

        # Job Satisfaction
        score += job_satisfaction * 4

        # Manager Support
        if manager_support == "Good":
            score += 8
        elif manager_support == "Excellent":
            score += 15
        elif manager_support == "Poor":
            score -= 10

        # Sleep
        if sleep_hours >= 7:
            score += 10
        elif sleep_hours <= 5:
            score -= 10

        # Weekend Work
        if weekend_work == "Sometimes":
            score -= 5
        elif weekend_work == "Often":
            score -= 15
        elif weekend_work == "Always":
            score -= 25

        score = max(0, min(score, 100))

        st.metric(
            "Work-Life Balance Score",
            f"{score:.0f}%"
        )

        if score >= 80:

            st.success(
                "🟢 Excellent Work-Life Balance"
            )

        elif score >= 60:

            st.warning(
                "🟡 Moderate Work-Life Balance"
            )

        else:

            st.error(
                "🔴 Poor Work-Life Balance"
            )
  

elif page == "Sentiment Analysis":

    st.header("😊 Employee Sentiment Analysis")

    employee_name = st.text_input(
        "Employee Name"
    )

    feedback = st.text_area(
        "Enter Employee Feedback"
    )

    if st.button("Analyze Sentiment"):

        score = analyzer.polarity_scores(
            feedback
        )

        compound = score["compound"]

        satisfaction_score = (
            (compound + 1) / 2
        ) * 100

        st.metric(
            "Employee Satisfaction Score",
            f"{satisfaction_score:.1f}%"
        )

        st.progress(
            satisfaction_score / 100
        )

        if compound >= 0.05:

            sentiment = "Positive"

            st.success(
                "😀 Positive Sentiment"
            )

        elif compound <= -0.05:

            sentiment = "Negative"

            st.error(
                "😞 Negative Sentiment"
            )

        else:

            sentiment = "Neutral"

            st.warning(
                "😐 Neutral Sentiment"
            )

        feedback_collection.insert_one({

            "hr_user":
                st.session_state.username,

            "company":
                st.session_state.company,

            "employee_name":
                employee_name,

            "feedback":
                feedback,

            "sentiment":
                sentiment,

            "sentiment_score":
                compound
        })

        st.subheader(
            "💡 HR Recommendations"
        )

        if sentiment == "Positive":

            st.write(
                "• Employee appears satisfied."
            )

            st.write(
                "• Continue recognition programs."
            )

            st.write(
                "• Maintain engagement levels."
            )

        elif sentiment == "Negative":

            st.write(
                "• Schedule one-on-one discussion."
            )

            st.write(
                "• Investigate workplace concerns."
            )

            st.write(
                "• Consider workload reduction."
            )

            st.write(
                "• Monitor employee wellbeing."
            )

        else:

            st.write(
                "• Gather more employee feedback."
            )

            st.write(
                "• Monitor engagement trends."
            )
elif page == "Chatbot":

    st.header("🤖 AI HR Assistant")

    user_question = st.text_input(
        "Ask HR Assistant"
    )

    if st.button("Ask"):

        question = user_question.lower()
        knowledge_base = {

    "hr analytics": """
    HR Analytics is the process of collecting and analyzing employee data to improve workforce decisions.
    """,

    "attrition": """
    Attrition refers to employees leaving an organization.
    """,

    "machine learning": """
    Machine Learning enables computers to learn from data and make predictions.
    """,

    "attrition prediction": """
    Attrition Prediction uses Machine Learning to identify employees who may leave the organization in the future.
    It helps HR teams take preventive actions and improve employee retention.
    """,

    "xgboost": """
    XGBoost (Extreme Gradient Boosting) is a Machine Learning algorithm used for classification and prediction tasks.
    In this project, XGBoost is used to predict employee attrition risk.
    """,

"sentiment analysis": """
Sentiment Analysis determines whether employee feedback is Positive, Negative, or Neutral.

It helps HR teams understand employee satisfaction and workplace morale.
""",

"work life balance": """
Work-Life Balance measures how effectively employees manage their professional and personal lives.

A healthy balance can reduce stress, improve productivity, and lower attrition.
""",

"layoff risk": """
Layoff Risk Prediction estimates the likelihood of employees being affected during workforce reductions.

Factors such as performance, skill level, productivity, and experience are considered.
""",

"employee retention": """
Employee Retention refers to an organization's ability to keep employees engaged and reduce employee turnover.

Higher retention leads to better productivity and lower recruitment costs.
""",

"features": """
This AI HR Analytics Platform provides:

• Employee Attrition Prediction
• AI Recommendations
• Prediction Reasoning
• Layoff Risk Prediction
• Work-Life Balance Calculator
• Employee Sentiment Analysis
• HR Analytics Dashboard
• Employee Records Management
• AI HR Assistant Chatbot
• MongoDB Data Storage
"""
    
    }

        response = None

        for key, value in knowledge_base.items():

            if key in question:

                response = value
                break
        if response is None:

            response = """
Sorry, I don't know that yet.

You can ask me about:

• HR Analytics
• Attrition
• Machine Learning
"""
        st.info(response)