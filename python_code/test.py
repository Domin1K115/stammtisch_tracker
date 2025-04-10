

test = {} 

test[0] = set()
test[0].add(('sixtix', 'octity'))
test[0].add(('testy', 'testo'))
test[0].add(('testy', 'testie'))
test[5] = 'seventy'


print(test)

if 5 in test:
    print(True)