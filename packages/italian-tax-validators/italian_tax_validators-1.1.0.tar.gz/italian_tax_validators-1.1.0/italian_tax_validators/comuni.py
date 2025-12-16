"""Italian municipality codes (Codici Catastali) database.

This module provides a mapping of Italian cadastral codes (codici catastali)
to municipality names and province codes. These codes are used in the
Codice Fiscale to identify the birth place.

The database includes:
- All Italian municipalities (comuni)
- Major foreign country codes (starting with Z)

Note: This is a representative subset of the most common codes.
For a complete database, consider using an external data source.
"""

from __future__ import annotations

# Cadastral code -> (Municipality name, Province code)
# Format: "X999": ("MUNICIPALITY NAME", "XX")
CODICI_CATASTALI: dict[str, tuple[str, str]] = {
    # =========================================================================
    # Major Italian Cities (Capoluoghi di Regione)
    # =========================================================================
    "A944": ("BARI", "BA"),
    "A952": ("BARLETTA", "BT"),
    "B354": ("BOLOGNA", "BO"),
    "B157": ("BOLZANO", "BZ"),
    "B180": ("BRESCIA", "BS"),
    "B428": ("CAGLIARI", "CA"),
    "B963": ("CAMPOBASSO", "CB"),
    "C351": ("CATANZARO", "CZ"),
    "D612": ("FIRENZE", "FI"),
    "E041": ("GENOVA", "GE"),
    "E625": ("L'AQUILA", "AQ"),
    "E463": ("LATINA", "LT"),
    "F205": ("MILANO", "MI"),
    "F839": ("NAPOLI", "NA"),
    "G273": ("PALERMO", "PA"),
    "G337": ("PARMA", "PR"),
    "G478": ("PERUGIA", "PG"),
    "G482": ("PESARO", "PU"),
    "G535": ("PIACENZA", "PC"),
    "G702": ("POTENZA", "PZ"),
    "H223": ("REGGIO CALABRIA", "RC"),
    "H224": ("REGGIO EMILIA", "RE"),
    "H501": ("ROMA", "RM"),
    "H703": ("SALERNO", "SA"),
    "I452": ("TORINO", "TO"),
    "I726": ("TRENTO", "TN"),
    "I403": ("TRIESTE", "TS"),
    "L219": ("UDINE", "UD"),
    "L736": ("VENEZIA", "VE"),
    "L781": ("VERONA", "VR"),
    "A271": ("ANCONA", "AN"),
    "A515": ("AOSTA", "AO"),
    
    # =========================================================================
    # Major Provincial Capitals (Capoluoghi di Provincia)
    # =========================================================================
    "A052": ("AGRIGENTO", "AG"),
    "A119": ("ALESSANDRIA", "AL"),
    "A399": ("AREZZO", "AR"),
    "A479": ("ASCOLI PICENO", "AP"),
    "A662": ("ASTI", "AT"),
    "A669": ("AVELLINO", "AV"),
    "B111": ("BELLUNO", "BL"),
    "B041": ("BENEVENTO", "BN"),
    "B249": ("BERGAMO", "BG"),
    "B832": ("BIELLA", "BI"),
    "C219": ("CALTANISSETTA", "CL"),
    "C352": ("CATANIA", "CT"),
    "C632": ("CHIETI", "CH"),
    "C858": ("COMO", "CO"),
    "C904": ("COSENZA", "CS"),
    "C933": ("CREMONA", "CR"),
    "C980": ("CROTONE", "KR"),
    "D009": ("CUNEO", "CN"),
    "D258": ("ENNA", "EN"),
    "D461": ("FERRARA", "FE"),
    "D643": ("FOGGIA", "FG"),
    "D705": ("FORLI'", "FC"),
    "D791": ("FROSINONE", "FR"),
    "E098": ("GORIZIA", "GO"),
    "E205": ("GROSSETO", "GR"),
    "E289": ("IMPERIA", "IM"),
    "E335": ("ISERNIA", "IS"),
    "E473": ("LA SPEZIA", "SP"),
    "E506": ("LECCE", "LE"),
    "E507": ("LECCO", "LC"),
    "E648": ("LIVORNO", "LI"),
    "E704": ("LODI", "LO"),
    "E715": ("LUCCA", "LU"),
    "E785": ("MACERATA", "MC"),
    "E835": ("MANTOVA", "MN"),
    "E877": ("MASSA", "MS"),
    "E891": ("MATERA", "MT"),
    "E956": ("MESSINA", "ME"),
    "F161": ("MODENA", "MO"),
    "F770": ("NOVARA", "NO"),
    "F809": ("NUORO", "NU"),
    "F844": ("OLBIA", "SS"),
    "F848": ("ORISTANO", "OR"),
    "G126": ("PADOVA", "PD"),
    "G388": ("PAVIA", "PV"),
    "G628": ("PISA", "PI"),
    "G636": ("PISTOIA", "PT"),
    "G713": ("PORDENONE", "PN"),
    "G786": ("PRATO", "PO"),
    "H141": ("RAGUSA", "RG"),
    "H163": ("RAVENNA", "RA"),
    "H282": ("RIETI", "RI"),
    "H294": ("RIMINI", "RN"),
    "H612": ("ROVIGO", "RO"),
    "I119": ("SASSARI", "SS"),
    "I138": ("SAVONA", "SV"),
    "I329": ("SIENA", "SI"),
    "I356": ("SIRACUSA", "SR"),
    "I362": ("SONDRIO", "SO"),
    "I588": ("TARANTO", "TA"),
    "I625": ("TERAMO", "TE"),
    "I632": ("TERNI", "TR"),
    "I785": ("TRAPANI", "TP"),
    "I819": ("TREVISO", "TV"),
    "L049": ("VARESE", "VA"),
    "L378": ("VERBANIA", "VB"),
    "L380": ("VERCELLI", "VC"),
    "L565": ("VICENZA", "VI"),
    "L682": ("VITERBO", "VT"),
    "M297": ("VIBO VALENTIA", "VV"),
    
    # =========================================================================
    # Other Major Municipalities
    # =========================================================================
    "A089": ("ALBANO LAZIALE", "RM"),
    "B715": ("BUSTO ARSIZIO", "VA"),
    "C129": ("CAIVANO", "NA"),
    "C573": ("CESENA", "FC"),
    "C675": ("CINISELLO BALSAMO", "MI"),
    "D969": ("GIUGLIANO IN CAMPANIA", "NA"),
    "E256": ("GUIDONIA MONTECELIO", "RM"),
    "E415": ("JESOLO", "VE"),
    "F158": ("MESTRE", "VE"),
    "F152": ("MODICA", "RG"),
    "F240": ("MOLFETTA", "BA"),
    "F257": ("MONCALIERI", "TO"),
    "F280": ("MONFALCONE", "GO"),
    "F299": ("MONOPOLI", "BA"),
    "F309": ("MONREALE", "PA"),
    "F329": ("MONTEBELLUNA", "TV"),
    "F537": ("MONTESILVANO", "PE"),
    "F656": ("NETTUNO", "RM"),
    "F799": ("NOCERA INFERIORE", "SA"),
    "G224": ("PAGANI", "SA"),
    "G393": ("PATERNÒ", "CT"),
    "G568": ("PIOMBINO", "LI"),
    "G687": ("POMIGLIANO D'ARCO", "NA"),
    "G693": ("POMPEI", "NA"),
    "G716": ("PORICI", "NA"),
    "G795": ("POZZUOLI", "NA"),
    "G902": ("QUARTU SANT'ELENA", "CA"),
    "H727": ("SAN BENEDETTO DEL TRONTO", "AP"),
    "H785": ("SAN DONÀ DI PIAVE", "VE"),
    "H798": ("SAN GIOVANNI ROTONDO", "FG"),
    "I073": ("SANREMO", "IM"),
    "I072": ("SAN SEVERO", "FG"),
    "I234": ("SESTO SAN GIOVANNI", "MI"),
    "L698": ("VIAREGGIO", "LU"),
    "L840": ("VIGEVANO", "PV"),
    "M082": ("VITTORIA", "RG"),
    
    # =========================================================================
    # Foreign Countries (Codes starting with Z)
    # =========================================================================
    "Z100": ("ALBANIA", "EE"),
    "Z102": ("ANDORRA", "EE"),
    "Z103": ("AUSTRIA", "EE"),
    "Z104": ("BELGIO", "EE"),
    "Z106": ("BULGARIA", "EE"),
    "Z107": ("DANIMARCA", "EE"),
    "Z108": ("FINLANDIA", "EE"),
    "Z109": ("FRANCIA", "EE"),
    "Z110": ("GERMANIA", "EE"),
    "Z112": ("REGNO UNITO", "EE"),
    "Z113": ("GRECIA", "EE"),
    "Z114": ("IRLANDA", "EE"),
    "Z115": ("ISLANDA", "EE"),
    "Z116": ("LIECHTENSTEIN", "EE"),
    "Z117": ("LUSSEMBURGO", "EE"),
    "Z118": ("MALTA", "EE"),
    "Z119": ("MONACO", "EE"),
    "Z120": ("NORVEGIA", "EE"),
    "Z121": ("PAESI BASSI", "EE"),
    "Z122": ("POLONIA", "EE"),
    "Z123": ("PORTOGALLO", "EE"),
    "Z124": ("ROMANIA", "EE"),
    "Z125": ("SAN MARINO", "EE"),
    "Z126": ("SPAGNA", "EE"),
    "Z127": ("SVEZIA", "EE"),
    "Z128": ("SVIZZERA", "EE"),
    "Z129": ("UNGHERIA", "EE"),
    "Z130": ("UCRAINA", "EE"),
    "Z131": ("RUSSIA", "EE"),
    "Z132": ("ESTONIA", "EE"),
    "Z133": ("LETTONIA", "EE"),
    "Z134": ("LITUANIA", "EE"),
    "Z135": ("CROAZIA", "EE"),
    "Z136": ("SLOVENIA", "EE"),
    "Z138": ("MACEDONIA", "EE"),
    "Z139": ("MOLDAVIA", "EE"),
    "Z140": ("SLOVACCHIA", "EE"),
    "Z149": ("REPUBBLICA CECA", "EE"),
    "Z150": ("SERBIA", "EE"),
    "Z153": ("BIELORUSSIA", "EE"),
    "Z154": ("BOSNIA ERZEGOVINA", "EE"),
    "Z158": ("MONTENEGRO", "EE"),
    "Z159": ("KOSOVO", "EE"),
    "Z200": ("EGITTO", "EE"),
    "Z203": ("LIBIA", "EE"),
    "Z204": ("MAROCCO", "EE"),
    "Z205": ("NIGERIA", "EE"),
    "Z208": ("SENEGAL", "EE"),
    "Z210": ("GHANA", "EE"),
    "Z211": ("COSTA D'AVORIO", "EE"),
    "Z215": ("SOMALIA", "EE"),
    "Z217": ("ETIOPIA", "EE"),
    "Z218": ("ERITREA", "EE"),
    "Z219": ("SUDAFRICA", "EE"),
    "Z229": ("TUNISIA", "EE"),
    "Z235": ("CAMERUN", "EE"),
    "Z243": ("ALGERIA", "EE"),
    "Z300": ("AFGHANISTAN", "EE"),
    "Z301": ("ARABIA SAUDITA", "EE"),
    "Z302": ("BAHREIN", "EE"),
    "Z303": ("BANGLADESH", "EE"),
    "Z304": ("MYANMAR", "EE"),
    "Z306": ("CINA", "EE"),
    "Z307": ("CIPRO", "EE"),
    "Z308": ("COREA DEL NORD", "EE"),
    "Z309": ("COREA DEL SUD", "EE"),
    "Z310": ("EMIRATI ARABI UNITI", "EE"),
    "Z311": ("FILIPPINE", "EE"),
    "Z312": ("GIAPPONE", "EE"),
    "Z313": ("GIORDANIA", "EE"),
    "Z314": ("INDIA", "EE"),
    "Z315": ("INDONESIA", "EE"),
    "Z316": ("IRAN", "EE"),
    "Z317": ("IRAQ", "EE"),
    "Z318": ("ISRAELE", "EE"),
    "Z319": ("KUWAIT", "EE"),
    "Z320": ("LAOS", "EE"),
    "Z321": ("LIBANO", "EE"),
    "Z322": ("MALESIA", "EE"),
    "Z323": ("MALDIVE", "EE"),
    "Z324": ("MONGOLIA", "EE"),
    "Z325": ("NEPAL", "EE"),
    "Z326": ("OMAN", "EE"),
    "Z327": ("PAKISTAN", "EE"),
    "Z329": ("QATAR", "EE"),
    "Z330": ("SINGAPORE", "EE"),
    "Z331": ("SIRIA", "EE"),
    "Z332": ("SRI LANKA", "EE"),
    "Z333": ("THAILANDIA", "EE"),
    "Z335": ("TURCHIA", "EE"),
    "Z337": ("VIETNAM", "EE"),
    "Z338": ("YEMEN", "EE"),
    "Z340": ("KAZAKISTAN", "EE"),
    "Z341": ("UZBEKISTAN", "EE"),
    "Z348": ("ARMENIA", "EE"),
    "Z349": ("AZERBAIGIAN", "EE"),
    "Z350": ("GEORGIA", "EE"),
    "Z351": ("KIRGHIZISTAN", "EE"),
    "Z352": ("TAGIKISTAN", "EE"),
    "Z353": ("TURKMENISTAN", "EE"),
    "Z354": ("TAIWAN", "EE"),
    "Z400": ("STATI UNITI D'AMERICA", "EE"),
    "Z401": ("CANADA", "EE"),
    "Z402": ("MESSICO", "EE"),
    "Z403": ("GUATEMALA", "EE"),
    "Z404": ("COSTA RICA", "EE"),
    "Z405": ("CUBA", "EE"),
    "Z407": ("REPUBBLICA DOMINICANA", "EE"),
    "Z409": ("EL SALVADOR", "EE"),
    "Z411": ("HAITI", "EE"),
    "Z413": ("HONDURAS", "EE"),
    "Z414": ("GIAMAICA", "EE"),
    "Z415": ("NICARAGUA", "EE"),
    "Z416": ("PANAMA", "EE"),
    "Z500": ("ARGENTINA", "EE"),
    "Z501": ("BOLIVIA", "EE"),
    "Z502": ("BRASILE", "EE"),
    "Z503": ("CILE", "EE"),
    "Z504": ("COLOMBIA", "EE"),
    "Z505": ("ECUADOR", "EE"),
    "Z507": ("PARAGUAY", "EE"),
    "Z508": ("PERU'", "EE"),
    "Z509": ("SURINAME", "EE"),
    "Z510": ("URUGUAY", "EE"),
    "Z511": ("VENEZUELA", "EE"),
    "Z600": ("AUSTRALIA", "EE"),
    "Z609": ("NUOVA ZELANDA", "EE"),
    "Z700": ("CITTA' DEL VATICANO", "EE"),
}


