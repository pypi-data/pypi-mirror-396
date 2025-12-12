from UzbekTokenization import PhraseTokenizer
from UzbekTokenization import WordTokenizer_


def tokenize(text, punctuation=True, pos=False, multi_word=False):
    list_with_phrases = PhraseTokenizer.tokenize(text, multi_word)

    list_text_with_phrase = []
    buffer = []

    for x in list_with_phrases:
        if " " not in x and "+" not in x:
            buffer.append(x)
        else:
            if buffer:
                merged = " ".join(buffer)
                list_text_with_phrase.append({"text": merged, "type": "merged"})
                buffer = []
            list_text_with_phrase.append({"text": x, "type": "original"})

    if buffer:
        merged = " ".join(buffer)
        list_text_with_phrase.append({"text": merged, "type": "merged"})

    results = []

    for text_or_phrase in list_text_with_phrase:
        if text_or_phrase["type"] == "original":
            results.append(text_or_phrase["text"])
        else:
            list_with_compound_and_kfsq = WordTokenizer_.tokenize(text_or_phrase["text"], punctuation, pos, multi_word)

            results.extend(list_with_compound_and_kfsq)

    return results
