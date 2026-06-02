"""
medicine_data.py
================
Reference data module for the prescription parser.

Contains a comprehensive Indian-market medicine database including
generic names, brand-to-generic mappings, ASR correction tables,
and extraction patterns.
"""

# --------------------------------------------------------------------------
# Common medicine / drug names (generic names)
# Covers generics widely prescribed in India across all major categories.
# --------------------------------------------------------------------------
COMMON_MEDICINES = [
    # -- Analgesics / Antipyretics / NSAIDs --
    "acetaminophen", "paracetamol", "aspirin", "ibuprofen", "diclofenac",
    "aceclofenac", "naproxen", "nimesulide", "piroxicam", "mefenamic acid",
    "ketorolac", "etoricoxib", "celecoxib", "tramadol", "morphine",
    "codeine", "tapentadol", "indomethacin", "oxaprozin",

    # -- Antibiotics --
    "amoxicillin", "amoxicillin clavulanate", "ampicillin", "azithromycin",
    "cefixime", "ceftriaxone", "cefuroxime", "cefpodoxime", "cephalexin",
    "cefadroxil", "cefdinir", "ciprofloxacin", "levofloxacin", "ofloxacin",
    "norfloxacin", "moxifloxacin", "gatifloxacin", "clarithromycin",
    "erythromycin", "roxithromycin", "clindamycin", "doxycycline",
    "tetracycline", "metronidazole", "tinidazole", "ornidazole",
    "nitrofurantoin", "sulfamethoxazole", "trimethoprim", "cotrimoxazole",
    "linezolid", "vancomycin", "gentamicin", "amikacin", "rifampicin",
    "isoniazid", "pyrazinamide", "ethambutol", "rifaximin",
    "nitazoxanide", "faropenem",

    # -- Antifungals --
    "fluconazole", "itraconazole", "ketoconazole", "clotrimazole",
    "miconazole", "terbinafine", "griseofulvin", "voriconazole",
    "amphotericin",

    # -- Antivirals --
    "acyclovir", "valacyclovir", "oseltamivir", "favipiravir",
    "remdesivir", "molnupiravir", "tenofovir", "lamivudine",
    "entecavir",

    # -- Antiparasitics / Anthelmintics --
    "albendazole", "mebendazole", "ivermectin", "chloroquine",
    "hydroxychloroquine", "artemether", "lumefantrine",
    "pyrantel", "praziquantel",

    # -- Gastrointestinal --
    "pantoprazole", "omeprazole", "esomeprazole", "rabeprazole",
    "lansoprazole", "ranitidine", "famotidine", "sucralfate",
    "domperidone", "metoclopramide", "ondansetron", "lactulose",
    "bisacodyl", "ispaghula", "loperamide", "rifaximin",
    "drotaverine", "dicyclomine", "hyoscine", "mebeverine",
    "ursodeoxycholic acid", "pancreatin",

    # -- Respiratory / Cough & Cold --
    "salbutamol", "levosalbutamol", "ipratropium", "tiotropium",
    "budesonide", "fluticasone", "beclomethasone", "formoterol",
    "salmeterol", "montelukast", "aminophylline", "theophylline",
    "dextromethorphan", "guaifenesin", "bromhexine", "ambroxol",
    "acetylcysteine", "carbocisteine",

    # -- Antihistamines / Anti-allergics --
    "cetirizine", "levocetirizine", "fexofenadine", "loratadine",
    "desloratadine", "chlorpheniramine", "diphenhydramine",
    "hydroxyzine", "promethazine", "cyproheptadine", "bilastine",
    "ebastine", "ketotifen",

    # -- Antihypertensives --
    "amlodipine", "nifedipine", "cilnidipine", "felodipine",
    "atenolol", "metoprolol", "bisoprolol", "nebivolol", "propranolol",
    "carvedilol", "labetalol",
    "enalapril", "ramipril", "lisinopril", "perindopril",
    "losartan", "telmisartan", "valsartan", "olmesartan", "irbesartan",
    "candesartan", "azilsartan",
    "hydrochlorothiazide", "chlorthalidone", "indapamide",
    "furosemide", "torsemide", "spironolactone", "eplerenone",
    "prazosin", "doxazosin", "clonidine", "methyldopa",
    "diltiazem", "verapamil",

    # -- Cardiac / Antiplatelets / Anticoagulants --
    "clopidogrel", "ticagrelor", "prasugrel",
    "warfarin", "acenocoumarol", "dabigatran", "rivaroxaban", "apixaban",
    "enoxaparin", "heparin",
    "digoxin", "amiodarone", "nitroglycerin", "isosorbide",

    # -- Lipid-lowering --
    "atorvastatin", "rosuvastatin", "simvastatin", "pravastatin",
    "pitavastatin", "fenofibrate", "gemfibrozil", "ezetimibe",

    # -- Antidiabetics --
    "metformin", "glimepiride", "glipizide", "glyburide", "gliclazide",
    "pioglitazone", "sitagliptin", "vildagliptin", "linagliptin",
    "saxagliptin", "teneligliptin", "empagliflozin", "dapagliflozin",
    "canagliflozin", "voglibose", "acarbose", "repaglinide",
    "insulin", "insulin glargine", "insulin aspart", "insulin lispro",

    # -- Thyroid --
    "levothyroxine", "carbimazole", "methimazole", "propylthiouracil",

    # -- Corticosteroids --
    "prednisolone", "prednisone", "methylprednisolone", "dexamethasone",
    "hydrocortisone", "deflazacort", "betamethasone", "triamcinolone",
    "mometasone", "clobetasol", "fluocinolone",

    # -- CNS / Psychiatry --
    "alprazolam", "diazepam", "clonazepam", "lorazepam", "clobazam",
    "zolpidem", "zopiclone", "melatonin",
    "escitalopram", "sertraline", "fluoxetine", "paroxetine",
    "duloxetine", "venlafaxine", "amitriptyline", "nortriptyline",
    "mirtazapine", "bupropion", "trazodone",
    "olanzapine", "risperidone", "quetiapine", "aripiprazole",
    "haloperidol", "chlorpromazine",
    "lithium",

    # -- Antiepileptics --
    "phenytoin", "carbamazepine", "oxcarbazepine", "sodium valproate",
    "divalproex", "levetiracetam", "lamotrigine", "topiramate",
    "gabapentin", "pregabalin", "lacosamide", "brivaracetam",

    # -- Urology --
    "tamsulosin", "alfuzosin", "silodosin", "dutasteride", "finasteride",
    "sildenafil", "tadalafil", "oxybutynin", "solifenacin", "mirabegron",

    # -- Topical / Dermatology --
    "mupirocin", "fusidic acid", "framycetin", "silver sulfadiazine",
    "calamine", "permethrin", "benzoyl peroxide", "adapalene",
    "tretinoin", "minoxidil", "povidone iodine",

    # -- Supplements / Vitamins --
    "calcium", "calcitriol", "cholecalciferol", "vitamin d3",
    "folic acid", "ferrous sulfate", "ferrous fumarate", "iron",
    "zinc", "vitamin b12", "methylcobalamin", "thiamine",
    "pyridoxine", "multivitamin", "vitamin c", "vitamin e",
    "omega 3", "coenzyme q10",

    # -- Others --
    "colchicine", "allopurinol", "febuxostat",
    "baclofen", "tizanidine", "chlorzoxazone", "thiocolchicoside",
    "tranexamic acid", "ethamsylate",
    "methotrexate", "hydroxychloroquine", "sulfasalazine",
    "mesalamine", "sacubitril",
]

