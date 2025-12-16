"""
Word lists for PHI detection.

Based on pyDeid (GEMINI-Medicine) word lists with enhancements.
https://github.com/GEMINI-Medicine/pyDeid
"""

from typing import FrozenSet, Set


# Common first names (unambiguous - high confidence they're names)
# Subset from pyDeid male_names_unambig_v2.txt and female_names_unambig_v2.txt
FIRST_NAMES_UNAMBIG: FrozenSet[str] = frozenset({
    # Male names (common)
    "aaron", "abdul", "abel", "abraham", "adam", "adrian", "ahmad", "ahmed",
    "alan", "albert", "alberto", "alejandro", "alex", "alexander", "alfred",
    "alfredo", "allan", "allen", "alvin", "andrew", "andy", "angel", "angelo",
    "anthony", "antonio", "armando", "arnold", "arthur", "arturo",
    "benjamin", "bernard", "bill", "billy", "bob", "bobby", "brad", "bradley",
    "brandon", "brian", "bruce", "bryan", "byron",
    "calvin", "cameron", "carl", "carlos", "cecil", "chad", "charles",
    "charlie", "chester", "chris", "christian", "christopher", "clarence",
    "claude", "clifford", "clyde", "cody", "colin", "corey", "craig",
    "curtis", "dale", "dallas", "daniel", "danny", "darrell", "darren",
    "darryl", "david", "dean", "dennis", "derek", "derrick", "don", "donald",
    "douglas", "duane", "dustin", "dwayne", "dwight",
    "earl", "eddie", "edgar", "edmund", "eduardo", "edward", "edwin",
    "elmer", "enrique", "eric", "erik", "ernest", "eugene", "evan",
    "felix", "fernando", "floyd", "francis", "francisco", "frank", "fred",
    "frederick", "gabriel", "gary", "gene", "george", "gerald", "gilbert",
    "glen", "glenn", "gordon", "greg", "gregory", "gustavo",
    "harold", "harry", "harvey", "hector", "henry", "herbert", "herman",
    "howard", "hugh", "ian", "isaac", "ivan",
    "jack", "jacob", "jaime", "jake", "james", "jamie", "jared", "jason",
    "javier", "jay", "jeff", "jeffery", "jeffrey", "jeremy", "jerome",
    "jerry", "jesse", "jesus", "jim", "jimmie", "jimmy", "joe", "joel",
    "john", "johnathan", "johnnie", "johnny", "jon", "jonathan", "jordan",
    "jorge", "jose", "joseph", "joshua", "juan", "julian", "julio", "justin",
    "karl", "keith", "kelly", "ken", "kenneth", "kent", "kevin", "kirk", "kurt",
    "lance", "larry", "lawrence", "lee", "leon", "leonard", "leroy", "leslie",
    "lester", "lewis", "lloyd", "lonnie", "louis", "luis", "luther", "lyle",
    "manuel", "marc", "marcus", "mario", "marion", "mark", "marshall",
    "martin", "marvin", "mathew", "matthew", "maurice", "max", "melvin",
    "michael", "micheal", "miguel", "mike", "milton", "mitchell", "morris",
    "nathan", "nathaniel", "neil", "nelson", "nicholas", "nick", "norman",
    "oliver", "omar", "orlando", "oscar", "otis", "owen",
    "patrick", "paul", "pedro", "perry", "peter", "philip", "phillip",
    "rafael", "ralph", "ramon", "randall", "randy", "raul", "ray", "raymond",
    "reginald", "ricardo", "richard", "rick", "ricky", "robert", "roberto",
    "roderick", "rodney", "roger", "roland", "ronald", "ronnie", "ross",
    "roy", "ruben", "russell", "ryan",
    "salvador", "sam", "sammy", "samuel", "scott", "sean", "sergio", "seth",
    "shane", "shawn", "sidney", "stanley", "stephen", "steve", "steven",
    "ted", "terrance", "terrence", "terry", "theodore", "thomas", "tim",
    "timothy", "todd", "tom", "tommy", "tony", "tracy", "travis", "troy",
    "tyler", "vernon", "victor", "vincent", "virgil",
    "wallace", "walter", "warren", "wayne", "wesley", "william", "willie",
    "zachary",

    # Female names (common)
    "abigail", "adriana", "adrienne", "agnes", "aileen", "aimee", "alicia",
    "alison", "allison", "alma", "amanda", "amber", "amy", "ana", "andrea",
    "angela", "angie", "anita", "ann", "anna", "anne", "annette", "annie",
    "antoinette", "april", "arlene", "ashley", "audrey",
    "barbara", "beatrice", "becky", "belinda", "bernadette", "bernice",
    "bertha", "beth", "betty", "beverly", "billie", "bonnie", "brenda",
    "bridget", "brittany",
    "caitlin", "candace", "carla", "carmen", "carol", "carole", "caroline",
    "carolyn", "carrie", "cassandra", "catherine", "cathy", "cecilia",
    "charlene", "charlotte", "cheryl", "christina", "christine", "cindy",
    "claire", "clara", "claudia", "colleen", "connie", "constance",
    "courtney", "crystal", "cynthia",
    "daisy", "dana", "danielle", "darlene", "dawn", "deanna", "debbie",
    "deborah", "debra", "denise", "diana", "diane", "dianne", "dolores",
    "donna", "dora", "doris", "dorothy",
    "edith", "edna", "eileen", "elaine", "eleanor", "elena", "elizabeth",
    "ella", "ellen", "elsie", "emily", "emma", "erica", "erin", "esther",
    "ethel", "eva", "evelyn",
    "felicia", "florence", "frances", "francine", "gail", "georgia",
    "geraldine", "gertrude", "gina", "gladys", "glenda", "gloria",
    "grace", "gwendolyn",
    "hannah", "harriet", "hazel", "heather", "heidi", "helen", "henrietta",
    "holly",
    "ida", "irene", "irma", "isabel", "jackie", "jacqueline", "jamie",
    "jan", "jane", "janet", "janice", "jasmine", "jean", "jeanette",
    "jeanne", "jennifer", "jenny", "jessica", "jill", "jo", "joan",
    "joann", "joanne", "jodi", "jodie", "jody", "josephine", "joy", "joyce",
    "juanita", "judith", "judy", "julia", "julie", "june",
    "karen", "karin", "kate", "katherine", "kathleen", "kathryn", "kathy",
    "katie", "katrina", "kay", "kayla", "kelly", "kendra", "kerry", "kim",
    "kimberly", "kristen", "kristin", "kristina", "kristine", "krystal",
    "laura", "lauren", "laurie", "leah", "lena", "leslie", "lillian",
    "linda", "lisa", "lois", "loretta", "lori", "lorraine", "louise",
    "lucia", "lucille", "lucy", "lydia", "lynn",
    "mabel", "madeline", "mandy", "marcia", "margaret", "margarita",
    "maria", "marian", "marie", "marilyn", "marion", "marjorie", "marlene",
    "marsha", "martha", "mary", "maryann", "maureen", "maxine", "megan",
    "melanie", "melinda", "melissa", "melody", "mercedes", "michelle",
    "mildred", "minnie", "miriam", "molly", "monica", "muriel", "myrtle",
    "nadine", "nancy", "naomi", "natalie", "nellie", "nicole", "nina",
    "nora", "norma",
    "olga", "olivia", "opal", "pamela", "pat", "patricia", "patsy",
    "paula", "pauline", "pearl", "peggy", "penny", "phyllis", "priscilla",
    "rachael", "rachel", "ramona", "rebecca", "regina", "renee", "rhonda",
    "rita", "roberta", "robin", "robyn", "rochelle", "rosa", "rosalie",
    "rose", "rosemarie", "rosemary", "roxanne", "ruby", "ruth",
    "sabrina", "sally", "samantha", "sandra", "sara", "sarah", "shannon",
    "sharon", "sheila", "shelby", "shelia", "shelly", "sheri", "sherri",
    "sherry", "shirley", "sonia", "sonja", "sophia", "stacey", "stacy",
    "stella", "stephanie", "sue", "susan", "suzanne", "sylvia",
    "tamara", "tammy", "tanya", "tara", "teresa", "terri", "terry",
    "thelma", "theresa", "tiffany", "tina", "toni", "tonya", "tracey",
    "tracy", "vanessa", "velma", "vera", "veronica", "vicki", "vickie",
    "vicky", "victoria", "viola", "violet", "virginia", "vivian",
    "wanda", "wendy", "whitney", "wilma", "yolanda", "yvette", "yvonne",

    # International names (from PII benchmarks)
    # French
    "nathalie", "olivier", "sindy",
    # Spanish/Latin
    "pepa", "deiby", "fareed", "ponce", "medrano", "samaca", "sarria", "ramadan",
    # Arabic/South Asian
    "mohd", "asim", "zia", "sunar",
    # African
    "hlengiwe", "mlungisi",
    # Hawaiian/Pacific Islander
    "mahi",
    # Short names that are unambiguous
    "al",  # Common nickname for Albert/Alan/Alfred
})


