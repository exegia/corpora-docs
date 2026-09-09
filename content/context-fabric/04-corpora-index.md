# Available Corpora

> Source: [https://context-fabric.ai/docs/corpora](https://context-fabric.ai/docs/corpora)

Context-Fabric works with any corpus in Text-Fabric format. This page catalogs 40+ known corpora across languages and time periods.

## Corpus Index

| Corpus | Language | Category | Period | Description |
|--------|----------|----------|--------|-------------|
| [oldassyrian](https://github.com/Nino-cunei/oldassyrian) | Akkadian | Historical | 2000-1600 BCE | Old Assyrian documents |
| [oldbabylonian](https://github.com/Nino-cunei/oldbabylonian) | Akkadian | Historical | 1900-1600 BCE | Old Babylonian letters |
| [ninmed](https://github.com/Nino-cunei/ninmed) | Akkadian | Historical | ca. 800 BCE | Medical Encyclopedia from Nineveh |
| [quran](https://github.com/q-ran/quran) | Arabic | Religious | 600-900 CE | Quranic Arabic Corpus (73 MB) |
| [fusus](https://github.com/among/fusus) | Arabic | Religious | Medieval | Ibn Arabi's Fusus Al Hikam |
| [nena_tf](https://github.com/CambridgeSemiticsLab/nena_tf) | Aramaic | Historical | Modern | North Eastern Neo-Aramaic |
| [wp6-missieven](https://github.com/CLARIAH/wp6-missieven) | Dutch | Historical | 1600-1800 CE | VOC General Missives |
| [wp6-daghregisters](https://github.com/CLARIAH/wp6-daghregisters) | Dutch | Historical | 1640-1641 | Batavia daily records |
| [wp6-ferdinandhuyck](https://github.com/CLARIAH/wp6-ferdinandhuyck) | Dutch | Literary | 1884 | Dutch novel by Jacob van Lennep |
| [mondriaan](https://github.com/annotation/mondriaan) | Dutch | Historical | 1892-1923 | Piet Mondriaan letters |
| [mobydick](https://github.com/annotation/mobydick) | English | Literary | 1851 | Herman Melville novel with NLP annotations |
| [banks](https://github.com/annotation/banks) | English | Literary | 1987 | Iain M. Banks' Consider Phlebas |
| [descartes-tf](https://github.com/CLARIAH/descartes-tf) | French/Latin/Dutch | Historical | 1619-1650 | Descartes correspondence |
| [lxx](https://github.com/CenterBLC/LXX) | Greek | Biblical | 300-100 BCE | Septuagint, Rahlfs edition (268 MB) |
| [n1904](https://github.com/CenterBLC/N1904) | Greek | Biblical | 100-400 CE | Nestle 1904 Greek New Testament (319 MB) |
| [SBLGNT](https://github.com/CenterBLC/SBLGNT) | Greek | Biblical | 100-400 CE | SBL Greek New Testament |
| [nestle1904](https://github.com/ETCBC/nestle1904) | Greek | Biblical | 100-400 CE | NT from LOWFAT-XML syntax trees |
| [Nestle1904GBI](https://github.com/tonyjurg/Nestle1904GBI) | Greek | Biblical | 100-400 CE | Nestle 1904 (tonyjurg) |
| [tischendorf_tf](https://github.com/codykingham/tischendorf_tf) | Greek | Biblical | 100-400 CE | Tischendorf 8th Edition Greek NT (34 MB) |
| [bible](https://github.com/pthu/bible) | Greek | Biblical | 300 BCE-400 CE | Greek OT, NT, and extra-biblical |
| [patristics](https://github.com/pthu/patristics) | Greek | Religious | 100-500 CE | Church Fathers |
| [greek_literature](https://github.com/pthu/greek_literature) | Greek | Literary | 400 BCE-400 CE | Perseus & Open Greek texts |
| [athenaeus](https://github.com/pthu/athenaeus) | Greek | Literary | 80-170 CE | Athenaeus' Deipnosophistae |
| [bhsa](https://github.com/ETCBC/bhsa) | Hebrew | Biblical | 1000-200 BCE | Biblia Hebraica Stuttgartensia Amstelodamensis (1.1 GB) |
| [dss](https://github.com/ETCBC/dss) | Hebrew | Religious | 300 BCE-100 CE | Dead Sea Scrolls (936 MB) |
| [sp](https://github.com/DT-UCPH/sp) | Hebrew | Biblical | 516 BCE-70 CE | Samaritan Pentateuch (147 MB) |
| [extrabiblical](https://github.com/ETCBC/extrabiblical) | Hebrew | Historical | 200 BCE-200 CE | Extra-biblical Hebrew texts |
| [suriano](https://github.com/HuygensING/suriano) | Italian | Historical | 1616-1623 | Diplomatic correspondence |
| [translatin-manif](https://github.com/HuygensING/translatin-manif) | Latin | Literary | Early Modern | Early modern Latin drama analysis |
| [dhammapada](https://github.com/ETCBC/dhammapada) | Pali | Religious | 300 BCE | Ancient Buddhist verses |
| [uruk](https://github.com/Nino-cunei/uruk) | Proto-Cuneiform | Historical | 4000-3100 BCE | Archaic tablets from Uruk |
| [peshitta](https://github.com/ETCBC/peshitta) | Syriac | Biblical | 1000 BCE-900 CE | Syriac Old Testament (55 MB) |
| [syrnt](https://github.com/ETCBC/syrnt) | Syriac | Biblical | 0-1000 CE | Syriac New Testament (52 MB) |
| [syriac](https://github.com/ETCBC/syriac) | Syriac | Religious | Various | Syriac texts collection |
| [cuc](https://github.com/DT-UCPH/cuc) | Ugaritic | Historical | 1223-1172 BCE | Copenhagen Ugaritic Corpus (1.6 MB) |

## Using a Corpus

To use any corpus with Context-Fabric:

1. Clone the repository or download the corpus
2. Point Context-Fabric to the directory containing `.tf` files

```python
from cfabric import Fabric

CF = Fabric('/path/to/corpus')
api = CF.loadAll()
api.makeAvailableIn(globals())
```

On first load, Context-Fabric compiles the corpus to its memory-mapped format (`.cfm` files) for faster subsequent loads.

## Resources

- [Creating Your Own Corpus](https://context-fabric.ai/docs/corpora/creating) — Build a corpus from your data
- [Text-Fabric Corpus Documentation](https://annotation.github.io/text-fabric/tf/about/corpora.html)
- [GitHub text-fabric topic](https://github.com/topics/text-fabric) — Discover community corpora
