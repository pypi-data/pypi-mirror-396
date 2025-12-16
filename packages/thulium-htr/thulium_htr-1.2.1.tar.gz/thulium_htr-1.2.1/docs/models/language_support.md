# Language Support

Thulium supports 52+ languages across 10 writing scripts.

## Supported Languages

### Latin Script (30 languages)

| Code | Language | Region |
|------|----------|--------|
| `en` | English | Global |
| `de` | German | Western Europe |
| `fr` | French | Western Europe |
| `es` | Spanish | Western Europe |
| `it` | Italian | Western Europe |
| `pt` | Portuguese | Western Europe |
| `nl` | Dutch | Western Europe |
| `pl` | Polish | Eastern Europe |
| `cs` | Czech | Eastern Europe |
| `hu` | Hungarian | Eastern Europe |
| `ro` | Romanian | Eastern Europe |
| `sv` | Swedish | Scandinavia |
| `nb` | Norwegian (Bokmål) | Scandinavia |
| `nn` | Norwegian (Nynorsk) | Scandinavia |
| `da` | Danish | Scandinavia |
| `fi` | Finnish | Scandinavia |
| `is` | Icelandic | Scandinavia |
| `lt` | Lithuanian | Baltic |
| `lv` | Latvian | Baltic |
| `et` | Estonian | Baltic |
| `tr` | Turkish | Middle East |
| `az` | Azerbaijani | Caucasus |
| `id` | Indonesian | Southeast Asia |
| `ms` | Malay | Southeast Asia |
| `vi` | Vietnamese | Southeast Asia |
| `tl` | Filipino | Southeast Asia |
| `sw` | Swahili | Africa |
| `hr` | Croatian | Balkans |
| `sr-latn` | Serbian (Latin) | Balkans |
| `sl` | Slovenian | Balkans |

### Cyrillic Script (8 languages)

| Code | Language | Region |
|------|----------|--------|
| `ru` | Russian | Eastern Europe |
| `uk` | Ukrainian | Eastern Europe |
| `be` | Belarusian | Eastern Europe |
| `bg` | Bulgarian | Balkans |
| `mk` | Macedonian | Balkans |
| `sr` | Serbian (Cyrillic) | Balkans |
| `kk` | Kazakh | Central Asia |
| `mn` | Mongolian | East Asia |

### Arabic Script (4 languages)

| Code | Language | Direction |
|------|----------|-----------|
| `ar` | Arabic | RTL |
| `fa` | Persian | RTL |
| `ur` | Urdu | RTL |
| `ps` | Pashto | RTL |

### Hebrew Script

| Code | Language | Direction |
|------|----------|-----------|
| `he` | Hebrew | RTL |
| `yi` | Yiddish | RTL |

### Greek Script

| Code | Language |
|------|----------|
| `el` | Greek |

### Georgian Script

| Code | Language |
|------|----------|
| `ka` | Georgian |

### Armenian Script

| Code | Language |
|------|----------|
| `hy` | Armenian |

### Devanagari Script

| Code | Language |
|------|----------|
| `hi` | Hindi |
| `mr` | Marathi |
| `ne` | Nepali |

### CJK (Chinese, Japanese, Korean)

| Code | Language | Script |
|------|----------|--------|
| `zh` | Chinese | Hanzi |
| `ja` | Japanese | Kanji + Kana |
| `ko` | Korean | Hangul |

### Other Indic Scripts

| Code | Language | Script |
|------|----------|--------|
| `bn` | Bengali | Bengali |
| `ta` | Tamil | Tamil |
| `te` | Telugu | Telugu |
| `th` | Thai | Thai |

## Usage

### Single Language

```python
from thulium import recognize_image

result = recognize_image("german_letter.png", language="de")
```

### Language Detection

```python
from thulium import recognize_image

result = recognize_image("document.png", language="auto")
print(f"Detected: {result.detected_language}")
```

### Language Profile Access

```python
from thulium.data.language_profiles import get_language_profile

profile = get_language_profile("de")
print(f"Name: {profile.name}")
print(f"Script: {profile.script}")
print(f"Alphabet: {profile.alphabet}")
```

## Script-Specific Processing

### Right-to-Left Scripts

Arabic, Hebrew, Persian, and Urdu are processed with automatic RTL handling:

```python
result = recognize_image("arabic.png", language="ar")
# Returns properly ordered RTL text
```

### CJK Scripts

Chinese, Japanese, and Korean use specialized tokenization:

```python
result = recognize_image("japanese.png", language="ja")
# Handles mixed Kanji/Hiragana/Katakana
```

## See Also

- [Model Zoo](model_zoo.md) — Pretrained models
- [Benchmarks](../evaluation/benchmarks.md) — Per-language metrics
