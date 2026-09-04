HAI 1.3

BTW ==========================================================================
BTW  tm_compile.lol — compilador Maquina de Turing -> JAJAJA, en LOLCODE
BTW
BTW  Espejo de proofs/tm_to_jajaja.py (misma codificacion):
BTW    <q>$      ::= <q>_$       (extension a la derecha, por estado)
BTW    <q>s      ::= s'<q'>      (movimiento R)
BTW    x<q>s   ::= <q'>xs'       (movimiento L, por cada simbolo x del alfabeto
BTW                              mas el blank)
BTW    |<q>s   ::= |<q'>_s'      (L pegado al tope izquierdo; extiende)
BTW    <halt>  ::= ~HALT         (firma de parada)
BTW    ::=
BTW    |<start><tape>$
BTW
BTW  Verificacion byte-a-byte contra el generador Python:
BTW  tools/compare_tm_compile.py
BTW ==========================================================================

BTW consts (truco lci: usar variables en llamadas, no ":")
I HAS A NL ITZ ":)"
I HAS A COL ITZ ":"
I HAS A JSEP ITZ "::::="

BTW ---- estructura TM (bukkit) ----
HOW IZ I NEWTM YR NAM AN YR START AN YR HALT
  I HAS A T ITZ A BUKKIT
  T HAS A NAME ITZ NAM
  T HAS A START ITZ START
  T HAS A HALT ITZ HALT
  T HAS A STATES ITZ A BUKKIT
  T HAS A NST ITZ 0
  T HAS A ALPHA ITZ A BUKKIT
  T HAS A NAL ITZ 0
  T HAS A TRANS ITZ A BUKKIT
  T HAS A NTR ITZ 0
  FOUND YR T
IF U SAY SO

HOW IZ I ADDSTATE YR TM AN YR S
  TM'Z STATES HAS A SRS TM'Z NST ITZ S
  TM'Z NST R SUM OF TM'Z NST AN 1
  FOUND YR 1
IF U SAY SO

HOW IZ I ADDSYM YR TM AN YR S
  TM'Z ALPHA HAS A SRS TM'Z NAL ITZ S
  TM'Z NAL R SUM OF TM'Z NAL AN 1
  FOUND YR 1
IF U SAY SO

HOW IZ I ADDTRANS YR TM AN YR QF AN YR SF AN YR QT AN YR ST AN YR MV
  I HAS A ROW ITZ A BUKKIT
  ROW HAS A SRS 0 ITZ QF
  ROW HAS A SRS 1 ITZ SF
  ROW HAS A SRS 2 ITZ QT
  ROW HAS A SRS 3 ITZ ST
  ROW HAS A SRS 4 ITZ MV
  TM'Z TRANS HAS A SRS TM'Z NTR ITZ ROW
  TM'Z NTR R SUM OF TM'Z NTR AN 1
  FOUND YR 1
IF U SAY SO

HOW IZ I COMPILE YR TM AN YR TAPE
  I HAS A OUT ITZ ""

  BTW extension DERECHA: <q>$ ::= <q>_$
  I HAS A I ITZ 0
  IM IN YR EXTEND
    BOTH SAEM I AN TM'Z NST, O RLY?
      YA RLY
        GTFO
    OIC
    I HAS A Q ITZ TM'Z STATES'Z SRS I
    DIFFRINT Q AN TM'Z HALT, O RLY?
      YA RLY
        OUT R SMOOSH OUT AN "<" AN Q AN ">$" AN JSEP AN "<" AN Q AN ">_" AN "$" AN NL MKAY
    OIC
    I R SUM OF I AN 1
  IM OUTTA YR EXTEND

  BTW transiciones
  I HAS A TI ITZ 0
  IM IN YR TRS
    BOTH SAEM TI AN TM'Z NTR, O RLY?
      YA RLY
        GTFO
    OIC
    I HAS A ROW ITZ TM'Z TRANS'Z SRS TI
    I HAS A Q ITZ ROW'Z SRS 0
    I HAS A S ITZ ROW'Z SRS 1
    I HAS A Q2 ITZ ROW'Z SRS 2
    I HAS A S2 ITZ ROW'Z SRS 3
    I HAS A MV ITZ ROW'Z SRS 4
    BOTH SAEM MV AN "R", O RLY?
      YA RLY
        BTW <q>s ::= s'<q'>
        OUT R SMOOSH OUT AN "<" AN Q AN ">" AN S AN JSEP AN S2 AN "<" AN Q2 AN ">" AN NL MKAY
      NO WAI
        I HAS A XI ITZ 0
        IM IN YR SYMS
          BOTH SAEM XI AN SUM OF TM'Z NAL AN 1, O RLY?
            YA RLY
              GTFO
          OIC
          I HAS A XS ITZ "_"
          DIFFRINT XI AN TM'Z NAL, O RLY?
            YA RLY
              XS R TM'Z ALPHA'Z SRS XI
          OIC
          BTW x<q>s ::= <q'>xs'
          OUT R SMOOSH OUT AN XS AN "<" AN Q AN ">" AN S AN JSEP AN "<" AN Q2 AN ">" AN XS AN S2 AN NL MKAY
          XI R SUM OF XI AN 1
        IM OUTTA YR SYMS
        BTW tope izquierdo: |<q>s ::= |<q'>_s'
        OUT R SMOOSH OUT AN "|<" AN Q AN ">" AN S AN JSEP AN "|<" AN Q2 AN ">" AN "_" AN S2 AN NL MKAY
    OIC
    TI R SUM OF TI AN 1
  IM OUTTA YR TRS

  BTW firma halt + separador + base
  OUT R SMOOSH OUT AN "<" AN TM'Z HALT AN ">" AN JSEP AN "~HALT" AN NL MKAY
  OUT R SMOOSH OUT AN JSEP AN NL MKAY
  OUT R SMOOSH OUT AN "|<" AN TM'Z START AN ">" AN TAPE AN "$" AN NL MKAY
  FOUND YR OUT
