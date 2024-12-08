""" Hi from Amina, Dastan, Roman

Usage example: python parser/src/export_to_csv.py --query "SELECT * FROM gz_lot" --output a.csv

"""

import logging

import psycopg
import csv
import argparse


def export_large_query_to_csv(db_config, query, output_file, chunk_size=10_000):
    logging.info("Starting export process")

    try:
        with psycopg.connect(**db_config) as conn:
            with conn.cursor(name='large_query_cursor') as cursor:
                logging.info("Executing query")
                cursor.execute(query)

                with open(output_file, mode='w', newline='', encoding='utf-8') as csvfile:
                    logging.info(f"Writing results to {output_file}")
                    writer = None
                    total_rows_processed = 0

                    while True:
                        rows = cursor.fetchmany(chunk_size)
                        if not rows:
                            break

                        if writer is None:
                            fieldnames = [desc[0] for desc in cursor.description]
                            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=";")
                            writer.writeheader()

                        writer.writerows(dict(zip(fieldnames, row)) for row in rows)

                        total_rows_processed += len(rows)
                        logging.info(f"Processed {total_rows_processed} rows...")

        logging.info(f"Export completed successfully. {total_rows_processed} rows written to {output_file}")

    except psycopg.OperationalError as oe:
        logging.error(f"Database connection error: {oe}")
    except Exception as e:
        logging.error(f"An error occurred during export: {e}")
    finally:
        logging.info("Export process completed")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    parser = argparse.ArgumentParser(description="Export large query result to a CSV file.")
    parser.add_argument("--query", required=True, help="SQL query to execute")
    parser.add_argument("--output", required=True, help="Path to the output CSV file")
    parser.add_argument("--chunk-size", default=10_000, type=int, help="Number of rows to fetch per batch (default: 10,000)")

    args = parser.parse_args()

    db_config = {
        "dbname": "procdb",
        "user": "user",
        "password": "pass",
        "host": "localhost",
        "port": 5432
    }

    export_large_query_to_csv(db_config, args.query, args.output, args.chunk_size)
