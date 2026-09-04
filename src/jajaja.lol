HAI 1.3

BTW ==========================================================================
BTW  JAJAJA runtime / libreria — LOLCODE 1.3 (runtime externo: lci)
BTW  Este archivo es ARMADO con tools/build_lol.py desde src/parts/*.lol
BTW  No edites el archivo ensamblado directamente; edita las partes.
BTW ==========================================================================

I HAS A NL ITZ ":)"
I HAS A TAB ITZ ":(09)"
I HAS A SPC ITZ " "
I HAS A TILD ITZ "~"
I HAS A HASH ITZ "#"

I HAS A PATSEP ITZ A BUKKIT
PATSEP HAS A SRS 0 ITZ ":"
PATSEP HAS A SRS 1 ITZ ":"
PATSEP HAS A SRS 2 ITZ "="

BTW ---- FIND: indice leftmost de NDL en HAY (bukkits); -1 si no hay ----
HOW IZ I FIND YR HAY AN YR HN AN YR NDL AN YR NN
  BOTH SAEM NN AN BIGGR OF NN AN SUM OF HN AN 1, O RLY?
    YA RLY
      FOUND YR -1
  OIC
  I HAS A K ITZ 0
  I HAS A RES ITZ -1
  I HAS A LIMIT ITZ DIFF OF HN AN NN
  IM IN YR SCAN
    DIFFRINT K AN BIGGR OF K AN SUM OF LIMIT AN 1, O RLY?
      YA RLY
        I HAS A HIT ITZ 1
        I HAS A J ITZ 0
        IM IN YR CMP
          BOTH SAEM J AN NN, O RLY?
            YA RLY
              GTFO
          OIC
          BOTH SAEM HAY'Z SRS SUM OF K AN J AN NDL'Z SRS J, O RLY?
            YA RLY
            NO WAI
              HIT R 0
              GTFO
          OIC
          J R SUM OF J AN 1
        IM OUTTA YR CMP
        HIT, O RLY?
          YA RLY
            RES R K
            GTFO
        OIC
        K R SUM OF K AN 1
      NO WAI
        GTFO
    OIC
  IM OUTTA YR SCAN
  FOUND YR RES
IF U SAY SO

BTW ---- estado global de la maquina (bukkits sobreviven a los bloques) ----
I HAS A RULES ITZ A BUKKIT
I HAS A NRULES ITZ 0
I HAS A BASE ITZ A BUKKIT
I HAS A BLEN ITZ 0
I HAS A OUTB ITZ A BUKKIT
I HAS A OUTN ITZ 0
I HAS A INP ITZ A BUKKIT
I HAS A INPLEN ITZ 0
I HAS A LINE ITZ A BUKKIT
I HAS A LN ITZ 0
I HAS A LINENO ITZ 0
I HAS A MODE ITZ "rules"
I HAS A STEPS ITZ 0
I HAS A STAT ITZ "RUNNING"
I HAS A MAXS ITZ 200000

BTW ---- helpers de la maquina ----

BTW APPENDOUT: agrega un char al buffer de salida
HOW IZ I APPENDOUT YR C
  OUTB HAS A SRS OUTN ITZ C
  OUTN R SUM OF OUTN AN 1
  FOUND YR 1
IF U SAY SO

BTW SETBASE: sustituye la base por un bukkit nuevo
HOW IZ I SETBASE YR NB AN YR NLN
  BASE R NB
  BLEN R NLN
  FOUND YR 1
IF U SAY SO

BTW OUTYARN: devuelve el buffer de salida como yarn
HOW IZ I OUTYARN
  I HAS A S ITZ ""
  I HAS A OI ITZ 0
  IM IN YR JOIN
    BOTH SAEM OI AN OUTN, O RLY?
      YA RLY
        GTFO
    OIC
    S R SMOOSH S AN OUTB'Z SRS OI MKAY
    OI R SUM OF OI AN 1
  IM OUTTA YR JOIN
  FOUND YR S
IF U SAY SO

BTW ---- LINEHANDLE: procesa la linea actual LINE (len LN) segun MODE ----
HOW IZ I LINEHANDLE
  LINENO R SUM OF LINENO AN 1
  BOTH SAEM MODE AN "rules", O RLY?
    YA RLY
      BOTH SAEM LN AN 0, O RLY?
        YA RLY
          FOUND YR "skip"
      OIC
      BOTH SAEM LINE'Z SRS 0 AN HASH, O RLY?
        YA RLY
          FOUND YR "skip-comment"
      OIC
      BTW cuenta espacios/tabs iniciales
      I HAS A LWS ITZ 0
      IM IN YR SKIPWS
        BOTH SAEM LWS AN LN, O RLY?
          YA RLY
            GTFO
        OIC
        EITHER OF BOTH SAEM LINE'Z SRS LWS AN SPC AN BOTH SAEM LINE'Z SRS LWS AN TAB, O RLY?
          YA RLY
            LWS R SUM OF LWS AN 1
          NO WAI
            GTFO
        OIC
      IM OUTTA YR SKIPWS
      BTW tambien recorta trailing ws (oracle: ln.strip() == "::=")
      I HAS A TWS ITZ 0
      I HAS A LASTC ITZ 0
      IM IN YR SKTW
        BOTH SAEM DIFF OF LN AN TWS AN LWS, O RLY?
          YA RLY
            GTFO
        OIC
        LASTC R DIFF OF DIFF OF LN AN TWS AN 1
        EITHER OF BOTH SAEM LINE'Z SRS LASTC AN SPC AN BOTH SAEM LINE'Z SRS LASTC AN TAB, O RLY?
          YA RLY
            TWS R SUM OF TWS AN 1
          NO WAI
            GTFO
        OIC
      IM OUTTA YR SKTW
      I HAS A REST ITZ DIFF OF DIFF OF LN AN LWS AN TWS
      I HAS A ISSEP ITZ 0
      BOTH SAEM REST AN 3, O RLY?
        YA RLY
          I HAS A C1 ITZ LINE'Z SRS LWS
          I HAS A C2 ITZ LINE'Z SRS SUM OF LWS AN 1
          I HAS A C3 ITZ LINE'Z SRS SUM OF LWS AN 2
          I HAS A P1 ITZ BOTH SAEM C1 AN ":"
          I HAS A P2 ITZ BOTH SAEM C2 AN ":"
          I HAS A P3 ITZ BOTH SAEM C3 AN "="
          BOTH SAEM BOTH OF P1 AN BOTH OF P2 AN P3 AN WIN, O RLY?
            YA RLY
              ISSEP R 1
          OIC
      OIC
      ISSEP, O RLY?
        YA RLY
          MODE R "base"
          FOUND YR "separator"
      OIC
      I HAS A KF ITZ I IZ FIND YR LINE AN YR LN AN YR PATSEP AN YR 3 MKAY
      BOTH SAEM KF AN -1, O RLY?
        YA RLY
          STAT R "SYNTAX_ERROR"
          FOUND YR "syntax-error"
      OIC
      BTW crea la regla
      I HAS A LHSB ITZ A BUKKIT
      I HAS A Q ITZ 0
      IM IN YR CL
        BOTH SAEM Q AN KF, O RLY?
          YA RLY
            GTFO
        OIC
        LHSB HAS A SRS Q ITZ LINE'Z SRS Q
        Q R SUM OF Q AN 1
      IM OUTTA YR CL
      I HAS A RHSB ITZ A BUKKIT
      I HAS A RLENO ITZ DIFF OF LN AN SUM OF KF AN 3
      I HAS A W ITZ 0
      IM IN YR CW
        BOTH SAEM W AN RLENO, O RLY?
          YA RLY
            GTFO
        OIC
        RHSB HAS A SRS W ITZ LINE'Z SRS SUM OF KF AN SUM OF 3 AN W
        W R SUM OF W AN 1
      IM OUTTA YR CW
      I HAS A REC ITZ A BUKKIT
      REC HAS A L ITZ LHSB
      REC HAS A LL ITZ KF
      REC HAS A T ITZ RHSB
      REC HAS A TN ITZ RLENO
      REC HAS A EM ITZ 0
      BOTH SAEM RLENO AN BIGGR OF RLENO AN 1, O RLY?
        YA RLY
          BOTH SAEM RHSB'Z SRS 0 AN TILD, O RLY?
            YA RLY
              REC'Z EM R 1
          OIC
      OIC
      RULES HAS A SRS NRULES ITZ REC
      NRULES R SUM OF NRULES AN 1
      FOUND YR "rule"
    NO WAI
      BTW MODE base: primera linea no-blanca y no-comentario es la base
      I HAS A LWS ITZ 0
      IM IN YR SK2
        BOTH SAEM LWS AN LN, O RLY?
          YA RLY
            GTFO
        OIC
        EITHER OF BOTH SAEM LINE'Z SRS LWS AN SPC AN BOTH SAEM LINE'Z SRS LWS AN TAB, O RLY?
          YA RLY
            LWS R SUM OF LWS AN 1
          NO WAI
            GTFO
        OIC
      IM OUTTA YR SK2
      BOTH SAEM LWS AN LN, O RLY?
        YA RLY
          FOUND YR "skip-blank"
      OIC
      BOTH SAEM LINE'Z SRS LWS AN HASH, O RLY?
        YA RLY
          FOUND YR "skip-comment"
      OIC
      I HAS A BQ ITZ 0
      IM IN YR CB
        BOTH SAEM BQ AN LN, O RLY?
          YA RLY
            GTFO
        OIC
        BASE HAS A SRS BQ ITZ LINE'Z SRS BQ
        BQ R SUM OF BQ AN 1
      IM OUTTA YR CB
      BLEN R LN
      MODE R "after"
      FOUND YR "base"
  OIC
  FOUND YR "noop"
IF U SAY SO

BTW ---- estado de transporte (solo el driver stdio lo usa) ----
I HAS A SECT ITZ "prog"
I HAS A MAXTXT ITZ ""
I HAS A TOK ITZ ""

BTW ---- lee el stream de transporte ----
IM IN YR EAT
  GIMMEH TOK
  BOTH SAEM TOK AN "<<EOF>>", O RLY?
    YA RLY
      GTFO
  OIC
  BOTH SAEM TOK AN "<<S1>>", O RLY?
    YA RLY
      SECT R "input"
    NO WAI
      BOTH SAEM TOK AN "<<S2>>", O RLY?
        YA RLY
          SECT R "ctrl"
        NO WAI
          BOTH SAEM TOK AN "<<N>>", O RLY?
            YA RLY
              BOTH SAEM SECT AN "prog", O RLY?
                YA RLY
                  BOTH SAEM STAT AN "RUNNING", O RLY?
                    YA RLY
                      I HAS A LHRES ITZ I IZ LINEHANDLE MKAY
                  OIC
                  I HAS A FLINE ITZ A BUKKIT
                  LINE R FLINE
                  LN R 0
              NO WAI
              BTW newline dentro de input se conserva como char
              BOTH SAEM SECT AN "input", O RLY?
                YA RLY
                  INP HAS A SRS INPLEN ITZ NL
                  INPLEN R SUM OF INPLEN AN 1
              OIC
            OIC
          NO WAI
            BTW <<T>> o char crudo
            I HAS A CH ITZ TOK
            BOTH SAEM TOK AN "<<T>>", O RLY?
              YA RLY
                CH R TAB
            OIC
            BOTH SAEM SECT AN "prog", O RLY?
              YA RLY
                BOTH SAEM STAT AN "RUNNING", O RLY?
                  YA RLY
                    LINE HAS A SRS LN ITZ CH
                    LN R SUM OF LN AN 1
                OIC
              NO WAI
                BOTH SAEM SECT AN "input", O RLY?
                  YA RLY
                    INP HAS A SRS INPLEN ITZ CH
                    INPLEN R SUM OF INPLEN AN 1
                  NO WAI
                    MAXTXT R SMOOSH MAXTXT AN CH MKAY
                OIC
            OIC
          OIC
      OIC
  OIC
IM OUTTA YR EAT

BTW ---- max_steps desde control ----
DIFFRINT MAXTXT AN "", O RLY?
  YA RLY
    MAXS R MAEK MAXTXT NUMBR
OIC

BTW ---- stdin: si hay input, base = input + " " + base ----
DIFFRINT INPLEN AN 0, O RLY?
  YA RLY
    I HAS A NB2 ITZ A BUKKIT
    I HAS A BI ITZ 0
    IM IN YR CIN1
      BOTH SAEM BI AN INPLEN, O RLY?
        YA RLY
          GTFO
      OIC
      NB2 HAS A SRS BI ITZ INP'Z SRS BI
      BI R SUM OF BI AN 1
    IM OUTTA YR CIN1
    NB2 HAS A SRS BI ITZ SPC
    BI R SUM OF BI AN 1
    I HAS A BJ ITZ 0
    IM IN YR CIN2
      BOTH SAEM BJ AN BLEN, O RLY?
        YA RLY
          GTFO
      OIC
      NB2 HAS A SRS SUM OF BI AN BJ ITZ BASE'Z SRS BJ
      BJ R SUM OF BJ AN 1
    IM OUTTA YR CIN2
    BASE R NB2
    BLEN R SUM OF BI AN BJ
OIC

BTW ---- maquina de Markov (rewrite ordenado; primera regla aplicable gana;
BTW      sustituye / emite de acuerdo a la especificacion) ----
IM IN YR MACH
  BOTH SAEM STAT AN "RUNNING", O RLY?
    YA RLY
    NO WAI
      GTFO
  OIC
  BOTH SAEM STEPS AN MAXS, O RLY?
    YA RLY
      GTFO
  OIC
  BTW intenta aplicar la primera regla cuyo lhs aparezca
  I HAS A RI ITZ 0
  I HAS A DID ITZ 0
  IM IN YR TRYR
    BOTH SAEM RI AN NRULES, O RLY?
      YA RLY
        GTFO
    OIC
    I HAS A RUL ITZ RULES'Z SRS RI
    BOTH SAEM RUL'Z LL AN 0, O RLY?
      YA RLY
        BTW lhs vacio: skip
      NO WAI
        I HAS A IDX ITZ I IZ FIND YR BASE AN YR BLEN AN YR RUL'Z L AN YR RUL'Z LL MKAY
        DIFFRINT IDX AN -1, O RLY?
          YA RLY
            BTW aplica: construye nueva base
            I HAS A NB3 ITZ A BUKKIT
            I HAS A WI ITZ 0
            I HAS A P1 ITZ 0
            IM IN YR PL
              BOTH SAEM P1 AN IDX, O RLY?
                YA RLY
                  GTFO
              OIC
              NB3 HAS A SRS WI ITZ BASE'Z SRS P1
              WI R SUM OF WI AN 1
              P1 R SUM OF P1 AN 1
            IM OUTTA YR PL
            RUL'Z EM, O RLY?
              YA RLY
                BTW emision: rhs[1:] al output (o newline si vacio)
                BOTH SAEM RUL'Z TN AN 1, O RLY?
                  YA RLY
                    I HAS A EMRES ITZ I IZ APPENDOUT YR NL MKAY
                  NO WAI
                    I HAS A TE ITZ 0
                    IM IN YR EMIT
                      BOTH SAEM TE AN DIFF OF RUL'Z TN AN 1, O RLY?
                        YA RLY
                          GTFO
                      OIC
                      I HAS A EMRES2 ITZ I IZ APPENDOUT YR RUL'Z T'Z SRS SUM OF TE AN 1 MKAY
                      TE R SUM OF TE AN 1
                    IM OUTTA YR EMIT
                OIC
              NO WAI
                BTW reemplazo: inserta rhs completo
                I HAS A TI ITZ 0
                IM IN YR INS
                  BOTH SAEM TI AN RUL'Z TN, O RLY?
                    YA RLY
                      GTFO
                  OIC
                  NB3 HAS A SRS WI ITZ RUL'Z T'Z SRS TI
                  WI R SUM OF WI AN 1
                  TI R SUM OF TI AN 1
                IM OUTTA YR INS
            OIC
            BTW sufijo tras el match
            I HAS A P2 ITZ SUM OF IDX AN RUL'Z LL
            IM IN YR SUF
              BOTH SAEM P2 AN BLEN, O RLY?
                YA RLY
                  GTFO
              OIC
              NB3 HAS A SRS WI ITZ BASE'Z SRS P2
              WI R SUM OF WI AN 1
              P2 R SUM OF P2 AN 1
            IM OUTTA YR SUF
            I HAS A DONEIT ITZ I IZ SETBASE YR NB3 AN YR WI MKAY
            STEPS R SUM OF STEPS AN 1
            DID R 1
            GTFO
        OIC
      OIC
    RI R SUM OF RI AN 1
  IM OUTTA YR TRYR
  DID, O RLY?
    YA RLY
    NO WAI
      GTFO
  OIC
IM OUTTA YR MACH

BTW ---- status final (si no paro por si solo, el presupuesto manda) ----
BOTH SAEM STAT AN "RUNNING", O RLY?
  YA RLY
    BOTH SAEM STEPS AN MAXS, O RLY?
      YA RLY
        STAT R "MAX_STEPS"
      NO WAI
        STAT R "HALTED"
    OIC
OIC

BTW ---- reporte final: output + frame ----
I HAS A FIN ITZ 0
IM IN YR DUMP
  BOTH SAEM FIN AN OUTN, O RLY?
    YA RLY
      GTFO
  OIC
  VISIBLE OUTB'Z SRS FIN!
  FIN R SUM OF FIN AN 1
IM OUTTA YR DUMP
VISIBLE ""
VISIBLE "<|JAJAJA|status=" !
VISIBLE STAT !
VISIBLE "|steps=" !
VISIBLE STEPS !
VISIBLE "|>"
KTHXBYE
