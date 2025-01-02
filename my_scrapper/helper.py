import pandas as pd

class ChampionConverter:
    def __init__(self):
        self.champions = [
            "Aatrox", "Ahri", "Akali", "Akshan", "Alistar", "Ambessa", "Amumu", "Anivia", "Annie", "Aphelios", "Ashe", "Aurelion Sol",
            "Aurora", "Azir", "Bard", "Bel'Veth", "Blitzcrank", "Brand", "Braum", "Briar", "Caitlyn", "Camille", "Cassiopeia", "Cho'Gath",
            "Corki", "Darius", "Diana", "Dr. Mundo", "Draven", "Ekko", "Elise", "Evelynn", "Ezreal", "Fiddlesticks", "Fiora", "Fizz", "Galio",
            "Gangplank", "Garen", "Gnar", "Gragas", "Graves", "Gwen", "Hecarim", "Heimerdinger", "Hwei", "Illaoi", "Irelia", "Ivern", "Janna",
            "Jarvan IV", "Jax", "Jayce", "Jhin", "Jinx", "K'Sante", "Kai'Sa", "Kalista", "Karma", "Karthus", "Kassadin", "Katarina", "Kayle",
            "Kayn", "Kennen", "Kha'Zix", "Kindred", "Kled", "Kog'Maw", "LeBlanc", "Lee Sin", "Leona", "Lillia", "Lissandra", "Lucian", "Lulu",
            "Lux", "Malphite", "Malzahar", "Maokai", "Master Yi", "Milio", "Miss Fortune", "Mordekaiser", "Morgana", "Naafiri", "Nami", "Nasus",
            "Nautilus", "Neeko", "Nidalee", "Nilah", "Nocturne", "Nunu & Willump", "Olaf", "Orianna", "Ornn", "Pantheon", "Poppy", "Pyke",
            "Qiyana", "Quinn", "Rakan", "Rammus", "Rek'Sai", "Rell", "Renata Glasc", "Renekton", "Rengar", "Riven", "Rumble", "Ryze", "Samira",
            "Sejuani", "Senna", "Seraphine", "Sett", "Shaco", "Shen", "Shyvana", "Singed", "Sion", "Sivir", "Skarner", "Smolder", "Sona",
            "Soraka", "Swain", "Sylas", "Syndra", "Tahm Kench", "Taliyah", "Talon", "Taric", "Teemo", "Thresh", "Tristana", "Trundle",
            "Tryndamere", "Twisted Fate", "Twitch", "Udyr", "Urgot", "Varus", "Vayne", "Veigar", "Vel'Koz", "Vex", "Vi", "Viego", "Viktor",
            "Vladimir", "Volibear", "Warwick", "Wukong", "Xayah", "Xerath", "Xin Zhao", "Yasuo", "Yone", "Yorick", "Yuumi", "Zac", "Zed",
            "Zeri", "Ziggs", "Zilean", "Zoe", "Zyra"
        ]

        self.champion_to_number = {champion: i for i, champion in enumerate(self.champions, start=1)}
        self.number_to_champion = {i: champion for i, champion in enumerate(self.champions, start=1)}

    def champion_to_num(self, champion_name):
        return self.champion_to_number.get(champion_name, None)

    def num_to_champion(self, number):
        return self.number_to_champion.get(number, None)
    
    def convert_date(date_str):
        """Convert datetime string to Unix timestamp"""
        return pd.to_datetime(date_str).timestamp()
    

def convert_to_minutes(time_str):
    """Convert time string (e.g., '15m 10s') to minutes (float)"""
    try:
        minutes = seconds = 0
        parts = time_str.lower().split()
        for part in parts:
            if 'm' in part:
                minutes = float(part.replace('m', ''))
            elif 's' in part:
                seconds = float(part.replace('s', ''))
        return round(minutes + seconds/60, 2)
    except:
        return 0.0
    
def convert_percentage_to_decimal(percentage_str):
    """Convert percentage string (e.g., 'P/Kill 43%') to decimal (0.43)"""
    try:
        # Extract number from string and convert to decimal
        num = float(''.join(filter(str.isdigit, percentage_str))) / 100
        return round(num, 2)
    except:
        return 0.0
    
def convert_tier_to_number(tier_str):
    """
    Convert tier string to number:
    Challenger -> 1
    Grandmaster -> 2
    Master -> 3
    Others -> 4
    """
    tier_map = {
        'challenger': 1,
        'grandmaster': 2,
        'master': 3
    }
    # Convert to lowercase and return mapped value or 4 for any other tier
    return tier_map.get(tier_str.lower().strip(), 4)

def convert_result_to_binary(result_str):
    """
    Convert match result to binary:
    Victory -> 1
    Defeat -> 0
    """
    return 1 if result_str.lower().strip() == 'victory' else 0