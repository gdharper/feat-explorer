import csv
import subprocess
import platform

##########################################################################################
# Global Constants and Context
##########################################################################################
inFile = "Feats.csv"
titleString = "Pathfinder Feat Explorer! Updated Jan 3, 2019\n"
         
filtKeys = set(["name", "types", "description", "benefits", "source", "prerequisites",
                "prerequisite_feats", "prerequisite_skills", "prerequisite_race"])

featList = []
featDict = {}
sources = []
filt = {}
filtList = []

#########################################################################################
# UI "Prettiness"
#########################################################################################
def featToString_Brief(feat):
    return feat["name"] + " - " + feat["description"]

def featToString(feat):
    lines = [featToString_Brief(feat),
             "Type(s): " + feat["types"],
             "Prerequisistes: " + feat["prerequisites"], 
             feat["benefit"]]
    return "\n".join(lines)

def featToString_Full(feat):
    return featToString(feat)

def filterToString(filtDict):
    filtStr = ""
    for k in [k for k in filtKeys if filt[k]]:
        inc = [key for key in filt[k].keys() if filt[k][key]]
        exc = [key for key in filt[k].keys() if not filt[k][key]]
        filtStr += "\t" + k + ": \n"
        if inc:
            filtStr += "\t\tIncludes: " + ", ".join(inc) + "\n"
        if exc:
            filtStr += "\t\tExcludes: " + ", ".join(exc) + "\n"

    return filtStr

def print_filter_state():
    fstr = filterToString(filt)
    if not fstr:
        fstr = "No Filter\n"
    else:
        fstr = "\n" + fstr
    print("Current Filter State: " + fstr)

def clearConsole():
    _ = subprocess.run("cls" if platform.system() == "Windows" else "clear", shell = True)
    print(titleString)

#########################################################################################
# State Actions
#########################################################################################
def view_feats():
    print("\n".join(map(featToString_Brief, filtList)))
    _ =input("\nPress [Enter] to return to initial program menu: ")
    return "base_menu"

def view_tree():
    print("view_tree")
    return "base_menu"

def tweak_filter_element(key):
    clearConsole()
    print_filter_state()
    print("Modifying filter based on feat " + key)

    if key == "prerequisites":
        print("select prerequisite type to filter:")
        options = { "1": ("General prerequisites", "prerequisites"),
                    "2": ("Prerequisite feats", "prerequisite_feats"),
                    "3": ("Prerequisite skills", "prerequisite_skills"),
                    "4": ("Prerequisite races", "prerequisite_race"),
                    "q": ("Return to previous menu", "")}

        opts = [k + " : " + v[0] for k,v in options.items()]
        print("\t " + "\n\t ".join(opts))

        response = ""
        while response not in options.keys(): response = input("Selection: ")
        if response == "q": return
        else: key = options[response][1]

    while filt[key]:
        response = input("Would you like to clear filtering based on feat " + key + " [yes/no] ? ").lower()
        if "yes".find(response) == 0:
            filt[key].clear()
            print("Removed filtering.")
        elif "no".find(response) == 0: break

    response = input("Term to add to filter: ").lower()
    while True:
        resp = input("[Include/Exclude] " + response +" from feat " + key + ": ").lower()
        if "include".find(resp) == 0:
            filt[key][response] = True
            break
        elif "exclude".find(resp) == 0:
            filt[key][response] = False 
            break

    print("Filtering selection to feats where feat " + key + " " + resp + "s " + response)
    print_filter_state()    

def modify_filter():
    print_filter_state()
    print("Select filter criteria to modify")
    options = {"0" : "Clear Filter",
               "1" : "name",
               "2" : "types",
               "3" : "description",
               "4" : "benefits",
               "5" : "source",
               "6" : "prerequisites",
               "q" : "Return"}

    for k,v in options.items():
        if k in ["0", "q"]: print("\t" + k + " : " + v)
        else: print("\t" + k + " : Edit filtering based on: " + v)

    key = input("Enter selection: ")
    while key not in options.keys(): key = input("INvalid selection.\nEnter selection: ")

    if key == "0": map(lambda k: filt[k].clear(), filt.keys())
    elif key == "q": return "edit_filter"
    else: tweak_filter_element(options[key])   

    while True:
        cont = input("Would you like to continue editing the filter? [yes/no]").lower()
        if "yes".find(cont) == 0: return "modify_filter"
        elif "no".find(cont) == 0: return "edit_filter"

def do_filter(feat):
    for k in [s for s in filt.keys() if filt[s]]:
        for key in filt[k].keys():
            if not ((key in feat[k].lower()) == filt[k][key]):
                return False
    return True

def apply_filter():
    print("Filtering feats")
    filtList.clear()
    filtList.extend([f for f in featList if do_filter(f)])
    return "edit_filter"

def print_feat():
    featName = input("Enter the name of the feat you wish to view: ").lower()
    if featName not in featDict: print("Invalid feat name")
    else: print(featToString_Full(featDict[featName]))

    while True:
        retry = input("Would you like to view another feat? [yes/no]").lower()
        if "yes".find(retry) == 0: return "print_feat"
        elif "no".find(retry) == 0: return "base_menu"


###############################################################################################################
# State Table
###############################################################################################################
states = {"base_menu" : {"transitions" : {"f" : ("edit_filter", "Update or apply current filter"),
                                          "v" : ("view_feats", "View filtered feat selection or output to file"),
                                          "t" : ("view_tree", "View filtered feat selection as dependency tree"),
                                          "p" : ("print_feat", "View a specific feat in the console"),
                                          "x" : ("exit", "Exit program")}},
          "edit_filter" : {"transitions" : {"m" : ("modify_filter", "Change elements of current filter"),
                                            "a" : ("apply_filter", "Apply current filter to feat database"),
                                            "b" : ("base_menu", "Return to initial program menu")}},
          "view_feats" : {"action" : view_feats},
          "view_tree" : {"action" : view_tree},
          "modify_filter" : {"action" : modify_filter},
          "apply_filter" : {"action" : apply_filter},
          "print_feat" : {"action" : print_feat},
          "exit" : {"action" : quit}}

###############################################################################################################
# Main Program Functionality
###############################################################################################################
def outputProgramState(transitions):
    print_filter_state()
    print("Number of feats in filtered selection: " + str(len(filtList)))

    print("Possible actions")
    for key, value in transitions.items(): print("\t" + key + " : " + value[1])

def executeState(state):
    clearConsole()

    if "action" in states[state]:
        return states[state]["action"]()
    
    transitions = states[state]["transitions"]
    outputProgramState(transitions)

    action = input("Please enter a selection: ")
    return transitions.get(action, (state, ""))[0]

if __name__ == "__main__":
    with open(inFile, "r") as csvFile:
        reader = csv.DictReader(csvFile)
        for row in reader:
            featList.append(row)
            featDict[row["name"].lower()] = row
            filtList.append(row)
            sources.append(row["source"])

    for k in filtKeys: filt[k] = {}

    current_state = "base_menu"
    while True: current_state = executeState(current_state)
        