MEDICINE_SET = set(COMMON_MEDICINES)

# --------------------------------------------------------------------------
# Brand name -> generic name mapping
# Comprehensive Indian pharmaceutical market coverage.
# --------------------------------------------------------------------------
BRAND_TO_GENERIC = {
    # -- Paracetamol brands --
    "crocin": "paracetamol",
    "dolo": "paracetamol",
    "calpol": "paracetamol",
    "tylenol": "paracetamol",
    "metacin": "paracetamol",
    "pacimol": "paracetamol",
    "pyrigesic": "paracetamol",
    "fepanil": "paracetamol",
    "p-500": "paracetamol",

    # -- NSAID brands --
    "brufen": "ibuprofen",
    "advil": "ibuprofen",
    "combiflam": "ibuprofen + paracetamol",
    "flexon": "ibuprofen + paracetamol",
    "ibugesic": "ibuprofen",
    "voveran": "diclofenac",
    "volini": "diclofenac",
    "dynapar": "diclofenac",
    "reactin": "diclofenac",
    "diclomol": "diclofenac + paracetamol",
    "hifenac": "aceclofenac",
    "zerodol": "aceclofenac",
    "acemiz": "aceclofenac",
    "zerodol-p": "aceclofenac + paracetamol",
    "zerodol-sp": "aceclofenac + paracetamol + serratiopeptidase",
    "enzoflam": "aceclofenac + paracetamol + serratiopeptidase",
    "naprosyn": "naproxen",
    "nise": "nimesulide",
    "nimulid": "nimesulide",
    "sumo": "nimesulide + paracetamol",
    "nicip": "nimesulide",
    "toradol": "ketorolac",
    "nucoxia": "etoricoxib",
    "etoshine": "etoricoxib",
    "celebrex": "celecoxib",
    "meftal": "mefenamic acid",
    "meftal-spas": "mefenamic acid + dicyclomine",
    "ecosprin": "aspirin",
    "disprin": "aspirin",
    "saridon": "propyphenazone + paracetamol + caffeine",

    # -- Antibiotic brands --
    "amoxil": "amoxicillin",
    "mox": "amoxicillin",
    "novamox": "amoxicillin",
    "wymox": "amoxicillin",
    "augmentin": "amoxicillin + clavulanate",
    "clavam": "amoxicillin + clavulanate",
    "moxikind-cv": "amoxicillin + clavulanate",
    "moxikind": "amoxicillin + clavulanate",
    "megamox": "amoxicillin + clavulanate",
    "azee": "azithromycin",
    "zithromax": "azithromycin",
    "azicip": "azithromycin",
    "azibact": "azithromycin",
    "azilide": "azithromycin",
    "zifi": "cefixime",
    "taxim-o": "cefixime",
    "taxim": "cefixime",
    "cefix": "cefixime",
    "mahacef": "cefixime",
    "omnacef": "cefixime",
    "hifen": "cefixime",
    "monocef": "ceftriaxone",
    "ceftum": "cefuroxime",
    "zinacef": "cefuroxime",
    "cefpod": "cefpodoxime",
    "cepodem": "cefpodoxime",
    "vantin": "cefpodoxime",
    "keflex": "cephalexin",
    "sporidex": "cephalexin",
    "droxyl": "cefadroxil",
    "odoxil": "cefadroxil",
    "omnicef": "cefdinir",
    "cipro": "ciprofloxacin",
    "ciplox": "ciprofloxacin",
    "cifran": "ciprofloxacin",
    "levoflox": "levofloxacin",
    "levomac": "levofloxacin",
    "tavanic": "levofloxacin",
    "lquin": "levofloxacin",
    "glevo": "levofloxacin",
    "oflox": "ofloxacin",
    "oflomac": "ofloxacin",
    "zanocin": "ofloxacin",
    "zenflox": "ofloxacin",
    "normet": "norfloxacin",
    "norflox": "norfloxacin",
    "uroflox": "norfloxacin",
    "moxiford": "moxifloxacin",
    "milflox": "moxifloxacin",
    "avelox": "moxifloxacin",
    "moxicip": "moxifloxacin",
    "klaricid": "clarithromycin",
    "biaxin": "clarithromycin",
    "claribid": "clarithromycin",
    "althrocin": "erythromycin",
    "erythrocin": "erythromycin",
    "roxid": "roxithromycin",
    "roxibid": "roxithromycin",
    "rulide": "roxithromycin",
    "dalacin": "clindamycin",
    "cleocin": "clindamycin",
    "doxy": "doxycycline",
    "doxt": "doxycycline",
    "periostat": "doxycycline",
    "metrogyl": "metronidazole",
    "flagyl": "metronidazole",
    "metris": "metronidazole",
    "tiniba": "tinidazole",
    "fasigyn": "tinidazole",
    "ornof": "ornidazole",
    "dazolic": "ornidazole",
    "o2": "ornidazole",
    "furadantin": "nitrofurantoin",
    "niftran": "nitrofurantoin",
    "bactrim": "cotrimoxazole",
    "septran": "cotrimoxazole",
    "linid": "linezolid",
    "lizolid": "linezolid",
    "zyvox": "linezolid",
    "rifagut": "rifaximin",
    "rcifax": "rifaximin",
    "nizonide": "nitazoxanide",

    # -- Antifungal brands --
    "flucos": "fluconazole",
    "zocon": "fluconazole",
    "diflucan": "fluconazole",
    "forcan": "fluconazole",
    "canditral": "itraconazole",
    "sporanox": "itraconazole",
    "itaspor": "itraconazole",
    "candid": "clotrimazole",
    "canesten": "clotrimazole",
    "daktarin": "miconazole",
    "lamisil": "terbinafine",
    "terbicip": "terbinafine",
    "tyza": "terbinafine",
    "gris": "griseofulvin",

    # -- Antiviral brands --
    "valcivir": "valacyclovir",
    "zovirax": "acyclovir",
    "tamiflu": "oseltamivir",
    "fabiflu": "favipiravir",

    # -- Anthelmintic brands --
    "zentel": "albendazole",
    "bandy": "albendazole",
    "albezole": "albendazole",
    "mebex": "mebendazole",
    "wormin": "mebendazole",
    "ivermectol": "ivermectin",
    "ivecop": "ivermectin",
    "vermact": "ivermectin",

    # -- GI / Antacid / PPI brands --
    "pan": "pantoprazole",
    "pantop": "pantoprazole",
    "pantocid": "pantoprazole",
    "nupenta": "pantoprazole",
    "pan-d": "pantoprazole + domperidone",
    "pantocid-d": "pantoprazole + domperidone",
    "prilosec": "omeprazole",
    "omez": "omeprazole",
    "ocid": "omeprazole",
    "nexium": "esomeprazole",
    "nexpro": "esomeprazole",
    "raciper": "esomeprazole",
    "sompraz": "esomeprazole",
    "razo": "rabeprazole",
    "rablet": "rabeprazole",
    "rabeloc": "rabeprazole",
    "happi": "rabeprazole",
    "prevacid": "lansoprazole",
    "lanzol": "lansoprazole",
    "zantac": "ranitidine",
    "rantac": "ranitidine",
    "aciloc": "ranitidine",
    "zinetac": "ranitidine",
    "histac": "ranitidine",
    "pepcid": "famotidine",
    "famocid": "famotidine",
    "topcid": "famotidine",
    "sucrafil": "sucralfate",
    "ulgel": "sucralfate",
    "gelusil": "aluminium hydroxide + magnesium hydroxide",
    "digene": "aluminium hydroxide + magnesium hydroxide + simethicone",
    "mucaine": "aluminium hydroxide + magnesium hydroxide + oxetacaine",

    # -- Antiemetic / Prokinetic brands --
    "emeset": "ondansetron",
    "ondem": "ondansetron",
    "zofran": "ondansetron",
    "vomikind": "ondansetron",
    "domstal": "domperidone",
    "vomistop": "domperidone",
    "motilium": "domperidone",
    "perinorm": "metoclopramide",
    "reglan": "metoclopramide",

    # -- Antispasmodic brands --
    "drotin": "drotaverine",
    "doverin": "drotaverine",
    "meftal-spas": "mefenamic acid + dicyclomine",
    "cyclopam": "dicyclomine",
    "colimex": "dicyclomine",
    "buscopan": "hyoscine",
    "mebiz": "mebeverine",
    "colospa": "mebeverine",

    # -- Laxative brands --
    "duphalac": "lactulose",
    "looz": "lactulose",
    "cremaffin": "liquid paraffin + milk of magnesia",
    "dulcolax": "bisacodyl",
    "softovac": "ispaghula",
    "isabgol": "ispaghula",

    # -- Anti-diarrheal --
    "imodium": "loperamide",
    "eldoper": "loperamide",

    # -- Antihistamine / Anti-allergy brands --
    "cetrizine": "cetirizine",
    "okacet": "cetirizine",
    "cetzine": "cetirizine",
    "alerid": "cetirizine",
    "zyrtec": "cetirizine",
    "levocet": "levocetirizine",
    "xyzal": "levocetirizine",
    "vozet": "levocetirizine",
    "lcz": "levocetirizine",
    "allegra": "fexofenadine",
    "fexova": "fexofenadine",
    "altiva": "fexofenadine",
    "claritin": "loratadine",
    "lorfast": "loratadine",
    "benadryl": "diphenhydramine",
    "avil": "pheniramine",
    "atarax": "hydroxyzine",
    "practin": "cyproheptadine",
    "ciplactin": "cyproheptadine",
    "sinarest": "paracetamol + chlorpheniramine + phenylephrine",
    "cheston": "cetirizine + paracetamol + phenylephrine",

    # -- Respiratory / Cough brands --
    "asthalin": "salbutamol",
    "ventolin": "salbutamol",
    "deriphyllin": "theophylline + etophylline",
    "duolin": "ipratropium + levosalbutamol",
    "budecort": "budesonide",
    "pulmicort": "budesonide",
    "foracort": "budesonide + formoterol",
    "seroflo": "fluticasone + salmeterol",
    "flohale": "fluticasone",
    "tiova": "tiotropium",
    "spiriva": "tiotropium",
    "montair": "montelukast",
    "montek": "montelukast",
    "singulair": "montelukast",
    "romilast": "montelukast",
    "montek-lc": "montelukast + levocetirizine",
    "montair-lc": "montelukast + levocetirizine",
    "alex": "chlorpheniramine + dextromethorphan",
    "brozeet": "bromhexine",
    "solvin": "bromhexine",
    "mucolite": "ambroxol",
    "ambrodil": "ambroxol",
    "ascoril": "salbutamol + bromhexine + guaifenesin",
    "grilinctus": "dextromethorphan",
    "tusq-dx": "dextromethorphan",
    "zedex": "dextromethorphan + cetirizine",
    "mucomix": "acetylcysteine",

    # -- Antihypertensive brands --
    "stamlo": "amlodipine",
    "amlong": "amlodipine",
    "amlokind": "amlodipine",
    "amlopin": "amlodipine",
    "norvasc": "amlodipine",
    "calcigard": "nifedipine",
    "depin": "nifedipine",
    "cilnidip": "cilnidipine",
    "cilacar": "cilnidipine",
    "aten": "atenolol",
    "tenormin": "atenolol",
    "betacard": "atenolol",
    "metolar": "metoprolol",
    "betaloc": "metoprolol",
    "seloken": "metoprolol",
    "concor": "bisoprolol",
    "nebicard": "nebivolol",
    "nebilong": "nebivolol",
    "nebula": "nebivolol",
    "ciplar": "propranolol",
    "inderal": "propranolol",
    "carloc": "carvedilol",
    "coreg": "carvedilol",
    "envas": "enalapril",
    "cardace": "ramipril",
    "ramistar": "ramipril",
    "altace": "ramipril",
    "zestril": "lisinopril",
    "listril": "lisinopril",
    "covance": "losartan",
    "losar": "losartan",
    "repace": "losartan",
    "losacar": "losartan",
    "cozaar": "losartan",
    "telma": "telmisartan",
    "telmikind": "telmisartan",
    "micardis": "telmisartan",
    "telma-h": "telmisartan + hydrochlorothiazide",
    "diovan": "valsartan",
    "valzaar": "valsartan",
    "olmezest": "olmesartan",
    "olmetec": "olmesartan",
    "benicar": "olmesartan",
    "olvance": "olmesartan",
    "avapro": "irbesartan",
    "irovel": "irbesartan",
    "atacand": "candesartan",
    "lasix": "furosemide",
    "fruselac": "furosemide",
    "dytor": "torsemide",
    "aldactone": "spironolactone",
    "lasilactone": "furosemide + spironolactone",
    "dilzem": "diltiazem",
    "calaptin": "verapamil",
    "minipress": "prazosin",

    # -- Cardiac / Antiplatelet / Anticoagulant brands --
    "clopitab": "clopidogrel",
    "clopilet": "clopidogrel",
    "plavix": "clopidogrel",
    "plagril": "clopidogrel",
    "brilinta": "ticagrelor",
    "ecosprin-av": "aspirin + atorvastatin",
    "acitrom": "acenocoumarol",
    "warf": "warfarin",
    "coumadin": "warfarin",
    "eliquis": "apixaban",
    "xarelto": "rivaroxaban",
    "pradaxa": "dabigatran",
    "clexane": "enoxaparin",
    "lanoxin": "digoxin",
    "cordarone": "amiodarone",
    "sorbitrate": "isosorbide",
    "nitrocontin": "nitroglycerin",

    # -- Lipid-lowering brands --
    "atorva": "atorvastatin",
    "lipitor": "atorvastatin",
    "tonact": "atorvastatin",
    "atorlip": "atorvastatin",
    "storvas": "atorvastatin",
    "rozavel": "rosuvastatin",
    "rosuvas": "rosuvastatin",
    "crestor": "rosuvastatin",
    "rosulip": "rosuvastatin",
    "simcard": "simvastatin",
    "zocor": "simvastatin",
    "lipicard": "fenofibrate",
    "lipikind": "fenofibrate",
    "fenolip": "fenofibrate",
    "ezetrol": "ezetimibe",
    "ezentia": "ezetimibe",

    # -- Antidiabetic brands --
    "glycomet": "metformin",
    "glucophage": "metformin",
    "obimet": "metformin",
    "glycomet-gp": "glimepiride + metformin",
    "gemer": "glimepiride + metformin",
    "amaryl": "glimepiride",
    "glimy": "glimepiride",
    "glimstar": "glimepiride",
    "glynase": "glipizide",
    "diamicron": "gliclazide",
    "glizid": "gliclazide",
    "pioz": "pioglitazone",
    "actos": "pioglitazone",
    "januvia": "sitagliptin",
    "istavel": "sitagliptin",
    "jalra": "vildagliptin",
    "galvus": "vildagliptin",
    "zita": "vildagliptin",
    "trajenta": "linagliptin",
    "onglyza": "saxagliptin",
    "ziten": "teneligliptin",
    "tenepure": "teneligliptin",
    "jardiance": "empagliflozin",
    "gibtulio": "empagliflozin",
    "forxiga": "dapagliflozin",
    "oxra": "dapagliflozin",
    "invokana": "canagliflozin",
    "vobose": "voglibose",
    "ppg": "voglibose",
    "glucobay": "acarbose",
    "lantus": "insulin glargine",
    "basalog": "insulin glargine",
    "novorapid": "insulin aspart",
    "humalog": "insulin lispro",
    "actrapid": "insulin regular",
    "mixtard": "insulin premixed",

    # -- Thyroid brands --
    "thyronorm": "levothyroxine",
    "eltroxin": "levothyroxine",
    "thyrox": "levothyroxine",
    "neo-mercazole": "carbimazole",
    "neomercazole": "carbimazole",

    # -- Corticosteroid brands --
    "wysolone": "prednisolone",
    "omnacortil": "prednisolone",
    "deltone": "prednisolone",
    "medrol": "methylprednisolone",
    "solumedrol": "methylprednisolone",
    "dexona": "dexamethasone",
    "decdan": "dexamethasone",
    "defcort": "deflazacort",
    "calcort": "deflazacort",
    "momate": "mometasone",
    "nasonex": "mometasone",
    "flonase": "fluticasone",
    "betnovate": "betamethasone",
    "tenovate": "clobetasol",
    "lobate": "clobetasol",
    "clobeta": "clobetasol",
    "kenacort": "triamcinolone",
    "panderm": "clobetasol + neomycin + miconazole",
    "quadriderm": "betamethasone + neomycin + clotrimazole",

    # -- Topical / Dermatology brands --
    "t-bact": "mupirocin",
    "mupibact": "mupirocin",
    "soframycin": "framycetin",
    "fucidin": "fusidic acid",
    "fucibact": "fusidic acid",
    "betadine": "povidone iodine",
    "silvadene": "silver sulfadiazine",
    "lacto calamine": "calamine",
    "mintop": "minoxidil",
    "tugain": "minoxidil",
    "finpecia": "finasteride",
    "propecia": "finasteride",

    # -- Nasal / ENT brands --
    "otrivin": "xylometazoline",
    "nasivion": "oxymetazoline",
    "xylomet": "xylometazoline",
    "flomist": "fluticasone nasal",
    "mometone": "mometasone nasal",

    # -- Psychiatry / CNS brands --
    "alprax": "alprazolam",
    "trika": "alprazolam",
    "restyl": "alprazolam",
    "calmpose": "diazepam",
    "valium": "diazepam",
    "lonazep": "clonazepam",
    "rivotril": "clonazepam",
    "epitril": "clonazepam",
    "ativan": "lorazepam",
    "frisium": "clobazam",
    "nitrest": "zolpidem",
    "stilnox": "zolpidem",
    "nexito": "escitalopram",
    "cipralex": "escitalopram",
    "stalopam": "escitalopram",
    "rexipra": "escitalopram",
    "serta": "sertraline",
    "daxid": "sertraline",
    "zoloft": "sertraline",
    "fludac": "fluoxetine",
    "prozac": "fluoxetine",
    "pexep": "paroxetine",
    "paxil": "paroxetine",
    "cymbalta": "duloxetine",
    "duzela": "duloxetine",
    "dulane": "duloxetine",
    "venlor": "venlafaxine",
    "effexor": "venlafaxine",
    "veniz": "venlafaxine",
    "tryptomer": "amitriptyline",
    "amitone": "amitriptyline",
    "mirtaz": "mirtazapine",
    "remeron": "mirtazapine",
    "oleanz": "olanzapine",
    "zyprexa": "olanzapine",
    "olanex": "olanzapine",
    "sizodon": "risperidone",
    "risperdal": "risperidone",
    "risdone": "risperidone",
    "qutan": "quetiapine",
    "seroquel": "quetiapine",
    "quel": "quetiapine",
    "abilify": "aripiprazole",
    "arip": "aripiprazole",
    "arzu": "aripiprazole",
    "serenace": "haloperidol",
    "lithosun": "lithium",

    # -- Antiepileptic brands --
    "eptoin": "phenytoin",
    "dilantin": "phenytoin",
    "tegretol": "carbamazepine",
    "zen": "carbamazepine",
    "mazetol": "carbamazepine",
    "trileptal": "oxcarbazepine",
    "oxetol": "oxcarbazepine",
    "valparin": "sodium valproate",
    "depakote": "divalproex",
    "encorate": "sodium valproate",
    "levipil": "levetiracetam",
    "keppra": "levetiracetam",
    "levesam": "levetiracetam",
    "lamictal": "lamotrigine",
    "lamitor": "lamotrigine",
    "topamax": "topiramate",
    "topamac": "topiramate",
    "gabapin": "gabapentin",
    "neurontin": "gabapentin",
    "gabantin": "gabapentin",
    "pregalin": "pregabalin",
    "lyrica": "pregabalin",
    "pregaba": "pregabalin",
    "prebel": "pregabalin",

    # -- Muscle relaxant brands --
    "myospaz": "chlorzoxazone",
    "flexura": "chlorzoxazone",
    "liofen": "baclofen",
    "sirdalud": "tizanidine",
    "tizafen": "tizanidine",
    "thiocolchicoside": "thiocolchicoside",
    "myoril": "thiocolchicoside",

    # -- Urology brands --
    "urimax": "tamsulosin",
    "flomax": "tamsulosin",
    "contiflo": "tamsulosin",
    "veltam": "tamsulosin",
    "alfoo": "alfuzosin",
    "silodal": "silodosin",
    "duprost": "dutasteride",
    "avodart": "dutasteride",
    "fincar": "finasteride",
    "viagra": "sildenafil",
    "manforce": "sildenafil",
    "penegra": "sildenafil",
    "cialis": "tadalafil",
    "megalis": "tadalafil",
    "tadacip": "tadalafil",

    # -- Supplement brands --
    "shelcal": "calcium + vitamin d3",
    "calcimax": "calcium + vitamin d3",
    "ccm": "calcium + vitamin d3",
    "gemcal": "calcium + vitamin d3",
    "tayo": "cholecalciferol",
    "d-rise": "cholecalciferol",
    "uprise": "cholecalciferol",
    "calcirol": "cholecalciferol",
    "arachitol": "cholecalciferol",
    "rocaltrol": "calcitriol",
    "alfa-d3": "alfacalcidol",
    "orofer": "iron + folic acid",
    "autrin": "ferrous fumarate + folic acid",
    "folvite": "folic acid",
    "becosules": "b-complex + vitamin c",
    "supradyn": "multivitamin",
    "revital": "multivitamin + ginseng",
    "zincovit": "multivitamin + zinc",
    "limcee": "vitamin c",
    "celin": "vitamin c",
    "neurobion": "vitamin b1 + b6 + b12",
    "methycobal": "methylcobalamin",
    "meconerv": "methylcobalamin",
    "rejunex": "methylcobalamin + alpha lipoic acid",

    # -- Gout brands --
    "zyloric": "allopurinol",
    "febuget": "febuxostat",
    "febucip": "febuxostat",
    "zurig": "febuxostat",

    # -- Miscellaneous brands --
    "librax": "chlordiazepoxide + clidinium",
    "norcolut": "norethisterone",
    "primolut": "norethisterone",
    "pause": "tranexamic acid",
    "tranexa": "tranexamic acid",
    "ethamsyl": "ethamsylate",
    "udiliv": "ursodeoxycholic acid",
    "ursocol": "ursodeoxycholic acid",
    "hcqs": "hydroxychloroquine",
    "saaz": "sulfasalazine",
    "mesacol": "mesalamine",
    "folitrax": "methotrexate",
}

