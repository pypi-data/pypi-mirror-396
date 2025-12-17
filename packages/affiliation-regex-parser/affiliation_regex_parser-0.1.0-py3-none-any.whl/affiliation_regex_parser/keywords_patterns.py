

from  .keyword_country_list import _country_list
from  .keyword_city_list import _city_list



def get_department_keywords():
    r =[
        "Department of",
        "Department for",
          "Dept. of",
            "Dept of",
            "Dept "
            "Section of"]
    return r

def get_faculty_keywords():
    r = ["Faculty of",
          "School of",
          "School",

            ]
    return r

def get_institute_keywords():
    r = ["Institute of",
        "Research Institute",
        "Center for",
        "Centre for",
        "Laboratory of",
        "Institute ",
        "Institute"
        ]
    return r


def get_org_keywords():
    return [
        "Hospital",
        "Health Sciences Centre",
        "Health Center",
        "Medical Center",
        "Clinic",
        "Company", "Corporation", "Limited", "Ltd", "LLC", "Inc", "PLC",
    ]


def get_university_keywords():
    r = ["University",
         "Medical Sciences University",
         "Universidad",
         "Universität",
         "Üniversitesi",
         "Universitesi",
         "Univ",
         "College of",
         "College",

         ]
    return r

def get_government_keywords():
    r = [
"Ministry of",
"Commission",
"National Center",
"Supreme Council",
"Government",
"Agency",
"Bureau",
"Secretariat",
        "National Centre for",
        "National Center for",
        "National Institute of",
        "National Institute for",
        "National Laboratory of",
        "National Laboratory for",
        "National Health Service",  
        "Public Health Agency",
        "Public Health Department",
        "Health Authority",
        "Regional Health Authority",
        "Health Service Executive",
        "Provincial Health Services Authority",
        "State Department of Health",
        "Ministry of Health",
    ]
    return r

def get_city_keywords():
    # # Read From Origin
    # df = pd.read_excel(DATA_DIR / 'worldcities.xlsx')
    # r = df['city'].unique().tolist()
    
    # Read from program
    r = _city_list()

    # Exception
    # r.remove("University")
    # r.remove("Center")
    # r.remove("Data")
    r.remove('king')
    r.remove('college')
    return r

def get_country_keywords():

    # Read from program
    r = _country_list()

    # Exception
    r.append("Scotland")
    r.append("USA")
    r.append("UK")
    r.append("Korea")
    r.append("GBR")
    r.append("BRA")
    r.append("NGA")
    r.append("Czech Republic")
    r.append("Czech")        
    return r

def get_country_alias_map():
    # کلیدها lower-case باشند
    return {
        "uk": "United Kingdom",
        "gb": "United Kingdom",
        "gbr": "United Kingdom",
        "united kingdom": "United Kingdom",
        "great britain": "United Kingdom",
        "czechia" : "Czechia",
        "czech republic" : "Czechia",
        "czech" : "Czechia",
        "bra" : "Brazil",
        "nga" : "Nigeria",
    }
