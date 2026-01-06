from datetime import *  # rule 5: wildcard import
import os

# rule 6: no docstrings

def messy_function(x):
    # TODO: Fix this function later  # rule 7: TODO found
    try:
        if x > 10:
            print("x is big")  # rule 1: print statement
            return True
    except:  # rule 6: bare except
        pass

    # rule 3: hardcoded secret (simulated)
    api_key = "12345-abcde-secret-key"
    
    # rule 4: unprofessional
    # shitty code but lets see
    return False