BRAND_SET = set(BRAND_TO_GENERIC.keys())

# --------------------------------------------------------------------------
# ASR correction table -- known Whisper / speech-to-text misspellings
# --------------------------------------------------------------------------
ASR_CORRECTIONS = {
    # Paracetamol
    "paracetmol": "paracetamol", "paracetamole": "paracetamol",
    "parastamol": "paracetamol", "parasitamol": "paracetamol",
    "paracetamal": "paracetamol", "paracitamol": "paracetamol",
    "paracetomol": "paracetamol", "parcetamol": "paracetamol",

    # Amoxicillin
    "amoxicilin": "amoxicillin", "amoxcillin": "amoxicillin",
    "amoxiciline": "amoxicillin", "amoxycillin": "amoxicillin",
    "amoxacilin": "amoxicillin", "amoxicllin": "amoxicillin",
    "amoxycilin": "amoxicillin", "amoxocellin": "amoxicillin",
    "amoxycylin": "amoxicillin",

    # Ciprofloxacin
    "ciproflaxin": "ciprofloxacin", "ciprofloxin": "ciprofloxacin",
    "ciprofoxacin": "ciprofloxacin", "ciproloxacin": "ciprofloxacin",
    "cyprofloxacin": "ciprofloxacin", "siprofloxacin": "ciprofloxacin",

    # Azithromycin
    "azithromicin": "azithromycin", "azithromysin": "azithromycin",
    "azitromycin": "azithromycin", "azithromycine": "azithromycin",
    "azythromycin": "azithromycin",

    # Cefixime
    "cefixim": "cefixime", "cephixime": "cefixime",
    "cefexime": "cefixime", "cefiксим": "cefixime",

    # Levofloxacin
    "levofloxin": "levofloxacin", "levoflaxin": "levofloxacin",
    "levofloxcin": "levofloxacin",

    # Ofloxacin
    "ofloxacine": "ofloxacin", "ofloxasin": "ofloxacin",

    # Moxifloxacin
    "moxifloxasin": "moxifloxacin", "moxifloxin": "moxifloxacin",

    # Metformin
    "metformine": "metformin", "metforman": "metformin",
    "metphormin": "metformin",

    # Ibuprofen
    "ibuprofin": "ibuprofen", "ibuprophen": "ibuprofen",
    "ibuprofene": "ibuprofen", "ibuprohen": "ibuprofen",

    # Aspirin
    "asprin": "aspirin", "asprine": "aspirin", "aspirine": "aspirin",

    # Atorvastatin
    "atorvastain": "atorvastatin", "atorvastin": "atorvastatin",
    "atorvastatine": "atorvastatin",

    # Rosuvastatin
    "rosuvastain": "rosuvastatin", "rosuvastatine": "rosuvastatin",
    "rosuvastin": "rosuvastatin",

    # Amlodipine
    "amlodapine": "amlodipine", "amlodepine": "amlodipine",
    "amlodipin": "amlodipine", "amlodapene": "amlodipine",

    # Pantoprazole
    "pantoprazol": "pantoprazole", "pantaprazole": "pantoprazole",
    "pantoprazle": "pantoprazole",

    # Omeprazole
    "omeprazol": "omeprazole", "omiprazole": "omeprazole",
    "omeprasole": "omeprazole",

    # Esomeprazole
    "esomeprazol": "esomeprazole", "esomiprazole": "esomeprazole",

    # Rabeprazole
    "rabeprazol": "rabeprazole", "rabiprazole": "rabeprazole",

    # Cetirizine
    "cetrizine": "cetirizine", "cetrazine": "cetirizine",
    "cetirizin": "cetirizine", "setrizine": "cetirizine",
    "ceterizine": "cetirizine",

    # Levocetirizine
    "levocetrizine": "levocetirizine", "levocetirizin": "levocetirizine",

    # Montelukast
    "monteleukast": "montelukast", "montelucast": "montelukast",
    "monteleucast": "montelukast", "montelukaste": "montelukast",

    # Metronidazole
    "metronidazol": "metronidazole", "metranidazole": "metronidazole",
    "metronidazle": "metronidazole",

    # Prednisolone
    "prednisolon": "prednisolone", "prednesolone": "prednisolone",

    # Losartan / Telmisartan
    "losartane": "losartan", "losartin": "losartan",
    "telmisartane": "telmisartan", "telmisartin": "telmisartan",
    "telmesartan": "telmisartan",

    # Ramipril
    "ramapril": "ramipril", "rampril": "ramipril",

    # Gabapentin / Pregabalin
    "gabapentine": "gabapentin", "gabapantin": "gabapentin",
    "pregabaline": "pregabalin", "pregablin": "pregabalin",
    "pragabalin": "pregabalin",

    # Sertraline / Fluoxetine / Escitalopram
    "sertralin": "sertraline", "sertaline": "sertraline",
    "fluoxetin": "fluoxetine", "fluoxatine": "fluoxetine",
    "escitaloprame": "escitalopram", "escitlopram": "escitalopram",

    # Clopidogrel
    "clopidogral": "clopidogrel", "clopidogril": "clopidogrel",

    # Clindamycin / Doxycycline / Clarithromycin
    "clindamicin": "clindamycin", "clindamycine": "clindamycin",
    "doxycyclin": "doxycycline", "doxicicline": "doxycycline",
    "clarithromicin": "clarithromycin", "claritromycin": "clarithromycin",

    # Furosemide / Spironolactone
    "furosemid": "furosemide", "furocemide": "furosemide",
    "frusemide": "furosemide",
    "spironolacton": "spironolactone",

    # Carbamazepine / Phenytoin / Levetiracetam
    "carbamazepin": "carbamazepine", "carbamazapine": "carbamazepine",
    "phenitoin": "phenytoin", "fenitoyn": "phenytoin",
    "levetiracetame": "levetiracetam", "levetiracitam": "levetiracetam",

    # Diclofenac / Aceclofenac
    "diclofenack": "diclofenac", "diclofinac": "diclofenac",
    "diclofenec": "diclofenac",
    "aceclofenack": "aceclofenac", "aceclofenec": "aceclofenac",

    # Acyclovir
    "aciclovir": "acyclovir", "asyclovir": "acyclovir",

    # Nimesulide
    "nimesulid": "nimesulide", "nimesuilde": "nimesulide",

    # Glimepiride
    "glimepirid": "glimepiride", "glimepride": "glimepiride",

    # Other common errors
    "valaciclovir": "valacyclovir",
    "salbutamole": "salbutamol",
    "tamsulocin": "tamsulosin",
    "ondansetrone": "ondansetron",
    "domperidon": "domperidone",
    "simvastatine": "simvastatin",
    "metoclopramid": "metoclopramide",
    "lansoprazol": "lansoprazole",
    "albendazol": "albendazole",
    "fluconazol": "fluconazole",
    "itraconazol": "itraconazole",
    "ornidazol": "ornidazole",
    "tinidazol": "tinidazole",
    "deflazacort": "deflazacort",
    "vildagliptin": "vildagliptin",
    "sitagliptin": "sitagliptin",
    "empagliflozine": "empagliflozin",
    "dapagliflozine": "dapagliflozin",
    "terbinafin": "terbinafine",
    "hydroxychloroquin": "hydroxychloroquine",
    "methylcobalamine": "methylcobalamin",
    "cholecalciferol": "cholecalciferol",
}

