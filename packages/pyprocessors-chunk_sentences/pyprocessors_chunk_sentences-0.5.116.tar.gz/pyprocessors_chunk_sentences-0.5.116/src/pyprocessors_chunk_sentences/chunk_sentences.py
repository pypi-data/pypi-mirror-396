import os
from abc import ABC, abstractmethod
from enum import Enum
from functools import lru_cache
from typing import Type, List, cast

import blingfire
import tiktoken
from collections_extended import RangeMap
from pydantic import BaseModel, Field
from pymultirole_plugins.v1.processor import ProcessorParameters, ProcessorBase
from pymultirole_plugins.v1.schema import Document, Sentence
from pymultirole_plugins.v1.segmenter import SegmenterBase, SegmenterParameters
from pysegmenters_blingfire.blingfire import BlingFireSegmenter
from pysegmenters_syntok.syntok_segmenter import SyntokSegmenter


class ChunkingUnit(str, Enum):
    character = "character"
    token = "token"


class TokenModel(str, Enum):
    wbd = "wbd"
    bert_base_tok = "bert_base_tok"
    bert_base_cased_tok = "bert_base_cased_tok"
    bert_chinese = "bert_chinese"
    bert_multi_cased = "bert_multi_cased"
    xlm_roberta_base = "xlm_roberta_base"
    gpt2 = "gpt2"
    gpt_4 = "gpt-4"
    gpt_4o = "gpt-4o"
    gpt_3_5_turbo = "gpt-3.5-turbo"
    text_embedding_ada_002 = "text-embedding-ada-002"
    text_embedding_3_small = "text-embedding-3-small"
    text_embedding_3_large = "text-embedding-3-large"
    roberta = "roberta"
    laser100k = "laser100k"
    laser250k = "laser250k"
    laser500k = "laser500k"


class ChunkSentencesParameters(ProcessorParameters):
    unit: ChunkingUnit = Field(
        ChunkingUnit.character,
        description="""Which chunking unit to use to compute boundaries, can be one of:<br/>
                            <li>`character`: group consecutive sentences until their size is just below `chunk_char_max_length` characters.
                            <li>`token`: group consecutive sentences until their size is just below `chunk_token_max_length` tokens.""")

    model: TokenModel = Field(
        TokenModel.wbd,
        description="""Which [Blingfire tokenization](
                            https://github.com/microsoft/BlingFire) model to use, can be one of:<br/>
                            <li>`wbd`: Default Tokenization Model - Pattern based
                            <li>`bert_base_tok`: BERT Base/Large - WordPiece
                            <li>`bert_base_cased_tok`: BERT Base/Large Cased - WordPiece
                            <li>`bert_chinese`: BERT Chinese - WordPiece
                            <li>`bert_multi_cased`: BERT Multi Lingual Cased - WordPiece
                            <li>`xlm_roberta_base`: XLM Roberta Tokenization - Unigram LM
                            <li>`gpt2`: Byte-BPE tokenization model for GPT-2 - byte BPE
                            <li>`gpt-4`: Byte-BPE tokenization model for GPT-4 - byte BPE
                            <li>`gpt-4o`: Byte-BPE tokenization model for GPT-4o - byte BPE
                            <li>`gpt-3.5-turbo`: Byte-BPE tokenization model for GPT-3.5 - byte BPE
                            <li>`text-embedding-ada-002`: cl100k_base tokenizer
                            <li>`text-embedding-3-small`: cl100k_base tokenizer
                            <li>`text-embedding-3-large`: cl100k_base tokenizer
                            <li>`roberta`: Byte-BPE tokenization model for Roberta model - byte BPE
                            <li>`laser100k`: Trained on balanced by language WikiMatrix corpus of 80+ languages - Unigram LM
                            <li>`laser250k`: Trained on balanced by language WikiMatrix corpus of 80+ languages - Unigram LM
                            <li>`laser500k`: Trained on balanced by language WikiMatrix corpus of 80+ languages - Unigram LM""",
        extra="advanced")
    chunk_char_max_length: int = Field(
        1024, description="Maximum size of chunks (number of characters). If 0 don't group."
    )
    chunk_token_max_length: int = Field(
        128, description="Maximum size of chunks (number of tokens) If 0 don't group."
    )
    overlap: int = Field(
        0, description="Number of overlapping sentences between chunks"
    )
    trunc_char_max_length: int = Field(
        0, description="If >0, truncate the document (number of characters)", extra="advanced"
    )
    trunc_token_max_length: int = Field(
        0, description="If >0, truncate the document (number of tokens)", extra="advanced"
    )


