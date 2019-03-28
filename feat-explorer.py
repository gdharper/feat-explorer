from collections import OrderedDict
import copy
import csv
from Feat import Feat
from FeatFilter import Filter
import platform
import subprocess
import sys

titleString = "Pathfinder Feat Explorer - Updated Jan 3, 2019\n"
def clearConsole():
    _=subprocess.run("cls" if platform.system() == "Windows" else "clear", shell = True)


class ProgramState:
    filtKeys = set(["name"," types","description","benefit","source","prerequisites",
                    "prerequisite_feats","prerequisite_skills","prerequisite_race"])

    def __init__(self, featList, stateTable, initialState):
        self.current_state = initialState
        self.states = stateTable
        self.filter = Filter()
        self.featlist = featList
        self.featdict = { f.name : f for f in self.featlist }
        self.selection = [] 

        # Enumerate all parent child relationships
        for f in self.featlist:
            for dep in f.deps:
                self.featdict[dep].children.append(f.name)
                f.parents.append(dep)

        # Remove nested parent-child links
        for f in self.featlist:
            toremove = set()
            for p in f.parents:
                for p_ in f.parents:
                    if p_ in self.featdict[p].parents:
                        toremove.add(p_)
            for n in toremove:
                f.parents.remove(n) 
                self.featdict[n].children.remove(f.name)

        self.applyFilter();  

    def executeState(self):
        clearConsole()
        print(titleString)
        self.current_state = self.states[self.current_state](self)

    def applyFilter(self):
        self.selection = [ f for f in self.featlist if self.filter.apply(f.raw) ]

    def tweakFilter(self, k):
        def prereq_type():
            print("Select prerequisite type to filter:")
            options = OrderedDict()
            options["1"] = ("General prerequisites", "prerequisites")
            options["2"] = ("Prerequisite feats", "prerequisite_feats")
            options["3"] =("Prerequisite skills", "prerequisite_skills")
            options["4"] = ("Prerequisite races", "prerequisite_race")
            print("\t " + "\n\t ".join([k+" : "+v[0] for k,v in options.items()]))
            response = input("Selection: ")
            while response not in options.keys(): response = input("Selection: ")
            return options[response][1]

        if k == "Clear Filter":
            self.filter.clear()
            return

        clearConsole()
        print(self)
        print("Modifying filter based on feat " + k)
    
        k = prereq_type() if k == "prerequisites" else k 
    
        if self.filter.containsKey(k):
            response = input("Clear filtering based on feat "+k+" [yes/no] ? ").lower()
            if "yes".find(response) == 0: state.filter.clearKey(k)

        term  = input("Term to add to filter: ").lower()
        while True:
            resp = input("[Include/Exclude] "+term+" from feat "+k+": ").lower()
            if "include".find(resp) == 0:
                self.filter.addKeyInclude(k, term)
                break
            elif "exclude".find(resp) == 0:
                self.filter.addKeyExclude(k, term)
                break

        print(self)    


    def __str__(self):
         return "Current filter state:\n"+str(self.filter)+"\n"+"Feats in current selection: "+str(len(self.selection))


########################################################################################
# State Actions
########################################################################################

def getViewString(selection):
    detailed = input("Output detailed feat information [yes/no] ? ").lower()
    return  "\n\n".join([str(f) for f in selection] \
                        if "yes".find(detailed) == 0 \
                        else [f.briefstr() for f in selection]) + "\n"

def view_feats(state):
    print(getViewString(state.selection))
    resp = input("View specific feat(s) in detail [yes/no]? ")
    if "yes".find(resp) == 0: _ = print_feat(state)
    return "do_filter"

def output_feats(state):
    outfile = input("Path to file for filtered selection output: ")
    with open(outfile, "w") as f:
        f.write(getViewString(state.selection))
    return "do_filter"
 
def output_tree(state):
    print(state)

    rootfeats = set()
    for f in state.selection:
        add = True
        for p in f.parents:
            if state.featdict[p] in state.selection: add = False
        if add: rootfeats.add(f)
   
    outstr = "\n".join([f.chainstr(state.featdict) for f in rootfeats])
    
    outfile = input("Output file path? [Empty String to print to console] ")
    if not outfile:
        print(outstr)
        _ = input("Press [Enter] to return to previous menu ")
    else:
        with open(outfile, "w") as ofile:
            ofile.write(outstr)
    
    return "do_filter"



def modify_filter(state):
    print(state)
    print("Select filter criteria to modify")
    options = OrderedDict()
    options["0"] = "Clear Filter"
    options["1"] = "name"
    options["2"] = "types"
    options["3"] = "description"
    options["4"] = "benefit"
    options["5"] = "source"
    options["6"] = "prerequisites"
    options["q"] = "Return"

    for k, v in options.items():
        if k in ["0", "q"]: print("\t" + k + " : " + v)
        else: print("\t" + k + " : Edit filtering based on: " + v)

    k = input("Enter selection: ")
    while k not in options.keys(): k = input("Invalid selection.\nEnter selection: ")

    if k == "q":
        return "do_filter"
    else: 
        state.tweakFilter(options[k])   

    while True:
        cont = input("Continue editing the filter [yes/no] ? ").lower()
        if "yes".find(cont) == 0: return "modify_filter"
        elif "no".find(cont) == 0: return "do_filter"

def apply_filter(state):
    state.applyFilter()
    return "do_filter"

def print_feat(state):
    featdict = { k.lower() : v for (k,v) in state.featdict.items() }

    while True:
        name = input("Enter the name of the feat you wish to view: ").lower()
        print()
        if name not in featdict.keys():
            print("Invalid feat name")
        else:
            print(featdict[name])
            print()
            tree = input("View child feats of " + name + " [yes/no] ? ").lower()
            if "yes".find(tree) == 0:
                print(featdict[name].chainstr(state.featdict))
                print()

        retry = input("View another feat? [yes/no]? ").lower()
        if "no".find(retry) == 0: return "base_menu"

def exit_program(_):
    clearConsole()
    quit() 

def simple_state(options):
    print("Possible actions:")
    for k, v in options.items(): print("\t"+k+" : "+v[1])
    print()
    
    k = input("Please enter a selection: ")
    while k not in options.keys():
        k = input("Invalid selection.\nPlease enter a selection: ")
    return options[k][0] 

def do_filter(state):
    print(state)
    options = OrderedDict()
    options["m"] = ("modify_filter",    "Change elements of current filter")
    options["a"] = ("apply_filter",     "Apply current filter to feat database")
    options["v"] = ("view_feats",       "View filtered selection")
    options["o"] = ("out_feats",        "Output filtered selection to file")
    options["t"] = ("out_tree",         "View feat tree for current selection")
    options["b"] = ("base_menu",        "Return to initial program menu")
    return simple_state(options)

def base_menu(_):
    options = OrderedDict() 
    options["f"] = ("do_filter", "Filter feat database and view filtered selection")
    options["p"] = ("print_feat", "View information for a specific feat")
    options["x"] = ("exit_program", "Exit program")
    return simple_state(options)

########################################################################################
# State Table
########################################################################################
states = {"base_menu" : base_menu,
          "do_filter" : do_filter,
          "view_feats" : view_feats,
          "out_feats" : output_feats,
          "out_tree" : output_tree,
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
    
    rawfeats = []
    with open(iFile, "r") as csvFile:
        reader = csv.DictReader(csvFile)
        rawfeats = [row for row in reader]

    feats = [Feat(raw) for raw in rawfeats]
    state = ProgramState(feats, states, "base_menu")
    while True:
        state.executeState()
       