# --------------------------------------------------------------------------
# Joined-word ASR corrections -- when Whisper splits a medicine name
# --------------------------------------------------------------------------
JOINED_ASR_CORRECTIONS = {
    "a moxicillin": "amoxicillin",
    "a moxicilin": "amoxicillin",
    "a moxy cillin": "amoxicillin",
    "para ceta mol": "paracetamol",
    "para cetamol": "paracetamol",
    "para cet amol": "paracetamol",
    "cipro floxacin": "ciprofloxacin",
    "cipro floxa cin": "ciprofloxacin",
    "azithro mycin": "azithromycin",
    "azithro my cin": "azithromycin",
    "met formin": "metformin",
    "met for min": "metformin",
    "ibu profen": "ibuprofen",
    "ibu pro fen": "ibuprofen",
    "ator vastatin": "atorvastatin",
    "ator va statin": "atorvastatin",
    "amlo dipine": "amlodipine",
    "pan to prazole": "pantoprazole",
    "panto prazole": "pantoprazole",
    "ome prazole": "omeprazole",
    "eso meprazole": "esomeprazole",
    "rabe prazole": "rabeprazole",
    "monte lukast": "montelukast",
    "monte lu kast": "montelukast",
    "levo floxacin": "levofloxacin",
    "levo cetiri zine": "levocetirizine",
    "levo cetirizine": "levocetirizine",
    "metro nidazole": "metronidazole",
    "metro ni dazole": "metronidazole",
    "clo pidogrel": "clopidogrel",
    "clopi dogrel": "clopidogrel",
    "pre gabalin": "pregabalin",
    "pre gablin": "pregabalin",
    "gaba pentin": "gabapentin",
    "gaba pen tin": "gabapentin",
    "rosu vastatin": "rosuvastatin",
    "diclof enac": "diclofenac",
    "diclo fenac": "diclofenac",
    "ace clofenac": "aceclofenac",
    "furo semide": "furosemide",
    "clari thromycin": "clarithromycin",
    "doxy cycline": "doxycycline",
    "clinda mycin": "clindamycin",
    "carba mazepine": "carbamazepine",
    "pred nisolone": "prednisolone",
    "dexa methasone": "dexamethasone",
    "hydro chlorothiazide": "hydrochlorothiazide",
    "hydro chloro thiazide": "hydrochlorothiazide",
    "spirono lactone": "spironolactone",
    "val sartan": "valsartan",
    "tel misartan": "telmisartan",
    "olme sartan": "olmesartan",
    "lis inopril": "lisinopril",
    "lor atadine": "loratadine",
    "ceti rizine": "cetirizine",
    "sal butamol": "salbutamol",
    "leve tiracetam": "levetiracetam",
    "lamo trigine": "lamotrigine",
    "escita lopram": "escitalopram",
    "cefix ime": "cefixime",
    "cef triaxone": "ceftriaxone",
    "cef uroxime": "cefuroxime",
    "cef podoxime": "cefpodoxime",
    "moxi floxacin": "moxifloxacin",
    "nime sulide": "nimesulide",
    "etorico xib": "etoricoxib",
    "glime piride": "glimepiride",
    "sita gliptin": "sitagliptin",
    "vilda gliptin": "vildagliptin",
    "empa gliflozin": "empagliflozin",
    "dapa gliflozin": "dapagliflozin",
    "defla zacort": "deflazacort",
    "methyl prednisolone": "methylprednisolone",
    "chlor pheniramine": "chlorpheniramine",
    "diphen hydramine": "diphenhydramine",
    "hydroxy chloroquine": "hydroxychloroquine",
    "methyl cobalamin": "methylcobalamin",
    "cholecal ciferol": "cholecalciferol",
}

