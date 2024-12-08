import asyncio
import csv
import itertools
import parser.src.provider as provider
from parser.src.app_settings import get_settings

QUERY = """
query getApplications($after: Int){
    items: TrdApp(limit: 200, after: $after){
        applicationId: id
        , advertisementId: buyId
        , supplierId
        , supplierBinIin
        , protId
        , protNumber
        , dateApply
        , applicationLots: AppLots {
            applicationLotId: id
            , lotId
            , applicationLotPrice: price
            , applicationLotAmount: amount
            , applicationLotDiscountValue: discountValue
            , applicationLotDiscountPrice: discountPrice
            , applicationLotStatus: RefAppStatus{
                applicationLotStatusId: id
                , applicationLotStatusName: nameRu
                , applicationLotStatusCode: code
            }
        }
    }
}
"""

settings = get_settings()


async def main():
    gz_provider = provider.GoszakupProvider(token=settings.goszakup_token)

    destination_file = open("./data/supplier_application_h15.csv", mode="a", newline="", encoding="utf-8")
    writer = csv.DictWriter(
        destination_file,
        fieldnames=[
            'applicationId',
            'advertisementId',
            'supplierId',
            'supplierBinIin',
            'protId',
            'protNumber',
            'dateApply',
            'applicationLotId',
            'lotId',
            'applicationLotPrice',
            'applicationLotAmount',
            'applicationLotDiscountValue',
            'applicationLotDiscountPrice',
            'applicationLotStatusId',
            'applicationLotStatusName',
            'applicationLotStatusCode',
        ],
        delimiter=";"
    )
    writer.writeheader()

    prepared_batch = []

    try:
        async for batch in gz_provider.parse_graphql(query=QUERY, sort_key="applicationId", after=0):
            for entry in batch:
                if entry["applicationLots"] is None:
                    entry["applicationLots"] = []

                local_entries = [
                    {
                        **{
                            key: value for key, value in entry.items() if key != "applicationLots"
                        },
                        **{
                            key: application_lot[key]
                            for key in (
                                "applicationLotId",
                                "lotId",
                                "applicationLotPrice",
                                "applicationLotAmount",
                                "applicationLotDiscountValue",
                                "applicationLotDiscountPrice",
                            )
                        },
                        "applicationLotStatusId": application_lot["applicationLotStatus"]["applicationLotStatusId"],
                        "applicationLotStatusName": application_lot["applicationLotStatus"]["applicationLotStatusName"],
                        "applicationLotStatusCode": application_lot["applicationLotStatus"]["applicationLotStatusCode"],
                    } for application_lot in entry["applicationLots"]
                ]
                prepared_batch.append(local_entries)

            if len(prepared_batch) >= 10_000:
                prepared_batch = list(itertools.chain.from_iterable(prepared_batch))
                writer.writerows(prepared_batch)
                prepared_batch = []

    finally:
        prepared_batch = list(itertools.chain.from_iterable(prepared_batch))
        writer.writerows(prepared_batch)
        destination_file.close()


if __name__ == '__main__':
    asyncio.run(main())
