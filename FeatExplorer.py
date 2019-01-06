from collections import OrderedDict
import csv
import platform
import subprocess
import sys

########################################################################################
# Global Constants and Context
########################################################################################
titleString = "Pathfinder Feat Explorer - Updated Jan 3, 2019\n"

class ProgramState:
    filtKeys = set(["name","types","description","benefits","source","prerequisites",
                    "prerequisite_feats","prerequisite_skills","prerequisite_race"])

    def __init__(self, featList, initialState):
        self.current_state = initialState
        self.filt = {}
        for k in ProgramState.filtKeys: self.filt[k] = {}
        self.featList = featList
        self.filteredSelection = []
        self.applyFilter()
 
    def clearFilterElement(self, key):
        self.filt[key].clear()

    def clearFilter(self):
        for key in self.filt.keys():
            self.clearFilterElement(key)

    def printFilterState(self):
        print("Current filter state:")
        if not any(self.filt.values()):
            print("No filter\n")
        else:
            filtStr = ""
            for k in filter(lambda k: self.filt[k] != {}, self.filt.keys()):
                inc = [key for key in self.filt[k].keys() if self.filt[k][key]]
                exc = [key for key in self.filt[k].keys() if not self.filt[k][key]]
                filtStr += "\t" + k + ": \n"
                if inc: filtStr += "\t\tIncludes: " + ", ".join(inc) + "\n"
                if exc: filtStr += "\t\tExcludes: " + ", ".join(exc) + "\n"
            print(filtStr)
        print("Feats in current selection: "+str(len(self.filteredSelection)))

    def containsFilter(self, k):
        return self.filt[k] != {}

    def requireValueIn(self, value, element):
        self.filt[element][value] = True

    def filterValueFrom(self, value, element):
        self.filt[element][value] = False

    def applyFilter(self):
        def do_filter(filt, feat):
            for k in filt.keys():
                for key in filt[k].keys():
                    if (key in feat[k].lower()) != filt[k][key]: return False
            return True

        self.filteredSelection = [f for f in self.featList if do_filter(self.filt, f)]


########################################################################################
# UI "Prettiness"
########################################################################################
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

def clearConsole():
    _=subprocess.run("cls" if platform.system() == "Windows" else "clear", shell = True)

########################################################################################
# State Actions
########################################################################################
def view_feats(state):
    print("\n".join(map(featToString_Brief, state.filteredSelection)))
    print() 
    resp = input("View a feat in detail [yes/no]? ")
    if "yes".find(resp) == 0: _=print_feat(state)
    _=input("\nPress [Enter] to return to filtering menu: ")
    return "edit_filter"

def view_tree(state):
    print("view_tree")
    return "base_menu"

def determine_prereq_type():
    print("select prerequisite type to filter:")
    options = OrderedDict()
    options["1"] = ("General prerequisites", "prerequisites")
    options["2"] = ("Prerequisite feats", "prerequisite_feats")
    options["3"] =("Prerequisite skills", "prerequisite_skills")
    options["4"] = ("Prerequisite races", "prerequisite_race")

    opts = [k + " : " + v[0] for k, v in options.items()]
    print("\t " + "\n\t ".join(opts))

    response = input("Selection: ")
    while response not in options.keys(): response = input("Selection: ")
    return options[response][1]

def tweak_filter_element(state, k):
    clearConsole()
    state.printFilterState()
    print("Modifying filter based on feat " + k)
    
    if k == "prerequisites": k = determine_prereq_type()
    if state.containsFilter(k):
        response = input("Clear existing filtering based on feat " + k + " [yes/no] ? ").lower()
        if "yes".find(response) == 0: state.clearFilterElement(k)

    response = input("Term to add to filter: ").lower()
    while True:
        resp = input("[Include/Exclude] "+response+" from feat "+k+": ").lower()
        if "include".find(resp) == 0:
            state.requireValueIn(response, k)
            break
        elif "exclude".find(resp) == 0:
            state.filterValueFrom(response, k)
            break

    state.printFilterState()    

def modify_filter(state):
    state.printFilterState()
    print("Select filter criteria to modify")
    options = OrderedDict()
    options["0"] = "Clear Filter"
    options["1"] = "name"
    options["2"] = "types"
    options["3"] ="description"
    options["4"] = "benefits"
    options["5"] = "source"
    options["6"] = "prerequisites"
    options["q"] = "Return"

    for k, v in options.items():
        if k in ["0", "q"]: print("\t" + k + " : " + v)
        else: print("\t" + k + " : Edit filtering based on: " + v)

    k = input("Enter selection: ")
    while k not in options.keys(): k = input("Invalid selection.\nEnter selection: ")

    if k == "0": state.clearFilter() 
    elif k == "q": return "edit_filter"
    else: tweak_filter_element(state, options[k])   

    while True:
        cont = input("Continue editing the filter? [yes/no]? ").lower()
        if "yes".find(cont) == 0: return "modify_filter"
        elif "no".find(cont) == 0: return "edit_filter"

def apply_filter(state):
    print("Filtering feats")
    state.applyFilter()
    return "edit_filter"

def print_feat(state):
    featDict = {}
    for feat in state.featList:
        featDict[feat["name"].lower()] = feat
    
    while True: 
        featName = input("Enter the name of the feat you wish to view: ").lower()
        print()
        if featName not in featDict: print("Invalid feat name")
        else: print(featToString_Full(featDict[featName]))
        print()
        while True:
            retry = input("View another feat? [yes/no]? ").lower()
            if "no".find(retry) == 0: return "base_menu"
            elif "yes".find(retry) == 0: break

def exit_program(_):
    clearConsole()
    quit()

def simple_state(options):
    def print_option(k, v): 
        print("\t"+k+" : "+v[1])

    print("Possible actions:")
    for k, v in options.items(): print_option(k, v)
    print()
    
    k = input("Please enter a selection: ")
    while k not in options.keys():
        k = input("Invalid selection.\nPlease enter a selection: ")
    return options[k][0]

def edit_filter(state):
    state.printFilterState()
    options = OrderedDict()
    options["m"] = ("modify_filter", "Change elements of current filter")
    options["a"] = ("apply_filter", "Apply current filter to feat database")
    options["v"] = ("view_feats", "View filtered selection or output to file")
    options["b"] =  ("base_menu", "Return to initial program menu")
    return simple_state(options)

def base_menu(_):
    options = OrderedDict()
    options["f"] = ("edit_filter", "Filter feat database and view filtered selection")
    options["p"] = ("print_feat", "View a specific feat in the console")
    options["t"] = ("view_tree", "View full feat tree")
    options["x"] = ("exit_program", "Exit program")
    return simple_state(options)

########################################################################################
# State Table
########################################################################################
states = {"base_menu" : base_menu,
          "edit_filter" : edit_filter,
          "view_feats" : view_feats,
          "view_tree" : view_tree,
          "modify_filter" : modify_filter,
          "apply_filter" : apply_filter,
          "print_feat" : print_feat,
          "exit_program" : exit_program}

########################################################################################
# Main Program Functionality
########################################################################################
if __name__ == "__main__":
    if len(sys.argv) > 1: iFile = sys.argv[1]
    else:
        print(titleString)
        iFile = input("Path to feat csv file: ")
    
    featList = []
    with open(iFile, "r") as csvFile:
        reader = csv.DictReader(csvFile)
        for row in reader: 
            featList.append(row)

    state = ProgramState(featList, "base_menu")
    while True:
        clearConsole()
        print(titleString)
        state.current_state = states[state.current_state](state)

