weatherDictionary = [
    ["MI", "Shallow"],
    ["PR", "Partial"],
    ["BC", "Patches"],
    ["DR", "Low Drifting"],
    ["BL", "Blowing"],
    ["SH", "Showers"],
    ["TS", "Thunderstorms"],
    ["FZ", "Freezing"],
    ["DZ", "Drizzle"],
    ["RA", "Rain"],
    ["SN", "Snow"],
    ["SG", "Snow Grains"],
    ["IC", "Ice Crystals"],
    ["PL", "Ice Pellets"],
    ["GR", "Hail"],
    ["GS", "Snow Pellets"],
    ["UP", "Unknown Precipitation"],
    ["BR", "Mist"],
    ["FG", "Fog"],
    ["FU", "Smoke"],
    ["VA", "Volcanic Ash"],
    ["DU", "Widespread Dust"],
    ["SA", "Sand"],
    ["HZ", "Haze"],
    ["PY", "Spray"],
    ["PO", "Dust Devils"],
    ["SQ", "Squalls"],
    ["FC", "Funnel Cloud"],
    ["SS", "Sandstorm"],
    ["DS", "Dust Storm"]
]

modifiersDictionary = [
    ["-", "Light"],
    ["+", "Heavy"],
    ["VC", "Nearby"],
    ["P", "More than"],
    ["M", "Less than"]
] 

skyDictionary = [
    ["BKN", "Broken"],
    ["CB", "Cumulonimbus"],
    ["CLR", "Sky Clear Below 12K AGL"],
    ["FEW", "Few Clouds"],
    ["OVC", "Overcast"],
    ["OVX", "Sky Obscured"],
    ["SCT", "Scattered Clouds"],
    ["SKC", "Sky Clear"],
    ["TCU", "Towering Cumulus"],
    ["CAVOK", "Cloud and Visibility OK"],
    ["VV", "Vertical Visibility"]
]

windDictionary = [
    ["00000", "Calm"],
    ["VRB", "Variable "],
    ["G", " Gusting "],
    ["P", " Greater Than "],
    ["KPH", " Kilometers/Hour"],
    ["MPS", " Meters/Second"],
    ["KT", " Knots"],
]

def translateModifiers(modString):
    result = modString if modString is not None else ""
    for kvpa in modifiersDictionary:
        result = result.replace(kvpa[0], kvpa[1] + " ")
    return result.strip()

def translateWeather(wxString):
    result = wxString if wxString is not None else ""
    for kvpa in weatherDictionary:
        result = result.replace(kvpa[0], kvpa[1] + " ")
    return translateModifiers(result)

def translateSky(skyString):
    result = skyString if skyString is not None else ""
    for kvpa in skyDictionary:
        result = result.replace(kvpa[0], kvpa[1] + " ")
    return  translateModifiers(result)

def translateWind(windString): 
    result = windString if windString is not None else ""
    for kvpa in windDictionary:
        result = result.replace(kvpa[0], kvpa[1])
    return  result.strip()

def translateCloudLayer(layer):
    #sample {"cover": "BKN","base": 9000}
    cover = translateSky(layer["cover"])
    base = layer["base"]
    return f"{cover} @ {base} AGL"