# --------------------------------------------------------------------------
# Frequency aliases
# --------------------------------------------------------------------------
FREQUENCY_ALIASES = {
    "od": "once daily", "o.d.": "once daily",
    "bd": "twice daily", "b.d.": "twice daily",
    "bid": "twice daily", "b.i.d.": "twice daily",
    "tid": "three times daily", "t.i.d.": "three times daily",
    "tds": "three times daily", "t.d.s.": "three times daily",
    "qid": "four times daily", "q.i.d.": "four times daily",
    "qds": "four times daily", "q.d.s.": "four times daily",
    "hs": "at bedtime", "h.s.": "at bedtime",
    "prn": "as needed", "p.r.n.": "as needed",
    "sos": "as needed", "stat": "immediately (one time)",
    "once a day": "once daily", "one time a day": "once daily",
    "once daily": "once daily", "once per day": "once daily",
    "twice a day": "twice daily", "two times a day": "twice daily",
    "twice daily": "twice daily", "twice per day": "twice daily",
    "three times a day": "three times daily",
    "thrice a day": "three times daily",
    "thrice daily": "three times daily",
    "three times daily": "three times daily",
    "four times a day": "four times daily",
    "four times daily": "four times daily",
    "every 4 hours": "every 4 hours",
    "every four hours": "every 4 hours",
    "every 6 hours": "every 6 hours",
    "every six hours": "every 6 hours",
    "every 8 hours": "every 8 hours",
    "every eight hours": "every 8 hours",
    "every 12 hours": "every 12 hours",
    "every twelve hours": "every 12 hours",
    "in the morning": "once daily (morning)",
    "in the evening": "once daily (evening)",
    "at night": "once daily (night)",
    "at bedtime": "at bedtime", "before bed": "at bedtime",
    "morning and evening": "twice daily (morning and evening)",
    "morning and night": "twice daily (morning and night)",
    "morning afternoon and night": "three times daily",
    "morning afternoon evening": "three times daily",
    "alternate days": "every alternate day",
    "every other day": "every alternate day",
    "once a week": "once weekly", "once weekly": "once weekly",
    "twice a week": "twice weekly",
}

