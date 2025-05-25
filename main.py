class Automaton:
    def __init__(self, transitions, accept_states):
        self.transitions = transitions
        self.accept_states = accept_states

        # Incluimos también destinos al calcular estados
        max_state = max(max(frm, to) for frm, to, _ in transitions)
        self.states = {i: {} for i in range(max_state + 1)}
        self.start_state = 0
        self._build_transitions(transitions)

    def _build_transitions(self, transitions):
        for from_state, to_state, symbol in transitions:
            self.states[from_state][symbol] = to_state

    def print_transitions(self):
        print("transitions = [")
        for frm, to, sym in self.transitions:
            print(f"    ({frm}, {to}, '{sym}'),")
        print("]")
        print(f"accept_states = {self.accept_states}\n")

    def process_tokens(self, input_text):
        tokens = []
        state = self.start_state
        buffer = ""
        last_token = None
        i = 0
        n = len(input_text)

        while i < n:
            c = input_text[i]

            # 0) Antes de todo, comprobamos si 'c' es un delimitador
            #     (operador, paréntesis, signo o cualquier no alfanumérico)
            #     Si buffer NO está vacío y estamos en estado de aceptación,
            #     volcamos buffer como token.
            #     (Lo de delimitador se refiere a que no es parte de un identificador o número)
            is_special = c in "+-*/=()"
            if is_special and buffer and state in self.accept_states:
                tokens.append('id' if state == ID_STATE else 'num')
                last_token = tokens[-1]
                buffer = ""
                state = self.start_state
                # NO return o continue, dejamos que el mismo 'c' se procese
                # como operador, paréntesis o signo abajo
                # De este modo solamente se me ocurre garantizar que SI esta dentro de un estado de aceptación
                # (Realmente todo lo esta, a excepción del estado 0, es gracioso jajajaja)

            # 1) espacios: simplemente los ignoramos
            if c.isspace():
                i += 1
                continue

            # 2) '+' / '-' → signo o operador
            if c in "+-":
                nxt = input_text[i+1] if i+1 < n else ""
                is_sign = last_token in (None, 'op', 'paren_open') and nxt.isdigit()
                if is_sign:
                    category = c  # lo trataremos como parte del número
                else:
                    tokens.append(c)
                    last_token = 'op'
                    i += 1
                    continue

            # 3) operadores puros */=
            elif c in "*/=":
                tokens.append(c)
                last_token = 'op'
                i += 1
                continue

            # 4) paréntesis
            elif c in "()":
                tokens.append(c)
                last_token = 'paren_open' if c == '(' else 'paren_close'
                i += 1
                continue

            # 5) letras y dígitos → categorías para la tabla
            elif c.isalpha():
                category = 'char'
            elif c.isdigit():
                category = 'num'

            # 6) Si llegamos aquí, intentamos transición en autómata
            if category in self.states[state]:
                state = self.states[state][category]
                buffer += c
                i += 1
            else:
                # si no hay transición válida, volvemos a reiniciar
                buffer = ""
                state = self.start_state
                # NO incrementamos i para reintentar con el mismo carácter

        # 7) al final volcamos lo que quede en buffer
        if buffer and state in self.accept_states:
            tokens.append('id' if state == ID_STATE else 'num')

        return tokens
    
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self, expected=None):
        tok = self.peek()
        if expected and tok != expected:
            raise SyntaxError(f"Se esperaba '{expected}', encontrado '{tok}'")
        self.pos += 1
        return tok

    def parse_S(self):
        if self.peek() != 'id':
            raise SyntaxError("S debe comenzar con identificador")
        self.consume('id')
        self.consume('=')
        self.parse_E()
        if self.pos != len(self.tokens) and self.peek() == ')':
            raise SyntaxError("Parentesis desbalanceados")
        if self.pos != len(self.tokens):
            raise SyntaxError("Hay tokens que no se pudieron consumir")
    def parse_E(self):
        self.parse_T()
        while self.peek() in ('+', '-'):
            self.consume()
            self.parse_T()

    def parse_T(self):
        self.parse_F()
        while self.peek() in ('*', '/'):
            self.consume()
            self.parse_F()

    def parse_F(self):
        tok = self.peek()
        if tok == 'id' or tok == 'num':
            self.consume()
            return
        if tok == '(':
            self.consume('(')
            self.parse_E()
            self.consume(')')
            return
        raise SyntaxError(f"Se esperaba id, num o '(', encontrado '{tok}'")

transitions = [
    (3, 4, '+'),
    (3, 4, '-'),
    (5, 5, 'num'),
    (0, 6, 'num'),
    (5, 5, 'char'),
    (0, 1, '/'),
    (6, 8, '+'),
    (5, 5, 'char'),
    (0, 1, '*'),
    (6, 8, '-'),
    (0, 2, '('),
    (5, 9, '+'),
    (7, 6, 'num'),
    (0, 5, 'char'),
    (5, 9, '-'),
    (0, 5, 'char'),
    (0, 1, '='),
    (0, 7, '+'),
    (0, 7, '-'),
    (0, 3, ')')
]

# Nombres de estados clave
ID_STATE   = 5   # identificadores
NUM_STATE  = 6   # número sin signo
SIGN_STATE = 7   # signo '+' o '-'
accept_states = {1, 2, 3, 4, 5, 6, 7, 8, 9}

# Se crea el autómata
automaton = Automaton(transitions, accept_states)

text = input("Enter input text: ")
tokens = automaton.process_tokens(text)
print("Tokens:", tokens)
parser = Parser(tokens)
try:
    parser.parse_S()
    print("Aceptado")
except SyntaxError as e:
    print('sintax error:', e)