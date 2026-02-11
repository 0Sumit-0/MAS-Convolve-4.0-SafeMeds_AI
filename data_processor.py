
def get_golden_dataset():
    """
    Returns a rich, verified dataset of common medications with clinically accurate
    safety tags for deterministic filtering.
    Source: Compiled from standard medical guidelines (NIH, Mayo Clinic, FDA labels).
    """
    knowledge_base = [
        # --- PAIN & INFLAMMATION ---
        {
            "text": "Ibuprofen (Advil, Motrin): NSAID for pain, fever, inflammation. WARNING: High risk of stomach bleeding, kidney damage, and cardiovascular events. Avoid in third trimester of pregnancy.",
            "source": "FDA Guidelines / NIH MedlinePlus",
            "safety_tags": ["stomach_ulcer", "kidney_disease", "pregnancy", "hypertension", "bleeding_disorder", "asthma"]
        },
        {
            "text": "Naproxen (Aleve): Stronger NSAID for joint pain and inflammation. Similar risks to ibuprofen but longer lasting. High GI bleeding risk.",
            "source": "Mayo Clinic",
            "safety_tags": ["stomach_ulcer", "kidney_disease", "pregnancy", "hypertension", "bleeding_disorder", "asthma"]
        },
        {
            "text": "Aspirin (Bayer): NSAID and blood thinner. Used for pain and heart attack prevention. WARNING: Severe bleeding risk. Reye's syndrome risk in children.",
            "source": "FDA Guidelines",
            "safety_tags": ["stomach_ulcer", "bleeding_disorder", "pregnancy", "kidney_disease", "asthma", "children"]
        },
        {
            "text": "Paracetamol (Acetaminophen, Tylenol): effective pain reliever and fever reducer. Not an NSAID. Safer for stomach. WARNING: Severe liver damage in high doses or with alcohol.",
            "source": "Harvard Health Publishing",
            "safety_tags": ["liver_disease", "alcohol_use_disorder"]
        },
        {
            "text": "Tramadol (Ultram): Opioid pain medication for moderate to severe pain. WARNING: Risk of addiction, respiratory depression, and seizures.",
            "source": "FDA Controlled Substance guidelines",
            "safety_tags": ["liver_disease", "kidney_disease", "respiratory_issues", "history_of_addiction", "pregnancy"]
        },

        {
            "text": "Calcium Carbonate (Tums, Rolaids): Antacid used to relieve heartburn, acid indigestion, and upset stomach. WARNING: Do not take more than recommended dose. Can cause constipation.",
            "source": "NIH MedlinePlus",
            "safety_tags": ["kidney_disease", "history_of_kidney_stones"]
        },
        # --- STOMACH & DIGESTION ---
        {
            "text": "Calcium Carbonate (Tums, Rolaids): Antacid used to quickly relieve heartburn, acid indigestion, and upset stomach. WARNING: Do not take more than maximum daily dose. Can cause constipation.",
            "source": "NIH MedlinePlus",
            "safety_tags": ["kidney_disease", "history_of_kidney_stones"]
        },
        # --- ANTIBIOTICS ---
        {
            "text": "Amoxicillin: Penicillin-type antibiotic for various bacterial infections. Ineffective against viruses.",
            "source": "Mayo Clinic Patient Care",
            "safety_tags": ["penicillin_allergy", "asthma", "kidney_disease"]
        },
        {
            "text": "Azithromycin (Z-Pak): Macrolide antibiotic used for respiratory and skin infections. Alternative for penicillin allergy. CAUTION: Can cause heart rhythm changes (QT prolongation).",
            "source": "NIH MedlinePlus",
            "safety_tags": ["heart_arrhythmia", "liver_disease"]
        },
        {
            "text": "Ciprofloxacin (Cipro): Fluoroquinolone antibiotic for severe infections. WARNING: Risk of tendon rupture and nerve damage.",
            "source": "FDA Black Box Warning",
            "safety_tags": ["tendon_issues", "myasthenia_gravis", "pregnancy", "children"]
        },

        # --- CARDIOVASCULAR & BLOOD PRESSURE ---
        {
            "text": "Lisinopril (Zestril): ACE inhibitor for high blood pressure and heart failure. CAUTION: Can cause dry cough and high potassium. Not for pregnancy.",
            "source": "FDA Approved Drug Products",
            "safety_tags": ["pregnancy", "kidney_disease", "diabetes", "history_of_angioedema"]
        },
        {
            "text": "Amlodipine (Norvasc): Calcium channel blocker for high blood pressure and angina. Common side effect is swelling in ankles.",
            "source": "American Heart Association",
            "safety_tags": ["liver_disease", "heart_failure"]
        },
        {
            "text": "Metoprolol (Lopressor): Beta-blocker for high blood pressure and angina. WARNING: Do not stop abruptly. Can worsen asthma.",
            "source": "Mayo Clinic",
            "safety_tags": ["asthma", "bradycardia", "diabetes", "heart_failure"]
        },
        {
            "text": "Warfarin (Coumadin): Strong anticoagulant (blood thinner) to prevent clots. WARNING: Very high risk of severe bleeding. Requires regular blood testing.",
            "source": "NIH Clinical Guidelines",
            "safety_tags": ["bleeding_disorder", "stomach_ulcer", "pregnancy", "liver_disease", "kidney_disease", "high_fall_risk"]
        },

        # --- DIABETES & METABOLISM ---
        {
            "text": "Metformin (Glucophage): First-line oral medication for Type 2 diabetes. Helps control blood sugar. CAUTION: Risk of lactic acidosis in kidney failure.",
            "source": "American Diabetes Association",
            "safety_tags": ["kidney_disease", "liver_disease", "heart_failure", "alcohol_use_disorder"]
        },
        {
            "text": "Insulin Glargine (Lantus): Long-acting basal insulin for Type 1 and Type 2 diabetes. WARNING: Risk of hypoglycemia (low blood sugar).",
            "source": "FDA Guidelines",
            "safety_tags": ["kidney_disease", "liver_disease"]
        },

        # --- ALLERGY & RESPIRATORY ---
        {
            "text": "Diphenhydramine (Benadryl): Antihistamine for allergies. WARNING: Causes significant drowsiness. Caution in elderly.",
            "source": "NIH MedlinePlus",
            "safety_tags": ["glaucoma", "prostate_issues", "elderly", "liver_disease"]
        },
        {
            "text": "Albuterol Inhaler (ProAir): Rescue inhaler for asthma attacks. Bronchodilator. Can cause jitteriness and fast heart rate.",
            "source": "Asthma and Allergy Foundation of America",
            "safety_tags": ["hypertension", "heart_arrhythmia", "diabetes"]
        },

        # --- SUPPLEMENTS & OTHER ---
        {
            "text": "St. John's Wort: Herbal supplement sometimes used for depression. WARNING: Dangerous interactions with many medications including antidepressants, birth control, and blood thinners.",
            "source": "NCCIH (NIH)",
            "safety_tags": ["taking_other_medications", "pregnancy", "sun_sensitivity"]
        },
        {
            "text": "Honey and Lemon Tea: Traditional soothing remedy for sore throat. Not medication. Safe for most.",
            "source": "Holistic Health Alliance",
            "safety_tags": ["diabetes"] # Tagged due to sugar content
        },
        {
            "text": "Calcium Carbonate (Tums, Rolaids): Antacid used to relieve heartburn, acid indigestion, and upset stomach. WARNING: Do not take more than recommended dose. Can cause constipation.",
            "source": "NIH MedlinePlus",
            "safety_tags": ["kidney_disease", "history_of_kidney_stones"]
        },
    ]
    return knowledge_base