IF U SAY SO

HOW IZ I TM_BININC
  I HAS A M ITZ I IZ NEWTM YR "binary_increment" AN YR "seek" AN YR "done" MKAY
  I HAS A A1 ITZ I IZ ADDSTATE YR M AN YR "seek" MKAY
  I HAS A A2 ITZ I IZ ADDSTATE YR M AN YR "carry" MKAY
  I HAS A A3 ITZ I IZ ADDSTATE YR M AN YR "done" MKAY
  I HAS A B1 ITZ I IZ ADDSYM YR M AN YR "0" MKAY
  I HAS A B2 ITZ I IZ ADDSYM YR M AN YR "1" MKAY
  I HAS A C1 ITZ I IZ ADDTRANS YR M AN YR "seek" AN YR "0" AN YR "seek" AN YR "0" AN YR "R" MKAY
  I HAS A C2 ITZ I IZ ADDTRANS YR M AN YR "seek" AN YR "1" AN YR "seek" AN YR "1" AN YR "R" MKAY
  I HAS A C3 ITZ I IZ ADDTRANS YR M AN YR "seek" AN YR "_" AN YR "carry" AN YR "_" AN YR "L" MKAY
  I HAS A C4 ITZ I IZ ADDTRANS YR M AN YR "carry" AN YR "1" AN YR "carry" AN YR "0" AN YR "L" MKAY
  I HAS A C5 ITZ I IZ ADDTRANS YR M AN YR "carry" AN YR "0" AN YR "done" AN YR "1" AN YR "L" MKAY
  I HAS A C6 ITZ I IZ ADDTRANS YR M AN YR "carry" AN YR "_" AN YR "done" AN YR "1" AN YR "L" MKAY
  FOUND YR M
IF U SAY SO

HOW IZ I TM_BITFLIP
  I HAS A M ITZ I IZ NEWTM YR "bit_flip" AN YR "flip" AN YR "done" MKAY
  I HAS A A1 ITZ I IZ ADDSTATE YR M AN YR "flip" MKAY
  I HAS A A2 ITZ I IZ ADDSTATE YR M AN YR "done" MKAY
  I HAS A B1 ITZ I IZ ADDSYM YR M AN YR "0" MKAY
  I HAS A B2 ITZ I IZ ADDSYM YR M AN YR "1" MKAY
  I HAS A C1 ITZ I IZ ADDTRANS YR M AN YR "flip" AN YR "0" AN YR "flip" AN YR "1" AN YR "R" MKAY
  I HAS A C2 ITZ I IZ ADDTRANS YR M AN YR "flip" AN YR "1" AN YR "flip" AN YR "0" AN YR "R" MKAY
  I HAS A C3 ITZ I IZ ADDTRANS YR M AN YR "flip" AN YR "_" AN YR "done" AN YR "_" AN YR "L" MKAY
  FOUND YR M
IF U SAY SO

HOW IZ I TM_PARITY
  I HAS A M ITZ I IZ NEWTM YR "parity" AN YR "even" AN YR "done" MKAY
  I HAS A A1 ITZ I IZ ADDSTATE YR M AN YR "even" MKAY
  I HAS A A2 ITZ I IZ ADDSTATE YR M AN YR "odd" MKAY
  I HAS A A3 ITZ I IZ ADDSTATE YR M AN YR "done" MKAY
  I HAS A B1 ITZ I IZ ADDSYM YR M AN YR "1" MKAY
  I HAS A C1 ITZ I IZ ADDTRANS YR M AN YR "even" AN YR "1" AN YR "odd" AN YR "1" AN YR "R" MKAY
  I HAS A C2 ITZ I IZ ADDTRANS YR M AN YR "odd" AN YR "1" AN YR "even" AN YR "1" AN YR "R" MKAY
  I HAS A C3 ITZ I IZ ADDTRANS YR M AN YR "even" AN YR "_" AN YR "done" AN YR "P" AN YR "L" MKAY
  I HAS A C4 ITZ I IZ ADDTRANS YR M AN YR "odd" AN YR "_" AN YR "done" AN YR "I" AN YR "L" MKAY
  FOUND YR M
IF U SAY SO

BTW ---- driver ----
I HAS A T1 ITZ I IZ TM_BININC MKAY
VISIBLE "==== binary_increment 1011 ===="
VISIBLE I IZ COMPILE YR T1 AN YR "1011" MKAY!
I HAS A T2 ITZ I IZ TM_BITFLIP MKAY
VISIBLE "==== bit_flip 1011 ===="
VISIBLE I IZ COMPILE YR T2 AN YR "1011" MKAY!
I HAS A T3 ITZ I IZ TM_PARITY MKAY
VISIBLE "==== parity 1111 ===="
VISIBLE I IZ COMPILE YR T3 AN YR "1111" MKAY!

KTHXBYE
