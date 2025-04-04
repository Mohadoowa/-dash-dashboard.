import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html, Input, Output

# Ссылки на Google Sheets для экспорта в CSV
file_id = "1ATITvw66m4Tz4TMAq5PRHYcBytFe_IbuT1p98z77L2w"
sheets = {
    "ФО 2025 ПЛАН": f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv&gid=0",
    "C&F": f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv&gid=2083183732",
    "Баланс": f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv&gid=1491596727"
}

# Загружаем данные
df_plan = pd.read_csv(sheets["ФО 2025 ПЛАН"])
df_cf = pd.read_csv(sheets["C&F"])
df_balance = pd.read_csv(sheets["Баланс"])

# Список месяцев
months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]

# Извлечение данных
income_data = df_plan.iloc[1, 1:13].astype(float)  # Доходы
expenses_data = df_plan.iloc[29, 1:13].astype(float)  # Расходы
profit_data = df_plan.iloc[30, 1:13].astype(float)  # Прибыль до распределения
profitability_data = df_plan.iloc[32, 1:13].astype(float)  # Рентабельность
cash_start = df_cf.iloc[0, 1:13].astype(float)  # Остаток ДС на начало месяца
cash_end = df_cf.iloc[1, 1:13].astype(float)  # Остаток ДС на конец месяца
rnd_expenses = df_plan.iloc[12, 1:13].astype(float)  # R&D
sales_management_expenses = df_plan.iloc[16, 1:13].astype(float)  # Продажи и управление
other_expenses = expenses_data - rnd_expenses - sales_management_expenses  # Прочие расходы

# Создаем Dash-приложение
app = dash.Dash(__name__, external_stylesheets=["https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap", "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css"])
server = app.server  # Для деплоя на Render

# Макет приложения
app.layout = html.Div([
    # Заголовок
    html.H1("Финансовый дашборд: Прогноз на 2025 год", style={
        'textAlign': 'center', 'color': '#2E7D32', 'fontFamily': 'Roboto', 'marginBottom': '20px'
    }),
    
    # Основные метрики с иконками
    html.Div([
        html.Div([
            html.I(className="fas fa-money-bill-wave", style={'fontSize': '24px', 'color': '#2E7D32', 'marginRight': '10px'}),
            html.Span(f"Общий доход: {df_plan.iloc[1, 13]:,.2f} грн", style={'fontSize': '18px', 'fontWeight': 'bold'})
        ], style={
            'background': 'linear-gradient(90deg, #C8E6C9, #FFFFFF)', 'borderRadius': '10px', 'padding': '15px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.1)', 'width': '30%'
        }),
        html.Div([
            html.I(className="fas fa-shopping-cart", style={'fontSize': '24px', 'color': '#D32F2F', 'marginRight': '10px'}),
            html.Span(f"Общие расходы: {df_plan.iloc[29, 13]:,.2f} грн", style={'fontSize': '18px', 'fontWeight': 'bold'})
        ], style={
            'background': 'linear-gradient(90deg, #FFCDD2, #FFFFFF)', 'borderRadius': '10px', 'padding': '15px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.1)', 'width': '30%'
        }),
        html.Div([
            html.I(className="fas fa-chart-line", style={'fontSize': '24px', 'color': '#1976D2', 'marginRight': '10px'}),
            html.Span(f"Прибыль: {df_plan.iloc[30, 13]:,.2f} грн", style={'fontSize': '18px', 'fontWeight': 'bold'})
        ], style={
            'background': 'linear-gradient(90deg, #BBDEFB, #FFFFFF)', 'borderRadius': '10px', 'padding': '15px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.1)', 'width': '30%'
        }),
    ], style={'display': 'flex', 'justify-content': 'space-around', 'margin': '20px 0'}),
    
    # Краткосрочный анализ доходности (последние 3 месяца)
    html.H3("Краткосрочный анализ доходности (последние 3 месяца)", style={'textAlign': 'center', 'color': '#2E7D32', 'fontFamily': 'Roboto'}),
    html.Div(id='short-term-profitability', style={'margin': '20px 0'}),
    
    # Выбор месяца
    html.Label("Выберите месяц для детализации:", style={'fontFamily': 'Roboto', 'fontSize': '16px'}),
    dcc.Dropdown(
        id='month-dropdown',
        options=[{'label': month, 'value': i} for i, month in enumerate(months)],
        value=None,
        clearable=True,
        placeholder="Все месяцы",
        style={'width': '50%', 'margin': '10px auto', 'fontFamily': 'Roboto'}
    ),
    
    # Графики
    dcc.Tabs([
        dcc.Tab(label="Доходы, расходы и прибыль", children=[
            dcc.Graph(id='income-expense-profit-graph')
        ]),
        dcc.Tab(label="Распределение расходов", children=[
            dcc.Graph(id='expense-distribution-graph')
        ]),
        dcc.Tab(label="Остатки денежных средств", children=[
            dcc.Graph(id='cash-balance-graph')
        ]),
        dcc.Tab(label="Тепловая карта доходов", children=[
            dcc.Graph(id='income-heatmap')
        ])
    ], style={'fontFamily': 'Roboto'})
], style={'backgroundColor': '#F5F5F5', 'padding': '20px', 'fontFamily': 'Roboto'})

