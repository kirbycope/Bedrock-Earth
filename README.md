[![YouTube Short](/bedrock-earth.png)](https://www.youtube.com/watch?v=vFGYWKiRhl8)

# Bedrock-Earth
Minecraft Earth was an augmented reality sandbox game developed by Mojang Studios and published by Xbox Game Studios. It was sunet and made my 7 year old very sad. We randomly watched a video about changing mobs on [YouTube](https://www.youtube.com/watch?v=OI1mfEEBZEM) and got inspired to make our own. I have made two datapacks ([CopeCraft](https://github.com/kirbycope/CopeCraft) and [SkyBlock](https://github.com/kirbycope/SkyBlock)) for Minecraft Java so this was a nice challange that used previously learned code.

I modified the models and behaviors of the mobs my son suggested (chicken and iron_golem). My wife did the textures. My son and I made the map. I also wrote a small datapack that gives you the spawn eggs if it is your first time joining the map.

## Installation
1. Download the [.mctemplate](https://github.com/kirbycope/Bedrock-Earth/raw/main/Bedrock-Earth.mctemplate)
1. Double-click the mctemplate file
1. Create a New World using the template
    - "Play" > "Create New"  > Scroll down to "Imported Templates" (Select "See More" if necessary)

## Releasing
Pushing a tag that starts with `v` (for example `git tag v1.0.0 && git push origin v1.0.0`) runs the Release workflow in `.github/workflows/release.yml`, which builds the world template and attaches `Bedrock-Earth.mctemplate` to a GitHub Release.

To build it locally, run `python tools/build_addon.py`. It writes `build/Bedrock-Earth.mctemplate`, which git ignores, and leaves the committed `Bedrock-Earth.mctemplate` as it is.
