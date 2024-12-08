import asyncio
import csv
import parser.src.provider as provider
from parser.src.app_settings import get_settings

QUERY = """
query getAdvertisements($after: Int){
    items: TrdBuy(limit: 200, after: $after){
        advertisementId: id
        , advertisementNumber: numberAnno
        , advertisementName: nameRu
        , totalSum
        , lotsCount: countLots
        , tradeMethodId: refTradeMethodsId
        , subjectTypeId: refSubjectTypeId
        , customerId: customerPid
        , advertisementStatusId: refBuyStatusId
        , startDate
        , repeatStartDate
        , endDate
        , repeatEndDate
        , publishDate
        , itogiDatePublic
        , tradeTypeId: refTypeTradeId
        , disablePersonId
        , singlOrgSign
        , isLightIndustry
        , isConstructionWork
        , purchaseTypeId: refSpecPurchaseTypeId
        , finYears: finYear
        , katos: kato
    }
}
"""


settings = get_settings()


async def main():
    gz_provider = provider.GoszakupProvider(token=settings.goszakup_token)
    destination_file = open("./data/advertisements_b2.csv", mode="a", newline="", encoding="utf-8")
    writer = csv.DictWriter(
        destination_file,
        fieldnames=[
            "advertisementId",
            "advertisementNumber",
            "advertisementName",
            "totalSum",
            "lotsCount",
            "tradeMethodId",
            "subjectTypeId",
            "customerId",
            "advertisementStatusId",
            "startDate",
            "repeatStartDate",
            "endDate",
            "repeatEndDate",
            "publishDate",
            "itogiDatePublic",
            "tradeTypeId",
            "disablePersonId",
            "singlOrgSign",
            "isLightIndustry",
            "isConstructionWork",
            "purchaseTypeId",
            "finYears",
            "katos"
        ],
        delimiter=";"
    )
    writer.writeheader()

    prepared_batch = []
    try:
        async for batch in gz_provider.parse_graphql(query=QUERY, sort_key="advertisementId", after=0):
            for entry in batch:
                if entry['finYears'] is None:
                    entry['finYears'] = []

                if entry['katos'] is None:
                    entry['katos'] = []

                entry['finYears'] = ':'.join([str(i) for i in entry['finYears']])
                entry['katos'] = ':'.join([str(i) for i in entry['katos']])

                prepared_batch.append(entry)
            if len(prepared_batch) >= 10_000:
                writer.writerows(prepared_batch)
                prepared_batch = []

    finally:
        writer.writerows(prepared_batch)
        destination_file.close()


if __name__ == '__main__':
    asyncio.run(main())
