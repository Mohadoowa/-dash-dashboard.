import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html

# Загружаем данные
file_path = "P&L Moodro.xlsx"
xls = pd.ExcelFile(file_path)

# Читаем листы
sheets = {sheet: xls.parse(sheet) for sheet in ["ФО 2025 ПЛАН", "C&F", "Баланс"]}

df_plan = sheets["ФО 2025 ПЛАН"]
df_cf = sheets["C&F"]
df_balance = sheets["Баланс"]

# Подготавливаем данные для графиков
months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
income = df_plan.iloc[1, 1:13].astype(float)
expenses = df_plan.iloc[2, 1:13].astype(float)
cash_balance = df_cf.iloc[0, 1:13].astype(float)
cash = df_balance.iloc[0, 1:6].astype(float)
inventory = df_balance.iloc[2, 1:6].astype(float)
finished_goods = df_balance.iloc[3, 1:6].astype(float)

# Создание графиков с Plotly
fig_income_expense = px.line(x=months, y=[income, expenses], labels={'x': 'Месяцы', 'y': 'Сумма, грн'},
                             title="Динамика доходов и расходов", markers=True)
fig_income_expense.update_traces(name="Доходы", line=dict(color="green"), selector=dict(name="wide_variable_0"))
fig_income_expense.update_traces(name="Расходы", line=dict(color="red"), selector=dict(name="wide_variable_1"))

fig_cash = px.bar(x=months, y=cash_balance, labels={'x': 'Месяцы', 'y': 'Сумма, грн'},
                   title="Остатки денежных средств по месяцам", color_discrete_sequence=["blue"])

fig_balance = px.line(x=months[:5], y=[cash, inventory, finished_goods],
                      labels={'x': 'Месяцы', 'y': 'Сумма, грн'},
                      title="Баланс активов и обязательств", markers=True)
fig_balance.update_traces(name="Денежные средства", line=dict(color="blue"))
fig_balance.update_traces(name="Запасы", line=dict(color="orange"))
fig_balance.update_traces(name="Готовая продукция", line=dict(color="purple"))

# Создаем Dash-приложение
app = dash.Dash(__name__)
server = app.server  # Необходимо для деплоя на Render

app.layout = html.Div([
    html.H1("Финансовый дашборд"),
    dcc.Tabs([
        dcc.Tab(label="Доходы и расходы", children=[dcc.Graph(figure=fig_income_expense)]),
        dcc.Tab(label="Остатки денежных средств", children=[dcc.Graph(figure=fig_cash)]),
        dcc.Tab(label="Баланс активов", children=[dcc.Graph(figure=fig_balance)])
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8080)