# Коллбэк для обновления графиков
@app.callback(
    [Output('income-expense-profit-graph', 'figure'),
     Output('expense-distribution-graph', 'figure'),
     Output('cash-balance-graph', 'figure'),
     Output('income-heatmap', 'figure'),
     Output('short-term-profitability', 'children')],
    [Input('month-dropdown', 'value')]
)
def update_graphs(selected_month):
    # Фильтрация данных
    if selected_month is None:
        filtered_months = months
        filtered_income = income_data
        filtered_expenses = expenses_data
        filtered_profit = profit_data
        filtered_rnd = rnd_expenses
        filtered_sales = sales_management_expenses
        filtered_other = other_expenses
        filtered_cash_start = cash_start
        filtered_cash_end = cash_end
        filtered_profitability = profitability_data
    else:
        filtered_months = [months[selected_month]]
        filtered_income = [income_data[selected_month]]
        filtered_expenses = [expenses_data[selected_month]]
        filtered_profit = [profit_data[selected_month]]
        filtered_rnd = [rnd_expenses[selected_month]]
        filtered_sales = [sales_management_expenses[selected_month]]
        filtered_other = [other_expenses[selected_month]]
        filtered_cash_start = [cash_start[selected_month]]
        filtered_cash_end = [cash_end[selected_month]]
        filtered_profitability = [profitability_data[selected_month]]

    # Линейный график доходов, расходов и прибыли
    fig_income_expense_profit = px.line(
        x=filtered_months,
        y=[filtered_income, filtered_expenses, filtered_profit],
        labels={'x': 'Месяц', 'y': 'Сумма, грн', 'color': 'Категория'},
        title="Доходы, расходы и прибыль по месяцам",
        color_discrete_sequence=['#2E7D32', '#D32F2F', '#1976D2']
    )
    fig_income_expense_profit.for_each_trace(lambda t: t.update(name=['Доходы', 'Расходы', 'Прибыль'][t.trace_index]))

    # Круговая диаграмма распределения расходов
    if selected_month is not None:
        fig_expense_distribution = px.pie(
            values=[filtered_rnd[0], filtered_sales[0], filtered_other[0]],
            names=['R&D', 'Продажи и управление', 'Прочие'],
            title=f"Распределение расходов за {filtered_months[0]}",
            color_discrete_sequence=['#2E7D32', '#AB47BC', '#42A5F5']
        )
    else:
        fig_expense_distribution = px.pie(
            values=[sum(rnd_expenses), sum(sales_management_expenses), sum(other_expenses)],
            names=['R&D', 'Продажи и управление', 'Прочие'],
            title="Распределение расходов за год",
            color_discrete_sequence=['#2E7D32', '#AB47BC', '#42A5F5']
        )

    # Линейный график остатка денежных средств
    fig_cash = px.line(
        x=filtered_months,
        y=[filtered_cash_start, filtered_cash_end],
        labels={'x': 'Месяц', 'y': 'Сумма, грн', 'color': 'Тип'},
        title="Остатки денежных средств",
        color_discrete_sequence=['#1976D2', '#42A5F5']
    )
    fig_cash.for_each_trace(lambda t: t.update(name=['Начало месяца', 'Конец месяца'][t.trace_index]))

    # Тепловая карта доходов
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=[income_data],
        x=months,
        y=['Доходы'],
        colorscale='Greens',
        text=[f"{val:,.2f}" for val in income_data],
        texttemplate="%{text}",
        textfont={"size": 12},
    ))
    fig_heatmap.update_layout(title="Тепловая карта доходов по месяцам", xaxis_title="Месяц", yaxis_title="")

    # Краткосрочный анализ доходности (последние 3 месяца)
    last_3_months = months[:3]  # Январь, Февраль, Март
    last_3_profitability = profitability_data[:3]
    last_3_income = income_data[:3]

    # Процент изменения доходности между последними двумя месяцами
    if len(last_3_profitability) >= 2:
        profitability_change = ((last_3_profitability[2] - last_3_profitability[1]) / last_3_profitability[1] * 100) if last_3_profitability[1] != 0 else 0
        arrow = "↑" if profitability_change > 0 else "↓"
        arrow_color = "#2E7D32" if profitability_change > 0 else "#D32F2F"
    else:
        profitability_change = 0
        arrow = ""
        arrow_color = "#000000"

    short_term_content = html.Div([
        html.Div([
            html.Span(f"Доходность (Март): {last_3_profitability[2]:.2f}%", style={'fontSize': '18px', 'fontWeight': 'bold'}),
            html.Span(f" {arrow} {profitability_change:.2f}%", style={'color': arrow_color, 'marginLeft': '10px'}),
        ], style={
            'background': 'linear-gradient(90deg, #C8E6C9, #FFFFFF)', 'borderRadius': '10px', 'padding': '15px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.1)', 'width': '30%', 'textAlign': 'center'
        }),
        dcc.Graph(
            figure=px.line(
                x=last_3_months,
                y=last_3_profitability,
                labels={'x': 'Месяц', 'y': 'Доходность, %'},
                title="Доходность за последние 3 месяца",
                color_discrete_sequence=['#2E7D32']
            ).update_traces(mode='lines+markers')
        )
    ], style={'display': 'flex', 'justify-content': 'space-around', 'align-items': 'center'})

    return fig_income_expense_profit, fig_expense_distribution, fig_cash, fig_heatmap, short_term_content

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8080)
