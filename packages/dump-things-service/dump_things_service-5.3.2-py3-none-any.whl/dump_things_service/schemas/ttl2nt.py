import sys

from rdflib import Graph


if len(sys.argv) > 1:
    input_ = sys.argv[1]
else:
    input_ = sys.stdin
g = Graph()
g.parse(input_, format='ttl')
print(g.serialize(format='nt'))
