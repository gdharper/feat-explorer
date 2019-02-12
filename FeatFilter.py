
class Filter: 
    def __init__(self):
        self.filter = {}

    def addKeyInclude(self, key, value):
        if key not in self.filter: self.filter[key] = {}
        self.filter[key][value] = True

    def addKeyExclude(self, key, value):
        if key not in self.filter: self.filter[key] = {}
        self.filter[key][value] = False

    def apply(self, rawfeat):
        for key in self.filter.keys():
            for term in self.filter[key].keys():
                if (term in rawfeat[key].lower()) != self.filter[key][term]:
                        return False
        return True

    def containsKey(self, key):
        return key in self.filter

    def clearKey(self, key):
        if key in self.filter: self.filter[key].clear()

    def clear(self):
        self.filter = {}

    def __str__(self):
        if any(self.filter.values()):
            filtstr = ""
            for k in [key for key in self.filter.keys() if self.filter[key]]:
                inc = [key for key in self.filter[k].keys() if self.filter[k][key]]
                exc = [key for key in self.filter[k].keys() if not self.filter[k][key]]
                filtstr += "\t" + k + ": \n"
                if inc: filtstr += "\t\tIncludes: " + ", ".join(inc) + "\n"
                if exc: filtstr += "\t\tExcludes: " + ", ".join(exc) + "\n"
            return filtstr;
        else:
            return "No filter\n"

