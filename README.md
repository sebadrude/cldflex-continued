# cldflex

Convert FLEx data to CLDF-ready CSV.

[![Versions](https://img.shields.io/pypi/pyversions/clld_morphology_plugin)](https://www.python.org/)
[![PyPI](https://img.shields.io/pypi/v/clld_morphology_plugin.svg)](https://pypi.org/project/clld_morphology_plugin)
[![License](https://img.shields.io/github/license/fmatter/cldflex)](https://www.apache.org/licenses/LICENSE-2.0)


Many descriptive linguists have annotated language data in a FLEx ([SIL's Fieldworks Lexical Explorer](https://software.sil.org/fieldworks/)) database, which provides perhaps the most popular and accessible assisted segmentation and annotation workflow.
However, a reasonably complete data export is only available in XML, which is not human-friendly, and is not readily converted to other data.
A data format growing in popularity is the [CLDF standard](https://cldf.clld.org/), a table-based approach with human-readable datasets, designed to be used in [CLLD](https://clld.org/) apps and easily processable by any software that can read [CSV](https://en.wikipedia.org/wiki/Comma-separated_values) files, including  [R](https://www.r-project.org/), [pandas](https://pandas.pydata.org/) or spreadsheet applications.
The goal of ``cldflex`` is to convert lexicon and corpus data stored in FLEx to CSV tables, primarily for use in CLDF datasets.

## Installation

`cldflex` is available on [PyPI](https://pypi.org/project/cldflex):
```shell
pip install cldflex
```

## Command line usage
At the moment, there are three commands: ``cldflex corpus`` for `.flextext` files; ``cldflex dictionary`` and `cldflex wordlist` for `.lift` files.
All commands create a number of CSV files.
One can either use [cldfbench](https://github.com/cldf/cldfbench) to create one's own CLDF datasets from these files, or add the `--cldf` argument to create a simple CLDF dataset.
Project-specific [configuration](#configuration) can be passed by `--conf your/config.yaml`, or creating a file `cldflex.yaml`

### `corpus`
Basic usage:

```shell
cldflex corpus texts.flextext
```

Connect the corpus with the lexicon:

```shell
cldflex corpus texts.flextext --lexicon lexicon.lift
```

Create a CLDF dataset:

```shell
cldflex corpus texts.flextext --lexicon lexicon.lift --cldf
```

### `dictionary`

Extract morphemes, morphs, and entries from `lexicon.lift`:

```shell
cldflex dictionary lexicon.lift
```

Create a CLDF dataset with a  [`Dictionary`](https://github.com/cldf/cldf/tree/master/modules/Dictionary) module:

```shell
cldflex dictionary lexicon.lift --cldf
```

### `wordlist`

Create a CLDF dataset with a  [`Wordlist`](https://github.com/cldf/cldf/tree/master/modules/Wordlist) module:

```shell
cldflex wordlist lexicon.lift --cldf
```

## API usage
The functions corresponding to the commands above are [`cldflex.corpus.convert()`](https://github.com/fmatter/cldflex/blob/4d9962ff53baab68a20ecce34f8623e87f7197ec/src/cldflex/corpus.py#L445) and [`cldflex.lift2csv.convert()`](https://github.com/fmatter/cldflex/blob/4d9962ff53baab68a20ecce34f8623e87f7197ec/src/cldflex/lift2csv.py#L130).

## Configuration
There is no default configuration.
Rather, `cldflex` will guess values for most of the parameters below and tell you what it's doing.
It is suggested to start out configuration-free until something goes wrong or you want to change something.
Create a [YAML](https://yaml.org/) file for CLI usage, pass a dict to the `convert` methods.
If a `cldflex.yaml` file sits in the current directory or next to your input file, it is picked up automatically.

* `obj_lg`: the object language
* `gloss_lg`: the (single) language used for glossing / translation — the *primary* analysis language (see [Analysis languages](#analysis-languages) below)
* `gloss_lgs`: an ordered list of analysis languages to keep; the first is primary (see below)
* `msa_lg`: the language used for storing POS information
* `lang_id`: the value to be used in the created tables
* `glottocode`: used to look up language metadata from glottolog
* `csv_cell_separator`: if there are multiple values in a cell (allomorphs, polysemy...), they are by default separated by `"; "`
* `form_slices`: set to `false` if you don't want form slices connecting morphs and word forms
* `mappings`: a dictionary specifying name changes of columns in the created CSV files

### Analysis languages
FLEx projects frequently have **two analysis (metadata) languages** — for example a regional/contact language (Portuguese, Spanish, French, Indonesian…) alongside a major language such as English. LIFT preserves the glosses and definitions in *all* of these languages, but it does **not** record which one FLEx treated as the primary analysis language (that ordering lives only in the unexported `.fwdata` project settings). `cldflex` therefore lets you decide.

The *primary* analysis language drives each sense's `Name`/`Description` (and hence the CLDF concept labels). Any additional kept languages are preserved as extra columns (`definition_<lang>`, `gloss_<lang>`, `note_..._<lang>`, …).

Control this with `gloss_lgs` (an ordered list) in your config, or the `--gloss-lgs` CLI flag (comma-separated). The first entry is primary; every listed language is kept; any analysis language found in the data but not listed is dropped.

```yaml
# keep both, Portuguese primary:
gloss_lgs: [pt, en]
# keep both, English primary:
# gloss_lgs: [en, pt]
# keep only Portuguese (drops the English columns):
# gloss_lgs: [pt]
```

```shell
cldflex dictionary lexicon.lift --gloss-lgs pt,en   # overrides the config
```

If you configure nothing, `cldflex` keeps **all** analysis languages it finds, guesses the primary as the most frequent one, and warns you that it guessed. The legacy singular `gloss_lg` still works: it names the primary and keeps every other language after it.

When a FLEx-generated `WritingSystems/` folder sits next to the input file, `cldflex` reads it to list the declared writing systems and to warn about configured language codes that aren't declared there (catching typos).