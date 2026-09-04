
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
