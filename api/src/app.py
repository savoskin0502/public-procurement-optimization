import locale
import os
import time
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from api.src.provider import GoszakupProvider

import pandas as pd
import streamlit as st

try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, 'en_US.utf8')
provider = GoszakupProvider(os.environ["GOSZAKUP_TOKEN"])

st.title("Win More Tenders with Price Recommendations")


def handle_search(query):
    result_message = st.empty()
    result_df = st.empty()

    if not query.strip():
        st.warning("Please enter a search query.")
        return

    progress_text = st.empty()
    progress_bar = st.progress(0)

    progress_text.write("Step 1: Searching lots...")
    time.sleep(0.1)
    progress_bar.progress(25)

    progress_text.write("Step 2: Collecting information about customer...")
    time.sleep(0.1)
    progress_bar.progress(50)

    progress_text.write("Step 3: Collecting information about advertisement...")
    time.sleep(0.1)
    progress_bar.progress(75)

    progress_text.write("Step 4: Making predictions...")
    time.sleep(0.1)
    progress_bar.progress(100)

    progress_text.empty()
    progress_bar.empty()

    result_message.success(f"Search results for lot number `{query}`")

    data = pd.DataFrame({
        'Lot Number': ["72915351-ЗЦПнеГЗ3"],
        'Lot Name': ["Промывалка"],
        'Description': ["Бутыль-промывалка 250 мл"],
        "Recommended Price": [locale.currency(21_200, grouping=True).replace("$", "₸")]
    })

    vertical_data = data.T
    vertical_data.columns = ["Value"]
    vertical_data.index.name = None

    st.markdown(
        """
        <style>
        .limited-table {
            width: 100%;
            min-width: 600px;
            margin: 0 auto;
            border-collapse: collapse;
            border: 1px solid #ddd;
        }
        .limited-table td {
            max-width: 400px;
            min-width: 400px;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .limited-table tr:last-child td{
            background-color: #d4f7d4; /* Light green for the last row */
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


    result_df.write(
        vertical_data.to_html(header=False, index=True, classes="limited-table"),
        unsafe_allow_html=True,
    )


if "search_lot_query" not in st.session_state:
    st.session_state.search_lot_query = ""


search_lot_query = st.text_input(
    "Input a lot number and receive an expertly calculated price recommendation",
    placeholder="Enter your lot number and press Enter",
)

st.markdown(
    "[Go to the public procurement website](https://goszakup.gov.kz/ru/search/lots)",
    unsafe_allow_html=True,
)
predefined_lot = st.button("or click here")
st.markdown(
    """
    <hr style='border: none; border-top: 1px solid #ccc; margin-top: 5px; width: 100%;'>
    """,
    unsafe_allow_html=True,
)

if predefined_lot:
    predefined_lot = "72915351-ЗЦПнеГЗ3"  # Text associated with the button
    handle_search(predefined_lot)
elif search_lot_query:
    handle_search(search_lot_query)


