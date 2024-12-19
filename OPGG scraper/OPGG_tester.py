from opgg.opgg import OPGG
from opgg.summoner import Summoner
from opgg.params import Region

import os
import sys

# Add module to path to reference opgg subdir from here.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from opgg.game import GameStats, Stats, Team
from opgg.opgg import OPGG

from opgg.champion import Champion, Passive, Spell, Price, Skin, ChampionStats
from opgg.summoner import Game, Participant, Summoner
from opgg.league_stats import LeagueStats, Tier, QueueInfo
from opgg.season import Season, SeasonInfo
from opgg.utils import Utils
import pprint

#from opggtests import OPGGTests

do_acct_id_search = True

def mainMAIN():    
    #opgg_obj = OPGG()
    #summoner: Summoner = opgg_obj.search("ASTROBOY99#NA1")
    #print(summoner)

    opgg = OPGG("AVCaop7DsXMxYghWRgonI__cn6cKD9EssfdNn-A8NhKvW2U")

    # Get a game object
    recent_ranked_games = opgg.get_recent_games(results=1, game_type="ranked", return_content_only=True)

    for game in recent_ranked_games:
        # 'participants' is likely a list; iterate over it
        #pprint.PrettyPrinter(width=20).pprint(game)
        print("game\n")
    

        
        
            #====================== FIND ACCOUNT ID FOR ALL 10 PLAYERS IN GAME ==================================
        if do_acct_id_search == True:
            participants = game["participants"]  # Direct dictionary indexing
            # Ensure the list is not empty
            if len(participants) == 0:
                print("No participants found.")

            seen_acct_ids = []  # Set to track unique Account IDs
            duplicate_found = False
            for participant in participants:
                summoner = participant["summoner"]  # Direct indexing again
                
                acct_id = summoner["acct_id"]       # Retrieve the 'acct_id'

                print(f"Account ID: {acct_id}")

                if acct_id in seen_acct_ids:        # check for acct_id dupes
                    print("duplicate found")
                    duplicate_found = True
                else:
                    seen_acct_ids.append(acct_id)

            # Part of Find acct IDs.
            if do_acct_id_search == True:       
                if duplicate_found == False:
                    print("No duplicate Account IDs found.")
        else:
                    print("Account IDs not being searched.")
        

#for trying shit out
def main():
     
     opgg_object = OPGG()

     summoner = opgg_object.search("Fraggetti#EUW", region='EUW')
     print(summoner)
        

if __name__ == "__main__":
    main()



'''
useful methods:

for instantiated object from class OPGG:     returns:
- .search("Fraggetti#EUW", region="EUW")     either a summoner object or a list of summoner objects.
- .get_recent_games()                        a list that contains one or multiple game objects.
- .get_summoner                              a summoner object.

for objects from class Participant:          
- .stats()                                   returns the object of type Stats
- .tier_info()                               returns the object of type Tier
- .role()                                    returns the string representing the role.
- .team_key()                                returns the string representing team color.
'''