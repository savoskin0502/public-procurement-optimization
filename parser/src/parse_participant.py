import asyncio
import csv
import parser.src.provider as provider
from parser.src.app_settings import get_settings

QUERY = """
query getParticipants($after: Int){
    items: Subjects(limit: 200, after: $after){
        participantId: pid
        , bin
        , iin
        , registrationDate: regdate
        , creationDate: crdate
        , website
        , countryName: RefCountries {
            nameRu
        }
        , katoList
        , isQuazi: qvazi
        , isCustomer: customer
        , isOrganizer: organizer
        , isNationalCompany: markNationalCompany
        , refKopfCode
        , isAssociationWithDisabilities: markAssocWithDisab
        , registrationYear: year
        , isResident: markResident
        , isSupplier: supplier
        , supplierType: typeSupplier
        , krpCode
        , branches
        , parentCompany: parentSubject
        , okedList
        , kseCode
        , isWorldCompany: markWorldCompany
        , isStateMonopoly: markStateMonopoly
        , isNaturalMonopoly: markNaturalMonopoly
        , isPatronymicProducer: markPatronymicProducer
        , isPatronymicSupplier: markPatronymicSupplyer
        , isSmallEmployer: markSmallEmployer
        , isSingleOrg: isSingleOrg
    }
}
"""


settings = get_settings()

async def main():
    gz_provider = provider.GoszakupProvider(token=settings.goszakup_token)
    destination_file = open("./data/participants.csv", mode="a", newline="", encoding="utf-8")
    writer = csv.DictWriter(
        destination_file,
        fieldnames=[
            "participantId",
            "bin",
            "iin",
            "registrationDate",
            "creationDate",
            "website",
            "countryName",
            "katoList",
            "isQuazi",
            "isCustomer",
            "isOrganizer",
            "isNationalCompany",
            "refKopfCode",
            "isAssociationWithDisabilities",
            "registrationYear",
            "isResident",
            "isSupplier",
            "supplierType",
            "krpCode",
            "branches",
            "parentCompany",
            "okedList",
            "kseCode",
            "isWorldCompany",
            "isStateMonopoly",
            "isNaturalMonopoly",
            "isPatronymicProducer",
            "isPatronymicSupplier",
            "isSmallEmployer",
            "isSingleOrg"
        ],
        delimiter=";"
    )
    writer.writeheader()
    prepared_batch = []

    try:
        async for batch in gz_provider.parse_graphql(query=QUERY, sort_key="participantId", after=0):
            for entry in batch:
                entry["countryName"] = entry["countryName"]["nameRu"]

                for nested_field in {"katoList", "branches"}:
                    if entry[nested_field] is None:
                        entry[nested_field] = []
                    entry[nested_field] = ':'.join([str(i) for i in entry[nested_field]])

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
