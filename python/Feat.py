import copy

class Feat:
    def __init__(self, rawfeat):
        self.raw = rawfeat
        self.name = rawfeat["name"]
        self.deps = [] if not rawfeat["prerequisite_feats"] else rawfeat["prerequisite_feats"].split(", ")
    
        self.parents = []
        self.children = [] 

    def __lt__(self, other):
        return self.name < other.name
     
    def chainstr(self, treedict):
        def buildchain(f, tree):
            return {} if not f.children else { tree[child].name : buildchain(tree[child], tree) for child in f.children }
 
        def buildchainstring(tree, parent, chaindict, cursor):
            seperator = " -> "
            base = ""
            for key in sorted(chaindict.keys()):
                if not key == sorted(chaindict.keys())[0]:
                    base += (" " * (cursor - len(seperator)))
                    base += seperator
                base += key
                otherparents = copy.deepcopy(tree[key].parents)
                if parent in otherparents: otherparents.remove(parent)
                parentstr = ""
                if otherparents:
                    parentstr += " ("
                    parentstr += ",".join(otherparents)
                    parentstr += ")"
                base += parentstr
                if chaindict[key]:
                    base += seperator
                    newcursor = cursor + len(seperator) + len(key) + len(parentstr)
                    base += buildchainstring(tree,key, chaindict[key], newcursor)
                else:
                    base += "\n"
            return base 


        return buildchainstring(treedict, "", {self.name : buildchain(self, treedict)}, 0)

    def briefstr(self):
        return self.raw["name"] + " - " + self.raw["description"]

    def __str__(self):
        def maybeAppendKey(key, raw, lines): 
            if raw[key]:
                lines.append(key.replace("_", " ").capitalize() + ": " + raw[key])
                return True
            return False

        lines = []
        lines.append(self.briefstr())
        maybeAppendKey("types", self.raw, lines)
        maybeAppendKey("prerequisites", self.raw, lines)

        for key in ["special", "benefit", "normal", "goal", "completion_benefit"]:
            if maybeAppendKey(key, self.raw, lines): lines.append("")

        return "\n".join(lines) 


       