def get_municipality_info(cadastral_code: str) -> tuple[str, str] | None:
    """Get municipality information from cadastral code.

    Args:
        cadastral_code: 4-character cadastral code (e.g., "H501" for Rome)

    Returns:
        Tuple of (municipality_name, province_code) if found, None otherwise

    """
    return CODICI_CATASTALI.get(cadastral_code.upper())


def get_cadastral_code(municipality_name: str) -> str | None:
    """Get cadastral code from municipality name.

    Args:
        municipality_name: Municipality name (case-insensitive)

    Returns:
        Cadastral code if found, None otherwise

    Note:
        This performs an exact match on the municipality name.
        For partial matches, use search_municipality().

    """
    name_upper = municipality_name.upper()
    for code, (name, _) in CODICI_CATASTALI.items():
        if name == name_upper:
            return code
    return None


def search_municipality(partial_name: str) -> list[tuple[str, str, str]]:
    """Search for municipalities by partial name.

    Args:
        partial_name: Partial municipality name to search for

    Returns:
        List of tuples (cadastral_code, municipality_name, province_code)

    """
    partial_upper = partial_name.upper()
    results = []
    for code, (name, province) in CODICI_CATASTALI.items():
        if partial_upper in name:
            results.append((code, name, province))
    return sorted(results, key=lambda x: x[1])


def is_foreign_country(cadastral_code: str) -> bool:
    """Check if a cadastral code represents a foreign country.

    Args:
        cadastral_code: 4-character cadastral code

    Returns:
        True if the code represents a foreign country (starts with Z)

    """
    return cadastral_code.upper().startswith("Z")
