# For-If Clauses

# Lexical Analysis
def lexer(s):
    tokens = []
    i = 0
    n = len(s)
    def add_token(token_type, value, pos):
        tokens.append((token_type, value, pos))
    def is_identifier_char(c):
        return c.isalnum() or c == '_'
    operators = {'%', '+', '-', '*', '/', '='}
    builtins = {"range", "len", "set", "list"}
    while i < n:
        c = s[i]
        if c.isspace():
            i += 1
            continue
        if c == '[':
            add_token("[", c, i)
            i += 1
            continue
        elif c == ']':
            add_token("]", c, i)
            i += 1
            continue
        elif c == '(':
            add_token("(", c, i)
            i += 1
            continue
        elif c == ')':
            add_token(")", c, i)
            i += 1
            continue
        elif c == ',':
            add_token(",", c, i)
            i += 1
            continue
        if c == '"':
            start = i
            i += 1
            while i < n and s[i] != '"':
                i += 1
            if i < n:
                i += 1
                add_token("STRING", s[start:i], start)
            else:
                add_token("INVALID", s[start:], start)
            continue
        if c.isdigit():
            start = i
            has_dot = False
            while i < n and (s[i].isdigit() or (s[i] == '.' and not has_dot)):
                if s[i] == '.':
                    has_dot = True
                i += 1
            number = s[start:i]
            if has_dot:
                add_token("DECIMAL", number, start)
            else:
                add_token("INTEGER", number, start)
            continue
        if c.isalpha() or c == '_':
            start = i
            while i < n and is_identifier_char(s[i]):
                i += 1
            word = s[start:i]
            if word == "for":
                add_token("for", word, start)
            elif word == "in":
                add_token("in", word, start)
            elif word == "if":
                add_token("if", word, start)
            elif word in builtins:
                add_token("BUILTIN", word, start)
            else:
                add_token("ID", word, start)
            continue
        if c in operators:
            if c == '=' and (i+1) < n and s[i+1] == '=':
                add_token("OPERATOR", "==", i)
                i += 2
                continue
            else:
                add_token("OPERATOR", c, i)
                i += 1
                continue
        add_token("INVALID", c, i)
        i += 1
    return tokens

tokens = []
currentTokenIndex = 0

def getToken():
    global currentTokenIndex, tokens
    if currentTokenIndex < len(tokens):
        token = tokens[currentTokenIndex]
        currentTokenIndex += 1
        return token
    return ("EOF", "EOF", -1)

def peekToken():
    global currentTokenIndex, tokens
    if currentTokenIndex < len(tokens):
        return tokens[currentTokenIndex]
    return ("EOF", "EOF", -1)

def error(msg, token=None):
    # If token provided, use its input index; otherwise use current pointer.
    index = token[2] if token and len(token) >= 3 else currentTokenIndex
    print(f"Error at input index {index}: {msg}")

# Predictive Recursive Descent Parser
# This parser uses a predictive recursive descent approach to parse the input tokens.
# Parsing Functions

# ListComp → "[" Expression ForClause IfClauseListOpt "]"
def parse_ListComp():
    token = getToken()
    if token[0] != "[":
        error(f"Expected '[' but found {token}", token)
        return False
    if not parse_Expression():
        error("Error in Expression")
        return False
    if not parse_ForClause():
        error("Error in ForClause")
        return False
    if not parse_IfClauseListOpt():
        error("Error in IfClauseListOpt")
        return False
    token = getToken()
    if token[0] != "]":
        error(f"Expected ']' but found {token}", token)
        return False
    return True

# ForClause → "for" Target "in" Expression
def parse_ForClause():
    token = getToken()
    if token[0] != "for":
        error(f"Expected 'for' but found {token}", token)
        return False
    if not parse_Target():
        error("Error in Target")
        return False
    token = getToken()
    if token[0] != "in":
        error(f"Expected 'in' but found {token}", token)
        return False
    if not parse_Expression():
        error("Error in Expression after 'in'")
        return False
    return True

# IfClauseListOpt → IfClause IfClauseListOpt | ε
def parse_IfClauseListOpt():
    token = peekToken()
    if token[0] == "if":
        if not parse_IfClause():
            return False
        if not parse_IfClauseListOpt():
            return False
    return True

# IfClause → "if" Expression
def parse_IfClause():
    token = getToken()
    if token[0] != "if":
        error(f"Expected 'if' but found {token}", token)
        return False
    if not parse_Expression():
        error("Error in Expression after 'if'")
        return False
    return True

# Target → ID
def parse_Target():
    token = getToken()
    if token[0] != "ID":
        error(f"Expected ID but found {token}", token)
        return False
    return True

# Expression → Term ExpressionPrime
def parse_Expression():
    if not parse_Term():
        error("Error in Term")
        return False
    return parse_ExpressionPrime()

# ExpressionPrime → OPERATOR Term ExpressionPrime | ε
def parse_ExpressionPrime():
    token = peekToken()
    if token[0] == "OPERATOR":
        getToken()  # consume operator
        if not parse_Term():
            error("Error in Term after operator", token)
            return False
        return parse_ExpressionPrime()
    return True

# Term → Factor
def parse_Term():
    return parse_Factor()

# Factor → ListComp | (ID | BUILTIN) FunctionCallOpt | INTEGER | DECIMAL | STRING | "(" Expression ")"
def parse_Factor():
    token = peekToken()
    if token[0] == "[":
        return parse_ListComp()  # Nested list comprehension
    if token[0] in ["ID", "BUILTIN"]:
        getToken()  # consume ID or BUILTIN
        if not parse_FunctionCallOpt():
            return False
        return True
    elif token[0] in ["INTEGER", "DECIMAL", "STRING"]:
        getToken()
        return True
    elif token[0] == "(":
        getToken()  # consume "("
        if not parse_Expression():
            return False
        token = getToken()
        if token[0] != ")":
            error(f"Expected ')' but found {token}", token)
            return False
        return True
    else:
        error(f"Unexpected token in Factor: {token}", token)
        return False

# FunctionCallOpt → "(" ArgListOpt ")" | ε
def parse_FunctionCallOpt():
    token = peekToken()
    if token[0] == "(":
        getToken()  # consume "("
        if not parse_ArgListOpt():
            return False
        token = getToken()
        if token[0] != ")":
            error(f"Expected ')' in function call but found {token}", token)
            return False
    return True

# ArgListOpt → Expression ("," Expression)* | ε
def parse_ArgListOpt():
    token = peekToken()
    if token[0] in ["ID", "BUILTIN", "INTEGER", "DECIMAL", "STRING", "(", "["]:
        if not parse_Expression():
            return False
        while True:
            token = peekToken()
            if token[0] == ",":
                getToken()  # consume ","
                if not parse_Expression():
                    return False
            else:
                break
    return True

# Main
if __name__ == "__main__":
    input_str = input()
    tokens = lexer(input_str)
    print("-"*40)
    print("\nTokens:\n")
    for i in tokens:
        print(i)
    print("-"*40)
    print("\nParsing...\n")
    currentTokenIndex = 0
    if parse_ListComp():
        if currentTokenIndex != len(tokens):
            error("Extra Tokens", peekToken())
        else:
            print("Parsed Successfully!")
    else:
        print("Parsing failed.")
