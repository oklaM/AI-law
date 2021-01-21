from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk
import pdfplumber
import os
from os.path import abspath, join, dirname, exists
import tqdm

es = Elasticsearch()

print(es.ping())

print(es.info())

print(es.cat.indices())

def create_index(client):
    """Creates an index in Elasticsearch if one isn't already there."""
    client.indices.create(
        index="ipo-doc-12",
        body={
            "settings": {"number_of_shards": 1},
            "mappings": {
                "properties": {
                    "name": {"type": "string", 
                        "index": "not_analyzed"},
                    "page": {"type": "integer"},
                    "content": {"type": "text"},
                }
            },
        },
        ignore=400,
    )

def generate_actions(pdf, path_pdf):
    """Reads the file and for each page
    yields a single document. This function is passed into the bulk()
    helper to create many documents in sequence.
    """
    global _id
    with pdfplumber.open(path_pdf) as f_pdf:  ## open pdf
        progress = tqdm.tqdm(unit="page", total=len(f_pdf.pages))
        for page in f_pdf.pages:
            doc = {
                "_id": _id,
                "name": pdf,
                "page": page.page_number,
                "content": page.extract_text(),
            }
            yield doc
            _id += 1

            progress.update(1)

def main():
    client = Elasticsearch(
        # Add your cluster configuration here!
    )
    print("Creating an index...")
    create_index(client)

    print("Indexing documents...")
    path = os.path.join(dirname(abspath(__file__)), 'pdf')
    pdfs = os.listdir(path)
    number_of_docs = len(pdfs)
    global _id
    _id = 1
    progress = tqdm.tqdm(unit="doc", total=number_of_docs)
    successes = 0
    for pdf in pdfs:
        path_pdf = os.path.join(path, pdf)
        for ok, action in streaming_bulk(
            client=client, index="ipo-doc-12", actions=generate_actions(pdf, path_pdf),
        ):
            pass
        progress.update(1)
        successes += 1
    print("Indexed %d/%d documents" % (successes, number_of_docs))


if __name__ == "__main__":
    main()