# TODOS

- complete py/t/test\_errors.py

- add typecheck tests -or- move typecheck code into py/eg ?
  - Add test t56.uxf that exercises all fixtypes in each of a
    list, map, and table
    (i.e., any→str, int↔float, str→bool|int|float|date|datetime|Pair|MyType)
  - Add test t41.uxf ... one for every fixtype that cannot work
  - Do 3 lots of tests covering built-in vtypes _and_ TTypes: for t40.uxf …:
      * no check, no fixtypes
      * check, no fixtypes
      * check, fixtypes

- code review

- release 1.0.0

- UXF libraries
    - for .js use Dart or TypeScript or similar that can output JS
    - uxf.rs uxf.cpp uxf.java uxf.rb ...

- Uniform eXchange Format - a 7"x9" PDF book? (see paper notes)

# IDEAS

- experiment with using uxf format to store various kinds of data,
  e.g., styled text, spreadsheet, graphics, etc.
