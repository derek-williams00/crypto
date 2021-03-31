import hashlib

HASH_ALGORITHM = "sha256"
STRING_ENCODING = "utf-8"

# Maps sha-256 hash digest to artifact #TODO: figure out the store
STORE = dict()

# Kinds of Artifacts:
UNK = "UNK" # Unknown
INT = "INT" # Integer
FLT = "FLT" # Floating point number
STR = "STR" # String (actually bytes)
MLT = "MLT" # Multiple labeled fields


#TODO: maintain sorted list of keys in artifact
#TODO: more doc-strings and testing

class Artifact:
    def __init__(self, value=None):
        self.kind = UNK
        self.value = None
        if type(value) == int:
            self.kind = INT
            self.value = value
        elif type(value) == float:
            self.kind = FLT
            self.value = value
        elif type(value) == str:
            self.kind = STR
            self.value = bytes(value, STRING_ENCODING)
        elif type(value) == bytes:
            self.kind = STR
            self.value = value
        elif type(value) == dict: #TODO handle single {"" : X} as X
            self.kind = MLT
            self.value = dict()
            for key, val in value.items():
                if type(key) != str:
                    raise Exception("Artifact label must be a string")
                self.value[key] = Artifact(val)

    def __len__(self):
        if self.kind == INT:
            return 1
        elif self.kind == FLT:
            return 1
        elif self.kind == STR:
            return 1
        elif self.kind == UNK:
            return 0
        elif self.kind == MLT:
            return len(self.value)

    def _hash_pipe(self):
        hsh = hashlib.sha256()
        if self.kind == INT or self.kind == FLT:
            str_val = str(self.value)
            bytes_val = bytes(str_val, STRING_ENCODING)
            hsh.update(bytes_val)
        elif self.kind == STR:
            hsh.update(self.value)
        elif self.kind == MLT:
            keys = list(self.value.keys())
            keys.sort()
            for key in keys:
                hsh.update(bytes(key, STRING_ENCODING))
                hsh.update(self.value[key].permaref())
        return hsh

    def permaref(self):
        '''Permanent content-based reference'''
        hsh = self._hash_pipe()
        return hsh.digest()

    def permaref_hex(self):
        hsh = self._hash_pipe()
        return hsh.hexdigest()

    def __hash__(self):
        hsh = self._hash_pipe()
        hex_digest = hsh.hexdigest()
        return int(hex_digest, 16)

    def __eq__(self, other):
        return self.permaref() == other.permaref()

    def __dict__(self):
        if self.kind == INT or self.kind == FLT or self.kind == STR:
            return {"": self.value}
        elif self.kind == MLT:
            return dict(self.value)
        return dict()

    def __str__(self):
        if self.kind == UNK:
            return "(UNKNOWN ARTIFACT)"
        if self.kind == INT or self.kind == FLT:
            return str(self.value)
        elif self.kind == STR:
            return str(self.value)
        elif self.kind == MLT:
            result = "("
            keys = list(self.value.keys())
            keys.sort()
            for key in keys:
                result += key
                result += ": "
                result += str(self.value[key])
                result += ", "
            return result[:-2] + ")"

    def store(self):
        '''Puts this artifact in the store'''
        if self.kind != INT and self.kind != FLT:
            STORE[hash(self)] = self

    def dispose(self):
        '''Removes this artifact from the store'''
        STORE.pop(hash(self))

