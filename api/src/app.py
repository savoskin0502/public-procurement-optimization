import asyncio
import datetime
import os
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

pricing_strategies = [0.94, 0.95, 0.96, 0.97, 0.98, 0.99, 1.0]
successes = [
    np.float64(1979.8184866891775),
    np.float64(1908.261819632896),
    np.float64(2119.9299452984737),
    np.float64(2074.3453225191824),
    np.float64(2177.133351210614),
    np.float64(2120.759620531656),
    np.float64(34695.66953559128)
]
failures = [56831, 129, 160, 171, 199, 169, 90929]

loaded_model = xgb.Booster()
loaded_model.load_model("xgb_model_v2.json")


LOT_SEARCH_QUERY = """
query getLots($after: Int, $lotNumber: String){
    items: Lots(limit: 200, after: $after, filter: {lotNumber: $lotNumber}){
        lotId: id
        , lotNumber
        , lotName: nameRu
        , lotDescription: descriptionRu
        , total_amount: amount
        , ad: TrdBuy {
            subjectType: RefSubjectType {
                subjectTypeId: id
            }
            startDate
            repeatStartDate
            endDate
            repeatEndDate
        }
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
    progress_bar.progress(33)

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
    progress_bar.progress(66)

    dmatrix_input = xgb.DMatrix(
        pd.DataFrame(
            [
                {
                    "total_amount": np.log2(input_row["total_amount"]),
                    "ad_duration_power": (
                            datetime.datetime.strptime(input_row["ad"]["endDate"], "%Y-%m-%d %H:%M:%S")
                            - datetime.datetime.strptime(input_row["ad"]["startDate"], "%Y-%m-%d %H:%M:%S")
                    ).days,
                    "is_subject_type_work": input_row["ad"]["subjectType"]["subjectTypeId"] == 2,
                    "is_subject_type_service": input_row["ad"]["subjectType"]["subjectTypeId"] == 3,
                }
            ]
        )
    )
    predictions = loaded_model.predict(dmatrix_input)

    progress_text.write("Step 3: Adjusting predictions...")
    progress_bar.progress(100)

    chosen_arm = thompson_sampling_bandit(len(pricing_strategies), successes, failures)
    adjusted_prediction = np.power(2, predictions[0]) * pricing_strategies[chosen_arm]
    print(pricing_strategies[chosen_arm], predictions[0])

    if not query.strip():
        st.warning("Please enter a search query.")
        return

    progress_text.empty()
    progress_bar.empty()

    result_message.success(f"Search results for lot number `{query}`")

    data = pd.DataFrame({
        "Lot Number": [input_row["lotNumber"]],
        "Lot Name": [input_row["lotName"]],
        "Description": [input_row["lotDescription"]],
        "Tender Start Date": [input_row["ad"]["startDate"]],
        "Tender End Date": [input_row["ad"]["endDate"]],
        "Initial Lot Price": [f"${input_row["total_amount"]:,.2f}".replace("$", "₸")],
        "Recommended Price": [
            f"${min(np.power(2, predictions[0]), input_row["total_amount"]):,.2f}".replace("$", "₸")
        ],
        "Price to Increase Winning Chances": [
            f"${adjusted_prediction:,.2f}".replace("$", "₸")
        ]
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
