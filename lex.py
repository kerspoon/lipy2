
import string 
import re

test_list = []

specialtokens = set("()'.")
atoms = string.ascii_letters + string.digits + "-_<>%=!^&?*+/"
normalchars = set(atoms)

# -----------------------------------------------------------------------------



def readtoken(text):
    text = text.strip()

    assert len(text) != 0, "invalid input: '" + text + "'"

    if text[0] in specialtokens:
        return text[0], text[1:]

    pattern = re.compile("([()'.]|[\w<>%=!^&?*+/-]+|\"[\w\s<>%=!^&?*+/-]+\")")
    result = pattern.match(text)
    
    assert result, "invalid input: '" + text + "'"
    if result.end() == len(text):
        return result.group(), ""

    return result.group() , text[result.end():]

def readtokens(text):
    res = []
    while len(text) != 0:
        tok, text = readtoken(text)
        res.append(tok)
    return res

def test_readtoken():
    print "testing: readtoken"
    assert readtoken("hello") == ('hello', "")
    # assert readtoken("") == ('', '')
    assert readtoken(atoms) == (atoms, "")
    assert readtoken("  spoone") == ('spoone', "")
    assert readtoken("(as") == ('(', "as")
    assert readtoken(")as") == (')', "as")
    assert readtoken("'as") == ("'", "as")
    assert readtoken("'as'") == ("'", "as'")
    assert readtoken("(hello)") == ("(", "hello)")
test_list.append(test_readtoken)


# -----------------------------------------------------------------------------

def tokenize(iterable):
    if isinstance(iterable,str):
        yield readtokens(iterable)
    else:
        for text in iterable:
            while len(text) != 0:
                tok, text = readtoken(text)
                yield tok

def test_tokenize():
    print "testing: tokenize"
    assert list(tokenize(["'(helloo)  "])) == ["'", '(', 'helloo', ')']
    assert list(tokenize([" ' ( helloo ) "])) == ["'", '(', 'helloo', ')']
test_list.append(test_tokenize)

# -----------------------------------------------------------------------------

for item in test_list:
    item()

# -----------------------------------------------------------------------------


