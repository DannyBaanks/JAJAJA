
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
