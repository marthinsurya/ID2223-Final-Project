from opgg.opgg import OPGG
from opgg.summoner import Summoner
from opgg.params import Region


def main():    
    opgg_obj = OPGG()

    summoner: Summoner = opgg_obj.search("killer#XUG2")
    print(summoner)


if __name__ == "__main__":
    main()