# --------------------------------------------------------------------------
# Dosage units
# --------------------------------------------------------------------------
DOSAGE_UNITS = [
    "mg", "milligram", "milligrams",
    "g", "gram", "grams",
    "mcg", "microgram", "micrograms",
    "ml", "milliliter", "milliliters", "millilitre", "millilitres",
    "l", "liter", "liters", "litre", "litres",
    "cc", "iu", "units", "unit",
    "tablet", "tablets", "tab", "tabs",
    "capsule", "capsules", "cap", "caps",
    "drop", "drops", "puff", "puffs",
    "spray", "sprays",
    "teaspoon", "teaspoons", "tsp",
    "tablespoon", "tablespoons", "tbsp",
    "patch", "patches",
    "suppository", "suppositories",
    "injection", "injections",
    "sachet", "sachets",
    "spoon", "spoons",
]

# --------------------------------------------------------------------------
# Duration units
# --------------------------------------------------------------------------
DURATION_UNITS = [
    "day", "days", "week", "weeks", "month", "months", "year", "years",
]

# --------------------------------------------------------------------------
# Common instruction phrases
# --------------------------------------------------------------------------
INSTRUCTION_PHRASES = [
    "before meals", "before food", "before eating", "before breakfast",
    "before lunch", "before dinner",
    "after meals", "after food", "after eating", "after breakfast",
    "after lunch", "after dinner",
    "with meals", "with food", "with breakfast", "with lunch", "with dinner",
    "on an empty stomach", "on empty stomach", "between meals",
    "with water", "with warm water", "with milk", "with juice", "with honey",
    "chew before swallowing", "chew and swallow", "dissolve in water",
    "apply on affected area", "apply topically", "apply externally",
    "apply to the skin",
    "inhale", "inhale orally",
    "under the tongue", "sublingual",
    "insert rectally", "insert vaginally",
    "at bedtime", "before bed", "before sleep", "before sleeping",
    "in the morning", "in the evening", "at night",
    "on waking up", "after waking up",
    "do not crush", "do not chew", "do not take with alcohol",
    "take with plenty of water", "shake well before use",
    "keep refrigerated", "avoid sunlight", "avoid sun exposure",
    "avoid dairy", "avoid milk", "avoid antacids",
    "as directed", "as prescribed",
    "if needed", "when needed", "as needed",
    "until finished", "complete the course",
]

