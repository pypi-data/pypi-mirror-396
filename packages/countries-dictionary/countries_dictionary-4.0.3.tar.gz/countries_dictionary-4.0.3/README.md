# Countries Dictionary
Countries Dictionary is a data-oriented module which provides dictionaries of countries and states, from members of UN to unrecognised ones.

I created this module as an offline source of countries' information which is easy to access and use by coders.

See [CHANGELOG.md](https://github.com/ThienFakeVN/countries_dictionary/blob/main/CHANGELOG.md) for changes of releases.

Before using, it is recommended to see the code on [GitHub](https://github.com/ThienFakeVN/countries_dictionary/) <!--or the below section--> to understand how the module works and how you can use it.
<!--
## Codes
### Main Countries Dictionary
The Countries Dictionary has a structure like this:
```python
COUNTRIES = {
    "Afghanistan": {
        "formal name": "Islamic Emirate of Afghanistan",
        "motto": "There is no god but God; Muhammad is the messenger of God",
        "continents": ["Asia"],
        "landlocked": True,
        "area": 652864.0,
        "land area": 652230.0,
        "population": 42045000,
        "official languages": ["Dari", "Pashto"],
        "nominal GDP": 16417000000,
        "HDI": 0.496,
        "ISO 3166-1": {"alpha-2": "AF", "alpha-3": "AFG", "numeric": "004"},
    },
    # ...
}
```

### Russia dictionary
The Russia dictionary has a structure like this:
```python
RUSSIA = {
    "Adygea": {
        "federal district": "Southern",
        "economic region": "North Caucasus",
        "landlocked": True,
        "capital/administrative centre": "Maykop",
        "area": 7792.0,
        "population": 501038,
        "ISO 3166-2:RU": "RU-AD",
    },
    # ...
}
```

### United States dictionary
The United States dictionary has a structure like this:
```python
UNITED_STATES = {
    "Alabama": {
        "capital": "Montgomery",
        "date of ratification/establishment/acquiring": "1819.12.14",
        "landlocked": False,
        "area": 135767.0,
        "population": 5024279,
        "House Representatives": 7,
        "ISO 3166-2:US": "US-AL",
    },
    # ...
}
```

### Vietnam dictionary
The Vietnam dictionary has a structure like this:
```python
VIETNAM = {
    "Hanoi": {
        "region": "Red River Delta",
        "landlocked": True,
        "administrative centre": "Hoàn Kiếm ward",
        "area": 3359.84,
        "population": 8807523,
        "ISO 3166-2:VN": "VN-HN",
    },
    # ...
}
```

### Countries Languages
Unused, as of now...

### Quick functions
There are many functions in this submodule.
```python
import countries_dictionary.quick_functions as qf # What have you expected?

# Converts the dictionary into JSON and creates/overwrites a JSON file which contains the converted dictionary
with open("countries_dictionary.json", "w") as f:
    f.write(qf.json_dictionary(indent=4))

# Prints a ISO 3166-2 code of a country
iso = qf.countries_iso_3166_2()
print(iso["Russia"]["ISO 3166-2"])
```

### ISO finder
*ISO finder* is a module which provides a function which has the same name. *ISO finder* can find a country based on the provided ISO code. Note that it does not include US states' postal codes.
```python
from countries_dictionary.iso_finder import iso_finder # 🥀

print(iso_finder("VN"))
print(iso_finder("RUS"))
print(iso_finder("840"))
```

### Unrecognised states
The unrecognised states Dictionary has a structure like this:

```python
UNRECOGNISED_STATES = {
    "Cook Islands": {
        "formal name": "Cook Islands",
        "motto": "",
        "continents": ["Oceania"],
        "landlocked": False,
        "area": 236.0,
        "land area": 236.0,
        "population": 15040,
        "official languages": ["English", "Cook Islands Māori", "Pukapukan"],
        "nominal GDP": 384000000,
        "HDI": 0,
        "ISO 3166-1": {"alpha-2": "CK", "alpha-3": "COK", "numeric": "184"},
    },
    # ...
    # Additional information may be added as comments in the codes
}
```

### Transnistria
The Transnistria Dictionary has a structure like this:
```python
TRANSNISTRIA = {
    "Camenca": {
        "administrative centre": "Camenca",
        "area": 434.5,
        "population": 21000,
    },
    # ...
}
```
-->