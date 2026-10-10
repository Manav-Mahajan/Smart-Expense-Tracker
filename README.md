# Smart Expense Tracker & Budget Manager
A professional, easy-to-use application built with Python and Streamlit to track your daily expenses, monitor your budgets, and gain insights into your financial habits.

## Features
- **Dashboard:** Interactive overview of your income, expenses, balance, and visual breakdown of where your money goes.
- **Add Transactions:** Quick entry for income and expenses with customizable categories.
- **Manage Transactions:** Search, filter, edit, and delete transactions.
- **Budgets:** Set up monthly budget limits per category and track your progress.
- **Reports:** Analyze your monthly savings and top spending categories, and export your data to CSV.
- **Settings:** Customize your currency symbol and switch between Dark/Light themes.

## Prerequisites
- **Python 3.8+** installed on your system.

## Setup Instructions (VS Code on Windows)

1. **Open VS Code**
   - Navigate to the project folder (`smart-expense-tracker`).
   - Open your terminal in VS Code (`Ctrl` + `` ` ``).

2. **Create a Virtual Environment (Recommended)**
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
3. Install Dependencies

powershell
pip install -r requirements.txt

 4.Run the Application

powershell
streamlit run app.py

 5.Using the App

The app will automatically open in your default web browser (usually at http://localhost:8501).
The database (expense_tracker.db) will be automatically created on the first launch.
Start by going to 'Add Transaction' and entering your first income or expense!

Technologies Used
Python
Streamlit (Web UI)
SQLite (Local Database)
Pandas (Data processing)
Plotly (Interactive Charts)


