import re

class KomaruTranspiler:
    def __init__(self):
        self.replacements = [
            # Keywords
            (r'\bif_cat\b', 'if'),
            (r'\belse_cat\b', 'else'),
            (r'\belif_cat\b', 'elif'),
            (r'\bwhile_cat\b', 'while'),
            (r'\bfor_cat\b', 'for'),
            (r'\bin_cat\b', 'in'),
            (r'\btry_cat\b', 'try'),
            (r'\bexcept_cat\b', 'except'),
            (r'\bdef_cat\b', 'def'),
            (r'\bclass_cat\b', 'class'),
            (r'\bimport_cat\b', 'import'),
            (r'\bfrom_cat\b', 'from'),
            (r'\bpounce\b', 'continue'),
            (r'\bescape\b', 'break'),
            (r'\bland\b', 'return'),
            
            # Built-ins functions
            (r'\bmeow\b', 'print'),
            (r'\bpurr\b', 'input'),
            (r'\bnap\b', 'time.sleep'),
            (r'\bhunt\b', 'os.walk'),
            (r'\bcatch\b', 'open'),
            (r'\bdrop\b', 'os.remove'),
            (r'\bgroom\b', 'sorted'),
            (r'\bstretch\b', 'len'),
            (r'\bplay\b', 'random.choice'),
            (r'\bchase\b', 'enumerate'),
            (r'\bclimb\b', 'range'),
            (r'\bscratch\b', 'str'),
            (r'\blick\b', 'int'),
            (r'\bbite\b', 'float'),
            (r'\bcuddle\b', 'list'),
            (r'\bpounce_on\b', 'dict'),
            (r'\bmark\b', 'set'),
            (r'\bgrowl\b', 'max'),
            (r'\bwhimper\b', 'min'),
            (r'\byowl\b', 'sum'),
        ]

    def transpile(self, code):
        """
        Transpiles KomaruScript code into Python code.
        """
        transpiled_code = code
        
        # Apply regex replacements
        for pattern, replacement in self.replacements:
            transpiled_code = re.sub(pattern, replacement, transpiled_code)
            
        # Add necessary coding header and imports for built-ins that might be used
        # We inject these standard libraries so nap(), play(), etc work out of the box
        header = "import time\nimport random\nimport os\nimport sys\n\n"
        
        return header + transpiled_code
