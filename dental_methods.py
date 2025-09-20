import math

# AlQahtani method stages
# Permanent teeth development stages (I-XIII for formation, i-viii for eruption/resorption)
ALQAHTANI_STAGES = [
    'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII', 'XIII',
    'i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii'
]

# Primary teeth development stages
PRIMARY_STAGES = [
    'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII', 'XIII',
    'i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii'
]

# Demirjian method stages
DEMIRIJAN_STAGES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

# Demirjian scoring table (self-weighted scores for each tooth at each stage)
# Based on Demirjian method for left mandibular teeth
DEMIRIJAN_SCORES = {
    '31': {'A': 0.00, 'B': 0.03, 'C': 0.12, 'D': 0.22, 'E': 0.42, 'F': 0.62, 'G': 0.82, 'H': 1.00},
    '32': {'A': 0.00, 'B': 0.03, 'C': 0.09, 'D': 0.18, 'E': 0.33, 'F': 0.50, 'G': 0.75, 'H': 1.00},
    '33': {'A': 0.00, 'B': 0.03, 'C': 0.09, 'D': 0.18, 'E': 0.32, 'F': 0.48, 'G': 0.67, 'H': 1.00},
    '34': {'A': 0.00, 'B': 0.04, 'C': 0.11, 'D': 0.21, 'E': 0.35, 'F': 0.50, 'G': 0.70, 'H': 1.00},
    '35': {'A': 0.00, 'B': 0.06, 'C': 0.13, 'D': 0.23, 'E': 0.37, 'F': 0.55, 'G': 0.75, 'H': 1.00},
    '36': {'A': 0.00, 'B': 0.06, 'C': 0.12, 'D': 0.22, 'E': 0.36, 'F': 0.53, 'G': 0.73, 'H': 1.00},
    '37': {'A': 0.00, 'B': 0.07, 'C': 0.13, 'D': 0.24, 'E': 0.39, 'F': 0.56, 'G': 0.76, 'H': 1.00}
}

# Demirjian age conversion tables (simplified versions)
# For males - Table 6 from Demirjian method
DEMIRIJAN_MALE_CONVERSION = {
    0.00: 4.0, 0.05: 4.5, 0.10: 5.0, 0.15: 5.5, 0.20: 6.0, 0.25: 6.5,
    0.30: 7.0, 0.35: 7.5, 0.40: 8.0, 0.45: 8.5, 0.50: 9.0, 0.55: 9.5,
    0.60: 10.0, 0.65: 10.5, 0.70: 11.0, 0.75: 11.5, 0.80: 12.0, 0.85: 12.5,
    0.90: 13.0, 0.95: 13.5, 1.00: 14.0, 1.05: 14.5, 1.10: 15.0, 1.15: 15.5,
    1.20: 16.0, 1.25: 16.5, 1.30: 17.0, 1.35: 17.5, 1.40: 18.0
}

# For females - Table 7 from Demirjian method
DEMIRIJAN_FEMALE_CONVERSION = {
    0.00: 4.0, 0.05: 4.5, 0.10: 5.0, 0.15: 5.5, 0.20: 6.0, 0.25: 6.5,
    0.30: 7.0, 0.35: 7.5, 0.40: 8.0, 0.45: 8.5, 0.50: 9.0, 0.55: 9.5,
    0.60: 10.0, 0.65: 10.5, 0.70: 11.0, 0.75: 11.5, 0.80: 12.0, 0.85: 12.5,
    0.90: 13.0, 0.95: 13.5, 1.00: 14.0, 1.05: 14.5, 1.10: 15.0, 1.15: 15.5,
    1.20: 16.0, 1.25: 16.5, 1.30: 17.0
}

def calculate_demirjian_score(tooth_stages, sex):
    """
    Calculate Demirjian dental age based on tooth stages.
    
    Args:
        tooth_stages (dict): Dictionary with tooth numbers as keys and stages as values
        sex (str): 'male' or 'female'
        
    Returns:
        float: Estimated dental age
    """
    total_score = 0.0
    
    # Calculate total score based on tooth stages
    for tooth, stage in tooth_stages.items():
        if tooth in DEMIRIJAN_SCORES and stage in DEMIRIJAN_SCORES[tooth]:
            total_score += DEMIRIJAN_SCORES[tooth][stage]
    
    # Convert score to age based on sex
    conversion_table = DEMIRIJAN_MALE_CONVERSION if sex.lower() == 'male' else DEMIRIJAN_FEMALE_CONVERSION
    
    # Find the closest score in the conversion table
    closest_score = min(conversion_table.keys(), key=lambda x: abs(x - total_score))
    estimated_age = conversion_table[closest_score]
    
    return estimated_age

def calculate_alqahtani_age(tooth_stages):
    """
    Placeholder for AlQahtani method calculation.
    In a complete implementation, this would use the London Atlas of Human Tooth Development.
    
    Args:
        tooth_stages (dict): Dictionary with tooth identifiers as keys and developmental stages as values
        
    Returns:
        float: Estimated dental age
    """
    # This is a simplified implementation
    # In a real application, this would involve comparison with the London Atlas illustrations
    # and more complex calculations based on the modified Moorrees and Bengston's criteria
    
    # For demonstration purposes, we'll return a dummy calculation
    # A real implementation would need to reference the actual Atlas
    stage_values = {stage: idx for idx, stage in enumerate(ALQAHTANI_STAGES)}
    
    total = 0
    count = 0
    
    for tooth, stage in tooth_stages.items():
        if stage in stage_values:
            total += stage_values[stage]
            count += 1
    
    if count > 0:
        # This is just a dummy calculation for demonstration
        avg_stage_value = total / count
        # Map to approximate age (this is not scientifically accurate)
        estimated_age = 5 + (avg_stage_value / len(ALQAHTANI_STAGES)) * 10
        return estimated_age
    
    return 0.0

def get_alqahtani_teeth():
    """
    Return list of teeth used in AlQahtani method
    """
    return [
        '21', '22', '23', '24', '25', '26', '27',  # Permanent upper left
        '31', '32', '33', '34', '35', '36', '37',  # Permanent lower left
        '61', '62', '63', '64', '65',              # Primary upper left
        '71', '72', '73', '74', '75'               # Primary lower left
    ]

def get_demirjian_teeth():
    """
    Return list of teeth used in Demirjian method
    """
    return ['31', '32', '33', '34', '35', '36', '37']  # Lower left permanent teeth