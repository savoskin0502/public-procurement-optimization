import asyncio
import os
import time
import sys

import numpy as np
import xgboost as xgb

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from api.src.provider import GoszakupProvider

import pandas as pd
import streamlit as st


def thompson_sampling_bandit(n_arms, successes, failures):
    sampled_values = [np.random.beta(successes[i] + 1, failures[i] + 1) for i in range(n_arms)]
    return np.argmax(sampled_values)


provider = GoszakupProvider(os.environ["GOSZAKUP_TOKEN"])

st.title("Win More Tenders with Price Recommendations")

pricing_strategies = [0.90, 0.95, 1.0, 1.05]
successes = [3993, 36798, 59183, 6]
failures = [20, 0, 0, 0]

loaded_model = xgb.Booster()
loaded_model.load_model("xgb_model.json")


LOT_SEARCH_QUERY = """
query getLots($after: Int, $lotNumber: String){
    items: Lots(limit: 200, after: $after, filter: {lotNumber: $lotNumber}){
        lotId: id
        , lotNumber
        , lotName: nameRu
        , lotDescription: descriptionRu
        , total_amount: amount
    }
}
"""


def handle_search(query):
    async def fetch_data():
        result = await provider.execute(
            url=provider.graphql_url,
            query=LOT_SEARCH_QUERY,
            headers=provider._headers,
            variables={"after": 0, "lotNumber": query},
        )
        return result["data"]["items"]

    result_message = st.empty()
    result_df = st.empty()

    progress_text = st.empty()
    progress_bar = st.progress(0)

    progress_text.write("Step 1: Searching lots...")
    progress_bar.progress(50)

    try:
        response = asyncio.get_event_loop().run_until_complete(fetch_data())
    except RuntimeError:
        response = asyncio.run(fetch_data())

    if response is None:
        progress_bar.empty()
        progress_text.empty()
        result_message.warning("Lot with such number was not found")
        return

    input_row = response[0]

    progress_text.write("Step 2: Making predictions...")
    progress_bar.progress(100)

    dmatrix_input = xgb.DMatrix(
        pd.DataFrame(
            [
                {
                    "total_amount": np.log2(input_row["total_amount"])
                }
            ]
        )
    )
    predictions = loaded_model.predict(dmatrix_input)

    chosen_arm = thompson_sampling_bandit(len(pricing_strategies), successes, failures)
    adjusted_prediction = predictions[0] * pricing_strategies[chosen_arm]
    print(pricing_strategies[chosen_arm], predictions[0])
    if not query.strip():
        st.warning("Please enter a search query.")
        return

    # progress_text.write("Step 2: Collecting information about customer...")
    # time.sleep(0.1)
    # progress_bar.progress(50)
    #
    # progress_text.write("Step 3: Collecting information about advertisement...")
    # time.sleep(0.1)
    # progress_bar.progress(75)
    #
    # progress_text.write("Step 4: Making predictions...")
    # time.sleep(0.1)
    # progress_bar.progress(100)

    progress_text.empty()
    progress_bar.empty()

    result_message.success(f"Search results for lot number `{query}`")

    data = pd.DataFrame({
        'Lot Number': [input_row["lotNumber"]],
        'Lot Name': [input_row["lotName"]],
        'Description': [input_row["lotDescription"]],
        "Initial Lot Price": [f"${input_row["total_amount"]:,.2f}".replace("$", "₸")],
        "Recommended Price": [
            f"${min(np.power(2, predictions[0]), input_row["total_amount"]):,.2f}".replace("$", "₸")
        ],
        "Adjusted Price": [f"${np.power(2, adjusted_prediction):,.2f}".replace("$", "₸")]
    })

    vertical_data = data.T
    vertical_data.columns = ["Value"]
    vertical_data.index.name = None

    st.markdown(
        """
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
        @media screen and (max-width: 600px) {
            .limited-table {
                min-width: 100%;
            }
            .limited-table td {
                max-width: 100%;
                min-width: auto;
                word-wrap: break-word;
                white-space: normal;
            }
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
