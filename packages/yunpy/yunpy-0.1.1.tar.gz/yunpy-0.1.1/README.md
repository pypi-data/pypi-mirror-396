# YunPy

[![PyPI version](https://img.shields.io/pypi/v/yunpy?color=blue)](https://pypi.org/project/yunpy/)
[![Python versions](https://img.shields.io/pypi/pyversions/yunpy)](https://pypi.org/project/yunpy/)
[![License](https://img.shields.io/pypi/l/yunpy)](LICENSE)
![Build](https://github.com/alxdrdelaporte/yunpy/actions/workflows/publish.yml/badge.svg?event=release)

This library automatically adds Middle Chinese phonetic glosses to plain text files, and converts the `.txt` format into annotated Webanno TSV 3.3 or XML.

 The converter is based on the [PHONO-ML database](https://doi.org/10.5281/zenodo.17349142), which maps Chinese characters to Middle Chinese readings (26 224 entries), rendering each reading in the [Baxter-Sagart reconstruction](https://sites.lsa.umich.edu/ocbaxtersagart/). The tool supports single-file and recursive directory processing via both a command-line interface and programmatic usage in Python.

## Features

### Lexicon exploration

* Display all known Middle Chinese transcriptions for a single character or a string
* Display detailed information (transcriptions, fanqie, sixtuples) for a single character or a string

### Text annotation

* Annotate and convert TXT to WebAnno TSV 3.3 (compatible with annotation tools such as [INCEpTION](https://inception-project.github.io/))
* Annotate and convert TXT to XML
* Process a single file or batch process multiple files from a directory 

> All of this can be done using either CLI or programmatic usage in Python

## Installation

```bash
pip install yunpy
```

## CLI usage

### Lexicon exploration

Display a character's known reading(s):

```bash
howtoread 左
```

Output:

```text
Character 左 has the following readings: tsaX, tsaH
```

This command can also be called on a string.

```bash
howtoread 左右流之
```

```text
Character 左 has the following readings: tsaX, tsaH
Character 右 has the following readings: hjuwX, hjuwH
Character 流 has the following reading: ljuw
Character 之 has the following reading: tsyi
```

Display detailed information about a character:

```bash
charinfo 左
```

Output:

```text
Character = 左
Fanqie = ['臧可', '則箇']
Sixtuples = ['果開一上歌精', '果開一去歌精']
Transcriptions = ['tsaX', 'tsaH']
```

This command can also be called on a string.

```bash
charinfo 左右
```

```text
Character = 左
Fanqie = ['臧可', '則箇']
Sixtuples = ['果開一上歌精', '果開一去歌精']
Transcriptions = ['tsaX', 'tsaH']


Character = 右
Fanqie = ['云久', '于救']
Sixtuples = ['流開三上尤云', '流開三去尤云']
Transcriptions = ['hjuwX', 'hjuwH']
```

> Characters not included in the database will *not* crash the program.

```bash
howtoread a
```

```text
No reading available for this character: a
```

```bash
charinfo a
```

```text
The character 'a' was not found in the database.
```

### Text annotation

#### Annotate and convert to Webanno TSV 3.3

An example `.txt` file is included. To run Webanno TSV 3.3 single file conversion on it, use the following command:

```bash
webanno --file example
```

```bash
webanno -f example
```

The resulting file will be saved at `./webanno_output/example.tsv`.

To annotate any `.txt` file into Webanno TSV 3.3:

```bash
webanno --file ./path_to/my_file.txt
```

```bash
webanno -f ./path_to/my_file.txt
```

The resulting file will be saved in a `./webanno_output/` directory, under the same name as the original file (`./webanno_output/my_file.tsv`).

Batch processing all `.txt` files from a directory:

```bash
webanno --directory ./path_to/my_directory
```

```bash
webanno -d ./path_to/my_directory
```

All resulting files will be saved in a `./webanno_output` subdirectory, under the same name as the original directory (`./webanno_output/my_directory/`).

#### Annotate and convert to XML

An example `.txt` file is included. To run XML single file conversion on it, use the following command:

```bash
yunpyxml --file example
```

```bash
yunpyxml -f example
```

The resulting file will be saved at `./xml_output/example.xml`.

To annotate any `.txt` file into XML:

```bash
yunpyxml --file ./path_to/my_file.txt
```

```bash
yunpyxml -f ./path_to/my_file.txt
```

The resulting file will be saved in a `./xml_output/` directory, under the same name as the original file (`./xml_output/my_file.tsv`).

Batch processing all `.txt` files from a directory:

```bash
yunpyxml --directory ./path_to/my_directory
```

```bash
yunpyxml -d ./path_to/my_directory
```

All resulting files will be saved in a `./xml_output` subdirectory, under the same name as the original directory (`./xml_output/my_directory/`).

## Programmatic Usage

`YunPy` was designed as a CLI tool first but can also be fully used in any Python script.

Lexicon exploration from `yunpy.utils` and `yunpy.Character`:

```python
from yunpy.utils import *

# Get all known readings from a character
readings = get_readings_from_character("左")

# Get all known sixtuples from a character
sixtuples = get_sixtuples_from_character("左")

# Get all known fanqie from a character
fanqie = get_fanqie_from_character("左")

# Get a list of all the characters registered in the database
all_characters = db_coverage()

# Get an informational message about PHONO-ML database
about = about_database()
```

```python
from yunpy.character import Character

# Check if a character is registered in the database
in_db = Character("左").is_in_db()

# Get a message showing all known readings for a character
howtoread = Character("左").set_character_readings_message()

# Get a message displaying detailed information for a character
charinfo = Character("左").set_message()
```
Text annotation from `yunpy.core`:

```python
from yunpy.core import export_webanno_constituents, process_dir

"""Annotate a single file from TXT into Webanno TSV 3.3"""

# Default output path ("./webanno_output")
export_webanno_constituents("./my_text.txt")
# Custom output path
export_webanno_constituents("./my_text.txt", "./my_output_dir")

""" Batch process all TXT files from a directory """

# Default output path ("./webanno_output")
process_dir("./my_input_dir", "webanno")
```

```python
from yunpy.core import export_xml, process_dir

""" Annotate a single file from TXT into YunPy XML """

# Default output path ("./xml_output")
export_xml("./my_text.txt")
# Custom output path
export_xml("./my_text.txt", "./my_output_dir")

""" Batch process all TXT files from a directory """

# Default output path ("./xml_output")
process_dir("./my_input_dir", "xml")
```

### Output formats

#### WebAnno TSV 3.3

Input:

```text
關關雎鳩，在河之洲；
```

Output:

```tsv
#FORMAT=WebAnno TSV 3.3
#T_SP=webanno.custom.Transcription|value
#T_SP=webanno.custom.Transcriptions|values
#T_SP=webanno.custom.Fanqie|value
#T_SP=webanno.custom.Sixtuples|value


#Text=關關雎鳩，在河之洲；
1-1	0-1	關	kwaen	_	古還	山合二平刪見
1-2	1-2	關	kwaen	_	古還	山合二平刪見
1-3	2-3	雎	tshjo	_	七余	遇開三平魚清
1-4	3-4	鳩	kjuw	_	居求	流開三平尤見
1-5	4-5	\，	p	_	_	_
1-6	5-6	在	*	dzojX|dzojH	昨宰|昨代	蟹開一上咍從|蟹開一去咍從
1-7	6-7	河	ha	_	胡歌	果開一平歌匣
1-8	7-8	之	tsyi	_	止而	止開三平之章
1-9	8-9	洲	tsyuw	_	職流	流開三平尤章
1-10	9-10	\；	p	_	_	_
```

#### YunPy XML

Input:

```text
關關雎鳩，在河之洲；
```

Output:

```xml
<?xml version='1.0' encoding='utf-8'?>
<ANNOTATED_TEXT>
 <line>
  <token>
   <character>關</character>
   <transcription>kwaen</transcription>
  </token>
  <token>
   <character>關</character>
   <transcription>kwaen</transcription>
  </token>
  <token>
   <character>雎</character>
   <transcription>tshjo</transcription>
  </token>
  <token>
   <character>鳩</character>
   <transcription>kjuw</transcription>
  </token>
  <token>
   <character>，</character>
  </token>
  <token>
   <character>在</character>
   <transcriptions>
    <transcription>dzojX</transcription>
    <transcription>dzojH</transcription>
   </transcriptions>
  </token>
  <token>
   <character>河</character>
   <transcription>ha</transcription>
  </token>
  <token>
   <character>之</character>
   <transcription>tsyi</transcription>
  </token>
  <token>
   <character>洲</character>
   <transcription>tsyuw</transcription>
  </token>
  <token>
   <character>；</character>
  </token>
 </line>
 </ANNOTATED_TEXT>
```

## Data sources

### PHONO-ML Database

**[*PHONO-ML*](https://doi.org/10.5281/zenodo.17349142)** is a database mapping Chinese characters to Middle Chinese phonetic transcriptions, covering 26 224 character/transcription pairs (or 20 276 characters), developed by principal investigator [Guillaume Jacques](https://crlao.cnrs.fr/membres/guillaume-jacques/) and software engineer [Alexander Delaporte](https://crlao.cnrs.fr/membres/alexander-delaporte/). 

`YunPy` includes a copy of PHONO-ML's `phonoML_characters.csv` table, which provides transcriptions and data about characters.

> You can display an informational message about [PHONO-ML](https://doi.org/10.5281/zenodo.17349142) by using the `database` command.

### Shijing-net corpus

**[*Shijing-net*](https://gitlab.huma-num.fr/chi-know-po/shijing-net)** is a digital corpus composed of the poetic *Shijing* 詩經 Anthology and multiple commentaries, developed within the **[CHI-KNOW-PO project](https://chi-know-po.gitpages.huma-num.fr/)** led by principal investigator [Marie Bizais-Lillig](https://www.usias.fr/fellows/fellows-2021/marie-bizais-lillig/#c112437), with research engineer [Ilaine Wang](http://www.inalco.fr/enseignant-chercheur/ilaine-wang).

`YunPy`'s example and test files were created from Shijing-net's TXT version.

## Authors 

* Alexander DELAPORTE ([@alxdrdelaporte](https://github.com/alxdrdelaporte))
* Qingqing XIE ([@Qingqing-ha](https://github.com/Qingqing-ha))

See the [AUTHORS](./AUTHORS.md) file for details.

## Licence

### Code

`YunPy`'s source code is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

### Data sources

*PHONO-ML Database* is licensed under the [Creative Commons Attribution 4.0 International (CC BY 4.0)](http://creativecommons.org/licenses/by/4.0/) License, and *Shijing-net* is licensed under the [Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](http://creativecommons.org/licenses/by-sa/4.0/) License. 

See the respective data sources for more information.