class SentenceResegmenter(str, Enum):
    blingfire = "blingfire"
    syntok = "syntok"


class ResegmenterParameters(ChunkSentencesParameters):
    sentence_resegmenter: SentenceResegmenter = Field(
        SentenceResegmenter.blingfire,
        description="""Which sentence segmenter to use to resegment big chunks:<br/>
                            <li>`blingfire`.
                            <li>`segtok`.""")


class MarkedSentence:
    def __init__(self, sentence: Sentence, is_marked=False, length=-1):
        self.sentence = sentence
        self.is_marked = is_marked
        self.length = length

    @property
    def start(self):
        return self.sentence.start

    @start.setter
    def start(self, value):
        self.sentence.start = value

    @property
    def end(self):
        return self.sentence.end

    @end.setter
    def end(self, value):
        self.sentence.end = value

    @property
    def metadata(self):
        return self.sentence.metadata


class WrappedSentence:
    def __init__(self, sentence: MarkedSentence, start=None, end=None):
        self.wrapped = sentence
        self.start = start if start is not None else sentence.start
        self.end = end if end is not None else sentence.end


class SentenceAnalysis(ABC):

    def __init__(self, text: str, sentence: Sentence):
        self.text = text
        self.sentence = sentence

    @abstractmethod
    def compute(self):
        pass

    @abstractmethod
    def __len__(self) -> int:
        pass

    @abstractmethod
    def split(self, max_len) -> List[MarkedSentence]:
        pass

    def maybe_split(self, max_len) -> List[MarkedSentence]:
        length = len(self)
        if length < max_len:
            return [MarkedSentence(sentence=self.sentence, length=length)]
        else:
            return self.split(max_len)


@lru_cache(maxsize=None)
def get_tiktoken_encoding(model_name: str) -> tiktoken.Encoding:
    return tiktoken.encoding_for_model(model_name)


class CharacterBasedSentenceAnalysis(SentenceAnalysis):

    def __init__(self, text: str, sentence: Sentence):
        super().__init__(text, sentence)

    def compute(self):
        pass

    def __len__(self) -> int:
        return self.sentence.end - self.sentence.start

    def split(self, max_len) -> List[MarkedSentence]:
        sub_sentences = []
        start = self.sentence.start
        while start < self.sentence.end:
            # TODO improve whitespace handling...
            end = min(start + max_len, self.sentence.end)
            s_text = self.text[start:end]
            s_text_left_strip = s_text.lstrip()
            s_text_right_strip = s_text.rstrip()
            start_shift = len(s_text) - len(s_text_left_strip)
            end_shift = len(s_text) - len(s_text_right_strip)
            if start_shift != (start - end):
                final_start = start + start_shift
                final_end = end - end_shift
                sub_sentences.append(MarkedSentence(Sentence(start=final_start, end=final_end,
                                                       metadata=self.sentence.metadata,
                                                       categories=self.sentence.categories),
                                              length=(final_end - final_start)))
            start = end
        return sub_sentences


