import pytesseract
import cv2
import numpy as np
from .image import preprocess_image, crop_mrz_region
from .mrz import parse_mrz
from .fulltext import extract_full_text
from .utils import format_date, get_country_name, calculate_issue_date_from_expiry, normalize_date, remove_accents, extract_matching_fullname, correct_common_misspellings

import os
# Limit Tesseract threads to avoid contention in low-resource environments (like K8s with <1 CPU)
os.environ['OMP_THREAD_LIMIT'] = '1'

def read_passport(image_path, crop_mrz=True, extra_fields=False):
    """
    Main function to read passport information.
    
    Args:
        image_path (str): Path to the passport image file.
        crop_mrz (bool): Whether to attempt to crop the MRZ region before OCR.
                         Defaults to True, which is usually better for accuracy.
        extra_fields (bool): Whether to attempt to extract non-MRZ fields (experimental).
    
    Returns:
        dict: Extracted information.
    """
    try:
        # 1. Preprocess
        processed_img = preprocess_image(image_path)
        
        result = {}

        # 2. Crop MRZ (Optional but recommended)
        if crop_mrz:
            ocr_img = crop_mrz_region(processed_img)
        else:
            ocr_img = processed_img

        # Optimize MRZ OCR: Downscale if too big (MRZ chars are large enough)
        # Reverting to 800px (v0.1.11 state)
        mrz_h, mrz_w = ocr_img.shape[:2]
        if mrz_w > 800:
            scale = 800 / mrz_w
            ocr_img = cv2.resize(ocr_img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

        # 3. OCR for MRZ
        # whitelist = A-Z, 0-9, <
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<' 
        text = pytesseract.image_to_string(ocr_img, config=custom_config)
        
        # 4. Parse MRZ
        mrz_data = parse_mrz(text)
        
        result.update(mrz_data)
        
        # 5. Full Text Extraction (for Date of Issue and Extra Fields)
        # We always run this now to get Date of Issue, as it's not in MRZ.
        # Optimize: Only look at the visual zone (top ~75% of image) to avoid re-reading MRZ
        height, width = processed_img.shape[:2]
        visual_zone_img = processed_img[:int(height * 0.75), :]
        
        # Further optimize: Resize visual zone if it's too big
        # 400px width is usually enough for "Place of Issue" (large text)
        vz_h, vz_w = visual_zone_img.shape[:2]
        if vz_w > 400:
            scale = 400 / vz_w
            visual_zone_img = cv2.resize(visual_zone_img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
            
        full_text_data = extract_full_text(visual_zone_img)
        extra = full_text_data["extracted_fields"]
        
        # Extract Date of Issue specifically
        if 'date_of_issue' in extra:
            result['date_of_issue'] = extra['date_of_issue']
            
        # Extract Place of Issue (Authority)
        if 'place_of_issue' in extra:
            result['place_of_issue'] = extra['place_of_issue']
            
        # Merge other extra fields if requested
        if extra_fields:
            for k, v in extra.items():
                if k not in result or not result[k]:
                    result[k] = v
        
        # Post-processing: Format dates and country names
        if 'birth_date' in result:
            result['birth_date'] = format_date(result['birth_date'])
        if 'expiry_date' in result:
            result['expiry_date'] = format_date(result['expiry_date'])
        if 'date_of_issue' in result:
            # date_of_issue comes from OCR (full text), so it might be dd/mm/yyyy
            result['date_of_issue'] = normalize_date(result['date_of_issue'])
            
        if 'place_of_issue' in result:
            result['place_of_issue'] = correct_common_misspellings(result['place_of_issue'], 'place_of_issue')
            
        # Fallback: If date_of_issue is missing, calculate from expiry_date (Expiry - 10 years)
        if 'date_of_issue' not in result and 'expiry_date' in result:
            calc_issue = calculate_issue_date_from_expiry(result['expiry_date'])
            if calc_issue:
                result['date_of_issue'] = calc_issue
            
        if 'nationality' in result:
            result['nationality'] = get_country_name(result['nationality'])
        if 'country' in result:
            result['country'] = get_country_name(result['country'])

        # Fullname Logic
        # Simply concatenate surname and name from MRZ
        mrz_surname = str(result.get('surname', '') or '').strip()
        mrz_name = str(result.get('name', '') or '').strip()
        
        # Convert to Title Case
        if mrz_surname:
            result['surname'] = mrz_surname.title()
        if mrz_name:
            result['name'] = mrz_name.title()
            
        result['fullname'] = f"{mrz_surname} {mrz_name}".strip().title()

        return result

    except Exception as e:
        return {"error": str(e)}
