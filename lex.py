
import string 

test_list = []

specialtokens = set("()'.")
atoms = string.ascii_letters + string.digits + "-_<>%=!^&?*+/"
normalchars = set(atoms)

# -----------------------------------------------------------------------------

def readtoken(input):
    tok = []
    ninput = input.lstrip()
    for x in ninput:
        if x in specialtokens:
            if len(tok) == 0: 
                tok = [x]
            break
        elif x in normalchars:
            tok.append(x)
        elif x in string.whitespace:
            break
        else:
            assert False, "invalid input"
    # assert len(tok) != 0
    ninput = ninput[len(tok):].rstrip()
    text = "".join(tok)
    return (text,ninput)

def test_readtoken():
    print "testing: readtoken"
    assert readtoken("hello") == ('hello', "")
    assert readtoken("") == ('', '')
    assert readtoken(atoms) == (atoms, "")
    assert readtoken("  spoone") == ('spoone', "")
    assert readtoken("(as") == ('(', "as")
    assert readtoken(")as") == (')', "as")
    assert readtoken("'as") == ("'", "as")
    assert readtoken("'as'") == ("'", "as'")
    assert readtoken("(hello)") == ("(", "hello)")
test_list.append(test_readtoken)

# -----------------------------------------------------------------------------

def tokenize(text):
    while len(text) != 0:
        (tok, text) = readtoken(text)
        yield tok

def test_tokenize():
    print "testing: tokenize"
    assert list(tokenize("'(helloo)  ")) == ["'", '(', 'helloo', ')']
    assert list(tokenize(" ' ( helloo ) ")) == ["'", '(', 'helloo', ')']
test_list.append(test_tokenize)

# -----------------------------------------------------------------------------

for item in test_list:
    item()

# -----------------------------------------------------------------------------
