from countries_dictionary.quick_functions import countries_iso_3166_2
from countries_dictionary.russia import RUSSIA
from countries_dictionary.united_states import UNITED_STATES
from countries_dictionary.vietnam import VIETNAM

countries = countries_iso_3166_2()

def iso_finder(code: str, info_included: str = None):
    """Returns the name of the country and their chosen information based on the provided ISO code"""
    for x in countries:
        y = countries[x].get(info_included, "") if info_included else ""
        iso_data = countries[x]["ISO 3166-1"]
        if code in (iso_data["alpha-2"], iso_data["alpha-3"], iso_data["numeric"], countries[x]["ISO 3166-2"]): return [x, y]
    raise Exception("No United Nations' member or observer state has this code")

def iso_ru_finder(code: str, info_included: str = None):
    """Returns the name of the Russian federal subject and their chosen information based on the provided ISO code
    (For occupied zones in Ukraine, check the Ukraine dictionary, it hasn't released though)"""
    for x in RUSSIA:
        y = RUSSIA[x].get(info_included, "") if info_included else ""
        if code == RUSSIA[x]["ISO 3166-2:RU"]: return [x, y]
    raise Exception("No Russian federal subject has this code")

def iso_us_finder(code: str, info_included: str = None):
    """Returns the name of the US state or territory and their chosen information based on the provided ISO code"""
    for x in UNITED_STATES:
        y = UNITED_STATES[x].get(info_included, "") if info_included else ""
        if code == UNITED_STATES[x]["ISO 3166-2:US"]: return [x, y]
    raise Exception("No US state or territory has this code")

def iso_vn_finder(code: str, info_included: str = None):
    """Returns the name of the Vietnamese province and their chosen information based on the provided ISO code"""
    for x in VIETNAM:
        y = VIETNAM[x].get(info_included, "") if info_included else ""
        if code == VIETNAM[x]["ISO 3166-2:VN"]: return [x, y]
    raise Exception("No Vietnamese province has this code")
