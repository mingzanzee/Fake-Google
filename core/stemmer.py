import re


def stem_tokens(tokens: list[str]) -> tuple[list[str]]:
    """
    Use Porter Stemmer algorithm to group equivalent words
    e.g. run, ran, runs, running are equivalent

    Algorithm implemented from scratch without libraries
    Reference source for details of algorithm: https://tartarus.org/martin/PorterStemmer/def.txt
    """
    # Need non-unique for term frequency (TF)
    non_unique = []
    # and unique for document frequency (DF)
    unique = set()

    for t in tokens:
        res = porter_transform(t)
        non_unique.append(res)
        unique.add(res)

    return (non_unique, unique)

def porter_transform(word: str) -> str:
    """
    The Porter Stemmer algorithm applied to a word
    """
    
    word = step_1a(word)

    word = step_1b(word)

    word = step_1c(word)

    word = step_2(word)

    word = step_3(word)

    word = step_4(word)

    word = step_5b(step_5a(word))

    return word


def step_1a(word: str) -> str:
    """
    For the following in the form (condition) S1 -> S2:
    SSES -> SS, IES -> I, SS -> SS, S -> (nothing)
    Longest match for S1 is applied
    Stem BEFORE S1 is used for condition checking
    Note that tokenization alr converted word to lowercase
    """
    length = len(word)
    # SSES -> SS
    if length >= 4 and word[-4:] == "sses":
        return word[:-4] + "ss"
    # IES -> I
    elif length >= 3 and word[-3:] == "ies":
        return word[:-3] + "i"
    elif length >= 2 and word[-2:] == "ss":
        return word
    elif length >= 1 and word[-1] == "s":
        return word[:-1]
    else:
        return word

def step_1b(word: str) -> str:
    """
    (m > 0) EED -> EE,
    (*v*) ED -> (nothing) then proceed to extra step,
    (*v*) ING -> (nothing) then proceed to extra step
    """
    length = len(word)
    
    if length >= 3 and word[-3:] == "eed":
        if m_value(word[:-3]) > 0:
            return word[:-3] + "ee"
        else:
            return word
    elif length >= 2 and word[-2:] == "ed":
        if contains_vowel(word[:-2]):
            return extra_step(word[:-2])
        else:
            return word
    elif length >= 3 and word[-3:] == "ing":
        if contains_vowel(word[:-3]):
            return extra_step(word[:-3])
        else:
            return word
        
    
    return word
    
def extra_step(word: str) -> str:
    """
    AT -> ATE                       conflat(ed)  ->  conflate
    BL -> BLE                       troubl(ed)   ->  trouble
    IZ -> IZE                       siz(ed)      ->  size
    (*d and not (*L or *S or *Z))
       -> single letter
                                    hopp(ing)    ->  hop
                                    tann(ed)     ->  tan
                                    fall(ing)    ->  fall
                                    hiss(ing)    ->  hiss
                                    fizz(ed)     ->  fizz
    (m=1 and *o) -> E               fail(ing)    ->  fail
                                    fil(ing)     ->  file
    """
    length = len(word)
    # first 3 are definitely distinct and have common outcome so can do tgt
    if length >= 2 and word[-2:] in ["at", "bl", "iz"]:
        return word + 'e'
    elif length >= 2 and word[-2] == word[-1] and word[-1] not in ['l', 's', 'z']:
        return word[:-1]
    elif m_value(word) == 1 and star_o(word):
        return word + 'e'
    else:
        return word
    

def step_1c(word: str) -> str:
    """
    (*v*) Y -> I                    happy        ->  happi
                                    sky          ->  sky
    """
    if len(word) >= 1 and word[-1] == 'y' and contains_vowel(word[:-1]):
        return word[:-1] + 'i'
    else:
        return word
    

def step_2(word: str) -> str:
    """
    (m>0) ATIONAL ->  ATE           relational     ->  relate
    (m>0) TIONAL  ->  TION          conditional    ->  condition
                                    rational       ->  rational
    (m>0) ENCI    ->  ENCE          valenci        ->  valence
    (m>0) ANCI    ->  ANCE          hesitanci      ->  hesitance
    (m>0) IZER    ->  IZE           digitizer      ->  digitize
    (m>0) ABLI    ->  ABLE          conformabli    ->  conformable
    (m>0) ALLI    ->  AL            radicalli      ->  radical
    (m>0) ENTLI   ->  ENT           differentli    ->  different
    (m>0) ELI     ->  E             vileli        - >  vile
    (m>0) OUSLI   ->  OUS           analogousli    ->  analogous
    (m>0) IZATION ->  IZE           vietnamization ->  vietnamize
    (m>0) ATION   ->  ATE           predication    ->  predicate
    (m>0) ATOR    ->  ATE           operator       ->  operate
    (m>0) ALISM   ->  AL            feudalism      ->  feudal
    (m>0) IVENESS ->  IVE           decisiveness   ->  decisive
    (m>0) FULNESS ->  FUL           hopefulness    ->  hopeful
    (m>0) OUSNESS ->  OUS           callousness    ->  callous
    (m>0) ALITI   ->  AL            formaliti      ->  formal
    (m>0) IVITI   ->  IVE           sensitiviti    ->  sensitive
    (m>0) BILITI  ->  BLE           sensibiliti    ->  sensible

    The test for the string S1 can be made fast by doing a program switch on
    the penultimate letter of the word being tested. This gives a fairly even
    breakdown of the possible values of the string S1. It will be seen in fact
    that the S1-strings in step 2 are presented here in the alphabetical order
    of their penultimate letter. Similar techniques may be applied in the other
    steps.
    """

    rules = [
        ("ational", "ate"),
        ("tional", "tion"),
        ("enci", "ence"),
        ("anci", "ance"),
        ("izer", "ize"),
        ("abli", "able"),
        ("alli", "al"),
        ("entli", "ent"),
        ("eli", "e"),
        ("ousli", "ous"),
        ("ization", "ize"),
        ("ation", "ate"),
        ("ator", "ate"),
        ("alism", "al"),
        ("iveness", "ive"),
        ("fulness", "ful"),
        ("ousness", "ous"),
        ("aliti", "al"),
        ("iviti", "ive"),
        ("biliti", "ble"),
    ]

    for suffix, replacement in rules:
        if word.endswith(suffix):
            stem = word[:-len(suffix)]
            if m_value(stem) > 0:
                return stem + replacement
            else:
                return word

    return word


