if __name__ == '__main__':

    cont = open('ref.bib', encoding='utf-8').readlines()
    a = cont[3].strip()
    print(a)
    print('http' in a and a.endswith(','))

    ret = []
    for line in cont:
        _l = line.strip()
        if 'http' in _l and _l.endswith(','):
            continue
        else:
            ret.append(line)
    print(ret[:10])
    open('nref.bib', 'w', encoding='utf-8').write(''.join(ret))
