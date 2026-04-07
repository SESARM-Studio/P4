# This file was generated on Tue Apr 7, 2026 14:21 (UTC+02) by REx v6.2-SNAPSHOT which is Copyright (c) 1979-2025 by Gunther Rademacher <grd@gmx.net>
# REx command line: -python -main -tree -lalr 1 martin.ebnf

import sys
from tree import *

class martin:

  class ParseException(Exception):

    def __init__(self, b, e, s, o, x):
      self.begin = b
      self.end = e
      self.state = s
      self.offending = o
      self.expected = x

    def error(self):
      if self.offending < 0:
        return "lexical analysis failed"
      else:
        return "syntax error"

    def serialize(self, eventHandler):
      pass

    def getBegin(self):
      return self.begin

    def getEnd(self):
      return self.end

    def getState(self):
      return self.state

    def getOffending(self):
      return self.offending

    def getExpected(self):
      return self.expected

    def isAmbiguousInput(self):
      return False

  class TopDownTreeBuilder:

    def reset(self, inputString):
      self.input = inputString
      self.stack = []
      self.top = -1

    def startNonterminal(self, name, begin):
      nonterminal = martin.Nonterminal(name, begin, begin)
      if self.top >= 0:
        self.addChild(nonterminal)
      self.top += 1
      self.stack[self.top] = nonterminal

    def endNonterminal(self, _, end):
      self.stack[self.top].end = end
      if self.top > 0:
        self.top -= 1

    def terminal(self, name, begin, end):
      self.addChild(martin.Terminal(name, begin, end))

    def whitespace(self, begin, end):
      pass

    def addChild(self, s):
      current = self.stack[self.top]
      current.addChild(s)

    def serialize(self, e):
      e.reset(self.input)
      self.stack[0].send(e)

  class Symbol:

    def __init__(self, name, begin, end):
      self.name = name
      self.begin = begin
      self.end = end

    def getName(self):
      return self.name

    def getBegin(self):
      return self.begin

    def getEnd(self):
      return self.end

  class Nonterminal(Symbol):

    def __init__(self, name, begin, end, children):
      super().__init__(name, begin, end)
      self.children = children

    def addChild(self, s):
      self.children = self.children.append(s)

    def send(self, e):
      e.startNonterminal(self.getName(), self.getBegin())
      pos = self.getBegin()
      for c in self.children:
        if pos < c.getBegin():
          e.whitespace(pos, c.getBegin())
        c.send(e)
        pos = c.getEnd()
      if pos < self.getEnd():
        e.whitespace(pos, self.getEnd())
      e.endNonterminal(self.getName(), self.getEnd())

  class Terminal(Symbol):

    def __init__(self, name, begin, end):
      super().__init__(name, begin, end)

    def send(self, e):
      e.terminal(self.getName(), self.getBegin(), self.getEnd())

  class XmlSerializer:

    def reset(self, inputString):
      sys.stdout.reconfigure(encoding="utf-8")
      print("<?xml version=\"1.0\" encoding=\"UTF-8\"?>", end="")
      self.input = inputString
      self.delayedTag = None
      self.hasChildElement = False
      self.depth = 0

    def startNonterminal(self, tag, _):
      if self.delayedTag != None:
        print("<", end="")
        print(self.delayedTag, end="")
        print(">", end="")
      self.delayedTag = tag
      if self.indent:
        print()
        for _ in range(self.depth):
          print("  ", end="")
      self.hasChildElement = False
      self.depth += 1

    def endNonterminal(self, tag, _):
      self.depth -= 1
      if self.delayedTag != None:
        self.delayedTag = None
        print("<", end="")
        print(tag, end="")
        print("/>", end="")
      else:
        if self.indent:
          if self.hasChildElement:
            print()
            for _ in range(self.depth):
              print("  ", end="")
        print("</", end="")
        print(tag, end="")
        print(">", end="")
      self.hasChildElement = True

    def whitespace(self, b, e):
      self.characters(b, e)

    def characters(self, b, e):
      if b < e:
        if self.delayedTag != None:
          print("<", end="")
          print(self.delayedTag, end="")
          print(">", end="")
          self.delayedTag = None
        i = b
        while i < e:
          c = self.input[i]
          i += 1
          if c == '&':
            print("&amp;", end="")
          elif c == '<':
            print("&lt;", end="")
          elif c == '>':
            print("&gt;", end="")
          else:
            print(str(c), end="")

    def terminal(self, tag, b, e):
      if tag[0] == '\'':
        tag = "TOKEN"
      self.startNonterminal(tag, b)
      self.characters(b, e)
      self.endNonterminal(tag, e)

  class ParseTreeBuilder:

    def reset(self, inputString):
        self.input = inputString

        # parse tree (unchanged)
        self.stack = []

        # AST
        self.ast_stack = []
        self.ast_root = None
        
    # ---------------- TERMINALS ----------------

    def terminal(self, name, begin, end):
        # ----- original parse tree -----
        term = martin.Terminal(name, begin, end)
        self.push(term)

        # ----- AST -----
        text = self.characters(begin, end)

        # literals
        if name == "Number":
            node = ASTNode("Number", value=text)

        # operators / parentheses
        else:
            node = ASTNode(text)

        self.ast_stack.append(node)


    # ---------------- NONTERMINALS ----------------
    def nonterminal(self, name, begin, end, count):

    # ----- keep original parse tree -----
      children = self.pop(count)
      self.push(martin.Nonterminal(name, begin, end, children))

      # ----- AST children -----
      ast_children = self.ast_stack[-count:] if count else []
      if count:
          self.ast_stack = self.ast_stack[:-count]

      # -------------------------------------
      # REMOVE GRAMMAR STRUCTURE
      # -------------------------------------
      if name in ("Expression", "Term", "Factor", "Primary"):

          # ---------- ( Expr ) ----------
          if (
              len(ast_children) == 3
              and ast_children[0].kind == "("
              and ast_children[2].kind == ")"
          ):
              node = ast_children[1]
              self.ast_stack.append(node)
              self.ast_root = node
              return

          # ---------- single child ----------
          if len(ast_children) == 1:
              node = ast_children[0]
              self.ast_stack.append(node)
              self.ast_root = node
              return

          # ---------- operator chain ----------
          # Example:
          # [A, *, B, *, C, *, D]
          if len(ast_children) >= 3:

              node = ast_children[0]
              i = 1

              while i < len(ast_children):
                  op = ast_children[i]
                  right = ast_children[i + 1]

                  if op.kind in {"+", "-", "*", "/"}:
                      op.children = [node, right]
                      node.parent = op
                      right.parent = op
                      node = op

                  i += 2

              self.ast_stack.append(node)
              self.ast_root = node
              return

      # fallback (rare)
      node = ASTNode(name, ast_children)
      self.ast_stack.append(node)
      self.ast_root = node

    # ---------------- SERIALIZATION ----------------

    def serialize(self, e):
        e.reset(self.input)
        for symbol in self.stack:
            symbol.send(e)


    # ---------------- HELPERS ----------------

    def characters(self, b, e):
        return self.input[b:e]

    def push(self, s):
        self.stack.append(s)

    def pop(self, count):
        if count == 0:
            return []
        result = self.stack[-count:]
        self.stack = self.stack[:-count]
        return result

  def __init__(self, inputString, t):
    self.initialize(inputString, t)

  def initialize(self, source, parsingEventHandler):
    self.eventHandler = parsingEventHandler
    self.input = source
    self.size = len(source)
    self.iStack = [0 for _ in range(192)]
    self.reset(0, 0, 0)

  def getInput(self):
    return self.input

  def getTokenOffset(self):
    return self.b0

  def getTokenEnd(self):
    return self.e0

  def reset(self, l, b, e):
    self.b0 = b; self.e0 = b
    self.l1 = l; self.b1 = b; self.e1 = e
    self.end = e
    self.eventHandler.reset(self.input)

  @staticmethod
  def getOffendingToken(e):
    if e.getOffending() < 0:
      return ""
    else:
      return martin.TOKEN[e.getOffending()]

  @staticmethod
  def getExpectedTokenSet(e):
    if e.expected < 0:
      return martin.getTokenSet(- e.state)
    else:
      return [martin.TOKEN[e.expected]]

  def getErrorMessage(self, e):
    message = e.error()
    found = martin.getOffendingToken(e)
    if found != "":
      message += ", found "
      message += found
    expected = martin.getExpectedTokenSet(e)
    message += "\nwhile expecting "
    delimiter = ""
    if len(expected) != 1:
      delimiter = "["
    for token in expected:
      message += delimiter
      message += token
      delimiter = ", "
    if len(expected) != 1:
      message += "]"
    message += "\n"
    size = e.getEnd() - e.getBegin()
    if size != 0 and found == "":
      message += "after successfully scanning "
      message += str(size)
      message += " characters beginning "
    line = 1
    column = 1
    for i in range(e.getBegin()):
      if self.input[i] == '\n':
        line += 1
        column = 1
      else:
        column += 1
    message += "at line "
    message += str(line)
    message += ", column "
    message += str(column)
    message += ":\n..."
    end = e.getBegin() + 64
    if end > len(self.input):
      end = len(self.input)
    message += self.input[e.getBegin() : end]
    message += "..."
    return message

  def parse_Expression(self):
    self.top = -1
    self.parse(0, 0, self.eventHandler)

  def push(self, state, lookback, begin):
    self.top += 3
    if self.top >= len(self.iStack):
      self.iStack.extend([0 for _ in range(len(self.iStack))])
    self.iStack[self.top - 2] = begin
    self.iStack[self.top - 1] = state
    self.iStack[self.top] = lookback

  def lookback(self, x, y):
    i = martin.LOOKBACK[y]
    l = martin.LOOKBACK[i]
    while l > x:
      i += 2
      l = martin.LOOKBACK[i]
    if l < x:
      return 0
    else:
      return martin.LOOKBACK[i + 1]

  def count(self, code):
    count = 0
    t = self.top
    while t >= 0:
      code = self.lookback(self.iStack[t], code)
      if code == 0:
        break
      count += 1
      t -= 3
    return count

  def parse(self, target, initialState, eventHandler):
    state = initialState
    bw = self.e0
    bs = self.e0
    es = self.e0
    t = self.top
    action = self.predict(state)
    nonterminalId = -1
    while True:
      argument = action >> 9
      lookback = (action >> 3) & 63
      shift = -1
      reduce = -1
      symbols = -1
      action &= 7
      if action == 1: # SHIFT
        shift = argument

      elif action == 2: # REDUCE
        reduce = argument
        symbols = lookback

      elif action == 3: # REDUCE+LOOKBACK
        reduce = argument
        symbols = self.count(lookback)

      elif action == 4: # SHIFT+REDUCE
        shift = state
        reduce = argument
        symbols = lookback + 1

      elif action == 5: # SHIFT+REDUCE+LOOKBACK
        shift = state
        reduce = argument
        symbols = self.count(lookback) + 1

      elif action == 6: # ACCEPT
        return

      else: # ERROR
        raise martin.ParseException(self.b1, self.e1, martin.TOKENSET[state] + 1, self.l1, -1)

      if shift >= 0:
        if nonterminalId < 0:
          if eventHandler != None:
            eventHandler.terminal(martin.TOKEN[self.l1], self.b1, self.e1)
          es = self.e1
          self.push(state, lookback, self.b1)
          self.consume(self.l1)
        else:
          self.push(state, lookback, bs)
        state = shift

      if reduce < 0:
        action = self.predict(state)
        nonterminalId = -1
      else:
        nonterminalId = reduce
        if symbols > 0:
          self.top -= symbols * 3
          state = self.iStack[self.top + 2]
          bs = self.iStack[self.top + 1]
        else:
          bs = self.b1
          es = self.b1
        if nonterminalId == target and t == self.top:
          bs = bw
          es = self.b1
          bw = self.b1
        if eventHandler != None:
          eventHandler.nonterminal(martin.NONTERMINAL[nonterminalId], bs, es, symbols)
        action = martin.goTo(nonterminalId, state)

  def consume(self, t):
    if self.l1 == t:
      self.b0 = self.b1; self.e0 = self.e1; self.l1 = 0
    else:
      self.error(self.b1, self.e1, 0, self.l1, t)

  def matchW(self, tokenSetId):
    while True:
      code = self.match(tokenSetId)
      if code != 1:                 # Whitespace
        break
    return code

  def error(self, b, e, s, l, t):
    raise martin.ParseException(b, e, s, l, t)

  def predict(self, dpi):
    d = dpi
    if self.l1 == 0:
      self.l1 = self.matchW(martin.TOKENSET[d])
      self.b1 = self.begin
      self.e1 = self.end
    j10 = (d << 4) + self.l1
    j11 = j10 >> 2
    action = martin.CASEID[(j10 & 3) + martin.CASEID[(j11 & 3) + martin.CASEID[j11 >> 2]]]
    return action >> 1

  def match(self, tokenSetId):
    self.begin = self.end
    current = self.end
    result = martin.INITIAL[tokenSetId]
    state = 0

    code = result & 7
    while code != 0:
      if current < self.size:
        c0 = ord(self.input[current])
      else:
        c0 = 0
      current += 1
      if c0 < 0x80:
        charclass = martin.MAP0[c0]
      elif c0 < 0xd800:
        c1 = c0 >> 5
        charclass = martin.MAP1[(c0 & 31) + martin.MAP1[(c1 & 31) + martin.MAP1[c1 >> 5]]]
      else:
        charclass = 0

      state = code
      i0 = (charclass << 3) + code - 1
      code = martin.TRANSITION[(i0 & 1) + martin.TRANSITION[i0 >> 1]]
      if code > 7:
        result = code
        code &= 7
        self.end = current

    result >>= 3
    if result == 0:
      self.end = current - 1
      return self.error(self.begin, self.end, state, -1, -1)

    if self.end > self.size:
      self.end = self.size
    return (result & 15) - 1

  @staticmethod
  def goTo(nonterminalId, state):
    i0 = (state << 3) + nonterminalId
    return martin.GOTO[(i0 & 3) + martin.GOTO[i0 >> 2]]

  @staticmethod
  def getTokenSet(tokenSetId):
    if tokenSetId < 0:
      s = - tokenSetId
    else:
      s = martin.INITIAL[tokenSetId] & 7
    tokenSet = []
    size = 0
    for i in range(0, 10, 32):
      j = i
      i0 = (i >> 5) * 7 + s - 1
      f = martin.EXPECTED[i0]
      while f != 0:
        if (f & 1) != 0:
          tokenSet.append(martin.TOKEN[j])
          size += 1
        j += 1
        f = (f >> 1) & 0x7fffffff
    return tokenSet

  MAP0 = [                                                                                                         #   0
    0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, #  37
    0, 0, 0, 1, 2, 3, 4, 0, 5, 0, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, #  74
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, # 111
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

  MAP1 = [                                                                                                         #   0
    54, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56,    #  27
    56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56,    #  54
    114, 88, 125, 125, 125, 125, 125, 125, 125, 125, 125, 125, 125, 125, 125, 125, 125, 125, 125, 125, 125, 125,   #  76
    125, 125, 125, 125, 125, 125, 125, 125, 125, 125, 125, 125, 8, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 0, 5, 0, 6, 7, # 105
    7, 7, 7, 7, 7, 7, 7, 7, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, # 142
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

  INITIAL = [                                                                                                      #   0
    1, 2, 59, 4, 61]

  TRANSITION = [                                                                                                   #   0
    37, 37, 37, 37, 40, 40, 37, 37, 36, 36, 36, 37, 37, 37, 42, 37, 37, 44, 45, 37, 37, 47, 48, 37, 37, 37, 50,    #  27
    37, 38, 38, 37, 39, 52, 52, 52, 37, 64, 0, 0, 31, 0, 32, 72, 0, 40, 40, 0, 48, 48, 0, 80, 0, 22, 22]

  EXPECTED = [                                                                                                     #   0
    130, 14, 178, 62, 946, 2, 4]

  CASEID = [                                                                                                       #   0
    8, 21, 8, 8, 8, 14, 17, 11, 42, 25, 27, 27, 28, 27, 27, 32, 27, 27, 36, 40, 27, 42, 27, 27, 27, 1410, 1426, 0, #  28
    0, 0, 0, 3112, 3186, 3202, 102, 102, 1302, 1302, 1302, 1302, 4386, 4402, 0, 0, 3080, 2066]

  TOKENSET = [                                                                                                     #   0
    3, 1, 3, 3, 3, 2, 4, 0]

  LOOKBACK = [                                                                                                     #   0
    32, 32, 32, 32, 32, 32, 28, 33, 38, 43, 43, 43, 43, 32, 32, 32, 32, 48, 53, 58, 63, 63, 63, 63, 32, 32, 68,    #  27
    73, 10, 9, 3, 2, 0, 10, 11, 3, 4, 0, 10, 12, 3, 5, 0, 8, 8, 7, 7, 0, 21, 20, 14, 13, 0, 21, 22, 14, 15, 0, 21, #  59
    23, 14, 16, 0, 19, 19, 18, 18, 0, 25, 25, 24, 24, 0, 26, 26, 0]

  GOTO = [                                                                                                         #   0
    10, 14, 15, 14, 19, 14, 23, 14, 27, 14, 6, 2585, 3185, 1237, 0, 0, 0, 0, 1237, 3593, 2585, 3185, 1237, 0,      #  24
    2641, 3185, 1237, 0, 0, 3241, 1237]

  TOKEN = [
      "%ERROR",
      "Whitespace",
      "Number",
      "'('",
      "'+'",
      "'-'",
      "%OTHER",
      "')'",
      "'*'",
      "'/'"]

  NONTERMINAL = [
      "Expression",
      "Term",
      "Factor",
      "Primary"]

def read(arg):
  if arg.startswith("{") and arg.endswith("}"):
    return arg[1:len(arg) - 1]
  else:
    with open(arg, "r", encoding="utf-8") as file:
      content = file.read()
    if len(content) > 0 and content[0] == "\ufeff":
      content = content[1:]
    return content

def main(args):
  if len(args) < 2:
    sys.stderr.write("Usage: python martin.py [-i] INPUT...\n")
    sys.stderr.write("\n")
    sys.stderr.write("  parse INPUT, which is either a filename or literal text enclosed in curly braces\n")
    sys.stderr.write("\n")
    sys.stderr.write("  Option:\n")
    sys.stderr.write("    -i     indented parse tree\n")
  else:
    indent = False
    for arg in args[1:]:
      if arg == "-i":
        indent = True
        continue
      #s = martin.XmlSerializer()
      #s.indent = indent
      b = martin.ParseTreeBuilder()
      inputString = read(arg)
      parser = martin(inputString, b)
      try:
        parser.parse_Expression()
        #b.serialize(s)
        print("Program")
        print_ast(b.ast_root)
      except martin.ParseException as pe:
        raise Exception ("ParseException while processing " + arg + ":\n" + parser.getErrorMessage(pe)) from pe

if __name__ == '__main__':
  sys.exit(main(sys.argv))

# End
