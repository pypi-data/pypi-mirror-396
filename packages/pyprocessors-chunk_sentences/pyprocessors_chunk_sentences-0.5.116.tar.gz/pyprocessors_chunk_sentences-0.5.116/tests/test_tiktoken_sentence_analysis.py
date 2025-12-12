import json
from pathlib import Path

from pymultirole_plugins.v1.schema import Document

from pyprocessors_chunk_sentences.chunk_sentences import TikTokenBasedSentenceAnalysis


def test():
    file = "data/news_fr.json"
    original_doc = load_document(file)
    model_name = "text-embedding-3-large"
    analysis = TikTokenBasedSentenceAnalysis(original_doc.text, original_doc.sentences[0], model_name)
    analysis.compute()
    sub_sentences = analysis.split(10)
    for sub_sentence in sub_sentences:
        sub_sentence_text = original_doc.text[sub_sentence.start:sub_sentence.end]
        print(f"{sub_sentence.length}: {sub_sentence_text}")


def load_document(file):
    testdir = Path(__file__).parent
    source = Path(testdir, file)
    with source.open("r") as fin:
        doc = json.load(fin)
        original_doc = Document(**doc)
    return original_doc
