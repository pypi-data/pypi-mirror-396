import json
from pathlib import Path

import pytest
from pymultirole_plugins.v1.schema import Document

from pyprocessors_chunk_sentences.chunk_sentences import (
    ChunkSentencesProcessor,
    ChunkSentencesParameters, ChunkingUnit, TokenModel, get_model, ResegmenterProcessor, ResegmenterParameters,
    SentenceResegmenter,
)


def test_model():
    model = ChunkSentencesProcessor.get_model()
    model_class = model.construct().__class__
    assert model_class == ChunkSentencesParameters


def test_chunk_sentences_char():
    testdir = Path(__file__).parent
    source = Path(testdir, "data/news_fr.json")
    with source.open("r") as fin:
        doc = json.load(fin)
        original_doc = Document(**doc)
    processor = ChunkSentencesProcessor()
    parameters = ChunkSentencesParameters()
    # docs = processor.process([Document(**doc)], parameters)
    # chunked: Document = docs[0]
    # assert len(original_doc.sentences) > len(chunked.sentences)
    # for sent in chunked.sentences:
    #     assert sent.end - sent.start <= parameters.chunk_char_max_length
    # result = Path(testdir, "data/news_fr_char_chunked.json")
    # with result.open("w") as fout:
    #     json.dump(chunked.dict(), fout, indent=2)

    parameters = ChunkSentencesParameters(chunk_char_max_length=3000, unit=ChunkingUnit.character)
    docs = processor.process([Document(**doc)], parameters)
    chunked2: Document = docs[0]
    assert len(original_doc.sentences) > len(chunked2.sentences)
    # assert len(chunked.sentences) > len(chunked2.sentences)
    result = Path(testdir, "data/news_fr_char_chunked2.json")
    with result.open("w") as fout:
        json.dump(chunked2.dict(), fout, indent=2)

    # # Chunk and truncate
    # parameters = ChunkSentencesParameters(trunc_char_max_length=3000, unit=ChunkingUnit.character)
    # docs = processor.process([Document(**doc)], parameters)
    # chunked3: Document = docs[0]
    # assert len(original_doc.sentences) > len(chunked3.sentences)
    # assert len(original_doc.text) > len(chunked3.text)
    # assert 2000 > len(chunked3.text)
    # result = Path(testdir, "data/news_fr_char_chunked3.json")
    # with result.open("w") as fout:
    #     json.dump(chunked3.dict(), fout, indent=2)
    #
    # # Truncate without chunking
    # parameters = ChunkSentencesParameters(chunk_char_max_length=0, trunc_char_max_length=3000, unit=ChunkingUnit.character)
    # docs = processor.process([Document(**doc)], parameters)
    # chunked4: Document = docs[0]
    # assert len(original_doc.sentences) >= len(chunked4.sentences)
    # assert len(chunked3.sentences) < len(chunked4.sentences)
    # assert len(original_doc.text) > len(chunked4.text)
    # assert len(chunked3.text) == len(chunked4.text)
    # assert 2000 > len(chunked4.text)
    # result = Path(testdir, "data/news_fr_char_chunked4.json")
    # with result.open("w") as fout:
    #     json.dump(chunked4.dict(), fout, indent=2)


