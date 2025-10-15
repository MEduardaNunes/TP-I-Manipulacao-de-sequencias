# Módulo de Recuperação de Informação (RI)

# <exp>         := <exp_or>                  
# <exp_or>      := <exp_and> (OR <exp_and>)* 
# <exp_and>     := <term> (AND <term>)*      
# <term>        := NOT <subexp> | <subexp>   
# <subexp>      := "(" <exp> ")" | <palavra> 
# <palavra>     := <letra> (<letra> | <digito>)*  

# <letra>       := "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h" | "i" | "j" | "k" | "l" | "m" | "n" | "o" | "p" | "q" | "r" | "s" | "t" | "u" | "v" | "w" | "x" | "y" | "z" | "A" | "B" | "C" | "D" | "E" | "F" | "G" | "H" | "I" | "J" | "K" | "L" | "M" | "N" | "O" | "P" | "Q" | "R" | "S" | "T" | "U" | "V" | "W" | "X" | "Y" | "Z"
# <digito>      := "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"