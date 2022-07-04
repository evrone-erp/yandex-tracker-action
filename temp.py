import re

string = '[ERPOPS-9] Update some feature'

print(re.match(r"[^[]*\[([^]]*)\]", string).groups()[0])
