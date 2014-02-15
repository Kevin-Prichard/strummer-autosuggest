#!/usr/bin/env python

import re, json, sys, getopt
import pprint

class mList(list):
    pass

pp = pprint.PrettyPrinter(indent=4)

def ngram_lookup_gen_terminus(fn_input,fn_output_json,fn_output_recs):
    root={}
    fh=open(fn_input,'r')
    wordrx = re.compile('\W+')

    records={}
    limit=9999999
    wc=0
    L=fh.readline()
    id_node="_id_"
    while L:
        label, id = L[:-1].split('\t')
        records[id]=label
        words = wordrx.split(label)
        for word in words:
            wl=len(word)
            pos=0
            ptr=root
            w = word.lower()
            for ch in w:
                if ch not in ptr:
                    ptr[ch]={}
                pos+=1
                if pos==wl:
                    if id_node not in ptr[ch]:
                        ptr[ch][id_node] = []
                    ptr[ch][id_node].append(int(id))
                else:
                    ptr=ptr[ch]

        wc+=1
        if wc>=limit: break
        L=fh.readline()

    fh.close()
    #pp.pprint(root)
    out_file_wi = open(fn_output_json,"w")
    out_file_wi.write( "var wordIndex="+json.dumps(root,sort_keys=True,separators=(',',':') )+";\n" );
    out_file_wi.close()

    out_file_recs = open(fn_output_recs,"w")
    out_file_recs.write( "var records="+json.dumps(records,sort_keys=True,separators=(',',':'))+";\n" );
    out_file_recs.close()


class NGramIdx():

    def __init__(self,ngram_length):
        self.ngram_length = ngram_length
        # dictionary of bigrams: ab->[list of word ids for 'ab' bigram]
        self.ngrams = {}
        # word to word id dict: apple->297
        self.ngram_words = {}
        # word id to word dict: 297->apple
        self.ngram_words_idx = {}
        # word-ID-to-source-ID table
        self.word_to_source = {}
        # Next word_id
        self.next_word_id = 0

    def add_word_to_source(self,word,source_id):
        word_id = self.ngram_words[word]
        if word_id not in self.word_to_source:
            self.word_to_source[word_id] = []
            if source_id not in self.word_to_source[word_id]:
                self.word_to_source[word_id].append(source_id)

    def accum_ngrams(self,word,source_id):
        # already in index?  early departure
        if word in self.ngram_words:
            self.add_word_to_source( word, source_id )
            return

        word_id = self.next_word_id
        self.next_word_id += 1
        # Add to word-to-id index
        self.ngram_words[word] = word_id
        # Add to id-to-word index
        self.ngram_words_idx[word_id] = word
        # Add word to sources      
        self.add_word_to_source( word, source_id )
        # Step through word chars
        L = len(word)
        for i in range(0,L):
            ngram_end_pos = i+self.ngram_length if i+self.ngram_length<L else L
            # Grab next ngram
            gram2 = word[i:ngram_end_pos]
            # New ngram?  Add to index with starting count and word id list
            if gram2 not in self.ngrams:
                self.ngrams[gram2] = {'count':1,'words':[word_id]}
            else:
                # Increment existing ngram count
                self.ngrams[gram2]['count'] += 1
                # Add word ID to the ngram's word ID list
                if word_id not in self.ngrams[gram2]['words']:
                    self.ngrams[gram2]['words'].append( word_id )

    def get_ngram_dict(self):
        return self.ngrams
        
    def get_word_index(self):
        return {
            'words_idx': self.ngram_words_idx,
            'sources_idx': self.word_to_source
        }


def ngram_lookup_gen_every(fn_input,fn_output_json,fn_output_recs,fn_output_ngram,lookup_limit=999,min_lookup_len=0):

    root={}
    fh=open(fn_input,'r')
    wordrx = re.compile('\W+')

    records={}
    id_node="_id_"
    
    ngram_indices = []
    for i in range(1,5):
        ngram_indices.append( NGramIdx(i) )

    L=fh.readline()

    # each line from the input
    while L:
        # split into label and id
        label, label_id = L[:-1].split('\t')
        # store the labels by label_id
        records[label_id]=label
        # get list of words from label
        words = wordrx.split(label)
        # scan word list
        for word in words:
            for i in range(0,4):
                ngram_indices[i].accum_ngrams(word.lower(),label_id)
