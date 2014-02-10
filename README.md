# strummer-autosuggest

## Introduction

An autosuggest utility that generates a word tree structure of terms from an id:description list, converts to JSON, so browser apps may preload for faster response time.  Additionally, it can also act as a nano-search engine to provide fast search on a self-contained, preloaded corpus.

This is really an experiment to see whether it's possible to produce a compact and fast lookup/search engine for Javascript.

Obviously the initial revision is not compact, though it is fast.  Ideas for compactness to follow.

I realize that experienced eyes will see this as a naive approach - it certainly is!  Indexes and searching have long been an interest, but not a profession.  So please make suggestions!

## Structure

The JSON produced by strummer is a character n-gram tree of terms in the input corpus, with IDs pointing to the strings indexed.

The test corpus is taken from USDA's Nutrition Database - http://www.ars.usda.gov/Services/docs.htm?docid=18879

And it was ingested to MySQL using this project: https://github.com/ionelanton/web2py-usdadb

### Corpus records:

```
var records={
  1001:"Butter, salted",
  1002:"Butter, whipped, with salt",
  1003:"Butter oil, anhydrous",
  ...
};
```


### Character n-gram tree:

```
var index={
  // every word is represented in a tree of
  // character n-grams with a common root
  "a":{
    "a":{
      "r":{
        "d"{
          "v"{
    ...
    "b":{ ...
    "c":{
      // every n-gram has a list of record IDs
      "_id_":[13954,13955,...]
  ...
}
```

## Efficiency

The first experiment is clearly not efficient, although it does compress pretty well (lots of redundancy!)  Once loaded into the web browser, it expands like water in sawdust!  That's not good, but made for a fun experiment.

See [Further Experiments To Come](Further_Experiments_To_Come.md) for future plans.

## The name

I was looking for a name that brings busy fingers to mind  I was also listening to the album Sandinista! while coding the initial experiment, so it's partly also a tribute to the Clash's late frontman.