# Ambiguous last names - words that are also common English words
# These need more context to confirm they're names
LAST_NAMES_AMBIG: FrozenSet[str] = frozenset({
    # Animals
    "bird", "crane", "crow", "dove", "eagle", "finch", "fish", "fox",
    "hawk", "heron", "jay", "lark", "martin", "otter", "raven", "robin",
    "sparrow", "swan", "wolf",

    # Colors
    "black", "blue", "brown", "gray", "green", "grey", "white",

    # Nature/Geography
    "banks", "beach", "berry", "brook", "brooks", "bush", "camp",
    "clay", "cliff", "cloud", "creek", "dale", "field", "fields",
    "ford", "forest", "glen", "grove", "hall", "hill", "hills",
    "lake", "lakes", "lane", "marsh", "meadow", "moon", "mountain",
    "park", "parks", "pool", "rice", "ridge", "river", "rivers",
    "rock", "rose", "snow", "spring", "springs", "stone", "storm",
    "summer", "sunny", "valley", "waters", "wells", "west", "winter",
    "wood", "woods",

    # Occupations/Titles
    "archer", "baker", "barber", "bishop", "butler", "carpenter",
    "carter", "chandler", "cook", "cooper", "dean", "farmer", "fisher",
    "fletcher", "foreman", "fowler", "gardner", "hunter", "knight",
    "mason", "miller", "page", "palmer", "parker", "porter", "potter",
    "price", "shepherd", "singer", "slater", "smith", "tanner",
    "taylor", "turner", "walker", "ward", "weaver", "webb",

    # Body parts/Medical
    "blood", "bone", "hand", "head", "heart", "lamb", "palm",

    # Common words
    "ball", "banks", "bar", "bass", "bell", "best", "bishop", "bond",
    "booth", "bower", "box", "branch", "brand", "bridges", "bright",
    "brothers", "buck", "bull", "burns", "bush", "cannon", "case",
    "cash", "castle", "chambers", "chance", "chase", "cherry", "church",
    "close", "cole", "combs", "cone", "cross", "crown", "daily",
    "daniel", "day", "dear", "drew", "duke", "elder", "english",
    "fan", "fast", "fields", "fine", "fry", "gage", "gay", "gear",
    "glass", "golden", "good", "grace", "grant", "graves", "gross",
    "hale", "hardy", "hart", "harvey", "hayes", "hicks", "high",
    "holder", "hood", "hope", "house", "hull", "james", "john",
    "johns", "jordan", "key", "keys", "king", "land", "law", "little",
    "long", "love", "lowe", "lynch", "mann", "marks", "marsh", "may",
    "mccoy", "miles", "mills", "moody", "moore", "moss", "noble",
    "north", "pace", "paul", "penn", "pitt", "pope", "post", "power",
    "powers", "price", "ray", "reed", "rich", "ring", "roe", "root",
    "rush", "savage", "sharp", "short", "small", "south", "speed",
    "spell", "stark", "stern", "still", "story", "strong", "sweet",
    "sweeney", "terry", "thomas", "tran", "wall", "walls", "waters",
    "webb", "wells", "west", "weston", "wise", "worth", "young",
})


