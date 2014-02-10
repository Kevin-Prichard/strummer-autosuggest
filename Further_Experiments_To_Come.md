### Character nodes -> strings

Currently character subtree nodes are represented with Py/JS dicts, also not so efficient.

One idea is-

```
var char_nodes {
  0: { // Root node
    char_node: "abcdefghijklmnopqrstuvwxyz",
    pointers: [ 1, 7, 9, 23, 57, ... ]
  },
  1: { // this is the node pointed to by "a" in the root node
    char_node: "..."
  }
}
```

A first pass at estimating the potential value of this approach, in binary encoding, can be found in forecast-binary-index-size.py.  Note this program expects to find a .gz version of the input file, to measure its size.

### Karthik's ideas here too...

### Gzip ID lists

JS implementations of the gzip decompressor exist, so compressing the ID list to a binary blob is possible.  But then cross-browser binary representation is problematic, with base64 being the least common denominator, and least efficient.

