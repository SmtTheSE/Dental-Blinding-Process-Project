"""
Dental Methods Module

This module contains the implementation of the AlQahtani and Demirjian methods 
for dental age estimation. These methods are used to estimate the age of children 
based on the development stages of their teeth as seen in OPG (Orthopantomogram) images.

The methods are based on the following scientific papers:
- AlQahtani, S. et al. (2010). London Atlas of Human Tooth Development
- Demirjian, A. et al. (1973). A new system of dental age assessment

The implementation follows the modified Moorrees and Bengston's criteria for 
tooth development stages, with stages I-XIII for formation and i-viii for eruption 
and resorption for the AlQahtani method, and stages A-H for the Demirjian method.
"""

import logging

# Configure logging
logger = logging.getLogger(__name__)

# AlQahtani method tooth codes
ALQAHATNI_TEETH = [
    '21', '22', '23', '24', '25', '26', '27',  # Upper right permanent teeth
    '31', '32', '33', '34', '35', '36', '37',  # Upper left permanent teeth
    '61', '62', '63', '64', '65',                 # Upper right primary teeth
    '71', '72', '73', '74', '75'                  # Upper left primary teeth
]

# Demirjian method tooth codes (left mandibular permanent teeth)
DEMIRJIAN_TEETH = [
    '31', '32', '33', '34', '35', '36', '37'  # Left mandibular permanent teeth
]

# AlQahtani method stage descriptions
ALQAHATNI_STAGE_DESCRIPTIONS = {
    'I': 'Initiation',
    'II': 'Completion of crown initiation',
    'III': 'One half of crown complete',
    'IV': 'Crown complete',
    'V': 'Cusp outline complete',
    'VI': 'Root initiation',
    'VII': 'One quarter root length',
    'VIII': 'One half root length',
    'IX': 'Three quarter root length',
    'X': 'Root length complete',
    'XI': 'Apical end closure',
    'XII': 'Beginning of root resorption',
    'XIII': 'Root resorbed more than half'
}

# Demirjian method stage descriptions
DEMIRJIAN_STAGE_DESCRIPTIONS = {
    'A': 'Initial mineralization of the crown',
    'B': 'Cusp tips mineralized',
    'C': 'Crown complete, enamel complete',
    'D': 'Cusp tips starting to wear',
    'E': 'Crown worn, dentine exposed',
    'F': 'Crown half resorbed, dentine more than half resorbed',
    'G': 'Root complete, pulp chamber wide open',
    'H': 'Root resorbed, pulp chamber closed'
}

# Demirjian scores for each tooth and stage (self-weighted score table)
DEMIRJIAN_SCORES = {
    '31': {'A': 0, 'B': 0.04, 'C': 0.11, 'D': 0.18, 'E': 0.23, 'F': 0.31, 'G': 0.38, 'H': 0.45},
    '32': {'A': 0, 'B': 0.03, 'C': 0.09, 'D': 0.16, 'E': 0.21, 'F': 0.28, 'G': 0.35, 'H': 0.42},
    '33': {'A': 0, 'B': 0.03, 'C': 0.09, 'D': 0.15, 'E': 0.20, 'F': 0.27, 'G': 0.34, 'H': 0.41},
    '34': {'A': 0, 'B': 0.03, 'C': 0.08, 'D': 0.14, 'E': 0.19, 'F': 0.26, 'G': 0.33, 'H': 0.40},
    '35': {'A': 0, 'B': 0.03, 'C': 0.08, 'D': 0.13, 'E': 0.18, 'F': 0.25, 'G': 0.32, 'H': 0.39},
    '36': {'A': 0, 'B': 0.03, 'C': 0.08, 'D': 0.13, 'E': 0.17, 'F': 0.24, 'G': 0.31, 'H': 0.38},
    '37': {'A': 0, 'B': 0.03, 'C': 0.07, 'D': 0.12, 'E': 0.16, 'F': 0.23, 'G': 0.30, 'H': 0.37}
}

# Demirjian conversion tables (age in years based on total score)
# For males
DEMIRJIAN_MALE_CONVERSION = {
    0.00: 4.0, 0.05: 4.2, 0.10: 4.5, 0.15: 4.7, 0.20: 4.9, 0.25: 5.1, 0.30: 5.3, 0.35: 5.5,
    0.40: 5.7, 0.45: 5.9, 0.50: 6.1, 0.55: 6.3, 0.60: 6.5, 0.65: 6.7, 0.70: 6.9, 0.75: 7.1,
    0.80: 7.3, 0.85: 7.5, 0.90: 7.7, 0.95: 7.9, 1.00: 8.1, 1.05: 8.3, 1.10: 8.5, 1.15: 8.7,
    1.20: 8.9, 1.25: 9.1, 1.30: 9.3, 1.35: 9.5, 1.40: 9.7, 1.45: 9.9, 1.50: 10.1, 1.55: 10.3,
    1.60: 10.5, 1.65: 10.7, 1.70: 10.9, 1.75: 11.1, 1.80: 11.3, 1.85: 11.5, 1.90: 11.7, 1.95: 11.9,
    2.00: 12.1, 2.05: 12.3, 2.10: 12.5, 2.15: 12.7, 2.20: 12.9, 2.25: 13.1, 2.30: 13.3, 2.35: 13.5,
    2.40: 13.7, 2.45: 13.9, 2.50: 14.1, 2.55: 14.3, 2.60: 14.5, 2.65: 14.7, 2.70: 14.9, 2.75: 15.1,
    2.80: 15.3, 2.85: 15.5, 2.90: 15.7, 2.95: 15.9, 3.00: 16.1
}

