
class Meta:

    def __init__(self, process):
        self.process = process

class Alignment:

    def __init__(self, id, source_ids, target_ids, meta):
        self.id = id
        self.source_ids = source_ids
        self.target_ids = target_ids
        self.meta = meta

    def addAlignedPair(self, source_id, target_id):
        self.source_ids.append(source_id)
        self.target_ids.append(target_id)

class AlignmentSet:

    def __init__(self, alignments):
        self.alignments = alignments

    def addAlignment(self, alignment):
        self.alignments.append(alignment)

    def removeAlignment(self, alignment):
        self.alignments.remove(alignment)

    def fetchAlignmentById(self, id):

        fetchedAlignment = next ( 
            (alignment for alignment in self.alignments if alignment.id == id), 
            None)
        
        return fetchedAlignment
    
    def fetchAlignmentBySourceId(self, source_id):

        fetchedAlignment = next ( 
            (alignment for alignment in self.alignments if alignment.source_ids.contains(source_id)), 
            None)
        
        return fetchedAlignment
    
    def fetchAlignmentByTargetId(self, target_id):

        fetchedAlignment = next ( 
            (alignment for alignment in self.alignments if alignment.target_ids.contains(target_id)), 
            None)
        
        return fetchedAlignment

class AlignmentSetManager:

    def __init__(self, alignmentSet):
        self.alignmentSet = alignmentSet

    

def convert_to_dict(obj):
    #if isinstance(obj, (Meta, Alignment)):
    return obj.__dict__
    #return obj


import json

meta = Meta("manual")

alignment = Alignment("66022021.9", ["66022021007"], ["660220210131"], meta)

json_str = json.dumps(alignment, default=convert_to_dict, indent=2)

print(json_str)
   