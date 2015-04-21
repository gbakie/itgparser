
from collections import defaultdict
from itgparser import ItgParser

def open_sentence_file(filename):
    fh = open(filename, 'r')

    sentences = []
    for line in fh:
        tokens = line.strip().split(' ')
        sentences.append(tokens)

    fh.close()

    return sentences


def open_dictionary_file(filename):
    fh = open(filename, 'r')
    
    d = defaultdict(float)
    for line in fh:
        tokens = line.strip().split('\t')
        key = (tokens[0], tokens[1])
        d[key] = float(tokens[2])

    fh.close()

    return d

def open_grammar_file(filename):
    fh = open(filename, 'r')
    
    d = defaultdict(list) 
    for line in fh:
        if line.startswith('#'):
            continue

        tokens = line.strip().split('\t')
        w, p, inv = tokens[0:3]
        ch = tokens[3:]

        rule = [float(w),int(inv),ch]
        d[p].append(rule)
        
    fh.close()
    return d


vocab = open_dictionary_file("data/itg.dict")
sentences_en = open_sentence_file("data/test.en") 
sentences_de = open_sentence_file("data/test.de") 
#gr = open_grammar_file("grammar.dat")


p = ItgParser(vocab)
p.enable_inv_rules(True)
for s_en,s_de in zip(sentences_en, sentences_de):
    print "English sentence: " + str(s_en)
    print "German sentence: " + str(s_de)
    a = p.parse(s_en, s_de)
    print "Alignment(en->ge) : " + str(a)
    print "\n"


print "English words aligned to eps(%): " + str(p.per_english_no_alignment())
print "German words aligned to eps(%): " + str(p.per_german_no_alignment())

print "In-order rule usage(%): " + str(p.per_dir_rules())
print "Swap rule usage(%): " + str(p.per_inv_rules())