# --------------------------------------------------------------------------
# Prescription splitting keywords
# --------------------------------------------------------------------------
PRESCRIPTION_DELIMITERS = [
    " and also ", " and then ", " also take ", " next ",
    " then take ", " additionally ", " along with ",
    " followed by ", " plus ", " and ",
]

# --------------------------------------------------------------------------
# Number words -> digit mapping
# --------------------------------------------------------------------------
NUMBER_WORDS = {
    "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
    "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
    "eleven": "11", "twelve": "12", "thirteen": "13", "fourteen": "14",
    "fifteen": "15", "twenty": "20", "thirty": "30",
    "half": "0.5", "quarter": "0.25",
}

# --------------------------------------------------------------------------
# Words that should never be matched as medicine names
# --------------------------------------------------------------------------
NON_MEDICINE_WORDS = {
    "take", "give", "prescribe", "recommend", "need", "should", "must",
    "daily", "twice", "once", "three", "four", "five", "times",
    "day", "days", "week", "weeks", "month", "months",
    "after", "before", "with", "without", "during",
    "meals", "food", "water", "milk", "juice",
    "morning", "evening", "night", "afternoon", "bedtime",
    "tablet", "tablets", "capsule", "capsules", "drops", "syrup",
    "the", "a", "an", "and", "or", "to", "of", "in", "on", "for",
    "please", "kindly", "also", "then", "next", "plus",
    "patient", "doctor", "prescribed", "prescription",
    "every", "each", "per", "hour", "hours",
    "empty", "stomach", "full",
    "apply", "inhale", "inject", "dissolve",
    "that", "this", "these", "those", "from", "into",
    "dose", "dosage", "course", "complete",
    "not", "do", "don", "does", "did",
    "mg", "ml", "gram", "grams", "milligram", "milligrams",
}
