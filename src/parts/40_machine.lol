
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
