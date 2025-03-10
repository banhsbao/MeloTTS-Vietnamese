import re
from typing import List

# Vietnamese vowels with diacritics
VIETNAMESE_VOWELS = {
    'a': 'aáàạảã',
    'ă': 'ăắằặẳẵ',
    'â': 'âấầậẩẫ',
    'e': 'eéèẹẻẽ',
    'ê': 'êếềệểễ',
    'i': 'iíìịỉĩ',
    'o': 'oóòọỏõ',
    'ô': 'ôốồộổỗ',
    'ơ': 'ơớờợởỡ',
    'u': 'uúùụủũ',
    'ư': 'ưứừựửữ',
    'y': 'yýỳỵỷỹ'
}

# Vietnamese consonants
VIETNAMESE_CONSONANTS = [
    'b', 'c', 'ch', 'd', 'đ', 'g', 'gh', 'gi', 'h', 'k', 'kh', 
    'l', 'm', 'n', 'ng', 'ngh', 'nh', 'p', 'ph', 'qu', 'r', 's', 
    't', 'th', 'tr', 'v', 'x'
]

# Vietnamese phoneme set
VIETNAMESE_PHONEMES = {
    # Vowels
    'a': 'a', 'á': 'a1', 'à': 'a2', 'ạ': 'a3', 'ả': 'a4', 'ã': 'a5',
    'ă': 'aw', 'ắ': 'aw1', 'ằ': 'aw2', 'ặ': 'aw3', 'ẳ': 'aw4', 'ẵ': 'aw5',
    'â': 'aa', 'ấ': 'aa1', 'ầ': 'aa2', 'ậ': 'aa3', 'ẩ': 'aa4', 'ẫ': 'aa5',
    'e': 'e', 'é': 'e1', 'è': 'e2', 'ẹ': 'e3', 'ẻ': 'e4', 'ẽ': 'e5',
    'ê': 'ee', 'ế': 'ee1', 'ề': 'ee2', 'ệ': 'ee3', 'ể': 'ee4', 'ễ': 'ee5',
    'i': 'i', 'í': 'i1', 'ì': 'i2', 'ị': 'i3', 'ỉ': 'i4', 'ĩ': 'i5',
    'o': 'o', 'ó': 'o1', 'ò': 'o2', 'ọ': 'o3', 'ỏ': 'o4', 'õ': 'o5',
    'ô': 'oo', 'ố': 'oo1', 'ồ': 'oo2', 'ộ': 'oo3', 'ổ': 'oo4', 'ỗ': 'oo5',
    'ơ': 'ow', 'ớ': 'ow1', 'ờ': 'ow2', 'ợ': 'ow3', 'ở': 'ow4', 'ỡ': 'ow5',
    'u': 'u', 'ú': 'u1', 'ù': 'u2', 'ụ': 'u3', 'ủ': 'u4', 'ũ': 'u5',
    'ư': 'uw', 'ứ': 'uw1', 'ừ': 'uw2', 'ự': 'uw3', 'ử': 'uw4', 'ữ': 'uw5',
    'y': 'y', 'ý': 'y1', 'ỳ': 'y2', 'ỵ': 'y3', 'ỷ': 'y4', 'ỹ': 'y5',
    
    # Consonants
    'b': 'b', 'c': 'k', 'ch': 'ch', 'd': 'z', 'đ': 'd',
    'g': 'g', 'gh': 'g', 'gi': 'z', 'h': 'h', 'k': 'k',
    'kh': 'kh', 'l': 'l', 'm': 'm', 'n': 'n', 'ng': 'ng',
    'ngh': 'ng', 'nh': 'nh', 'p': 'p', 'ph': 'f', 'qu': 'kw',
    'r': 'r', 's': 's', 't': 't', 'th': 'th', 'tr': 'ch',
    'v': 'v', 'x': 's'
}

def text_to_phonemes(text: str) -> List[str]:
    """Convert Vietnamese text to phonemes."""
    text = text.lower()
    words = text.split()
    phonemes = []
    
    for word in words:
        # Handle each syllable
        syllables = split_vietnamese_syllables(word)
        for syllable in syllables:
            phoneme_sequence = convert_syllable_to_phonemes(syllable)
            phonemes.extend(phoneme_sequence)
        phonemes.append(' ')
    
    return phonemes[:-1]  # Remove last space

def split_vietnamese_syllables(word: str) -> List[str]:
    """Split a Vietnamese word into syllables."""
    # Basic implementation - can be improved with more complex rules
    return [word]  # For now, treat each word as one syllable

def convert_syllable_to_phonemes(syllable: str) -> List[str]:
    """Convert a Vietnamese syllable to its phoneme sequence."""
    phonemes = []
    
    # Find initial consonant
    initial = ''
    for cons in sorted(VIETNAMESE_CONSONANTS, key=len, reverse=True):
        if syllable.startswith(cons):
            initial = cons
            syllable = syllable[len(cons):]
            break
    
    if initial:
        phonemes.append(VIETNAMESE_PHONEMES[initial])
    
    # Process the remaining part (nucleus + final)
    remaining = syllable
    for char in remaining:
        if char in VIETNAMESE_PHONEMES:
            phonemes.append(VIETNAMESE_PHONEMES[char])
    
    return phonemes

def normalize_vietnamese_text(text: str) -> str:
    """Normalize Vietnamese text for TTS processing."""
    # Convert to lowercase
    text = text.lower()
    
    # Replace common abbreviations and numbers
    text = re.sub(r'\d+', lambda m: num2words(int(m.group()), lang='vi'), text)
    
    # Handle basic punctuation
    text = re.sub(r'[,.!?]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def num2words(num: int, lang='vi') -> str:
    """Convert number to Vietnamese words."""
    # Basic implementation - should be expanded
    units = ['không', 'một', 'hai', 'ba', 'bốn', 'năm', 'sáu', 'bảy', 'tám', 'chín']
    if 0 <= num < 10:
        return units[num]
    return str(num)  # Return as is for now 