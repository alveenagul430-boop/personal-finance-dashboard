from dotenv import load_dotenv      #load_dotenv lets Python read your .env file
import os     #lets us retrieve the key
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import date,datetime

#----------------------------
load_dotenv(dotenv_path=".env")  #This loads the private key from .env without putting the key directly in Python code

API_KEY = os.getenv("GOLD_API_KEY")
st.write("Current folder:", os.getcwd())
st.write("API key loaded:", API_KEY is not None)
#---------------------------cache for storing memory for gold rate provided by API----------------------

@st.cache_data(ttl=1800)#1800seconds means your dashboard can reuse the cached price for 30 minutes before requesting fresh data from the API
def get_gold_price(currency):
    headers = {"x-access-token": API_KEY, "Content-Type": "application/json"}
    url = f"https://www.goldapi.io/api/price/XAU/{currency}"
    response = requests.get(url, headers=headers)  # it will get response from API key in header and will show it in python dictionaries
    data = response.json()  # extract desired data from the whole API response
    if "error"in data:
        st.error(data["error"])
        return None

    return data #rest of program can't access data yet because it is inside the function.We use return to send it back out.


#----------------------------Title---------------------------

st.title("Alveena's finance Dashboard") # it will put a giant title on my web page
st.write("Track your income, expenses, savings, investments, and portfolio.")
#---------------------------user data entry--------------------

income=st.number_input("please enter your current monthly income")
st.header("Financial Information") #This separates input area from the rest of the dashboard.

st.write("your current income is :",income)
food=st.number_input("please enter your expense on food")# it will ask for user's tt expense on these things
transport=st.number_input("please enter your expense on transport")
bills=st.number_input("please enter your expense on bills")
investment=st.number_input("please enter how much would you like to invest?")
savings_goal = st.number_input("Enter your monthly savings goal")

gold=st.number_input("please enter your investment on gold")#it will ask for how much user will like to invest in respective things
gold_purchase_price=st.number_input("please enter the price you paid per gram of gold")#it will ask for how much per gram of gold user paid
#gold_purchase_price is what user paid per gram of gold & Current_price_24k is what API says the current price is


stocks=st.number_input("please enter your investment on stocks")
mutual_funds=st.number_input("please enter your investment on mutual funds")

currency=st.selectbox("Select currency",["USD","EUR","IDR","PKR"])#it will show a dropdown menu for currency selection

#------------------------calculations---------------------------
total_expense=food+transport+bills
total_investment=gold+stocks+mutual_funds
if total_investment>0:          #it will calc what is %age of ur investments
    gold_percentage=(gold/total_investment)*100
    stocks_percentage=(stocks/total_investment)*100
    mutual_funds_percentage = (mutual_funds / total_investment) * 100
else:
    gold_percentage=0
    stocks_percentage=0
    mutual_funds=0

balance=income - total_expense - total_investment
saving_difference=balance-savings_goal

if gold_purchase_price > 0:
    gold_grams = gold / gold_purchase_price
else:
    gold_grams = 0

#------------------------gold API------------
data=get_gold_price(currency)
if data is not None: #this means that only try to read gold price if API actually return with avlid data
    current_price_24k = data["melt_price_per_gram"]["24k"] #separate [] shows data has a dictionary inside another dictionary
    current_price_22k = data["melt_price_per_gram"]["22k"]

    st.header(" Gold & Savings")
    st.write("24k gold price:",current_price_24k)
    st.write("22k gold price:",current_price_22k)

else:
    current_price_24k = 0
    current_price_22k = 0#We always create gold_profit, even when the API fails, so Python won't get a NameError

gold_current_value = gold_grams * current_price_24k #That's the estimated current value of your gold.like how much it costs
gold_profit = gold_current_value - gold

if gold_profit > 0:
    st.success(f"Gold profit: {gold_profit:.2f}")#.2f → format the number as a floating-point number with 2 decimal places

elif gold_profit < 0:
    st.error(f"Gold loss: {abs(gold_profit):.2f}")

else:
    st.info("No gold profit or loss")