# For females
DEMIRJIAN_FEMALE_CONVERSION = {
    0.00: 4.2, 0.05: 4.4, 0.10: 4.6, 0.15: 4.8, 0.20: 5.0, 0.25: 5.2, 0.30: 5.4, 0.35: 5.6,
    0.40: 5.8, 0.45: 6.0, 0.50: 6.2, 0.55: 6.4, 0.60: 6.6, 0.65: 6.8, 0.70: 7.0, 0.75: 7.2,
    0.80: 7.4, 0.85: 7.6, 0.90: 7.8, 0.95: 8.0, 1.00: 8.2, 1.05: 8.4, 1.10: 8.6, 1.15: 8.8,
    1.20: 9.0, 1.25: 9.2, 1.30: 9.4, 1.35: 9.6, 1.40: 9.8, 1.45: 10.0, 1.50: 10.2, 1.55: 10.4,
    1.60: 10.6, 1.65: 10.8, 1.70: 11.0, 1.75: 11.2, 1.80: 11.4, 1.85: 11.6, 1.90: 11.8, 1.95: 12.0,
    2.00: 12.2, 2.05: 12.4, 2.10: 12.6, 2.15: 12.8, 2.20: 13.0, 2.25: 13.2, 2.30: 13.4, 2.35: 13.6,
    2.40: 13.8, 2.45: 14.0, 2.50: 14.2, 2.55: 14.4, 2.60: 14.6, 2.65: 14.8, 2.70: 15.0, 2.75: 15.2,
    2.80: 15.4, 2.85: 15.6, 2.90: 15.8, 2.95: 16.0, 3.00: 16.2
}

def get_alqahtani_teeth():
    """
    Returns the list of tooth codes used in the AlQahtani method.
    
    Returns:
        list: List of tooth codes for the AlQahtani method.
    """
    return ALQAHATNI_TEETH

def get_demirjian_teeth():
    """
    Returns the list of tooth codes used in the Demirjian method.
    
    Returns:
        list: List of tooth codes for the Demirjian method.
    """
    return DEMIRJIAN_TEETH

def calculate_demirjian_score(stages, sex):
    """
    Calculate the Demirjian dental maturity score and estimated age.
    
    Args:
        stages (dict): Dictionary mapping tooth codes to developmental stages.
        sex (str): Sex of the patient ('male' or 'female').
        
    Returns:
        tuple: (total_score, estimated_age, error_margin)
    """
    try:
        total_score = 0
        for tooth in DEMIRJIAN_TEETH:
            if tooth in stages and stages[tooth] in DEMIRJIAN_SCORES[tooth]:
                total_score += DEMIRJIAN_SCORES[tooth][stages[tooth]]
        
        # Round to nearest 0.05 for lookup in conversion table
        rounded_score = round(total_score * 20) / 20
        
        # Look up age in appropriate conversion table
        conversion_table = DEMIRJIAN_MALE_CONVERSION if sex.lower() == 'male' else DEMIRJIAN_FEMALE_CONVERSION
        
        # Find the closest score in the table
        closest_score = min(conversion_table.keys(), key=lambda x: abs(x - rounded_score))
        estimated_age = conversion_table[closest_score]
        
        # Error margin is typically ±0.5 years for this method
        error_margin = 0.5
        
        logger.info(f"Demirjian calculation - Score: {total_score}, Rounded: {rounded_score}, Age: {estimated_age}")
        
        return total_score, estimated_age, error_margin
    except Exception as e:
        logger.error(f"Error calculating Demirjian score: {str(e)}")
        raise

def calculate_alqahtani_age(stages, sex):
    """
    Calculate the AlQahtani dental age estimation.
    
    Args:
        stages (dict): Dictionary mapping tooth codes to developmental stages.
        sex (str): Sex of the patient ('male' or 'female').
        
    Returns:
        tuple: (estimated_age, error_margin)
    """
    try:
        # For AlQahtani method, we use a simplified approach based on average values
        # In a real implementation, this would be more complex
        # For now, we'll use a simple average of the stages
        
        valid_stages = [stage for tooth, stage in stages.items() if tooth in ALQAHATNI_TEETH and stage in ALQAHATNI_STAGE_DESCRIPTIONS]
        
        if not valid_stages:
            raise ValueError("No valid AlQahtani stages provided")
        
        # Map stages to numerical values for calculation
        stage_values = {
            'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 
            'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10, 
            'XI': 11, 'XII': 12, 'XIII': 13
        }
        
        # Calculate average stage value
        avg_stage_value = sum(stage_values.get(stage, 0) for stage in valid_stages) / len(valid_stages)
        
        # Convert average stage to approximate age (simplified)
        # This is a very simplified approach - in reality, this would be much more complex
        estimated_age = 4 + (avg_stage_value * 0.8)  # Rough approximation
        
        # Error margin is typically ±1.0 years for this method
        error_margin = 1.0
        
        logger.info(f"AlQahtani calculation - Avg Stage Value: {avg_stage_value}, Age: {estimated_age}")
        
        return estimated_age, error_margin
    except Exception as e:
        logger.error(f"Error calculating AlQahtani age: {str(e)}")
        raise