import asyncio
import csv
import parser.src.provider as provider
from parser.src.app_settings import get_settings

QUERY = """
query getLots($after: Int){
    items: Lots(limit: 200, after: $after){
        lotId: id
        , lotNumber
        , lotName: nameRu
        , lotDescription: descriptionRu
        , lotStatusId: refLotStatusId
        , isUnionLots: unionLots
        , totalCount: count
        , totalAmount: amount
        , customerId
        , advertisementId: trdBuyId
        , isDumping: dumping
        # плановый способ закупки
        , planTradeMethodId: refTradeMethodsId
        # фактический способ закупки
        factTradeMethodId: refBuyTradeMethodsId
        , psdSign
        , isConsultingServices: consultingServices
        , singlOrgSign
        , isLightIndustry
        , isConstructionWork
        , isDisablePersonAdvertisement: disablePersonId
        , plansIds: pointList
    }
}
"""


settings = get_settings()


async def main():
    gz_provider = provider.GoszakupProvider(token=settings.goszakup_token)
    destination_file = open("./data/lots_e5.csv", mode="a", newline="", encoding="utf-8")
    writer = csv.DictWriter(
        destination_file,
        fieldnames=[
            'lotId',
            'lotNumber',
            'lotName',
            'lotDescription',
            'lotStatusId',
            'isUnionLots',
            'totalCount',
            'totalAmount',
            'customerId',
            'advertisementId',
            'isDumping',
            'planTradeMethodId',
            'factTradeMethodId',
            'psdSign',
            'isConsultingServices',
            'singlOrgSign',
            'isLightIndustry',
            'isConstructionWork',
            'isDisablePersonAdvertisement',
            'plansIds',
        ],
        delimiter=";"
    )
    writer.writeheader()

    prepared_batch = []
    try:
        async for batch in gz_provider.parse_graphql(query=QUERY, sort_key="lotId", after=0):
            for entry in batch:
                if entry['plansIds'] is None:
                    entry['plansIds'] = []
                entry['plansIds'] = ':'.join([str(i) for i in entry['plansIds']])

                prepared_batch.append(entry)
            if len(prepared_batch) >= 10_000:
                writer.writerows(prepared_batch)
                prepared_batch = []

        writer.writerows(prepared_batch)
    finally:
        writer.writerows(prepared_batch)
        destination_file.close()


if __name__ == '__main__':
    asyncio.run(main())
