import requests
import sys
def main():
    '''
    Main loop for the CLI app. Pass --help to see usage information.
    Is not importable as a module.

    Usage: python3 cli.py [options] <imdb_id>
    Options:
        -h, --help      Show this help message and exit
        -ak, --apikey   Set or update the OMDB API key
    This program allows you to search information from the OMDB database using an IMDB ID.
    You must first set an API key using the --apikey flag followed by your key.
    A key can be obtained from http://www.omdbapi.com/apikey.aspx, free of charge.
    Once the key is set, you can retrieve information by providing a valid IMDB ID as an argument.
    Example usage:
        To set your API key:
        $  python3 cli.py --apikey your_api_key_here
        To retrieve information for a specific IMDB ID:
        $  python3 cli.py tt0111161
    That's all there is to it!
    '''
    ###Function definitions###
    def help():

        print("Usage: python3 cli.py [options] <imdb_id>")
        print("Options:")
        print("  -h, --help      Show this help message and exit")
        print("  -ak, --apikey   Set or update the OMDB API key")
        print("This program allows you to search information from the OMDB database using an IMDB ID.\n" \
        "You must first set an API key using the --apikey flag followed by your key.\n" \
        "A key can be obtained from http://www.omdbapi.com/apikey.aspx, free of charge." \
        "\n" \
        "Once the key is set, you can retrieve information by providing a valid IMDB ID as an argument.\n"\
        "Example usage:\n"\
        "   To set your API key:\n"\
        "       $  python3 cli.py --apikey your_api_key_here\n"\
        "   To retrieve information for a specific IMDB ID:\n"\
        "       $  python3 cli.py tt0111161\n"\
        "That's all there is to it!"
        )
        sys.exit(0)
    def set_apikey(key):
        with open('.apikey', 'w') as f:
            f.write(f"{key}\n")
        print(f"Saved key: {key}")
        sys.exit()
    def printout(response): ##taken right from last lab... -mbeda93
        '''Prints out the response data in its final form'''
        #Dynamic emojis for ratings etc
        def get_title_emoji(mode): #Dynamic emojification for the title display
            """Returns an emoji representing the mode (movie or series).
            mode must be a string"""
            if mode == "movie":
                return "🎬"
            elif mode == "series":
                return "📡"
        def get_parentalrating_emoji(parentalrating): #Dynamic emojification for the rating display
            """Returns an emoji representing the content rating. Should cover common ratings.
            rating must be a string"""
            parentalrating = parentalrating.upper()
            if parentalrating in ["G", "PG", "TV-Y", "TV-G"]:
                return "🟢" 
            elif parentalrating in ["PG-13", "TV-PG"]:
                return "🟡"
            elif parentalrating in ["R", "TV-14"]:
                return "🟠"
            elif parentalrating in ["NC-17", "TV-MA"]:
                return "🛑"
            else:
                return "❓"
        def get_rotten_tomatoes_emoji(score): #Dynamic emojification for the Rotten Tomatoes score display
            """Returns an emoji representing the Rotten Tomatoes score.
            score must be an integer between 0 and 100"""
            if score >= 75:
                return "🍅"  # Fresh
            elif 50 <= score < 75:
                return "🟠"  # Average
            else:
                return "🤢"  # Rotten
        def get_metacritic_emoji(score): #Dynamic emojification for the Metacritic score display
            """Returns an emoji representing the Metacritic score.
            score must be an integer between 0 and 100"""
            if score >= 75:
                return "🎯"  # Excellent
            elif 50 <= score < 75:
                return "🟡"  # Average
            else:
                return "🔴"  # Poor
        def get_imdb_emoji(score): #Dynamic emojification for the IMDB score display
            """Returns an emoji representing the IMDB score.
            score must be a float between 0 and 10"""
            if score >= 7.5:
                return "🌟"  # Excellent
            elif 5.0 <= score < 7.5:
                return "⭐"  # Average
            else:
                return "💫"  # Poor
        def get_awards_emoji(awards): #Dynamic emojification for the Awards display
            """Returns an emoji representing the Awards received.
            awards must be a string"""
            awards = awards.lower()
            if "oscar" in awards:
                return "🏆"  # Oscar
            elif "golden globe" in awards:
                return "🎖️"  # Golden Globe
            elif "emmy" in awards:
                return "📺"  # Emmy
            else:
                return "🎉"  # General Award

        #Pick apart the response and print it nicely
        title_emoji = get_title_emoji(response.get('Type'))
        print(f"\n{title_emoji} Title: {response.get('Title')} ({response.get('Year')})")

        if 'Rated' in response and response.get('Rated') != "N/A":
            parentalrating = response.get('Rated')
            parentalrating_emoji = get_parentalrating_emoji(parentalrating)
            print(f"{parentalrating_emoji} Rated: {response.get('Rated')}")

        if 'totalSeasons' in response and response.get('totalSeasons') != "N/A":
            print(f"📺 Total Seasons: {response.get('totalSeasons')}")

        if 'Released' in response and response.get('Released') != "N/A":
            print(f"🗓️  Release Date: {response.get('Released')}")

        if 'Runtime' in response and response.get('Runtime') != "N/A":
            print(f"⏲️  Runtime: {response.get('Runtime')}")

        if 'Genre' in response and response.get('Genre') != "N/A":
            print(f"🎞️  Genre: {response.get('Genre')}")

        if 'Director' in response and response.get('Director') != "N/A":
            print(f"👤 Directed by: {response.get('Director')}")

        if 'Plot' in response and response.get('Plot') != "N/A":
            print(f"📝 Plot: {response.get('Plot')}")

        if 'Awards' in response and response.get('Awards') != "N/A":
            awards = response.get('Awards')
            awards_emoji = get_awards_emoji(awards)
            print(f"{awards_emoji} Awards: {response.get('Awards')}")

        if 'Ratings' in response and response.get('Ratings') and len(response.get('Ratings')) > 0:
            print("\nRatings:")
            for rating in response['Ratings']:
                if rating['Source'] == "Rotten Tomatoes" and rating['Value'] != "N/A":
                    rt_score = int(rating['Value'].rstrip('%'))
                    rt_emoji = get_rotten_tomatoes_emoji(rt_score)
                    print(f"    {rt_emoji} Rotten Tomatoes Score: {rating['Value']}")

                if rating['Source'] == "Internet Movie Database" and rating['Value'] != "N/A":
                    imdb_score = float(rating['Value'].split('/')[0])
                    get_imdb_emoji(imdb_score)
                    print(f"    ⭐ IMDB Rating: {rating['Value']}")

                if rating['Source'] == "Metacritic" and rating['Value'] != "N/A":
                    mc_score = int(rating['Value'].split('/')[0])
                    print(f"    {get_metacritic_emoji(mc_score)} Metacritic Score: {rating['Value']}")


    ##Help (if this breaks then maybe i should reconsider my life choices)
    if '--help' in sys.argv or '-h' in sys.argv:
        help()
    
    elif len(sys.argv) <= 1:
        print("Missing arguments. Use --help to see more information.")

    ##Add/Update API Key from omdbapi to disk
    elif '-ak' in sys.argv or '--apikey' in sys.argv:
        # Find exactly where the flag is, and take the next item
            if len(sys.argv) >3:
                print("Too many arguments. Use --help to see more information.")
                sys.exit(1)
            elif len(sys.argv) <3:
                print("Missing API key. Use --help to see more information.")
                sys.exit(1)
            elif '-ak' in sys.argv:
                key = sys.argv[sys.argv.index('-ak') + 1]
            elif '--apikey' in sys.argv:
                key = sys.argv[sys.argv.index('--apikey') + 1]

            ##write the key
            set_apikey(key)

    ##search for title via imdb id
    elif sys.argv[1].startswith('tt') and len(sys.argv) == 2:
        imdb_id = sys.argv[1]
        #load the api key file, if none is found prompt for one to be set
        try:
            with open('.apikey', 'r') as f:
                apikey = f.read().strip()
        except:
            print("API key file not found. Please set your API key using the --apikey flag.")
            print("A key can be obtained from http://www.omdbapi.com/apikey.aspx, free of charge")
            sys.exit(1)
        
        #make the API request
        url = f"http://www.omdbapi.com/?apikey={apikey}&i={imdb_id}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("Response") == "True":
                printout(data)
            else:
                print(f"Error: {data.get('Error')}")
                print("Did you enter a valid IMDB ID")
        else:
            print(f"HTTP Error: {response.status_code}")
            if response.status_code == 401:
                print("Did you enter a valid API key?")
                print("Use the --apikey flag to set or update your key.")
            elif response.status_code == 403:
                print("Access forbidden. Check your API key and permissions.")
                print("Use the --apikey flag to set or update your key.")
            elif response.status_code == 500:
                print("Server error at OMDB API. Please try again later.")
            elif response.status_code == 503:
                print("Service unavailable. The OMDB API may be down for maintenance.")

    else:
        print("Invalid input. Use --help to see more information.")
        sys.exit(1)

if __name__ == "__main__":
    main()
