from bs4 import BeautifulSoup
import os
from lxml.etree import Element, SubElement, tostring

class Vocab:
    def __init__(self, english, german, hint):
        self.english = english
        self.german = german
        self.hint = hint

    def __repr__(self):
        return '{} | {} | {}'.format(self.english[0], self.german[0], self.hint)

class Unit:
    def __init__(self, name):
        self.name = name
        self.vocabs = []

def read_unit_file(filename):
    with open(filename) as fp:
        soup = BeautifulSoup(fp, 'html.parser')
        unit = None

        vocabs = soup.find_all('row')
        for vocab in vocabs:
            # title of unit
            if unit is None and len(list(vocab.children)) == 3:
                filename_unit = os.path.basename(filename)
                splitinfo = filename_unit.split('_')
                chapter = splitinfo[1].upper()
                number = splitinfo[2]
                title = vocab.find_all('entry')[0].string.strip()
                name = '{}|{} - {}'.format(chapter, number, title)
                unit = Unit(name)
            # 3 elements and 4 line feeds
            if len(list(vocab.children)) == 7:
                entries = vocab.find_all('entry')
                if not 'Word/phrase' in entries[0].string:
                    # split to extract second meanings
                    english = entries[0].string.strip().split('; ')
                    german = entries[1].string.strip().split('; ')
                    hint = entries[2].string.strip()
                    voc = Vocab(english, german, hint)
                    unit.vocabs.append(voc)
    return unit

# read all units

# dir which contains xml files generated from doc files
path = 'xml'
units = []
for root, dirs, files in os.walk(path):
   for filename in files:
      unit = read_unit_file(os.path.join(root, filename))
      units.append(unit)

# generate xml
xml = Element('units')
for unit in units:
    unit_xml = SubElement(xml, 'unit')
    title_xml = SubElement(unit_xml, 'title')
    title_xml.text = unit.name

    vocables_xml = SubElement(unit_xml, 'vocables')
    for vocab in unit.vocabs:
        vocab_xml = SubElement(vocables_xml, 'vocable')

        first_meaning_xml = SubElement(vocab_xml, 'first_meaning')
        for meaning in vocab.german:
            meaning_xml = SubElement(first_meaning_xml, 'value')
            meaning_xml.text = meaning

        second_meaning_xml = SubElement(vocab_xml, 'second_meaning')
        for meaning in vocab.english:
            meaning_xml = SubElement(second_meaning_xml, 'value')
            meaning_xml.text = meaning

        # hint = SubElement(vocab_xml, 'hint')
        # hint.text = vocab.hint

xml_doc = tostring(xml, pretty_print=True).decode('utf-8')
xml_doc = """<?xml version='1.0' encoding='UTF-16' standalone='yes'?>\n""" + xml_doc

with open('vocab.xml', 'w') as file:
    file.write(xml_doc)
