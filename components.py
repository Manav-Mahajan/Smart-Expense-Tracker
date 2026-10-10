import plotly.express as px

def plot_income_vs_expense(df, currency):
    """Returns a donut chart comparing total income and total expense."""
    if df.empty:
        return None
    summary = df.groupby('type')['amount'].sum().reset_index()
    if summary.empty:
        return None
    fig = px.pie(summary, values='amount', names='type', hole=0.5, 
                 title="Income vs Expenses", 
                 color='type', color_discrete_map={'Income':'#2ecc71', 'Expense':'#e74c3c'})
    fig.update_traces(textinfo='percent+label')
   
    fig.update_layout(margin=dict(t=40, b=10, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig

def plot_monthly_spending(df, currency):
    """Returns a bar chart showing expense trends over months."""
    if df.empty:
        return None
    expenses = df[df['type'] == 'Expense'].copy()
    if expenses.empty:
        return None
    
    
    expenses['month'] = expenses['date'].str[:7]
    monthly = expenses.groupby('month')['amount'].sum().reset_index()
    
    fig = px.bar(monthly, x='month', y='amount', title="Monthly Expenses Trend",
                 labels={'month': 'Month', 'amount': f'Amount ({currency})'},
                 color_discrete_sequence=['#e74c3c'])
    fig.update_layout(margin=dict(t=40, b=10, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig

def plot_category_breakdown(df, currency):
    """Returns a pie chart showing expense breakdown by category."""
    if df.empty:
        return None
    expenses = df[df['type'] == 'Expense']
    if expenses.empty:
        return None
        
    cat_summary = expenses.groupby('category')['amount'].sum().reset_index()
    fig = px.pie(cat_summary, values='amount', names='category', 
                 title="Expense Category Breakdown", hole=0.4)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(margin=dict(t=40, b=10, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig
