from pykakasi import kakasi
import datetime

kk = kakasi()
kk.setMode('H', 'a')
kk.setMode('K', 'a')
kk.setMode('J', 'a')
conv = kk.getConverter()


def to_roma(word):
    return conv.do(word)

def to_shell(cmd_list, path, is_parallel=True):
    join_str =  ' &\n' if is_parallel else '\n'
    if type(cmd_list) == list:
        text = join_str.join(cmd_list)
    else:
        text = cmd_list
    with open(path, 'w') as file:
        file.write(text)
