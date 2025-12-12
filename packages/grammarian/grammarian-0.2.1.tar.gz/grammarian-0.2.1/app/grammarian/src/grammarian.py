import ctypes
from importlib import resources
from .utilities import GrammarianException, GrammarianCheck

class Grammarian:
    def __init__(self):
        base_path = resources.files("grammarian.src")
        self.so_path = base_path.joinpath("grammar.so")
        self.file_path = ctypes.c_char_p(str(base_path.joinpath("words_alpha.txt")).encode('utf-8'))
        self.grammar_checker = ctypes.CDLL(self.so_path)
        self.check_word = self.grammar_checker.check_word
        self.check_word.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self.check_word.restype = ctypes.c_bool
        self.seek_corects = self.grammar_checker.seek_corects
        self.seek_corects.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
        self.best_word = self.grammar_checker.best_word
        self.best_word.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self.best_word.restype = ctypes.POINTER(1 * ctypes.c_char_p)
        self.free = self.grammar_checker.free_words

    def check_grammar(self, word : str, size: int = 5)->GrammarianCheck:
            if size > 0:
                self.seek_corects.restype = ctypes.POINTER(size * ctypes.c_char_p)
                self.free.argtypes = [ctypes.POINTER(size * ctypes.c_char_p), ctypes.c_int]

            word = word.replace(" ", "").lower().strip(".,<>/?'\\|=+-_*()&^%$#@![]{}1234567890~`")
            if(len(word) > 46):
                raise GrammarianException("Word given is too long. Grammarian checks words 46 letter long or shorter")
            byte_word = ctypes.c_char_p(word.encode('utf-8'))
            if self.check_word(byte_word, self.file_path):
                return GrammarianCheck(is_correct=True)
            else:
                if size <= 0:
                     return GrammarianCheck(is_correct=False)
                size_c = ctypes.c_int(size)
                suggestions = self.seek_corects(byte_word, self.file_path, size_c)
                response : list[str] = []
                for i in range(size):
                    response.append(suggestions.contents[i].decode('utf-8'))
                self.free(suggestions, size_c)
                return GrammarianCheck(is_correct=False, suggestions=response)
    def quick_swap(self, word : str) -> str:
        word_carved = word.replace(" ", "").lower().strip(".,<>/?'\\|=+-_*()&^%$#@![]{}")
        if(len(word) > 46):
            raise GrammarianException("Word given is too long. Grammarian checks words 46 letter long or shorter")
        byte_word = ctypes.c_char_p(word_carved.encode('utf-8'))
        if self.check_word(byte_word, self.file_path):
            return word
        else:
            self.free.argtypes = [ctypes.POINTER(1 * ctypes.c_char_p), ctypes.c_int]
            response = self.best_word(byte_word, self.file_path)
            word_str = response.contents[0].decode('utf-8')
            self.free(response, 1)
            return word_str
            