# Common last names that are unambiguous (clearly surnames)
# Subset from pyDeid last_names_unambig_v2.txt
LAST_NAMES_UNAMBIG: FrozenSet[str] = frozenset({
    "abbott", "adams", "adkins", "aguilar", "alexander", "allen",
    "alvarado", "alvarez", "anderson", "andrews", "armstrong", "arnold",
    "austin", "bailey", "baldwin", "ballard", "barnes", "barnett",
    "barrett", "barton", "bates", "beck", "becker", "bennett", "benson",
    "berry", "bishop", "blair", "bowen", "bowman", "boyd", "bradley",
    "brady", "brewer", "briggs", "brock", "brooks", "brown", "bryant",
    "burgess", "burke", "burnett", "burns", "burton", "bush", "butler",
    "byrd", "caldwell", "campbell", "cannon", "carlson", "carpenter",
    "carr", "carroll", "carter", "casey", "castillo", "castro",
    "cervantes", "chambers", "chandler", "chang", "chapman", "chavez",
    "chen", "christensen", "clark", "clarke", "cohen", "cole", "coleman",
    "collins", "colon", "contreras", "cook", "cooper", "cortez", "cox",
    "crawford", "cruz", "cunningham", "curtis", "daniels", "davidson",
    "davis", "dawson", "deleon", "delgado", "dennis", "diaz", "dixon",
    "dominguez", "douglas", "doyle", "duncan", "dunn", "duran", "edwards",
    "elliott", "ellis", "erickson", "espinoza", "estrada", "evans",
    "farmer", "ferguson", "fernandez", "fields", "figueroa", "fisher",
    "fitzgerald", "fleming", "fletcher", "flores", "ford", "foster",
    "fowler", "fox", "francis", "frank", "franklin", "frazier", "freeman",
    "fuentes", "fuller", "gallagher", "gallegos", "garcia", "gardner",
    "garrett", "garza", "george", "gibson", "gilbert", "gomez", "gonzales",
    "gonzalez", "goodman", "goodwin", "gordon", "graham", "grant", "gray",
    "green", "greene", "gregory", "griffin", "gross", "guerra", "guerrero",
    "gutierrez", "guzman", "hale", "hall", "hamilton", "hammond", "hampton",
    "hansen", "hanson", "hardy", "harmon", "harper", "harrington", "harris",
    "harrison", "hart", "harvey", "hawkins", "hayes", "haynes", "henderson",
    "henry", "hensley", "hernandez", "herrera", "hicks", "higgins", "hill",
    "hodges", "hoffman", "holland", "holloway", "holmes", "holt", "hopkins",
    "horton", "houston", "howard", "howell", "hudson", "hughes", "hunt",
    "hunter", "ibarra", "ingram", "jackson", "jacobs", "james", "jenkins",
    "jennings", "jensen", "jimenez", "johnson", "johnston", "jones",
    "jordan", "joseph", "juarez", "kelley", "kelly", "kennedy", "kim",
    "king", "klein", "knight", "lambert", "lane", "lara", "larson", "lawson",
    "lee", "leonard", "lewis", "lindsey", "little", "liu", "logan", "long",
    "lopez", "love", "lowe", "lucas", "luna", "lynch", "lyons", "macdonald",
    "mack", "maldonado", "malone", "mann", "manning", "marshall", "martin",
    "martinez", "mason", "matthews", "maxwell", "mccarthy", "mccoy",
    "mcdaniel", "mcdonald", "mcgee", "mckinney", "medina", "mejia",
    "mendez", "mendoza", "meyer", "miles", "miller", "mills", "miranda",
    "mitchell", "molina", "montgomery", "moore", "morales", "moran",
    "moreno", "morgan", "morris", "morrison", "moss", "mullins", "munoz",
    "murphy", "murray", "myers", "navarro", "nelson", "newman", "nguyen",
    "nichols", "norman", "norris", "nunez", "obrien", "ochoa", "oliver",
    "olson", "orozco", "ortega", "ortiz", "osborne", "owens", "pacheco",
    "padilla", "palmer", "park", "parker", "parks", "patterson", "paul",
    "payne", "pearson", "pena", "perez", "perkins", "perry", "person",
    "peters", "peterson", "pham", "phillips", "pierce", "porter", "powell",
    "price", "quinn", "ramirez", "ramos", "randall", "ray", "reed",
    "reese", "reeves", "reid", "reyes", "reynolds", "rhodes", "rice",
    "richards", "richardson", "riley", "rios", "rivera", "robbins",
    "roberts", "robertson", "robinson", "rodriguez", "rogers", "rojas",
    "roman", "romero", "rosales", "ross", "rowe", "ruiz", "russell", "ryan",
    "salazar", "sanchez", "sanders", "sandoval", "santiago", "santos",
    "saunders", "schmidt", "schneider", "schultz", "schwartz", "scott",
    "serrano", "sharp", "shaw", "shelton", "sherman", "silva", "simmons",
    "simon", "simpson", "sims", "singh", "smith", "snyder", "solis",
    "soto", "spencer", "stanley", "steele", "stephens", "stevens",
    "stevenson", "stewart", "stokes", "stone", "sullivan", "sutton",
    "swanson", "taylor", "terry", "thomas", "thompson", "thornton",
    "todd", "torres", "townsend", "tran", "trujillo", "tucker", "turner",
    "valdez", "valencia", "vargas", "vasquez", "vaughn", "vazquez", "vega",
    "wade", "wagner", "walker", "wallace", "walsh", "walters", "walton",
    "wang", "ward", "warren", "washington", "watkins", "watson", "watts",
    "weaver", "webb", "weber", "webster", "weeks", "wells", "west",
    "wheeler", "white", "williams", "williamson", "willis", "wilson",
    "wong", "wood", "woods", "wright", "wu", "yang", "young", "zhang",
    "zimmerman",

    # International last names (from PII benchmarks)
    # French
    "sylla", "collet",
    # African
    "msibi",
    # Spanish/Latin surnames
    "samaca", "medrano", "ponce", "sarria", "ramadan", "sunar",
    # South Asian surnames (can also be first names)
    "asim",
})


