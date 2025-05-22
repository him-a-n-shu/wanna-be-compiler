from collections import deque

# ========== Lexer ==========

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
        if c in '[](),':
            add_token(c, c, i)
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
                if s[i] == '.': has_dot = True
                i += 1
            num = s[start:i]
            add_token("DECIMAL" if has_dot else "INTEGER", num, start)
            continue
        if c.isalpha() or c == '_':
            start = i
            while i < n and is_identifier_char(s[i]):
                i += 1
            word = s[start:i]
            if word in {"for","in","if"}:
                add_token(word, word, start)
            elif word in builtins:
                add_token("BUILTIN", word, start)
            else:
                add_token("ID", word, start)
            continue
        if c in operators:
            if c == '=' and i+1<n and s[i+1]=='=':
                add_token("OPERATOR", "==", i)
                i += 2
            else:
                add_token("OPERATOR", c, i)
                i += 1
            continue
        add_token("INVALID", c, i)
        i += 1
    tokens.append(("$", "$", n))
    return tokens

# ========== Grammar Definition ==========

grammar = {
    'ListComp': [['[', 'Expression', 'ForClause', 'IfClauseListOpt', ']']],
    'ForClause': [['for', 'Target', 'in', 'Expression']],
    'IfClauseListOpt': [['IfClause', 'IfClauseListOpt'], []],
    'IfClause': [['if', 'Expression']],
    'Target': [['ID']],
    'Expression': [['Term', 'ExpressionPrime']],
    'ExpressionPrime': [['OPERATOR', 'Term', 'ExpressionPrime'], []],
    'Term': [['Factor']],
    'Factor': [['ID', 'FunctionCallOpt'], ['BUILTIN', 'FunctionCallOpt'], ['INTEGER'], ['DECIMAL'], ['STRING'], ['(', 'Expression', ')']],
    'FunctionCallOpt': [['(', 'ArgListOpt', ')'], []],
    'ArgListOpt': [['Expression', 'ArgListPrime'], []],
    'ArgListPrime': [[',', 'Expression', 'ArgListPrime'], []],
}

# ========== LL(1) Parsing Table ==========
parsing_table = {
    'ListComp': {'[': grammar['ListComp'][0]},
    'ForClause': {'for': grammar['ForClause'][0]},
    'IfClauseListOpt': {'if': grammar['IfClauseListOpt'][0], ']': grammar['IfClauseListOpt'][1]},
    'IfClause': {'if': grammar['IfClause'][0]},
    'Target': {'ID': grammar['Target'][0]},
    'Expression': {t: grammar['Expression'][0] for t in ['ID', 'BUILTIN', 'INTEGER', 'DECIMAL', 'STRING', '(']},
    'ExpressionPrime': {'OPERATOR': grammar['ExpressionPrime'][0], **{t: grammar['ExpressionPrime'][1] for t in ['for','if',']',')',',','$']}},
    'Term': {t: grammar['Term'][0] for t in ['ID', 'BUILTIN', 'INTEGER', 'DECIMAL', 'STRING', '(']},
    'Factor': {
        'ID': grammar['Factor'][0], 'BUILTIN': grammar['Factor'][1],
        'INTEGER': grammar['Factor'][2], 'DECIMAL': grammar['Factor'][3],
        'STRING': grammar['Factor'][4], '(': grammar['Factor'][5]
    },
    'FunctionCallOpt': {'(': grammar['FunctionCallOpt'][0], **{t: grammar['FunctionCallOpt'][1] for t in ['OPERATOR','for','if',']',')',',','$']}},
    'ArgListOpt': {**{t: grammar['ArgListOpt'][0] for t in ['ID','BUILTIN','INTEGER','DECIMAL','STRING','(']}, ')': grammar['ArgListOpt'][1]},
    'ArgListPrime': {',': grammar['ArgListPrime'][0], ')': grammar['ArgListPrime'][1]},
}

# ========== Parser ==========

def parse(tokens):
    stack = deque()
    stack.append('$')
    stack.append('ListComp')
    index = 0

    while stack:
        top = stack.pop()
        current_token = tokens[index]
        tok_type = current_token[0]

        # Accept
        if top == tok_type == '$':
            return True

        # Non-terminal
        if top in parsing_table:
            entry = parsing_table[top].get(tok_type)
            if entry is None:
                print(f"Syntax error: no rule for {top} on lookahead '{tok_type}'")
                return False
            for sym in reversed(entry):
                if sym:
                    stack.append(sym)
        else:
            # Terminal
            if top == tok_type:
                index += 1
            else:
                print(f"Syntax error: expected '{top}' but found '{tok_type}'")
                return False
    return False

# ========== Main ==========
text = input()
tokens = lexer(text)
print("-"*40)
print("Tokens:")
for i in tokens:
    print(i)
print("-"*40)
print("Parsing...")
if parse(tokens):
    print("Input parsed successfully.")
else:
    print("Parsing failed.")
