# DnDGMod: A Dungeons & Degenerate Gamblers Modloader
> ⚠️ Mods using this software are able to inject code into your *Dungeons & Degenerate Gamblers* executable!
> The DnDGMod team is **not** responsible for the contents of any mod not officially endorsed. Stay safe out there, 
> gamblers!
> ---
> 🏴‍☠️ The DnDGMod team does **not** condone piracy! Please **do not** distrubute compiled *Dungeons and 
> Degenerate Gamblers* executables (modded or unmodded) or decompiled source code. Thank you, gamblers!

## Installation
DnDGMod is available from [PyPI](https://pypi.org/project/dndgmod/) (Currently Windows-Only):
```
pip install dndgmod
```

## Quickstart
### Initialization
Run this command to set up DnDGMod's `AppData` directory, install dependencies, and decompile your (locally stored) 
*Dungeons and Degenerate Gamblers* executable using GDRE Tools:
```
dndgmod init
```

### Using an Existing Mod
1. Open the directory where mods are stored:
      ```
      dndgmod open
      ```
2. Drag the mod's `.dndg` file into the opened `AppData` directory.
(NOTE TO FUTURE SETH: .dndg is just .zip with a different name)
3. [Recompile *Dungeons & Degenerate Gamblers*](#recompile-dungeons-degenerate-gamblers)

### Creating a New Mod
1. Create a mod skeleton:
      ```
      dndgmod create
      ```
2. Edit the mod files... Here are the docs: https://docs.google.com/document/d/1LKXtTyZchio7B-XRmeaSFV9jk7oYMQoV6p4m0zurUyg
3. [Recompile *Dungeons & Degenerate Gamblers*](#recompile-dungeons-degenerate-gamblers)

### Recompile *Dungeons & Degenerate Gamblers*
Run this command to recompile *Dungeons & Degenerate Gamblers* using Godot (which is automatically installed during 
[Initialization](#initialization)):
```
dndgmod compile
```
