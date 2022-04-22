# TODOS

- allow a ktype of null (`?`)
  This is because the user may want any valid ktype for the key but still
  want a specific type for the vtype, e.g.,
  `{? int 1 2 <two> 3 (:6548:) 4}`

- make ttype valid as a vtype for maps, lists, and tables
    - add tests
    - update the check*() methods
    - update the docs & egs

- Writer → Writer2 & create new Writer
    - map|list|table:
	{COMMENT ktype vtype values}
	{COMMENT ktype values}
	{COMMENT values}
	{ktype vtype values}
	{ktype values}
	{values}
	[COMMENT vtype values]
	[vtype values]
	[values]
	(COMMENT ttype values)
	(ttype values)
    - treat empty and one item maps lists & tables as scalars
    - ∴ add `@property\ndef is_scalar(self)` to Map and List
    - so should only need two methods: write\_collection() and write\_one()

- SQLite (see paper notes)
    - test uxf to sqlite: t2.uxf t4.uxf t15.uxf t22.uxf t24.uxf t35.uxf
    - sqlite\_to\_uxf
    - test sqlite to uxf: t2.sqlite t4.sqlite t15.sqlite (should round trip)

- XML (see paper notes)
    - uxf\_to\_xml: same tests as JSON for full round trip
    - xml\_to\_uxf: same tests as JSON for full round trip

- make sure all test files have some nulls (`?`s) (for every typed value),
  esp. t4, t24, t34

- test --check and --fix-types:
  - Add test t40.uxf that exercises all fixtypes in each of a
    list, map, and table
    (i.e., any→str, int↔float, str→bool|int|float|date|datetime)
  - Add test t41.uxf ... one for every fixtype that cannot work
  - Do 3 lots of tests: for t40.uxf ...:
      * no check, no fixtypes
      * check, no fixtypes
      * check, fixtypes

-  --strip-comments
  Offer this?

- create tests t50.uxf ... one for every error or warning that uxf.py
  can produce to ensure they all work & are understandable.

- create a book markup, either pure uxf, or uxf-inspired.

    uxf 1.0 book 1.0
    = P Style Text
    = B Text
    = BI Text
    = I Text
    [#<Style is either a predefined style name or a map of on-the-fly style
    attributes (incl. &lt;parent&gt; for inheriting), or null for inheriting
    the default. TType P holds paragraphs, TType B holds bold and TType I
    holds italic, etc.>
      (P?<This is the start of a para with some> (B<bold text> (I and some
      bold italic since this is nested inside the B,>))(BI<or here we have
      both.>) <Now we're back to body text.>)
      (P<style name><Body text>)
      (P{<fontfamily> <helvetica> <fontsize> 11.5}<More text in the default
      paragraph style but with the font and font size overwridden.>)

  May be better to use uxf-inspired since the above is a bit heavy!

- UXF libraries
    - for .js use Dart or TypeScript or similar that can output JS
    - uxf.rs uxf.cpp uxf.java uxf.rb ...

# IDEAS

- port my python apps to use UXF (e.g., instead of ini, SQLite, & custom
  formats)
- port my Rust apps to use UXF (e.g., instead of ini, SQLite, & custom
  formats), once I have a Rust UXF library
- experiment with using uxf format to store various kinds of data,
  e.g., styled text, spreadsheet, graphics, etc.