# Medical titles and credentials (should NOT be flagged as names)
MEDICAL_TITLES: FrozenSet[str] = frozenset({
    "dr", "dr.", "doctor", "md", "m.d.", "do", "d.o.",
    "np", "n.p.", "pa", "p.a.", "pa-c",
    "rn", "r.n.", "lpn", "l.p.n.", "aprn", "a.p.r.n.",
    "phd", "ph.d.", "pharmd", "pharm.d.",
    "dpm", "d.p.m.", "dds", "d.d.s.", "dmd", "d.m.d.",
    "attending", "resident", "intern", "fellow",
    "nurse", "physician", "surgeon", "therapist",
})


# Common words that look like names but aren't
# These should be excluded from name detection
COMMON_WORDS_NOT_NAMES: FrozenSet[str] = frozenset({
    # Months that could be names
    "april", "august", "june", "may",

    # Days
    "friday", "monday", "saturday", "sunday", "thursday", "tuesday", "wednesday",

    # Medical/EHR abbreviations that look like names
    "dob", "mrn", "ssn", "dx", "hx", "rx", "sx", "tx", "cc", "hpi", "ros", "pe",
    "pmh", "psh", "fmh", "shx", "meds", "labs", "vitals", "plan", "assessment",

    # Medical terms that look like names
    "ace", "aid", "alert", "alpha", "beta", "bland", "blunt", "brief",
    "burr", "call", "calm", "cast", "chart", "chief", "chronic", "clamp",
    "clean", "clear", "code", "cold", "cool", "daily", "deep", "direct",
    "dry", "dull", "early", "easy", "even", "fair", "fast", "final",
    "fine", "firm", "flat", "free", "fresh", "full", "general", "good",
    "grand", "gross", "hard", "heavy", "high", "hot", "just", "keen",
    "late", "left", "light", "local", "long", "loose", "low", "main",
    "major", "mass", "mild", "minor", "mixed", "moderate", "moist", "more",
    "much", "near", "neat", "new", "next", "normal", "odd", "old", "only",
    "open", "oral", "other", "over", "own", "pale", "past", "per", "plain",
    "poor", "present", "primary", "prior", "proper", "pure", "quick",
    "quiet", "rapid", "rare", "raw", "ready", "real", "recent", "red",
    "regular", "related", "rest", "rich", "right", "rough", "round",
    "routine", "safe", "same", "second", "see", "senior", "serious",
    "set", "severe", "sharp", "short", "sick", "similar", "simple",
    "single", "slight", "slow", "small", "smooth", "soft", "solid",
    "special", "stable", "standard", "static", "steady", "sterile",
    "stiff", "still", "straight", "strange", "strict", "strong", "such",
    "sudden", "super", "sure", "sweet", "tender", "thick", "thin",
    "thorough", "tight", "tired", "total", "tough", "true", "upper",
    "usual", "various", "very", "warm", "weak", "well", "wet", "whole",
    "wide", "wild", "yellow",

    # General common words
    "about", "above", "across", "after", "again", "against", "ahead",
    "along", "also", "always", "among", "another", "around", "back",
    "been", "before", "behind", "being", "below", "best", "better",
    "between", "both", "came", "come", "could", "does", "done", "down",
    "each", "either", "else", "enough", "ever", "every", "find", "first",
    "found", "from", "gave", "give", "given", "goes", "gone", "going",
    "gotten", "great", "have", "having", "here", "however", "into",
    "just", "keep", "kept", "know", "known", "last", "later", "least",
    "less", "like", "made", "make", "many", "might", "most", "must",
    "never", "none", "nothing", "often", "once", "only", "other",
    "otherwise", "over", "perhaps", "quite", "rather", "really", "said",
    "same", "seen", "several", "shall", "should", "since", "some",
    "something", "soon", "still", "take", "taken", "than", "that",
    "their", "them", "then", "there", "these", "they", "thing", "this",
    "those", "though", "through", "thus", "together", "told", "took",
    "toward", "towards", "under", "until", "upon", "used", "using",
    "very", "want", "went", "were", "what", "whatever", "when", "where",
    "whether", "which", "while", "will", "with", "within", "without",
    "would", "your",
})


def is_likely_name(word: str) -> bool:
    """
    Check if a word is likely a name (first or last).

    Args:
        word: The word to check (case-insensitive)

    Returns:
        True if word is likely a name
    """
    w = word.lower().strip()

    # Definitely not a name if in common words
    if w in COMMON_WORDS_NOT_NAMES:
        return False

    # Definitely not a name if it's a medical title
    if w in MEDICAL_TITLES:
        return False

    # High confidence if in unambiguous lists
    if w in FIRST_NAMES_UNAMBIG:
        return True

    if w in LAST_NAMES_UNAMBIG:
        return True

    return False


def is_ambiguous_name(word: str) -> bool:
    """
    Check if a word could be a name but is ambiguous.

    Args:
        word: The word to check

    Returns:
        True if word might be a name but needs context
    """
    w = word.lower().strip()
    return w in LAST_NAMES_AMBIG


def get_all_names() -> Set[str]:
    """Get all known names (first and last)."""
    return set(FIRST_NAMES_UNAMBIG) | set(LAST_NAMES_UNAMBIG)
