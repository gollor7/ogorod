eng_alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
popular_words = [
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'I',
    'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
    'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
    'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what',
    'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me',
    'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know', 'take',
    'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other',
    'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also',
    'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way',
    'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us',
    'is', 'are', 'was', 'were', 'been', 'has', 'had', 'did', 'am', 'being',
    'may', 'might', 'shall', 'should', 'must', 'ought', 'would', 'can', 'could', 'will',
    'having', 'does', 'let', 'made', 'make', 'makes', 'doing', 'done', 'got', 'getting',
    'goes', 'went', 'gone', 'coming', 'came', 'comes', 'says', 'saying', 'said', 'seen',
    'seeing', 'see', 'looked', 'looking', 'looks', 'watched', 'watching', 'watch', 'know', 'knows',
    'knew', 'knowing', 'think', 'thought', 'thinking', 'believe', 'believes', 'believing', 'understand', 'understood',
    'understanding', 'try', 'tries', 'trying', 'tried', 'need', 'needs', 'needing', 'needed', 'feel',
    'feels', 'feeling', 'felt', 'leave', 'leaves', 'leaving', 'left', 'put', 'puts', 'putting',
    'keep', 'keeps', 'keeping', 'kept', 'start', 'starts', 'starting', 'started', 'begin', 'begins',
    'beginning', 'began', 'begun', 'run', 'runs', 'running', 'ran', 'live', 'lives', 'living',
    'lived', 'move', 'moves', 'moving', 'moved', 'hear', 'hears', 'hearing', 'heard', 'listen',
    'listens', 'listening', 'listened', 'talk', 'talks', 'talking', 'talked', 'speak', 'speaks', 'speaking',
    'spoke', 'spoken', 'write', 'writes', 'writing', 'wrote', 'written', 'read', 'reads', 'reading',
    'come', 'comes', 'coming', 'came', 'ask', 'asks', 'asking', 'asked', 'tell', 'tells',
    'telling', 'told', 'call', 'calls', 'calling', 'called', 'try', 'tries', 'trying', 'tried',
    'open', 'opens', 'opening', 'opened', 'close', 'closes', 'closing', 'closed', 'stop', 'stops',
    'stopping', 'stopped', 'wait', 'waits', 'waiting', 'waited', 'stand', 'stands', 'standing', 'stood',
    'sit', 'sits', 'sitting', 'sat', 'lie', 'lies', 'lying', 'lay', 'laid', 'rise',
    'rises', 'rising', 'rose', 'risen', 'fall', 'falls', 'falling', 'fell', 'fallen', 'hold',
    'holds', 'holding', 'held', 'bring', 'brings', 'bringing', 'brought', 'carry', 'carries', 'carrying'
]

with open('cipher_text.txt', 'r', encoding='utf-8') as file:
    cipher = file.read().lower()

def decoder_Caesar():
    key = 0
    result_separated = []
    match_key = {}
    while key != len(eng_alphabet):
        key += 1
        for letter in cipher:
            if letter in eng_alphabet:
                if eng_alphabet.index(letter) + key >= len(eng_alphabet):
                    index = eng_alphabet.index(letter) + key - len(eng_alphabet)
                else:
                    index = eng_alphabet.index(letter) + key
                result_separated.append(eng_alphabet[index])
            else:
                result_separated.append(letter)
        result_joined = ''.join(result_separated)
        result = result_joined.split()
        match = set(result) & set(popular_words)
        match_key[len(match)] = key


        result.clear()
        result_separated.clear()

    max_key = match_key[max(match_key)]
    key = max_key
    for letter in cipher:
        if letter in eng_alphabet:
            if eng_alphabet.index(letter) + key >= len(eng_alphabet):
                index = eng_alphabet.index(letter) + key - len(eng_alphabet)
            else:
                index = eng_alphabet.index(letter) + key
            result_separated.append(eng_alphabet[index])
        else:
            result_separated.append(letter)
    result_joined = ''.join(result_separated)
    result = result_joined.split()
    print(match_key)
    print('найбільш ймовірна розшифровка шляхом шифру Цезаря: ', result)


def decoder_atbash():
    result_separated = []
    for letter in cipher:
        if letter in eng_alphabet:
            result_separated.append(eng_alphabet[len(eng_alphabet) - 1 - eng_alphabet.index(letter)])
        else:
            result_separated.append(letter)
    result_joined = ''.join(result_separated)
    result = result_joined.split()
    print('розшифровка шляхом атбашу:', result)


def decoder_Wiggineer():
    ci_list = []
    ci_list_1 = []
    ciphers_ceasar = {}
    text = list(cipher)
    index_alphabet = 0
    length = len(cipher)
    key_length = 1
    while key_length != 21:
        index_lists = 0
        index_letter = 0
        for u in range(key_length):
            dodanok = 0
            index_lists += 1
            ciphers_ceasar[f'text_{key_length}_{index_lists}'] = []
            for l in range(index_lists):
                dodanok += 1
                while index_letter < len(text):
                    ciphers_ceasar[f'text_{key_length}_{index_lists}'].append(text[index_letter])
                    index_letter += key_length
                index_letter = 0
                index_letter += dodanok

        index_lists_1 = 1
        while index_lists > index_lists_1:
            current_list = ciphers_ceasar[f'text_{key_length}_{index_lists_1}']
            colvo_letters = current_list.count(eng_alphabet[index_alphabet])
            a = (colvo_letters/length)**2
            ci_list.append(a)
            if index_alphabet < 25:
                index_alphabet += 1
            index_lists_1 += 1
        ci = sum(ci_list)
        ci_list_1.append(ci)
        ci_list.clear()
        print(ci)
        key_length += 1
    # ci - coincidence index
    print(ci_list_1)











decoder_Caesar()
decoder_atbash()
decoder_Wiggineer()






