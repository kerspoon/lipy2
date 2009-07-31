
import re
import objects
import string

test_list = []

# -----------------------------------------------------------------------------

re_num = re.compile(r"^[-+]?\d+$")
normalchars = set(string.ascii_letters + string.digits + "-_<>%=!^&?*+/")

def isnumber(str):
    return re_num.match(str) != None

def test_isnumber():
    print "testing: isnumber"
    assert isnumber("0")
    assert isnumber("1")
    assert isnumber("10")
    assert isnumber("0001")
    assert isnumber("01234567890")
    assert isnumber("+0")
    assert isnumber("+1")
    assert isnumber("+10")
    assert isnumber("+0001")
    assert isnumber("+01234567890")
    assert isnumber("-0")
    assert isnumber("-1")
    assert isnumber("-10")
    assert isnumber("-0001")
    assert isnumber("-01234567890")
    assert False == isnumber("")
    assert False == isnumber("--1")
    assert False == isnumber("_5")
    assert False == isnumber("asdf")
    assert False == isnumber("5a")
    assert False == isnumber("a5")
    assert False == isnumber("5a5")
    assert False == isnumber("a5a")
    assert False == isnumber("+a1")
    assert False == isnumber("+9a")
    assert False == isnumber("-9a")
    assert False == isnumber("-a3")
    assert False == isnumber("-10+")
test_list.append(test_isnumber)

# -----------------------------------------------------------------------------

def parse(tokens):
    """take the token list from the lexer and make it into an object"""
    # might be nice to treat tokens as a generator 
    # we could then run the lexer and parser in almost parallel
    # change tokens[0] to tokens.pop() and tokens[1:] to tokens
    # would take a bit of rearanging too

    first_tok = tokens.next()
    
    assert len(first_tok) != 0, "zero sized token"
    assert first_tok != ".", "found '.' outside of pair"
    assert first_tok != ")", "found ')' mismatched bracket"

    if first_tok == "'":
        return (QUOTE, (parse(tokens), NIL))
    elif first_tok == "(":
        sec_tok = parse(tokens)
        if sec_tok == ")":
            return NIL
        elif sec_tok == ".":
            return (sec_tok, parse(tokens))
        else:
            ...


    if first_tok == "(":
        # we either have a pair or list or nil
        # deal with nil first 
        if tokens[1] == ")":
            return objects.nil, tokens[2:]
        # now we have a list or pair
        # either way parse the first element
        car, tokens = parse(tokens[1:])
        if tokens[0] == ".":
            # we have a pair
            # parse the second element
            cdr, tokens = parse(tokens[1:])
            # check the close bracket
            assert tokens[0] == ")", "missing cdr of pair"
            # make the final object
            obj = objects.pair(car,cdr)
        else:
            # we have a list
            list = [car]
            # grab each element and store as a list
            # tokens = tokens[1:]
            while tokens[0] != ")":
                cdr, tokens = parse(tokens)
                list.append(cdr)
            # then in reverse put each element into a pair
            obj = objects.pair(list.pop(),objects.nil)
            for item in reversed(list):
                obj = objects.pair(item,obj)

        # return both the object and the remaining tokens
        return obj, tokens[1:]
    elif tokens[0] == "'":
        # we have a quote
        # reader tranform: 'obj to (quote obj)
        # grab the next element
        obj, tokens = parse(tokens[1:])
        # make the new form
        obj = objects.pair(obj,objects.nil)
        return objects.pair(objects.mksym("quote"),obj), tokens
    else:
        # we have a symbol or a number
        if isnumber(tokens[0]):
            return objects.number(int(tokens[0])) , tokens[1:]
        # we must be left with a symbol 
        # just check that is is only made of valid chars
        assert set(tokens[0]).issubset(normalchars), "Invalid atom in symbol"
        return objects.mksym(tokens[0]) , tokens[1:]

def test_parse():
    print "testing: parse"
    n5 = objects.number(5)
    s1 = objects.mksym("spoon")
    s2 = objects.mksym("boop")
    j1 = objects.pair(s1,objects.pair(s2,objects.nil))
    assert parse(["(", ")"]) == (objects.nil , [])
    assert parse(["spoon"]) == (s1 , [])
    assert parse(["5"]) == (n5 , [])
    assert parse(["(", "spoon", ".", "boop", ")"]) == (objects.pair(s1,s2), [])
    assert parse(["(", "spoon", "boop", ")"]) == (j1, [])
test_list.append(test_parse)

# -----------------------------------------------------------------------------

for item in test_list:
    item()

# -----------------------------------------------------------------------------

