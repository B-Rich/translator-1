#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import json
import http.client
from urllib.parse import quote
from urllib.parse import urlparse
try:
    import colorama
    colorama.init()
except ImportError:
    colorama = False

SYNONYMS = {
    'auto': ['auto', 'detect'],
    'af': ['af', 'afrikaans'],
    'sq': ['sq', 'albanian'],
    'ar': ['ar', 'arabic'],
    'hy': ['hy', 'armenian'],
    'az': ['az', 'azerbaijani'],
    'eu': ['eu', 'basque'],
    'be': ['be', 'belarusian'],
    'bn': ['bn', 'bengali'],
    'bg': ['bg', 'bulgarian'],
    'ca': ['ca', 'catalan'],
    'zh-CN': ['cn', 'zh-cn', 'china', 'chinese'],
    'hr': ['hr', 'croatian'],
    'cs': ['cs', 'cz', 'czech'],
    'da': ['da', 'danish'],
    'nl': ['nl', 'dutch'],
    'en': ['en', 'eng', 'english'],
    'et': ['et', 'est', 'estonian'],
    'tl': ['tl', 'filipino'],
    'fi': ['fi', 'finnish'],
    'fr': ['fr', 'french'],
    'gl': ['gl', 'galician'],
    'ka': ['ka', 'georgian'],
    'de': ['de', 'german'],
    'el': ['el', 'greek'],
    'gu': ['gu', 'gujarati'],
    'ht': ['ht', 'haitian', 'creole'],
    'iw': ['iw', 'hebrew'],
    'hi': ['hi', 'hindi'],
    'hu': ['hu', 'hungarian'],
    'is': ['is', 'icelandic'],
    'id': ['id', 'indonesian'],
    'ga': ['ga', 'irish'],
    'it': ['it', 'italian'],
    'ja': ['ja', 'jp', 'jap', 'japanese'],
    'kn': ['kn', 'kannada'],
    'ko': ['ko', 'korean'],
    'la': ['la', 'latin'],
    'lv': ['lv', 'latvian'],
    'lt': ['lt', 'lithuanian'],
    'mk': ['mk', 'macedonian'],
    'ms': ['ms', 'malay'],
    'mt': ['mt', 'maltese'],
    'no': ['no', 'norwegian'],
    'fa': ['fa', 'persian'],
    'pl': ['pl', 'pol', 'polish'],
    'pt': ['pt', 'portuguese'],
    'ro': ['ro', 'romanian'],
    'ru': ['ru', 'russian'],
    'sr': ['sr', 'serbian'],
    'sk': ['sk', 'slovak'],
    'sl': ['sl', 'slovenian'],
    'es': ['es', 'spanish'],
    'sw': ['sw', 'swahili'],
    'sv': ['sv', 'swedish'],
    'ta': ['ta', 'tamil'],
    'te': ['te', 'telugu'],
    'th': ['th', 'thai'],
    'tr': ['tr', 'turkish'],
    'uk': ['uk', 'ukrainian'],
    'ur': ['ur', 'urdu'],
    'vi': ['vi', 'vietnamese'],
    'cy': ['cy', 'welsh'],
    'yi': ['yi', 'yiddish'],
}

def get_language(code):
    for (key, val) in list(SYNONYMS.items()):
        if code in val:
            return key
    raise ValueError('Unknown language: {0}'.format(code))

if len(sys.argv) < 4:
    print('Too few arguments. Usage:', file=sys.stderr)
    print('{0} source target "text 1" "text 2"'.format(sys.argv[0]),
        file=sys.stderr)
    print('Example: {0} english japanese "Good morning"'.format(sys.argv[0]),
        file=sys.stderr)
    sys.exit(1)

def parse(content):
    data = content
    data = data.replace('[,', '["",')
    data = data.replace(',,', ',"",')
    data = data.replace(',,', ',"",')
    data = json.loads(data)

    data = \
    {
        'sentences':
        [
            {
                'translation': entry[0],
                'original': entry[1]
            } for entry in data[0]
        ],
        'dict':
        [
            {
                'type': entry[0],
                'basic-list': entry[1],
                'entries':
                [
                    {
                        'word': word[0],
                        'reverse': word[1],
                        'importance': float(word[3]) if len(word) > 3 else 0
                    } for word in entry[2]
                ]
            } for entry in data[1]
        ]
    }

    return data

def translate(source_language, target_language, text):
    url = (
        'https://translate.google.com/translate_a/single' +
        '?client=x' +
        '&ie=UTF-8' +
        '&oe=UTF-8' +
        '&dt=bd' +
        '&dt=ex' +
        '&dt=ld' +
        '&dt=md' +
        '&dt=qca' +
        '&dt=rw' +
        '&dt=rm' +
        '&dt=ss' +
        '&dt=t' +
        '&dt=at' +
        '&hl={0}' +
        '&sl={0}' +
        '&tl={1}' +
        '&q={2}').format(source_language, target_language, quote(text))

    host = urlparse(url).netloc
    client = http.client.HTTPSConnection(host, timeout=3)
    client.request('GET', url)
    response = client.getresponse()
    encoding = response.headers.get_content_charset()
    content = response.read().decode(encoding)
    return parse(content)

def set_red_color():
    if colorama:
        print(colorama.Fore.RED + colorama.Style.BRIGHT, end='')

def set_translucent_color():
    if colorama:
        print(colorama.Fore.WHITE + colorama.Style.DIM, end='')

def reset_color():
    if colorama:
        print(colorama.Fore.RESET + colorama.Style.RESET_ALL, end='')

def print_sentence(sentence):
    print('  ', end=' ')
    set_red_color()
    print(sentence['translation'], end=' ')
    reset_color()

    if 'transliteration' not in sentence:
        return
    if not sentence['transliteration']:
        return

    set_translucent_color()
    print('(Transliteration: {0})'.format(sentence['transliteration']), end='')
    reset_color()

def print_dict_group(group):
    max_importance = max(e['importance'] for e in group['entries'])
    print()
    if 'type' in group:
        print('Dictionary ({0}):'.format(group['type']))
    else:
        print('Dictionary:')

    for entry in group['entries']:
        print('  ', end=' ')
        set_red_color()
        print(entry['word'], end=' ')
        reset_color()

        if not 'reverse' in entry:
            continue

        set_translucent_color()
        print('(Reverse translation: {0})'.format(', '.join(entry['reverse'])))
        reset_color()

def print_dict(dict):
    for group in sorted(dict, key = lambda g: len(g['entries'])):
        print_dict_group(group)

if __name__ == '__main__':
    try:
        source_language = get_language(sys.argv[1].lower())
        target_language = get_language(sys.argv[2].lower())
    except ValueError as e:
        print(e, file=sys.stderr)
        sys.exit(1)

    for text in sys.argv[3:]:
        print('Translating "{0}":'.format(text))

        data = translate(source_language, target_language, text)

        for sentence in data['sentences']:
            print_sentence(sentence)
        print()

        if 'dict' in data:
            print_dict(data['dict'])
        print()
