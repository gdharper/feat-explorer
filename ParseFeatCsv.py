import csv
from shutil import copyfile

featTypes = ["achievement", "armor_mastery", "betrayal", "blood_hex", "combat", 
             "critical", "esoteric", "faction", "familiar", "general", "grit",
             "item_creation", "item_mastery", "meditation", "metamagic", "monster",
             "mythic", "panache", "performance", "racial", "shield_mastery", 
             "stare", "story", "style", "targeting", "teamwork", "trick", "weapon_mastery"]

featKeys = set(["name", "description", "prerequisites", "prerequisite_feats", "benefit", "normal", 
                "special", "source", "goal", "completion_benefit", "suggested_traits", "prerequisite_skills"])
    

def parseFeatRow(row):
    feat = {}
    for key in featKeys: feat[key] = row[key]

    # Rename this field
    feat["prerequisite_race"] = row["race_name"]
    
    types = set()
    for typ in featTypes: 
        if typ.lower() in row["type"].lower() or row.get(typ, "") == "1": types.add(typ)
        
    # Special cases because of shitty csv
    if "Item Creation".lower() in row["type"].lower(): types.add("item_creation")
    if "Item Mastery".lower() in row["type"].lower(): types.add("item_mastery")
    if row["companion_familiar"] == "1": types.add("familiar")

    # Special case becasue of crappy escaping in csv
    if "mythic" in types: feat["name"] = "Mythic " + feat["name"]

    feat["types"] = "/".join(types)

    return feat


iFile = "FeatsBase.csv"
oFile = "Feats.csv"

feats = []
with open(iFile, 'r') as csvFile:
    reader = csv.DictReader(csvFile)
    feats.extend(map(parseFeatRow, reader))

outkeys = ["name", "types", "prerequisites", "description", "benefit", "normal", "special", "goal",
           "completion_benefit", "prerequisite_feats", "prerequisite_skills", "prerequisite_race", "suggested_traits", "source"]

with open(oFile, "w") as outCsv:
    writer = csv.DictWriter(outCsv, outkeys)
    writer.writeheader()
    writer.writerows(feats)

copyfile(oFile, oFile+".bak")
