from mrz.checker.td1 import TD1CodeChecker
from mrz.checker.td2 import TD2CodeChecker
from mrz.checker.td3 import TD3CodeChecker
import re

def parse_mrz(mrz_text):
    """
    Parses MRZ text and returns a dictionary of fields.
    Handles TD1 (ID cards), TD2, and TD3 (Passports).
    """
    lines = [line.strip() for line in mrz_text.split('\n') if len(line.strip()) > 10]
    
    # Filter out lines that don't look like MRZ
    # MRZ lines usually contain '<<'
    mrz_lines = [line for line in lines if '<' in line]
    
    if not mrz_lines:
        return {"error": "No MRZ lines found"}

    # Try to clean up OCR errors common in MRZ
    # e.g. spaces are not allowed in MRZ usually
    # Clean up OCR errors
    # MRZ only contains A-Z, 0-9, and <
    cleaned_lines = []
    for line in mrz_lines:
        # Replace common OCR misinterpretations if necessary (optional, but risky)
        # Keep only valid characters
        cleaned = re.sub(r'[^A-Z0-9<]', '', line.upper())
        
        # Heuristic: The end of the line is usually fillers '<<<<'.
        # If we see K or X repeated at the end, it's likely a mistake.
        # We'll look for the last chunk of the string.
        # If the last 5 chars contain multiple Ks or Xs, replace them.
        
        # A safer heuristic: Replace any sequence of 3+ 'K's or 'X's with '<'s
        # But names can have K or X.
        # However, fillers are usually at the end.
        
        # Let's try to fix the trailing part of the line.
        # Find the last alphanumeric character that is NOT K or X (to be safe? no, names have K/X).
        # Actually, standard MRZ lines (TD3) are 44 chars.
        # If we have > 44 chars, we might have noise.
        # If we have < 44 chars, we might be missing fillers.
        
        # Specific fix for the user's issue: KKKK at the end -> <<<<
        # Regex: Replace K or X with < if followed by < or end of line, recursively?
        # Simpler: If we see a sequence of 2 or more K/X/< mixed at the end of the line, make them all <.
        
        match = re.search(r'([KX<]{3,})$', cleaned)
        if match:
            suffix = match.group(1)
            # If this suffix is mostly K/X/<, replace with <
            cleaned = cleaned[:match.start(1)] + '<' * len(suffix)

        # Aggressive cleaning for separators:
        # If K or X is adjacent to <, it's likely a misread <
        # e.g. <K -> <<, X< -> <<
        # Run this multiple times to handle chains like <KX<
        for _ in range(3):
            cleaned = re.sub(r'(?<=<)[KX]', '<', cleaned)
            cleaned = re.sub(r'[KX](?=<)', '<', cleaned)

        # Heuristic: PP at start of line 1 -> P<
        if line.startswith('PP'):
            cleaned = 'P<' + cleaned[2:]

        cleaned_lines.append(cleaned)
    
    mrz_lines = cleaned_lines
    
    # Adaptive Padding
    # Determine likely format based on line count and max length
    if not mrz_lines:
        return {"error": "No MRZ lines found"}
        
    max_len = max(len(l) for l in mrz_lines)
    target_len = 0
    
    if len(mrz_lines) == 3:
        target_len = 30 # TD1
    elif len(mrz_lines) == 2:
        # Heuristic for TD3 (Passport) vs TD2
        # Passports usually start with 'P'
        if mrz_lines[0].startswith('P'):
             target_len = 44
        elif max_len > 38: # Closer to 44 than 36
            target_len = 44 # TD3
        else:
            target_len = 36 # TD2
            
    if target_len > 0:
        padded_lines = []
        for line in mrz_lines:
            if len(line) < target_len:
                # Pad with <
                line = line + '<' * (target_len - len(line))
            elif len(line) > target_len:
                # We will handle trimming in the candidate generation phase
                pass 
            padded_lines.append(line)
        mrz_lines = padded_lines

    # 1. Generate candidates for length fixing
    candidates = []
    
    # Base candidate
    candidates.append(mrz_lines)
    
    # Length fixing candidates
    if len(mrz_lines[0]) > 44 or len(mrz_lines[1]) > 44:
        l1_opts = [mrz_lines[0]]
        if len(mrz_lines[0]) > 44:
            l1_opts.append(mrz_lines[0][:44])
            l1_opts.append(mrz_lines[0][-44:])
            
        l2_opts = [mrz_lines[1]]
        if len(mrz_lines[1]) > 44:
            l2_opts.append(mrz_lines[1][:44])
            l2_opts.append(mrz_lines[1][-44:])
            
        for l1 in l1_opts:
            for l2 in l2_opts:
                if l1 == mrz_lines[0] and l2 == mrz_lines[1]:
                    continue
                candidates.append([l1, l2] + mrz_lines[2:])

    # 2. For each candidate, apply heuristics and check validity
    best_result = None
    
    for cand in candidates:
        # Check if valid as is
        res = _parse_with_type_check(cand)
        
        # Apply VNM heuristic aggressively
        # If VNM, check for invalid K usage in Line 1
        # We do this regardless of validity because for fake passports, validity might never be True.
        if res.get('country') == 'VNM' or res.get('nationality') == 'VNM':
            line1 = cand[0]
            # Regex: K followed by a consonant (except H) or end of line?
            # Vietnamese K is always followed by H or Vowel.
            # Consonants: B, C, D, G, K, L, M, N, P, Q, R, S, T, V, X
            # We can be safe and say: if K is followed by D, T, B, M, N, L, S... it's likely <
            
            new_line1 = re.sub(r'K(?=[BCDFGKLMNPQRSTVX<])', '<', line1)
            
            if new_line1 != line1:
                cand[0] = new_line1
                # Re-parse with new line 1
                res = _parse_with_type_check(cand)

        if res.get('valid'):
            return res
            
        # If not valid, try K-repair on this candidate (if not already covered by VNM heuristic)
        # This is for non-VNM or other K cases
        line1 = cand[0]
        if 'K' in line1:
            line1_no_k = line1.replace('K', '<')
            cand_k = [line1_no_k] + cand[1:]
            res_k = _parse_with_type_check(cand_k)
            if res_k.get('valid'):
                return res_k
        
        # Keep track of the "best" invalid result
        # Priority:
        # 1. Valid result (returned immediately above)
        # 2. Result with VNM country (heuristic)
        # 3. Result with a detected type (TD1/TD2/TD3)
        # 4. Any result
        
        if best_result is None:
            best_result = res
        else:
            # Check if current res is "better" than best_result
            
            # If best_result has a warning/error and res has a type, res is better
            if 'type' in res and 'type' not in best_result:
                best_result = res
            # If both have type, prefer VNM (existing heuristic)
            elif 'type' in res and 'type' in best_result:
                if res.get('country') == 'VNM' and best_result.get('country') != 'VNM':
                    best_result = res
                # If both are same country or neither is VNM, maybe prefer the one with more fields?
                # For now, stick to VNM preference or first found.
            # If best_result has error and res has warning, res is better?
            elif 'error' in best_result and 'warning' in res:
                best_result = res

    # If nothing worked to make it valid, return the best result we found
    # (likely the one with heuristics applied)
    return best_result

