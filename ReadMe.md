# SqlInsight

### Scope
The mean of `SqlInsight` is to allow to querying the structured content of `SQL` 
source files by using the `DQL` part of the `SQL` language to retrieve insights
about data and metadata of parsed `SQL` files.

### How does it work?
`SqlInsight` is a command line utility that should be invoked by passing as
command line argument the filesystem location of a folder containing source
`SQL` code. It then reads each file whose extension is `.sql` and parses it
by understanding is syntactic structure. Structured data read is then put
into a new `SQLite` database that can be queried at will. Here is the help:

```batch
 λ python sqlinsight.py --help
(c) 2020 Giovanni Lombardo mailto://g.lombardo@protonmail.com
sqlinsight.py version 1.0.0
usage: sqlinsight.py [-h] [-e ENCODING] location

It parses and extract insightful metadata about SQL source files allowing them to be retrieved from a new metadata
database through SQL queries.

positional arguments:
  location              The filesystem location where SQL source files are stored.

optional arguments:
  -h, --help            show this help message and exit
  -e ENCODING, --encoding ENCODING
                        The encoding to use for reading SQL source files.
```

### How do I ..

1. ... retrieve the number of statements of each `SQL` source file sorted by 
ascending number of statements? 
 
```sql
SELECT 
    Files.path, COUNT(*) AS NoStatements 
FROM 
    Statements INNER JOIN Files ON 
        Statements.file == Files.identifier 
GROUP BY (file) 
ORDER BY NoStatements;
```
