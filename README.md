# po-translator

## Usage

**Library**

```python
from po_translator.translator import POFileTranslator

file = POFileTranslator(
    path="example.po",
    api="google",
    source_lang="en",
    target_lang="tr",
)

file.translate()
file.save()
```

**CLI**

```bash
po-translator example.po --api google -s en -t tr
```