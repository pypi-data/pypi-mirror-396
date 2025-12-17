# Brawl Stars Wrapper (BSWrapper) - TestPyPI Exclusive

## APOLOGIES IN ADVANCE. NOT VERY GOOD WITH MAKING DOCS LOL. IF YOU CAN MAKE A BETTER README.md THEN BY ALL MEANS SUBMIT A ISSUE ON GITHUB LOL.

Current Version: 0.1.0

## How to install it
```bash
pip install -i https://test.pypi.org/simple bswrapper
```

## Example Usage

```python
from bswrapper import BSWrapper

client = BSWrapper('THY_API_TOKEN')

# For Player info
player = client.getplayer('#TAG or TAG (without #)')
print(player.name) # shows players name

# For Club info
club = client.getclub('#TAG or TAG (without #)')
print(club.name)
```

## Different calls

Player Stats (so far):
    tag
    name
    trophies
    highest
    explevel
    club

Club Stats (so far):
    tag
    name 
    trophies
    required
    type (e.g. Open, Closed, Invite Only)

# API How to:

- Visit https://developer.brawlstars.com

- Sign in, and click my account.

- Make a new api key, give it a name, description and YOUR IP ADDRESS. Whether that be your server IP or your computer IP. If you're doing this, I'm sure you can find out your IP address. Or just use https://whatismyipaddress.com. 

Any who, do what you want. I'll try my best to keep it up to date. It's open source after all lol