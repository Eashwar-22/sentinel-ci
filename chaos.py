from datetime import *  # RULE 5: Wildcard import
import os

# RULE 6: No docstrings

def messy_function(x):
    # TODO: Fix this function later  # RULE 7: TODO found
    try:
        if x > 10:
            print("x is big")  # RULE 1: Print statement
            return True
    except:  # RULE 6: Bare except
        pass

    # RULE 3: Hardcoded secret (simulated)
    api_key = "12345-abcde-secret-key"
    
    # RULE 4: Profanity/Unprofessional
    # This code is sh*t but it works
    return False
