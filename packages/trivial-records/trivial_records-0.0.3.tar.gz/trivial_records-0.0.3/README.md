
# Trivial Records

A tiny library to parse and generate text containing lists of records.

## Why not just JSON?

It's a bit more convenient for the human; easier to write and read this:

```
Refactoring
author Martin Fowler
publisher Addison-Wesley

A Philosophy of Software Design
author John Ousterhout
publisher Yaknyam Press
```

than to write and read this:

```
{"Refactoring": {"author": "Martin Fowler", "publisher": "Addison-Wesley"}, "A Philosophy of Software Design": {"author": "John Ousterhout", "publisher": "Yaknyam Press"}}
```

or write this:

```
{
  "Refactoring": {
    "author": "Martin Fowler",
    "publisher": "Addison-Wesley"
  },
  "A Philosophy of Software Design": {
    "author": "John Ousterhout",
    "publisher": "Yaknyam Press"
  }
}
```

## What does it offer?

Not much, it's really trivial.

Functions `stream_to_record_dictionary` and `string_to_record_dictionary` give you a Python dictionary.

Functions `record_dictionary_to_string_generator` and `record_dictionary_to_string` take the Python dictionary and give you a string.
