import matplotlib.pyplot as plt
import pandas as pd
import pycountry
import spacy
import streamlit as st
from forex_python.converter import CurrencyRates

nlp = spacy.load("en_core_web_sm")
c = CurrencyRates()


def get_exchange_rate(from_currency, to_currency):
    return c.get_rate(from_currency, to_currency)


def convert_expense(expense, from_currency, to_currency):
    rate = get_exchange_rate(from_currency, to_currency)
    return expense * rate


def categorize_expense(expense_name):
    categories = {
        "food": [
            "restaurant",
            "grocery",
            "food",
            "coffee",
            "breakfast",
            "lunch",
            "dinner",
            "snack",
            "meal",
            "cafe",
            "local stall",
            "bakery",
            "bar",
            "beverage",
            "buffet",
            "catering",
            "chocolate",
            "cocktail",
            "deli",
            "dessert",
            "fast food",
            "fish",
            "grill",
            "ice cream",
            "pizza",
            "pub",
            "seafood",
            "smoothie",
            "sushi",
            "tapas",
            "tea",
        ],
        "travel": [
            "hotel",
            "flight",
            "taxi",
            "train",
            "bus",
            "car rental",
            "transportation",
            "parking",
            "uber",
            "transport",
            "airport",
            "cruise",
            "rental car",
            "road trip",
            "tour",
        ],
        "accommodation": [
            "hotel",
            "hostel",
            "motel",
            "lodging",
            "accommodation",
            "airbnb",
            "apartment",
            "bed and breakfast",
            "cabin",
            "resort",
            "villa",
        ],
        "shopping": [
            "shopping",
            "clothing",
            "electronics",
            "furniture",
            "bookstore",
            "supermarket",
            "gifts",
            "boutique",
            "department store",
            "jewelry",
            "mall",
            "market",
            "outlet",
            "shoes",
            "sporting goods",
            "toys",
        ],
        "miscellaneous": [
            "miscellaneous",
            "general",
            "expense",
            "others",
            "fees",
            "charges",
            "insurance",
            "internet",
            "maintenance",
            "subscription",
            "utility",
        ],
    }

    # Use SpaCy to categorize expense name
    doc = nlp(expense_name.lower())
    for token in doc:
        for category, keywords in categories.items():
            if token.text in keywords:
                return category
    return "miscellaneous"


def forex():
    st.title("Expense Manager")
    col1, col2 = st.columns(2)

    # Get the list of available currencies
    currency_list = sorted([currency.alpha_3 for currency in pycountry.currencies])

    # Input home and foreign currencies
    home_currency_default = currency_list.index("USD")
    foreign_currency_default = currency_list.index("INR")
    home_currency = col1.selectbox(
        "Select your home currency:", currency_list, index=home_currency_default
    )
    foreign_currency = col2.selectbox(
        "Select the foreign currency:", currency_list, index=foreign_currency_default
    )

    exchange_rate = 0
    if home_currency and foreign_currency:
        try:
            exchange_rate = get_exchange_rate(home_currency, foreign_currency)
        except Exception as e:
            st.error(f"Error: {e}")

    # Input expense details
    expense_name = col1.text_input("Enter the expense name:")
    foreign_expense = col2.number_input(
        f"Enter the expense in foreign currency ({foreign_currency}):", value=0.0
    )

    # Add expenses to a table
    if "expense_table" not in st.session_state:
        st.session_state.expense_table = []

    if st.button("Add Expense"):
        if expense_name and foreign_expense and home_currency and foreign_currency:
            try:
                converted_expense = convert_expense(
                    foreign_expense, foreign_currency, home_currency
                )
                expenses_category = categorize_expense(expense_name)
                new_expense = {
                    "Expense Name": expense_name,
                    "Expense Category": expenses_category,
                    f"Expense in {foreign_currency}": foreign_expense,
                    f"Expense in {home_currency}": converted_expense,
                }
                st.session_state.expense_table.append(new_expense)
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please fill in all the required fields.")

    # Display expenses table
    if st.session_state.expense_table:
        expenses_df = pd.DataFrame(st.session_state.expense_table)
        st.write("Expenses Table:")
        st.table(expenses_df)

        # Display total home currency spent
        total_home_currency = expenses_df[f"Expense in {home_currency}"].sum()

        # Pie chart of expense
        expenses_by_category = expenses_df.groupby(["Expense Category"]).sum()[
            f"Expense in {home_currency}"
        ]
        fig, ax = plt.subplots()
        ax.pie(
            expenses_by_category,
            labels=expenses_by_category.index,
            autopct="%1.1f%%",
            startangle=90,
        )
        ax.axis("equal")
        st.write("Total Expenses by Category:")
        st.pyplot(fig)

        # Display metrics side by side
        with col1:
            st.metric("Current Exchange Rate", round(exchange_rate, 2))
        with col2:
            st.metric(
                f"Total Home Currency Spent ({home_currency})",
                round(total_home_currency, 2),
            )

        # Add a button to reset expenses
        if st.button("Reset Expenses"):
            st.session_state.expense_table = []
            st.experimental_rerun()
    else:
        st.write("No expenses added yet.")


if __name__ == "__main__":
    forex()
