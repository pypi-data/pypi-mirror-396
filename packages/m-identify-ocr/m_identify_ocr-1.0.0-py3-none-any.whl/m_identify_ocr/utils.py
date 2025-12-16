from datetime import datetime

COUNTRY_CODES = {
    "VNM": "Vietnam",
    "USA": "United States",
    "GBR": "United Kingdom",
    "FRA": "France",
    "DEU": "Germany",
    "JPN": "Japan",
    "KOR": "South Korea",
    "CHN": "China",
    "CAN": "Canada",
    "AUS": "Australia",
    "RUS": "Russia",
    "ITA": "Italy",
    "ESP": "Spain",
    "THA": "Thailand",
    "SGP": "Singapore",
    "MYS": "Malaysia",
    "IDN": "Indonesia",
    "PHL": "Philippines",
    "IND": "India",
    "ZAF": "South Africa",
    "NZL": "New Zealand",
    "BRA": "Brazil",
    "MEX": "Mexico",
    "SWE": "Sweden",
    "NOR": "Norway",
    "DNK": "Denmark",
    "FIN": "Finland",
    "CHE": "Switzerland",
    "AUT": "Austria",
    "BEL": "Belgium",
    "NLD": "Netherlands",
    "POL": "Poland",
    "TUR": "Turkey",
    "GRC": "Greece",
    "PRT": "Portugal",
    "IRL": "Ireland",
    "ARG": "Argentina",
    "CHL": "Chile",
    "COL": "Colombia",
    "PER": "Peru",
    "VEN": "Venezuela",
    "EGY": "Egypt",
    "NGA": "Nigeria",
    "KEN": "Kenya",
    "SAU": "Saudi Arabia",
    "ARE": "United Arab Emirates",
    "ISR": "Israel",
    # Add more as needed
}

def get_country_name(code):
    return COUNTRY_CODES.get(code, code)

def format_date(mrz_date_str):
    """
    Converts MRZ date (YYMMDD) to dd-MM-YYYY.
    Handles century guessing (cutoff at current year + some buffer or standard MRZ rules).
    MRZ doesn't have century.
    """
    if not mrz_date_str or len(mrz_date_str) != 6 or not mrz_date_str.isdigit():
        return mrz_date_str
    
    try:
        yy = int(mrz_date_str[:2])
        mm = int(mrz_date_str[2:4])
        dd = int(mrz_date_str[4:6])
        
        # Century guessing
        # Usually, if YY > current_year % 100 + buffer, it's 19YY.
        # But for expiry date, it's usually 20YY.
        # For birth date, it could be 19YY or 20YY.
        # This is ambiguous without context (birth vs expiry).
        # We'll use a simple heuristic:
        # If > 50 -> 19YY, else 20YY. (Simple pivot)
        # Or we can pass field type.
        
        # Let's just use datetime to parse and pivot around 50 for now.
        # Python's strptime %y pivots around 68 usually, or current time.
        
        current_year = datetime.now().year
        century = 2000
        if yy > (current_year % 100) + 10: # If year is significantly in future, assume past (19xx)
             # This logic is tricky for expiry dates which ARE in future.
             pass
             
        # Better approach:
        # We don't know if it's birth or expiry here easily without context.
        # Let's just return dd-MM-YY first? User asked for YYYY.
        # Let's assume standard pivot 50 for now.
        
        year = 2000 + yy
        if year > current_year + 15: # If date is > 15 years in future, likely 19xx (for birth date)
             year -= 100
             
        # Wait, for expiry date, 2029 is valid. 2000+29 = 2029.
        # For birth date, 96 -> 2096 (too far) -> 1996.
        
        return f"{dd:02d}-{mm:02d}-{year}"
    except:
        return mrz_date_str

def calculate_issue_date_from_expiry(expiry_date_str):
    """
    Calculates issue date as expiry date - 10 years.
    expiry_date_str should be in dd-MM-YYYY format.
    """
    if not expiry_date_str:
        return None
        
    try:
        # Parse dd-MM-YYYY
        dt = datetime.strptime(expiry_date_str, "%d-%m-%Y")
        
        # Subtract 10 years
        try:
            new_date = dt.replace(year=dt.year - 10)
        except ValueError:
            # Handle Feb 29 on leap year (e.g. 2024 -> 2014)
            new_date = dt.replace(year=dt.year - 10, day=28)
            
        return new_date.strftime("%d-%m-%Y")
    except:
        return None