class TokenBasedSentenceAnalysis(SentenceAnalysis):

    def __init__(self, text: str, sentence: Sentence):
        super().__init__(text, sentence)
        self.tokens = None

    @abstractmethod
    def encode(self, text: str) -> List[int]:
        pass

    @abstractmethod
    def decode(self, tokens: List[int]) -> str:
        pass

    def compute(self):
        self.tokens = self.encode(self.text[self.sentence.start:self.sentence.end])

    def __len__(self) -> int:
        return len(self.tokens)

    def split(self, max_len) -> List[MarkedSentence]:
        sub_sentences = []
        start_token_index = 0
        start = self.sentence.start
        while start_token_index < len(self.tokens):
            # index of the end token taking into account that maybe we reached the end of input
            end_token_index = min(start_token_index + max_len, len(self.tokens))
            # rebuild the text of the subsequence of tokens
            sub_sentence_text = self.decode(self.tokens[start_token_index:end_token_index])
            # actual number of tokens in the sub sentence
            nb_tokens = end_token_index - start_token_index
            # get ready to continue the loop
            start_token_index = end_token_index
            # this might be the end index of the sub sentence
            end = start + len(sub_sentence_text)
            # this is the covered text
            covered_s_text = self.text[start:min(end, len(self.text))]
            if covered_s_text == sub_sentence_text:
                # most of the time it is working: decode(encode(text)) == text
                sub_sentences.append(MarkedSentence(Sentence(start=start, end=end,
                                                       metadata=self.sentence.metadata,
                                                       categories=self.sentence.categories),
                                              length=nb_tokens))
                start = end
            else:
                # but sometimes it isn't working...
                # so try to find individual words in the original sentence
                words = sub_sentence_text.split()
                sentence_start = -1
                sentence_end = -1
                for word in words:
                    # unknown characters seem to be messy
                    if word == '�':
                        continue
                    try:
                        word_start_index = self.text.index(word, start if sentence_end == -1 else sentence_end)
                        if sentence_start == -1:
                            sentence_start = word_start_index
                        sentence_end = word_start_index + len(word)
                    except ValueError:
                        pass
                if sentence_start != -1 and sentence_end != -1:
                    sub_sentences.append(MarkedSentence(Sentence(start=sentence_start, end=sentence_end,
                                                           metadata=self.sentence.metadata,
                                                           categories=self.sentence.categories),
                                                  length=nb_tokens))
                    start = sentence_end
                else:
                    # FIXME here we should implement a brute force approach:
                    # - do a substring of the remaining text (from "end")
                    # - find space characters in that new input (will be an issue for languages without any space character...)
                    # - tokenize up to that space character, count the number of tokens
                    # - if below the max token, progress to the next space character, etc...
                    raise Exception("unable to compute sub sentences of the required length")
        return sub_sentences


class TikTokenBasedSentenceAnalysis(TokenBasedSentenceAnalysis):

    def __init__(self, text: str, sentence: Sentence, model_name: str):
        super().__init__(text, sentence)
        self.encoding = get_tiktoken_encoding(model_name)

    def encode(self, text: str) -> List[int]:
        return self.encoding.encode(text)

    def decode(self, tokens: List[int]) -> str:
        return self.encoding.decode(tokens)


def analyze_sentence(params: ChunkSentencesParameters, text: str, sentence: Sentence) -> SentenceAnalysis:
    # FIXME restore other models
    if params.unit == ChunkingUnit.token:
        if params.model.startswith("gpt-") or "text-embedding" in params.model:
            analysis = TikTokenBasedSentenceAnalysis(text, sentence, params.model)
        else:
            # force text-embedding-ada-002 in any other case
            analysis = TikTokenBasedSentenceAnalysis(text, sentence, "text-embedding-ada-002")
    else:
        analysis = CharacterBasedSentenceAnalysis(text, sentence)
    analysis.compute()
    return analysis


