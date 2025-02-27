from flask import Flask, request, render_template, jsonify
import pandas as pd

# Initialize Flask app
app = Flask(__name__)

# Load financial data
try:
    financial_data = pd.read_csv(r"C:/Users/Admin/Downloads/financial_data.csv")
except Exception as e:
    financial_data = pd.DataFrame()
    print(f"Error loading data: {e}")

# Predefined valid queries
valid_queries = [
    "What is the total revenue?",
    "How has net income changed over the last year?",
    "What is the total assets growth over the last year?"
]


# Helper function to calculate growth safely
def calculate_growth(current, previous):
    if previous == 0 or pd.isna(previous):
        return None
    return ((current - previous) / previous) * 100


# Function to process user query
def handle_query(company, query):
    if financial_data.empty:
        return "Financial data is unavailable or could not be loaded."

    # Filter financial data by company
    company_data = financial_data[financial_data["Company Name"] == company]

    if company_data.empty:
        return f"No data found for {company}."

    if query == "What is the total revenue?":
        # Fetch the latest revenue
        latest_data = company_data.iloc[-1]
        return f"The total revenue for {company} in {latest_data['Fiscal Year']} was ${latest_data['Total Revenue']:,}."

    elif query == "How has net income changed over the last year?":
        # Sort data by Fiscal Year
        company_data = company_data.sort_values("Fiscal Year")
        latest_year = company_data.iloc[-1]
        previous_year = company_data.iloc[-2]
        # Calculate the change percentage
        growth = calculate_growth(latest_year["Net Income"], previous_year["Net Income"])
        if growth is not None:
            return f"Net income for {company} changed by {growth:.2f}% from {previous_year['Fiscal Year']} to {latest_year['Fiscal Year']}."
        return "Insufficient data for net income comparison."

    elif query == "What is the total assets growth over the last year?":
        # Sort data by Fiscal Year
        company_data = company_data.sort_values("Fiscal Year")
        latest_year = company_data.iloc[-1]
        previous_year = company_data.iloc[-2]
        # Calculate the change percentage
        growth = calculate_growth(latest_year["Total Assets"], previous_year["Total Assets"])
        if growth is not None:
            return f"Total assets for {company} grew by {growth:.2f}% from {previous_year['Fiscal Year']} to {latest_year['Fiscal Year']}."
        return "Insufficient data for total assets comparison."

    # Handle unknown or custom queries
    return "Sorry, I can only provide information on predefined queries."


# Homepage route
@app.route("/")
def home():
    # Extract unique companies to dynamically populate dropdown
    companies = financial_data["Company Name"].unique().tolist()
    return render_template("chatbot.html", companies=companies, queries=valid_queries)


# Route to handle query submission from the frontend
@app.route("/query", methods=["POST"])
def query():
    try:
        # Parse JSON data payload from frontend
        data = request.get_json()
        company = data.get("company")
        predefined_query = data.get("predefined_query")
        custom_query = data.get("custom_query")

        # Choose the query to prioritize (predefined > custom)
        query_to_use = predefined_query if predefined_query else custom_query

        if not company or not query_to_use:
            return jsonify({"error": "Please select a valid company or query."}), 400

        # Generate response using helper function
        response_text = handle_query(company, query_to_use)

        return jsonify({"response": response_text})

    except Exception as e:
        # Handle unexpected errors gracefully
        return jsonify({"error": str(e)}), 500


# Run the server
if __name__ == "__main__":
    app.run(debug=True)