def normalize_date(date_str):
    """
    Normalizes a date string (dd/mm/yyyy, dd.mm.yyyy, etc.) to dd-mm-yyyy.
    """
    if not date_str:
        return None
        
    # Replace common separators with -
    date_str = date_str.replace('/', '-').replace('.', '-')
    
    # Check if it matches dd-mm-yyyy
    # If it's d-m-yyyy, pad with 0
    try:
        parts = date_str.split('-')
        if len(parts) == 3:
            d, m, y = parts
            return f"{int(d):02d}-{int(m):02d}-{y}"
    except:
        pass
        

        
    return date_str

import unicodedata

def remove_accents(input_str):
    """
    Removes accents from a string (e.g. 'Nguyễn Văn A' -> 'Nguyen Van A').
    """
    if not input_str:
        return ""
    
    # Normalize unicode characters to decomposed form (NFD)
    nfkd_form = unicodedata.normalize('NFD', input_str)
    
    # Filter out non-spacing mark characters (accents)
    # Also handle specific Vietnamese chars like Đ/đ which might not be decomposed by NFD alone in some cases,
    # but usually 'Đ' is a separate char. unicodedata.normalize('NFKD') might be better?
    # Actually 'Đ' is 'LATIN CAPITAL LETTER D WITH STROKE'. It doesn't decompose to D + stroke in NFD.
    # We need to handle Đ manually.
    
    output = ""
    for char in nfkd_form:
        if unicodedata.category(char) != 'Mn':
            output += char
            
    # Manual fixes for common Vietnamese chars that don't decompose
    output = output.replace('Đ', 'D').replace('đ', 'd')
    
    return output

def extract_matching_fullname(visual_fullname, mrz_fullname):
    """
    Tries to find the mrz_fullname inside visual_fullname (ignoring case, accents, spaces).
    Returns the matching part of visual_fullname (preserving original accents/spacing).
    """
    if not visual_fullname or not mrz_fullname:
        return None
        
    # Prepare target (MRZ)
    # Remove accents (just in case), lower, remove spaces
    target = remove_accents(mrz_fullname).lower().replace(' ', '')
    
    if not target:
        return None
        
    # Process visual_fullname char by char to build map
    clean_visual = []
    mapping = [] # clean_index -> original_index
    
    for i, char in enumerate(visual_fullname):
        if char.isspace():
            continue
            
        # Normalize char
        clean_char = remove_accents(char).lower()
        
        # If clean_char is empty (e.g. weird symbol), skip
        if not clean_char:
            continue
            
        # If clean_char is multiple chars (rare but possible), handle it
        # For our remove_accents, it's usually 1-to-1 or 1-to-0.
        # But if it returns multiple chars, we map all to the same original index.
        for c in clean_char:
            clean_visual.append(c)
            mapping.append(i)
            
    clean_visual_str = "".join(clean_visual)
    
    # Find target in clean_visual_str
    try:
        start_idx = clean_visual_str.index(target)
        end_idx = start_idx + len(target) - 1
        
        # Map back to original indices
        orig_start = mapping[start_idx]
        orig_end = mapping[end_idx]
        
        # Return substring
        return visual_fullname[orig_start : orig_end + 1]
    except ValueError:
        return None

from difflib import get_close_matches

KNOWN_PLACES_OF_ISSUE = [
    "Cuc Quan ly xuat nhap canh",
    "Immigration Department",
    "Ministry of Foreign Affairs",
    "Department of State",
    "Passport Office"
]

def correct_common_misspellings(text, field_type):
    """
    Corrects common OCR errors for specific fields using fuzzy matching.
    """
    if not text:
        return text
        
    if field_type == 'place_of_issue':
        # Check against known list
        matches = get_close_matches(text, KNOWN_PLACES_OF_ISSUE, n=1, cutoff=0.6)
        if matches:
            return matches[0]
            
    return text