class ChunkSentencesProcessor(ProcessorBase):
    """Group sentences by chunks of given max length.
    To be used in a segmentation pipeline."""

    def process(
            self, documents: List[Document], parameters: ProcessorParameters
    ) -> List[Document]:
        params: ChunkSentencesParameters = cast(ChunkSentencesParameters, parameters)
        # each chunk must contain (2*overlap + N) sentences where N >= 1
        min_nb_sentences_in_chunk = 2 * params.overlap + 1
        # so, to simplify, given a max length for a chunk...
        max_len = params.chunk_token_max_length if params.unit == ChunkingUnit.token else params.chunk_char_max_length
        # ... each sentence must be smaller enough to fit at least (2*overlap + 1) in the chunk
        sentence_max_len = max_len // min_nb_sentences_in_chunk
        if sentence_max_len <= 0:
            sentence_max_len = 1

        for document in documents:
            if len(document.sentences) == 0:
                continue
            # first split sentences so they are smaller than sentence_max_len
            marked_sub_sentences: List[MarkedSentence] = []
            for sentence in document.sentences:
                analysis = analyze_sentence(params, document.text, sentence)
                sub_sentences = analysis.maybe_split(sentence_max_len)
                marked_sub_sentences.extend(sub_sentences)

            # then group them in chunks
            # index of the sentence of the current chunk (included)
            chunk_start_sentence_index = 0
            # prepare the final list of sentences
            document.sentences = []
            while True:
                # length of the current chunk (in tokens or chars)
                chunk_len = 0
                # first put the minimum number of sentences into the chunk
                current_index = chunk_start_sentence_index
                upper_bound_index = min(chunk_start_sentence_index + min_nb_sentences_in_chunk, len(marked_sub_sentences))
                while current_index < upper_bound_index:
                    # include (sub-)sentence into the chunk
                    chunk_len += marked_sub_sentences[current_index].length
                    current_index += 1
                # then put as many (sub-)sentences that can fit into the chunk
                while current_index < len(marked_sub_sentences) and chunk_len + marked_sub_sentences[current_index].length <= max_len:
                    chunk_len += marked_sub_sentences[current_index].length
                    current_index += 1
                # we have our chunk
                # it's a sentence having the start offset of the first one of the chunk...
                chunk = marked_sub_sentences[chunk_start_sentence_index].sentence
                # ... and the end offset of the last one of the chunk
                chunk.end = marked_sub_sentences[current_index - 1].sentence.end
                document.sentences.append(chunk)
                # stop if last chunk reached
                if current_index == len(marked_sub_sentences):
                    break
                # get ready for the next chunk
                # don't forget the overlap so start before the end of the last chunk
                chunk_start_sentence_index = max(0, current_index - params.overlap)
        return documents

    @classmethod
    def tokenize_with_model(cls, model, stext):
        if isinstance(model, int):
            tokens = blingfire.text_to_ids(model, stext, len(stext), unk=0,
                                           no_padding=True) if model != -1 else blingfire.text_to_words(
                stext).split(' ')
        else:
            tokens = model.encode(stext)
        return tokens

    @classmethod
    def get_model(cls) -> Type[BaseModel]:
        return ChunkSentencesParameters


