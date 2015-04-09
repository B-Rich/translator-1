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

def get_language(code):
    synonyms = {'auto':['auto','detect'],'af':['af','afrikaans'],'sq':['sq','albanian'],'ar':['ar','arabic'],'hy':['hy','armenian'],'az':['az','azerbaijani'],'eu':['eu','basque'],'be':['be','belarusian'],'bn':['bn','bengali'],'bg':['bg','bulgarian'],'ca':['ca','catalan'],'zh-CN':['cn','zh-cn','china','chinese'],'hr':['hr','croatian'],'cs':['cs','cz','czech'],'da':['da','danish'],'nl':['nl','dutch'],'en':['en','eng','english'],'et':['et','est','estonian'],'tl':['tl','filipino'],'fi':['fi','finnish'],'fr':['fr','french'],'gl':['gl','galician'],'ka':['ka','georgian'],'de':['de','german'],'el':['el','greek'],'gu':['gu','gujarati'],'ht':['ht','haitian','creole'],'iw':['iw','hebrew'],'hi':['hi','hindi'],'hu':['hu','hungarian'],'is':['is','icelandic'],'id':['id','indonesian'],'ga':['ga','irish'],'it':['it','italian'],'ja':['ja','jp','jap','japanese'],'kn':['kn','kannada'],'ko':['ko','korean'],'la':['la','latin'],'lv':['lv','latvian'],'lt':['lt','lithuanian'],'mk':['mk','macedonian'],'ms':['ms','malay'],'mt':['mt','maltese'],'no':['no','norwegian'],'fa':['fa','persian'],'pl':['pl','pol','polish'],'pt':['pt','portuguese'],'ro':['ro','romanian'],'ru':['ru','russian'],'sr':['sr','serbian'],'sk':['sk','slovak'],'sl':['sl','slovenian'],'es':['es','spanish'],'sw':['sw','swahili'],'sv':['sv','swedish'],'ta':['ta','tamil'],'te':['te','telugu'],'th':['th','thai'],'tr':['tr','turkish'],'uk':['uk','ukrainian'],'ur':['ur','urdu'],'vi':['vi','vietnamese'],'cy':['cy','welsh'],'yi':['yi','yiddish']}
    for (key, val) in list(synonyms.items()):
        if code in val:
            return key
    raise ValueError('Unknown language: {0}'.format(code))

if len(sys.argv) < 4:
    print('Too few arguments. Usage:', file=sys.stderr)
    print('{0} sourceLanguage destinationLanguage "text to translate" "text to translate 2"'.format(sys.argv[0]), file=sys.stderr)
    print('Example: {0} english japanese "Good morning"'.format(sys.argv[0]), file=sys.stderr)
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
                        'reverse_translation': word[1],
                        'importance': float(word[3]) if len(word) > 3 else 0
                    } for word in entry[2]
                ]
            } for entry in data[1]
        ]
    }

    return data

try:
    langSrc = get_language(sys.argv[1].lower())
    langDest = get_language(sys.argv[2].lower())
except ValueError as e:
    print(e, file=sys.stderr)
    sys.exit(1)

for text in sys.argv[3:]:
    print('Translating "{0}":'.format(text))

    url = 'https://translate.google.com/translate_a/single?client=x&ie=UTF-8&oe=UTF-8&dt=bd&dt=ex&dt=ld&dt=md&dt=qca&dt=rw&dt=rm&dt=ss&dt=t&dt=at&hl={0}&sl={0}&tl={1}&q={2}'.format(langSrc, langDest, quote(text))
    host = urlparse(url).netloc
    headers = { 'User-Agent': r'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.2.16) Gecko/20110319 Firefox/3.6.1' }
    client = http.client.HTTPSConnection(host, timeout=3)
    client.request('GET', url, headers=headers)
    response = client.getresponse()
    encoding = response.headers.get_content_charset()
    content = response.read().decode(encoding)
    data = parse(content)

    for sentence in data['sentences']:
        print('  ', end=' ')
        if colorama:
            print(colorama.Fore.RED + colorama.Style.BRIGHT, end='')
        print(sentence['translation'], end=' ')
        if 'transliteration' in sentence and sentence['transliteration']:
            if colorama:
                print(colorama.Fore.WHITE + colorama.Style.DIM, end='')
            print('(Transliteration: {0})'.format(sentence['transliteration']), end='')
    if colorama:
        print(colorama.Fore.RESET + colorama.Style.RESET_ALL, end='')
    print()

    if 'dict' in data:
        for dict in sorted(data['dict'], key = lambda x: len(x['entries'])):
            max_importance = max(e['importance'] for e in dict['entries'])
            print()
            print('Dictionary ({0}):'.format(dict['type']) if 'type' in dict and dict['type'] else 'Dictionary:')
            for entry in dict['entries']:
                if colorama:
                    print(colorama.Fore.RED, end='')
                print('  ', end=' ')
                print(entry['word'], end=' ')
                if 'reverse_translation' in entry and entry['reverse_translation']:
                    if colorama:
                        print(colorama.Fore.WHITE + colorama.Style.DIM, end='')
                    print('(Reverse translation: {0})'.format(', '.join(entry['reverse_translation'])))
                    if colorama:
                        print(colorama.Fore.RESET + colorama.Style.RESET_ALL, end='')
    print()
