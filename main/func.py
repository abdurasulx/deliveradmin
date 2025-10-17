from latinUzConverter.core import LatinUzConverter

conv = LatinUzConverter()

def transliterate_to_krill(text):
    if not text:  # None yoki bo‘sh string bo‘lsa
        return ""
    try:
        return conv.transliterate(text, 'cyrillic')
    except Exception as e:
        print(f"Transliteration to Cyrillic failed: {e}")
        return text  # xato bo‘lsa asl matnni qaytaradi

def transliterate_to_latin(text):
    if not text:
        return ""
    try:
        return conv.transliterate(text, 'latin')
    except Exception as e:
        print(f"Transliteration to Latin failed: {e}")
        return text
