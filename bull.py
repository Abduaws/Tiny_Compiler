s = "N+I+$+(((!*(N+I))+(N+I))(O))*((!*(N+I))+(N+I))+(!*(N+I))"

s = s.replace("N", "NUMBER")
s = s.replace("I", "ID")
s = s.replace("(", "[")
s = s.replace(")", "]")
s = s.replace("+", "|")
s = s.replace("O", "EQ|LE|LT|GE|GT|NE|AND|OR")
s = s.replace("!", "NOT")
s = s.replace("$", "ε")

print(s)