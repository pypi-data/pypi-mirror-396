from .core import extend, combine, consonants, vowels, finals

def _find_in_list(base_list: list, target) -> int:
    for i, obj in enumerate(base_list):
        if obj == target:
            return i
    return -1

def encode(text: str) -> bytes:
    """
    a custom encoding function for korean texts

    example:
    한 -> ㅎㅏㄴ -> 18 0 4 -> b"\\x12\\0\\x04"
    """
    encoded = []
    for char in text:
        extended = extend(char)
        encoded.append(_find_in_list(consonants, extended[0]))
        encoded.append(_find_in_list(vowels, extended[1]))
        if len(extended) == 3:
            encoded.append(_find_in_list(finals, extended[2]))
        else:
            encoded.append(0)
    return bytes(encoded)

def decode(data: bytes) -> str:
    """
    a custom decoding function for korean texts

    example:
    b"\\x12\\0\\x04" -> 18 0 4 -> ㅎㅏㄴ -> 한
    """
    korean_text = ""
    for consonant, vowel, final in [data[i:i + 3] for i in range(0, len(data), 3)]:
        korean_text += combine(
            consonants[consonant] +
            vowels[vowel] +
            finals[final]
        )
    return korean_text