def step_3(word: str) -> str:
    """
    Step 3 of Porter Stemmer.
    (m>0) ICATE -> IC, etc.
    
    Rules applied in order with longest match.
    """
    rules = [
        ("icate", "ic"),
        ("ative", ""),
        ("alize", "al"),
        ("iciti", "ic"),
        ("ical", "ic"),
        ("ful", ""),
        ("ness", ""),
    ]

    for suffix, replacement in rules:
        if word.endswith(suffix):
            stem = word[:-len(suffix)]

            if m_value(stem) > 0:
                return stem + replacement
            else:
                return word

    return word
    
def step_4(word: str) -> str:
    """
    Step 4 of Porter Stemmer.
    (m>1) AL ->, etc.
    
    Rules applied in order with longest match.
    """
    rules = [
        "al",
        "ance",
        "ence",
        "er",
        "ic",
        "able",
        "ible",
        "ant",
        "ement",
        "ment",
        "ent",
        "ion",
        "ou",
        "ism",
        "ate",
        "iti",
        "ous",
        "ive",
        "ize",
    ]

    for suffix in rules:
        if word.endswith(suffix):
            stem = word[:-len(suffix)]

            if suffix == "ion":
                # Stem must end in s or t
                if len(stem) == 0 or stem[-1] not in ("s", "t"):
                    return word

            if m_value(stem) > 1:
                return stem
            else:
                return word

    return word
    

def step_5a(word: str) -> str:
    """
    Step 5a of Porter Stemmer.
    (m>1) E ->,
    (m=1 and not *o) E ->
    """
    length = len(word)
    
    if length < 2:
        return word
    
    if word[-1] == 'e':
        stem = word[:-1]
        m = m_value(stem)
        
        # (m>1) E ->
        if m > 1:
            return stem
        
        # (m=1 and not *o) E ->
        elif m == 1 and not star_o(stem):
            return stem
        
        else:
            return word
    
    return word

def step_5b(word: str) -> str:
    """
    Step 5b of Porter Stemmer.
    (m > 1 and *d and *L) -> single letter
    """
    length = len(word)
    
    if length < 2:
        return word
    
    # Check: m > 1 AND ends with double consonant (like -ll, -ss, -tt)
    # AND the last letter is L
    if m_value(word) > 1 and word[-2] == word[-1] and word[-1] == "l":
        return word[:-1]  # Remove the last character
    
    return word


# helper functions used in the Porter Stemmer algorithm
def contains_vowel(word: str) -> bool:
    """
    In the algorithm, a vowel is a, e, i, o, u,
    or y preceded by a consonant
    """
    return bool(re.search(r'a|e|i|o|u|[^aeiou]y', word))

def m_value(word: str) -> int:
    """
    I define the m-value as the value of m in [C](VC){m}[V]
    in the expected structure of a word
    """
    vowels = 'aeiou'

    # Step 1: Convert to C/V with correct y-handling
    cv = []
    for i, char in enumerate(word):
        if char in vowels:
            cv.append('V')
        elif char == 'y':
            if i == 0 or word[i-1] in vowels:
                cv.append('C')  # y at start or after vowel = consonant
            else:
                cv.append('V')  # y after consonant = vowel
        else:
            cv.append('C')
    
    # Step 2: Compress consecutive identical characters
    compressed = []
    for char in cv:
        if not compressed or compressed[-1] != char:
            compressed.append(char)
    
    cv_string = ''.join(compressed)
    
    # Step 3: Count VC sequences
    return len(re.findall(r'VC', cv_string))

def star_o(word: str) -> bool:
    """
    *o  - the stem ends cvc, where the second c is not W, X or Y (e.g. -WIL, -HOP).
    """
    if len(word) < 3:
        return False
    
    ending = word[-3:]
    
    vowels = "aeiou"
    cv = []
    for i, char in enumerate(ending):
        if char in vowels:
            cv.append('V')
        elif char == 'y':
            if i == 0 or ending[i-1] in vowels:
                cv.append('C')  # y at start or after vowel = consonant
            else:
                cv.append('V')  # y after consonant = vowel
        else:
            cv.append('C')

    return cv == ['C', 'V', 'C'] and ending[-1] not in ['w', 'x', 'y']
    