st.write("24k gold price is :",current_price_24k)
st.write("22k gold price is :",current_price_22k)

if income > 0:               #its actually setting a condition that if income is greater the 0 then show investment % otherwise show 0
    investment_percentage = (investment / income) * 100
else:
    investment_percentage = 0

saving_difference=balance-savings_goal
if saving_difference > 0:    #it is comparison for your savings goal
    st.success(f"You are above your savings goal by: {saving_difference:.2f}")#

elif saving_difference < 0:
    st.warning(f"You are below your savings goal by: {abs(saving_difference):.2f}")#abs is use to remove -ive sign when user is below on saving goal
else:
    st.success("You have reached your savings goal!")


if savings_goal>0:  #this part is kind of saving goal indicator
    savings_progress=balance/savings_goal

else:
    savings_progress = 0
savings_progress = max(0, min(savings_progress, 1)) #it will keep progress bar in bw 0 &100%
st.progress(savings_progress)


st.header("Financial Summary")#This gives metrics their own dashboard section.
col1,col2,col3,col4,col5=st.columns(5) #it will introduce columns
with col1:st.metric("income",income)   #st.metric() is a Streamlit component designed specifically for dashboard numbers.
with col2:st.metric("transport",transport)#it makes an important number stand out(BOLD), rather than displaying it like ordinary text.
with col3:st.metric("bills",bills)
with col4:st.metric("food",food)
with col5:st.metric("investment",investment)

st.write("your remaining balance is :",balance)# it will tell the remaining balance of user
#st.write("current 24k gold price is:",current_price_24k)#it will tell on dashboard 24k gold price of what API tells it
#st.write("current 22k gold price is:",current_price_22k)
st.write("your  investment percentage is :",investment_percentage)

#-----------------------expense data-----------
expense_data = {
    "Category": ["food", "transport", "bills"],
    "Amount": [food, transport, bills]}

investment_data = {
    "Category": ["gold", "stocks", "mutual Funds"],
    "Amount": [gold,stocks,mutual_funds]}

df = pd.DataFrame(expense_data)     #it will convert expense data into data frame
investment_df= pd.DataFrame(investment_data) #

#-----------------------plotly----------
#---------------expense bar---------------------

st.header("Expense Analysis")
fig = px.bar(df,x="Category",y="Amount", title="My Expenses")#labels are giving names to x and y axis
st.plotly_chart(fig) # st.plotly says that Take this Plotly figure and display it on my webpage."
#--------------investment bar--------

st.header(" Investment Analysis")
col1,col2=st.columns(2)
with col1:
    investment_fig=px.bar(investment_df,x="Category",y="Amount", title="My Investment")#here we dont use df cz it only store expense value
    st.plotly_chart(investment_fig)

#--------------pie chart--------------
with col2:
    allocation_fig=px.pie(investment_df,names="Category",values="Amount",title="Portfolio Allocation")
    st.plotly_chart(allocation_fig) #it will create a pie chart showing how our investment is divided bw gold,stocks and mutual funds
#st.columns(2) divides the page into two areas, and with col1 / with col2 decides which chart goes where.both will appear parallel to each other
#--------------------CSV File----------------------

finance_data = {
    "date":str(date.today()), #tell current date on which csv file was made
    "time":datetime.now().strftime("%H:%M:%S"), #tell exact hr min and sec of csv file
    "Income": income,
    "Food": food,
    "Transport": transport,
    "Bills": bills,
    "Investment": investment,
    "Savings Goal": savings_goal,
    "remaining balance":balance,  #it will save the calculated results in CSV file
    "savings difference":saving_difference,
    "Gold Investment": gold,
    "Stocks": stocks,
    "Mutual Funds": mutual_funds}
finance_df=pd.DataFrame([finance_data])#it will turn finance data to a pandas table&[] will tell pandas to treat dictionary as complete row
csv=finance_df.to_csv(index=False)#it will turn table to a csv format & will amke it ready to downaload

st.download_button("Download My Finance Data",csv,"finance_data.csv","text/csv")#text/csv tells streamlit that file is a csv file

