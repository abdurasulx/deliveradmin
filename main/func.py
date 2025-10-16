from latinUzConverter.core import LatinUzConverter
conv = LatinUzConverter()
def transliterate_to_krill(text):
    return conv.transliterate(text,'cyrillic')
def transliterate_to_latin(text):
    return conv.transliterate(text,'latin')