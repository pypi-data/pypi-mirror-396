import pytesseract
import re

def extract_full_text(image):
    """
    Performs OCR on the full image and attempts to extract fields using keywords.
    """
    # Use default config for full text (no whitelist, standard psm)
    # psm 3 = Fully automatic page segmentation, but no OSD. (Default)
    
    # Use default config for full text (no whitelist, standard psm)
    # psm 3 = Fully automatic page segmentation, but no OSD. (Default)
    
    # Use standard English model
    custom_config = r'--oem 3 --psm 3'
    text = pytesseract.image_to_string(image, lang='eng', config=custom_config)
    
    data = {"full_text": text}
    
    # Simple keyword extraction
    # This is very basic and depends heavily on the OCR quality and layout
    
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Common keywords in passports (English/Vietnamese)
    keywords = {
        "surname": ["Surname", "Ho va ten", "Họ và tên"],
        "given_names": ["Given names", "Ten", "Tên"],
        "nationality": ["Nationality", "Quoc tich", "Quốc tịch"],
        "date_of_birth": ["Date of birth", "Ngay sinh", "Ngày sinh"],
        "place_of_birth": ["Place of birth", "Noi sinh", "Nơi sinh"],
        "sex": ["Sex", "Gioi tinh", "Giới tính"],
        "id_number": ["ID No", "So GCMND", "Số GCMND", "Personal No"],
        "date_of_expiry": ["Date of expiry", "Co gia tri den", "Có giá trị đến"],
        "date_of_expiry": ["Date of expiry", "Co gia tri den", "Có giá trị đến"],
        "date_of_issue": ["Date of issue", "Ngay cap", "Ngày cấp"],
        "place_of_issue": ["Place of issue", "Authority", "Issuing Authority", "Noi cap", "Nơi cấp", "Co quan cap", "Cơ quan cấp"]
    }
    
    extracted = {}
    
    # Import remove_accents from utils (need to move it or duplicate it to avoid circular import if utils imports fulltext)
    # utils imports fulltext? No, core imports both. utils is independent.
    from .utils import remove_accents
    
    for key, kw_list in keywords.items():
        for i, line in enumerate(lines):
            # Normalize line for keyword search
            line_norm = remove_accents(line).lower()
            
            # Check if this line contains any of the keywords for this field
            match = False
            matched_kw = ""
            for kw in kw_list:
                # Normalize keyword too
                kw_norm = remove_accents(kw).lower()
                if kw_norm in line_norm:
                    match = True
                    matched_kw = kw # Keep original kw for length check if needed, or just use kw_norm
                    break
            
            if match:
                # Found the label line.
                final_value = None
                
                # Strategy 1: Look at the NEXT line
                if i + 1 < len(lines):
                    next_line = lines[i+1].strip()
                    next_line_norm = remove_accents(next_line).lower()
                    
                    # Check if next_line is itself a label
                    is_next_label = False
                    for other_k, other_kw_list in keywords.items():
                        for other_kw in other_kw_list:
                            other_kw_norm = remove_accents(other_kw).lower()
                            if other_kw_norm in next_line_norm and len(other_kw_norm) > 3:
                                is_next_label = True
                                break
                        if is_next_label: break
                    
                    if not is_next_label and len(next_line) > 1:
                        final_value = next_line
                
                # Strategy 2: Check the SAME line
                if not final_value:
                    # Remove the matched keyword from the line
                    # We need to be careful because we matched on normalized string.
                    # Simple approach: Replace the matched part in the original line? Hard because indices shift.
                    # Alternative: Just split by colon/separators.
                    
                    # Let's try removing the keyword from the normalized line, then mapping back? Too complex.
                    # Simpler: Just split by ':' if present.
                    if ':' in line:
                        parts = line.split(':', 1)
                        if len(parts) > 1:
                            candidate = parts[1].strip()
                            if len(candidate) > 2:
                                final_value = candidate
                    else:
                        # Fallback: Regex replace of the keyword (fuzzy)
                        # Or just take the whole line if it's long enough and not just the keyword?
                        pass

                if final_value:
                    # Clean up the value
                    
                    # Special handling for Date fields
                    if 'date' in key:
                        # Find first occurrence of DD/MM/YYYY or DD-MM-YYYY or DD.MM.YYYY
                        # Also support YYYY
                        date_match = re.search(r'\b(\d{2}[/\.-]\d{2}[/\.-]\d{4})\b', final_value)
                        if date_match:
                            final_value = date_match.group(1)
                        else:
                            # Try finding just 6 digits? No, too risky.
                            # Just clean up noise
                            pass

                    # Remove leading/trailing special chars
                    final_value = re.sub(r'^[^a-zA-Z0-9]+', '', final_value)
                    
                    # Enforce ASCII/English only (remove accents)
                    final_value = remove_accents(final_value)
                    
                    # Specific post-processing
                    if key == 'sex':
                        # Look for M, F, Nam, Nu
                        if 'M' in final_value or 'Nam' in final_value:
                            final_value = 'M'
                        elif 'F' in final_value or 'Nu' in final_value:
                            final_value = 'F'
                        else:
                            continue # Not a valid sex value
                            
                    extracted[key] = final_value
                    break # Found value for this key, stop searching lines
        
        if key in extracted:
            continue
            
    data["extracted_fields"] = extracted
    return data
