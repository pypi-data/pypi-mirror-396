# UzbekTokenization
A package designed for segmenting Uzbek texts into (a) words (with compound words and phrases), (b) syllables, (c) affixes, and (d) characters.


## Features
* **Word Tokenization**: Divide the text into words (with compound words and phrases).
* **Syllable Tokenization**:Divide the word into syllables.
* **Affix Tokenization**: Divide the word into affixes.
* **Char Tokenization**: Divide the text into characters.



## GitHub
To work with the project, it can be downloaded from [GitHub](https://github.com/ddasturbek/UzbekTokenization):
```bash
git clone https://github.com/ddasturbek/UzbekTokenization.git
```

## Install
Installing the libraries: To use the project, install this library from [PyPI](https://pypi.org/project/UzbekTokenization):
```bash
pip install UzbekTokenization
```

# Usage
Using the library is very easy. You can perform tokenization processes through the following code examples.

## Word Tokenization

```Python
from UzbekTokenization import WordTokenizer as wt

text = "Uzoq davom etgan janjaldan keyin mashinaning abjag‘i chiqdi."

print(wt.tokenize(text))
print(wt.tokenize(text, multi_word=True))
print(wt.tokenize(text, multi_word=True, pos=True))


""" Results
['Uzoq', 'davom etgan', 'janjaldan', 'keyin', 'mashinaning', 'abjag‘i chiqdi', '.']
['Uzoq', 'davom+etgan', 'janjaldan', 'keyin', 'mashinaning', 'abjag‘i+chiqdi', '.']
['Uzoq', 'davom+etgan(VERB)', 'janjaldan', 'keyin', 'mashinaning', 'abjag‘i+chiqdi', '.']
"""

```
This Word Tokenization program tokenizes Uzbek language texts into words. It separates compound words (verbs, adverbs, pronouns, and interjections) and KFSQ (Ko‘makchi Fe'lli So‘z Qo‘shilmasi, Compound Verb Phrases) as single units, for example, 'idrok etmoq', 'mana bu', 'hech narsa', 'sevib boshlamoq'. Furthermore, it also tokenizes Uzbek language phrases (idioms) separately.

## Syllable Tokenization

```Python
from UzbekTokenization import SyllableTokenizer as st

print(st.tokenize("Gul"))  # Gul
print(st.tokenize("Yulduz"))  # Yul-duz
print(st.tokenize("shashlik"))  # shash-lik
print(st.tokenize("BOG‘BON"))  # BOG‘-BON
print(st.tokenize("kelinglar"))  # ke-ling-lar
print(st.tokenize("yangilik"))  # yan-gi-lik
print(st.tokenize("Agglyutinativ"))  # ag-glyu-ti-na-tiv
print(st.tokenize("Salom barchaga"))  # Salom barchaga
```
This Syllable Tokenization program tokenizes Uzbek language words into syllables. It correctly separates the letter combinations and symbols O‘o‘ G‘g‘ as well as the digraphs Shsh Chch Ngng. Furthermore, the ng may appear either as a digraph or as separate letters (n and g) within a word; in such cases, they are not separated if they form a digraph, but can be separated if they appear as individual letters. Some complex words do not follow the rules, which is why a list of them has been compiled within the program. It is case-sensitive.

## Affix Tokenization

```Python
from UzbekTokenization import AffixTokenizer as at

print(at.tokenize("Serquyosh"))  # Ser-quyosh
print(at.tokenize("KITOBLAR"))  # KITOB-LAR
print(at.tokenize("o‘qiganman"))  # o‘qi-gan-man
print(at.tokenize("Salom odamlar"))  # Salom odamlar
```
This Affixes Tokenization program tokenizes Uzbek language words into affixes. Affixes in Uzbek are of two types: derivational (word-forming) and inflectional (form-forming). Inflectional affixes, in turn, are divided into two types: lexical inflectional and syntactic inflectional affixes.

The program specifically separates syntactic inflectional affixes that consist of two or more characters. This is because derivational affixes, lexical inflectional affixes, and single-character syntactic inflectional affixes resemble individual letters within the word stem, making it complicated to distinguish between the affix and the letters of the word stem in those cases.

The program only tokenizes words into affixes; if a text (a phrase or sentence) is provided, it returns it as is. It is case-sensitive.

## Char Tokenization

```Python
from UzbekTokenization import CharTokenizer as ct

print(ct.tokenize("o‘g‘ri"))  # ['o‘', 'g‘', 'r', 'i']
print(ct.tokenize("choshgoh"))  # ['ch', 'o', 'sh', 'g', 'o', 'h']
print(ct.tokenize("bodiring"))  # ['b', 'o', 'd', 'i', 'r', 'i', 'ng']
print(ct.tokenize("Salom, dunyo!"))  # ['S', 'a', 'l', 'o', 'm', ',', 'd', 'u', 'n', 'y', 'o', '!']
print(ct.tokenize("Salom, dunyo!", True))  # ['S', 'a', 'l', 'o', 'm', ',', ' ', 'd', 'u', 'n', 'y', 'o', '!']
```
This Char Tokenization program works correctly for Uzbek language letters, because in Uzbek, the letter combinations and symbols O‘o‘ G‘g‘ and the digraphs Shsh Chch Ngng are considered as a single character. If the value True is provided as the second parameter to the tokenize function, it performs the tokenization while also taking into account the spaces.


# License
This project is licensed under the [MIT License](https://opensource.org/license/mit).
