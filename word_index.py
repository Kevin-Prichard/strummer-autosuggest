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


def ngram_lookup_gen_every(fn_input,fn_output_json,fn_output_recs,lookup_limit=999,min_lookup_len=0):
    root={}
    fh=open(fn_input,'r')
    wordrx = re.compile('\W+')

    records={}
    id_node="_id_"

    L=fh.readline()

    # each line from the input
    while L:
        # split into label and id
        label, id = L[:-1].split('\t')
        # store the labels by id
        records[id]=label
        # get list of words from label
        words = wordrx.split(label)
        # scan word list
        for word in words:
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
                    if len(ptr[ch][id_node]) < lookup_limit and int(id) not in ptr[ch][id_node]:
                        ptr[ch][id_node].append( int(id) )
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
        opts, args = getopt.getopt(argv[1:], "dhi:o:r:s:p:", ["debug", "help", "input=", "index-output=", "record-output=", "start-char", "pointer-limit"] )
    except getopt.GetoptError:
        usage()
    DEBUG = False
    for opt, arg in opts:
        if DEBUG: print "opt %s, arg %s" % (opt, arg)
        if opt in ('-d','--debug'):
            DEBUG = True
        elif opt in ("-h", "--help"):
            usage()
        elif opt in ('-i','--input'):
            if arg is None:
                usage("-i|--input-file is a required argument!")
            input_file=arg
        elif opt in ("-o", "--index-output"):
            if arg is None:
                usage("-o|--index-output is a required argument!")
            index_output=arg
        elif opt in ("-r", "--record-output"):
            if arg is None:
                usage("-r|--record-output is a required argument!")
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

    if DEBUG:
        print "ngram_lookup_gen_every( fn_input=%s, fn_output_json=%s, fn_output_recs=%s, lookup_limit=%s, min_lookup_len=%s)" % ( \
            input_file if input_file is not None else "None", \
            index_output if index_output is not None else "None", \
            record_output if record_output is not None else "None", \
            pointer_limit if pointer_limit is not None else "None", \
            start_char_num if start_char_num is not None else "None" \
        )

    if input_file is None or index_output is None or record_output is None:
        usage("You need to give some options, man!")

    ngram_lookup_gen_every( fn_input=input_file, fn_output_json=index_output, fn_output_recs=record_output, lookup_limit=pointer_limit, min_lookup_len=start_char_num)


if __name__ == "__main__":
    main(sys.argv)