class ResegmenterProcessor(ChunkSentencesProcessor):
    """ Resegment existing sentences to split them if too large."""
    def resegment_chunk(self, sentence_resegmenter: SegmenterBase, ctext: str):
        chunk = Document(text=ctext)
        chunks: List[Document] = sentence_resegmenter.segment([chunk], SegmenterParameters())
        return chunks[0]

    def process(
            self, documents: List[Document], parameters: ProcessorParameters
    ) -> List[Document]:
        params: ResegmenterParameters = cast(ResegmenterParameters, parameters)
        sentence_resegmenter = SyntokSegmenter() if params.sentence_resegmenter == SentenceResegmenter.syntok else BlingFireSegmenter()
        trunc_size = params.trunc_token_max_length if params.unit == ChunkingUnit.token else params.trunc_char_max_length
        for document in documents:
            chunks = document.sentences or [Sentence(start=0, end=len(document.text))]
            sentences = []
            for chunk in chunks:
                csentences = []
                new_sentences = []
                ctext = document.text[chunk.start:chunk.end]
                result = self.resegment_chunk(sentence_resegmenter, ctext)
                if result:
                    for csent in result.sentences:
                        csentences.append(Sentence(start=csent.start, end=csent.end, metadata=chunk.metadata))
                msentences = [MarkedSentence(s) for s in csentences]
                for cstart, cend, meta in self.group_sentences(ctext, msentences,
                                                               params):
                    new_sentences.append(Sentence(start=cstart, end=cend, metadata=meta))
                last_end = new_sentences[-1].end if len(new_sentences) > 0 else trunc_size or len(ctext)
                if len(new_sentences) == 0:
                    new_sentences.append(Sentence(start=0, end=last_end, metadata=chunk.metadata))
                for new_sentence in new_sentences:
                    sentences.append(Sentence(start=new_sentence.start + chunk.start, end=new_sentence.end + chunk.start, metadata=chunk.metadata))
            document.sentences = sentences
        return documents

    @classmethod
    def group_sentences(cls, text: str, sentences: List[MarkedSentence], params: ChunkSentencesParameters):
        uncase = 'bert' in params.model.value and 'cased' not in params.model.value
        h = get_model(params.model.value) if params.unit == ChunkingUnit.token else None
        trunc_size = params.trunc_token_max_length if params.unit == ChunkingUnit.token else params.trunc_char_max_length
        chunk_size = params.chunk_token_max_length if params.unit == ChunkingUnit.token else params.chunk_char_max_length
        overlap = params.overlap
        chunks = RangeMap()
        start = 0
        text_length = 0
        for sent in sentences:
            if h is not None:
                stext = text[sent.start:sent.end].lower() if uncase else text[sent.start:sent.end]
                tokens = cls.tokenize_with_model(h, stext)
                if trunc_size > 0 and (text_length + len(tokens)) > trunc_size:
                    break
                text_length += len(tokens)
                end = start + len(tokens)
                if end > start:
                    chunks[start:end] = WrappedSentence(sent, start=start, end=end)
                start = end
            else:
                if trunc_size > 0 and sent.end > trunc_size:
                    break
                text_length = sent.end
                chunks[sent.start:sent.end] = WrappedSentence(sent)

        if chunk_size > 0:
            cstart = 0
            cend = 0
            while cend < text_length:
                ranges = chunks.get_range(cstart, cstart + chunk_size)
                if ranges.start is None or ranges.end is None:
                    break
                candidate_sents = list(ranges.values())
                csstart = candidate_sents[0].wrapped.start
                cmeta = candidate_sents[0].wrapped.metadata
                if len(candidate_sents) == 1:
                    cend = candidate_sents[-1].end
                    cnext_start = cend
                    csend = candidate_sents[-1].wrapped.end
                elif len(candidate_sents) > 1:
                    last_index = len(candidate_sents) - 1
                    if len(candidate_sents) > 2:
                        if ranges.end != candidate_sents[last_index].end:
                            last_index -= 1
                        marked = [index for index, cs in enumerate(candidate_sents) if index > 1 and cs.wrapped.is_marked]
                        if marked:  # Force to segment before all marked sentences
                            last_index = min(marked[0] - 1, last_index)
                    cend = candidate_sents[last_index].end
                    cnext_start = candidate_sents[last_index - overlap].end if (last_index - overlap >= 0) else cend
                    csend = candidate_sents[last_index].wrapped.end
                yield (csstart, csend, cmeta)
                cstart = cnext_start
        else:
            for csent in chunks.values():
                yield (csent.wrapped.start, csent.wrapped.end, csent.wrapped.metadata)

    @classmethod
    def tokenize_with_model(cls, model, stext):
        if isinstance(model, int):
            tokens = blingfire.text_to_ids(model, stext, len(stext), unk=0,
                                           no_padding=True) if model != -1 else blingfire.text_to_words(
                stext).split(' ')
        else:
            tokens = model.encode(stext)
        return tokens

    @classmethod
    def get_model(cls) -> Type[BaseModel]:
        return ChunkSentencesParameters


@lru_cache(maxsize=None)
def get_model(model: str):
    # load a provided with the package model
    if model == TokenModel.wbd.value:
        return -1
    elif model.startswith("gpt-") or "text-embedding" in model:
        h = tiktoken.encoding_for_model(model)
    else:
        h = blingfire.load_model(os.path.join(os.path.dirname(blingfire.__file__), f"{model}.bin"))
    return h