def test_chunk_sentences_token():
    parameters = ChunkSentencesParameters(unit=ChunkingUnit.token, chunk_token_max_length=60, overlap=0)
    h = get_model(parameters.model.value)

    testdir = Path(__file__).parent
    source = Path(testdir, "data/news_fr.json")
    with source.open("r") as fin:
        doc = json.load(fin)
        original_doc = Document(**doc)

    processor = ChunkSentencesProcessor()
    # docs = processor.process([Document(**doc)], parameters)
    # chunked: Document = docs[0]
    # assert len(original_doc.sentences) > len(chunked.sentences)
    # for sent in chunked.sentences:
    #     ctext = chunked.text[sent.start:sent.end]
    #     print("===========================================================")
    #     print(ctext)
    #     stokens = ChunkSentencesProcessor.tokenize_with_model(h, chunked.text[sent.start:sent.end])
    #     assert len(stokens) <= parameters.chunk_token_max_length
    # result = Path(testdir, "data/news_fr_token_chunked.json")
    # with result.open("w") as fout:
    #     json.dump(chunked.dict(), fout, indent=2)
    #
    # docs = processor.process([Document(**doc)], parameters)
    # chunked: Document = docs[0]
    # assert len(original_doc.sentences) > len(chunked.sentences)
    # for sent in chunked.sentences:
    #     ctext = chunked.text[sent.start:sent.end]
    #     print("===========================================================")
    #     print(ctext)
    #     stokens = ChunkSentencesProcessor.tokenize_with_model(h, chunked.text[sent.start:sent.end])
    #     print (len(stokens))
    #     assert len(stokens) <= parameters.chunk_token_max_length
    # result = Path(testdir, "data/news_fr_token_chunked_over1.json")
    # with result.open("w") as fout:
    #     json.dump(chunked.dict(), fout, indent=2)
    #
    # h = get_model(parameters.model.value)
    # docs = processor.process([Document(**doc)], parameters)
    # chunked2: Document = docs[0]
    # assert len(original_doc.sentences) > len(chunked2.sentences)
    # for sent in chunked2.sentences:
    #     stokens = ChunkSentencesProcessor.tokenize_with_model(h, chunked2.text[sent.start:sent.end])
    #     assert len(stokens) <= parameters.chunk_token_max_length
    # result = Path(testdir, "data/news_fr_token_chunked2.json")
    # with result.open("w") as fout:
    #     json.dump(chunked2.dict(), fout, indent=2)
    #
    # parameters = ChunkSentencesParameters(unit=ChunkingUnit.token, model=TokenModel.bert_multi_cased,
    #                                       chunk_token_max_length=512)
    # h = get_model(parameters.model.value)
    # docs = processor.process([Document(**doc)], parameters)
    # chunked2: Document = docs[0]
    # assert len(original_doc.sentences) > len(chunked2.sentences)
    # for sent in chunked2.sentences:
    #     stokens = ChunkSentencesProcessor.tokenize_with_model(h, chunked2.text[sent.start:sent.end])
    #     assert len(stokens) <= parameters.chunk_token_max_length
    # result = Path(testdir, "data/news_fr_token_chunked2.json")
    # with result.open("w") as fout:
    #     json.dump(chunked2.dict(), fout, indent=2)

    parameters = ChunkSentencesParameters(unit=ChunkingUnit.token, model=TokenModel.gpt_4,
                                          chunk_token_max_length=8000)
    h = get_model(parameters.model.value)
    docs = processor.process([Document(**doc)], parameters)
    chunked2: Document = docs[0]
    assert len(original_doc.sentences) > len(chunked2.sentences)
    for sent in chunked2.sentences:
        stokens = ChunkSentencesProcessor.tokenize_with_model(h, chunked2.text[sent.start:sent.end])
        assert len(stokens) <= parameters.chunk_token_max_length
    result = Path(testdir, "data/news_fr_token_chunked3.json")
    with result.open("w") as fout:
        json.dump(chunked2.dict(), fout, indent=2)

    # Chunk and truncate
    # parameters = ChunkSentencesParameters(unit=ChunkingUnit.token, model=TokenModel.gpt_4o,
    #                                       chunk_token_max_length=128, trunc_token_max_length=256)
    # h = get_model(parameters.model.value)
    # docs = processor.process([Document(**doc)], parameters)
    # chunked4: Document = docs[0]
    # assert len(original_doc.sentences) > len(chunked4.sentences)
    # doc_tok_length = 0
    # for sent in chunked4.sentences:
    #     stokens = ChunkSentencesProcessor.tokenize_with_model(h, chunked4.text[sent.start:sent.end])
    #     doc_tok_length += len(stokens)
    #     assert len(stokens) <= parameters.chunk_token_max_length
    # assert len(original_doc.text) > len(chunked4.text)
    # assert 256 > doc_tok_length
    # result = Path(testdir, "data/news_fr_token_chunked4.json")
    # with result.open("w") as fout:
    #     json.dump(chunked4.dict(), fout, indent=2)

    # Truncate without chunking
    # parameters = ChunkSentencesParameters(unit=ChunkingUnit.token, model=TokenModel.gpt_4o,
    #                                       chunk_token_max_length=0, trunc_token_max_length=256)
    # docs = processor.process([Document(**doc)], parameters)
    # chunked5: Document = docs[0]
    # assert len(original_doc.sentences) >= len(chunked5.sentences)
    # doc_tok_length = 0
    # for sent in chunked5.sentences:
    #     stokens = ChunkSentencesProcessor.tokenize_with_model(h, chunked5.text[sent.start:sent.end])
    #     doc_tok_length += len(stokens)
    # assert len(original_doc.text) > len(chunked5.text)
    # assert 256 > doc_tok_length
    # result = Path(testdir, "data/news_fr_token_chunked5.json")
    # with result.open("w") as fout:
    #     json.dump(chunked5.dict(), fout, indent=2)


def test_chunk_sentences_token_overlap_one_chunk():
    parameters = ChunkSentencesParameters(unit=ChunkingUnit.token, model=TokenModel.gpt_4,
                                          chunk_token_max_length=8000, overlap=3)
    testdir = Path(__file__).parent
    source = Path(testdir, "data/news_fr.json")
    with source.open("r") as fin:
        doc = json.load(fin)
        original_doc = Document(**doc)

    processor = ChunkSentencesProcessor()

    h = get_model(parameters.model.value)
    docs = processor.process([Document(**doc)], parameters)
    chunked2: Document = docs[0]
    assert len(original_doc.sentences) > len(chunked2.sentences)
    for sent in chunked2.sentences:
        stokens = ChunkSentencesProcessor.tokenize_with_model(h, chunked2.text[sent.start:sent.end])
        assert len(stokens) <= parameters.chunk_token_max_length
    result = Path(testdir, "data/news_fr_token_chunked3.json")
    with result.open("w") as fout:
        json.dump(chunked2.dict(), fout, indent=2)