#             ngram_idx.accum_ngrams(word.lower(),label_id)
            wl=len(word)
            pos=0
            # reset ptr to tree root
            ptr=root
            w = word.lower()
            # scan word's chars
            for ch in w:
                # extend tree if char is new
                if ch not in ptr:
                    ptr[ch]={}
                pos+=1
                # if minimum lookup threshold...
                if pos>=min_lookup_len:
                    # add an _id_ node (list of matching records) if needed
                    if id_node not in ptr[ch]:
                        ptr[ch][id_node] = []
                    # add this id, if not already in list, and list length limit not met yet
                    if len(ptr[ch][id_node]) < lookup_limit and int(label_id) not in ptr[ch][id_node]:
                        ptr[ch][id_node].append( int(label_id) )
                # advance ptr to next node level
                ptr=ptr[ch]

        # set up next while loop, working within Py's lack of a do-while-condition loop
        L=fh.readline()

    fh.close()
    #pp.pprint(root)
    out_file_wi = open(fn_output_json,"w")
    out_file_wi.write( "var wordIndex="+json.dumps(root,sort_keys=True,separators=(',',':') )+";\n" );
    out_file_wi.close()

    out_file_recs = open(fn_output_recs,"w")
    out_file_recs.write( "var records="+json.dumps(records,sort_keys=True,separators=(',',':'))+";\n" );
    out_file_recs.close()

    out_file_2grams = open(fn_output_ngram,"w")
    indices = {}
    for i in range(0,4):
        indices[i] = {
            'ngram_idx' : ngram_indices[i].get_ngram_dict(),
            'words_sources' : ngram_indices[i].get_word_index()
        }
    out_file_2grams.write( "var ngram_indices="+ \
        json.dumps( indices, sort_keys=True,indent=4,separators=(',',':') )+ \
        ';' \
    )
    out_file_2grams.close()

def usage(error_message=None):

    print """word_index.py -i|--input="input.tsv" -o|--index-output="index_output.js" -r|--record-output="record_output.js [-s|--start-char=n] [-p|--pointer-limit] [-d|--debug]
1. The .tsv file is a tab-separated text file of "id \\t text" records.
2. -s|--start-char=n (default 3) - Specifies the typed character number that word_index.py should begin supplying record IDs at.  "a".."ab".."abc" boom! IDs become available after third char typed.
3. -p|--pointer-limit=m (default 50) - Limit the number of record IDs to m, to reduce JSON payload size.

Example:
./word_index.py --input lookup_table.tsv --index-output test_index.js --record-output test_records.js -s 0 -p 25
"""

    if error_message is not None:
        print "Error: %s" % error_message
    sys.exit()

def main(argv):
    input_file=None
    index_output=None
    record_output=None
    start_char_num=3
    pointer_limit=50

    try:
        print repr(argv[1:])
        opts, args = getopt.getopt(argv[1:], "dhi:o:r:s:p:g:", 
            [ "debug", "help", "input=", "index-output=", "record-output=", "start-char", "pointer-limit", "ngram-output"] )
    except getopt.GetoptError:
        usage()
    DEBUG = False
    print repr(opts)
    for opt, arg in opts:
        if DEBUG: print "opt %s, arg %s" % (opt, arg)
        if opt in ('-d','--debug'):
            DEBUG = True
        elif opt in ("-h", "--help"):
            usage()
        elif opt in ('-i','--input'):
            if arg is None:
                usage("-i|--input-file requires an argument!")
            input_file=arg
        elif opt in ("-o", "--index-output"):
            if arg is None:
                usage("-o|--index-output requires an argument!")
            index_output=arg
        elif opt in ("-r", "--record-output"):
            if arg is None:
                usage("-r|--record-output requires an argument!")
            record_output=arg
        elif opt in ("-s", "--start-char"):
            try:
                arg = int(arg)
                assert arg >= 0
            except:
                usage("-s|--start-char must be an integer! '%s'" % arg)
            start_char_num=arg
        elif opt in ("-p", "--pointer-limit"):
            try:
                arg=int(arg)
                assert arg > 0, 'x is less than zero'
            except:
                usage("-p|--pointer-limit must be an integer! '%s'" % arg)
            pointer_limit=arg
        elif opt in ("-g", "--ngram-output"):
            if arg is None:
                usage("-g|--ngram-output requires an argument!")
            ngram_output=arg
            print 'ngram_output: '+repr(ngram_output)

    if DEBUG:
        print "ngram_lookup_gen_every( fn_input=%s, fn_output_json=%s, fn_output_recs=%s, fn_output_ngram=%s, lookup_limit=%s, min_lookup_len=%s)" % ( \
            input_file if input_file is not None else "None", \
            index_output if index_output is not None else "None", \
            record_output if record_output is not None else "None", \
            ngram_output if ngram_output is not None else "None", \
            pointer_limit if pointer_limit is not None else "None", \
            start_char_num if start_char_num is not None else "None" \
        )

    if input_file is None or index_output is None or record_output is None:
        usage("You need to give some options, man!")

    ngram_lookup_gen_every(
        fn_input=input_file,
        fn_output_json=index_output,
        fn_output_recs=record_output,
        fn_output_ngram=ngram_output,
        lookup_limit=pointer_limit,
        min_lookup_len=start_char_num )


if __name__ == "__main__":
    main(sys.argv)