def _parse_with_type_check(mrz_lines):
    try:
        if len(mrz_lines) == 2 and len(mrz_lines[0]) == 44:
            return _parse_td3(mrz_lines)
        elif len(mrz_lines) == 3 and len(mrz_lines[0]) == 30:
            return _parse_td1(mrz_lines)
        elif len(mrz_lines) == 2 and len(mrz_lines[0]) == 36:
            return _parse_td2(mrz_lines)
        else:
            return {
                "raw_mrz": mrz_lines,
                "warning": "Could not detect standard MRZ format (TD1/TD2/TD3)"
            }
    except Exception as e:
        return {
            "raw_mrz": mrz_lines,
            "error": str(e)
        }

def _parse_td3(mrz_lines):
    checker = TD3CodeChecker(mrz_lines[0] + '\n' + mrz_lines[1])
    fields = checker.fields()
    
    surname = str(fields.surname) if fields.surname else None
    name = str(fields.name) if fields.name else None
    
    if surname == 'None': surname = None
    if name == 'None': name = None
    
    # Manual fallback if library fails to extract names
    if not surname and not name:
        try:
            # Line 1 format: P<CCCSURNAME<<GIVEN<NAMES<<<<...
            # Chars 0-2: Doc Type
            # Chars 2-5: Country
            # Chars 5+: Names
            line1 = mrz_lines[0]
            if len(line1) > 5:
                # Extract name section
                name_section = line1[5:]
                # Split by double separator '<<'
                parts = name_section.split('<<')
                if len(parts) >= 1:
                    surname = parts[0].replace('<', ' ').strip()
                if len(parts) >= 2:
                    name = parts[1].replace('<', ' ').strip()
        except:
            pass

    return {
        "type": "TD3",
        "surname": surname,
        "name": name,
        "country": fields.country,
        "nationality": fields.nationality,
        "birth_date": fields.birth_date,
        "expiry_date": fields.expiry_date,
        "sex": fields.sex,
        "document_number": fields.document_number,
        "valid": bool(checker)
    }

def _parse_td1(mrz_lines):
    checker = TD1CodeChecker(mrz_lines[0] + '\n' + mrz_lines[1] + '\n' + mrz_lines[2])
    fields = checker.fields()
    return {
        "type": "TD1",
        "surname": fields.surname,
        "name": fields.name,
        "country": fields.country,
        "nationality": fields.nationality,
        "birth_date": fields.birth_date,
        "expiry_date": fields.expiry_date,
        "sex": fields.sex,
        "document_number": fields.document_number,
        "valid": bool(checker)
    }

def _parse_td2(mrz_lines):
    checker = TD2CodeChecker(mrz_lines[0] + '\n' + mrz_lines[1])
    fields = checker.fields()
    return {
        "type": "TD2",
        "surname": fields.surname,
        "name": fields.name,
        "country": fields.country,
        "nationality": fields.nationality,
        "birth_date": fields.birth_date,
        "expiry_date": fields.expiry_date,
        "sex": fields.sex,
        "document_number": fields.document_number,
        "valid": bool(checker)
    }