def test_chunk_sentences_token_overlap_many_chunks():
    parameters = ChunkSentencesParameters(unit=ChunkingUnit.token, model=TokenModel.gpt_4,
                                          chunk_token_max_length=500, overlap=3)
    testdir = Path(__file__).parent
    source = Path(testdir, "data/news_fr.json")
    with source.open("r") as fin:
        doc = json.load(fin)
        original_doc = Document(**doc)
        for sentence in original_doc.sentences:
            print("original doc sentences:")
            sentence_text = original_doc.text[sentence.start:sentence.end].replace('\n', ' ')
            print(f"  {sentence_text}")

    processor = ChunkSentencesProcessor()

    h = get_model(parameters.model.value)
    docs = processor.process([Document(**doc)], parameters)
    chunked2: Document = docs[0]
    assert len(original_doc.sentences) > len(chunked2.sentences)
    assert len(chunked2.sentences) == 2
    for sent in chunked2.sentences:
        print("chunked doc sentences:")
        sentence_text = original_doc.text[sent.start:sent.end].replace('\n', ' ')
        print(f"  {sentence_text}")
        stokens = ChunkSentencesProcessor.tokenize_with_model(h, chunked2.text[sent.start:sent.end])
        assert len(stokens) <= parameters.chunk_token_max_length
    result = Path(testdir, "data/news_fr_token_chunked3.json")
    with result.open("w") as fout:
        json.dump(chunked2.dict(), fout, indent=2)


@pytest.mark.skip(reason="Not a test")
def test_blingfire():
    import blingfire
    s = "Эpple pie. How do I renew my virtual smart card?: /Microsoft IT/ 'virtual' smart card certificates for DirectAccess are valid for one year. In order to get to microsoft.com we need to type pi@1.2.1.2."

    print('-----------------------')
    print(s)
    words = blingfire.text_to_words(s).split(' ')  # sequence length: 128, oov id: 100
    print(len(words))
    print(words)

    for m in TokenModel:
        if m != TokenModel.wbd:
            # one time load the model (we are using the one that comes with the package)
            h = get_model(m.value)
            print('-----------------------')
            print("Model: %s" % m.value)

            # use the model from one or more threads
            ids = blingfire.text_to_ids(h, s, len(s), unk=0, no_padding=True)  # sequence length: 128, oov id: 100
            print(len(ids))  # returns a numpy array of length 128 (padded or trimmed)
            print(ids)  # returns a numpy array of length 128 (padded or trimmed)

            tokens = blingfire.text_to_words_with_model(h, s).split(' ')  # sequence length: 128, oov id: 100
            print(len(tokens))  # returns a numpy array of length 128 (padded or trimmed)
            print(tokens)  # returns a numpy array of length 128 (padded or trimmed)

            # free the model at the end
            blingfire.free_model(h)
            print("Model Freed")


def test_resegmenter():
    testdir = Path(__file__).parent
    source = Path(testdir, "data/commute64wllm-document-2021%20Tiwari%20SCR%20lung%20cerebral%20organoids.pdf.json")
    with source.open("r") as fin:
        doc = json.load(fin)
        original_doc = Document(**doc)
    processor = ResegmenterProcessor()
    parameters = ResegmenterParameters(unit=ChunkingUnit.token, chunk_token_max_length=512)
    h = get_model(parameters.model.value)
    docs = processor.process([Document(**doc)], parameters)
    chunked: Document = docs[0]
    assert len(original_doc.sentences) < len(chunked.sentences)
    for sent in chunked.sentences:
        ctext = chunked.text[sent.start:sent.end]
        print("===========================================================")
        print(ctext)
        stokens = ChunkSentencesProcessor.tokenize_with_model(h, chunked.text[sent.start:sent.end])
        assert len(stokens) <= parameters.chunk_token_max_length
    result = Path(testdir, "data/commute64wllm-document-2021%20Tiwari%20SCR%20lung%20cerebral%20organoids_resegmented.json")
    with result.open("w") as fout:
        json.dump(chunked.dict(), fout, indent=2)

    source = Path(testdir, "data/testconvert-document-PC_Kairntech_Python_BackportsSecurit%C3%A9-v2.docx.json")
    with source.open("r") as fin:
        doc = json.load(fin)
        original_doc = Document(**doc)
    processor = ResegmenterProcessor()
    parameters = ResegmenterParameters(unit=ChunkingUnit.token, chunk_token_max_length=128, sentence_resegmenter=SentenceResegmenter.syntok)
    h = get_model(parameters.model.value)
    docs = processor.process([Document(**doc)], parameters)
    chunked: Document = docs[0]
    assert len(original_doc.sentences) < len(chunked.sentences)
    for sent in chunked.sentences:
        ctext = chunked.text[sent.start:sent.end]
        print("===========================================================")
        print(ctext)
        stokens = ChunkSentencesProcessor.tokenize_with_model(h, chunked.text[sent.start:sent.end])
        assert len(stokens) <= parameters.chunk_token_max_length
    result = Path(testdir, "data/testconvert-document-PC_Kairntech_Python_BackportsSecurit%C3%A9-v2_resegmented.json")
    with result.open("w") as fout:
        json.dump(chunked.dict(), fout, indent=2)
