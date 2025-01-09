# DnDGMod: A Dungeons & Degenerate Gamblers Modloader
![Python Version](https://img.shields.io/pypi/pyversions/dndgmod) ![Python Implementation](https://img.shields.io/pypi/implementation/dndgmod) ![Commit Activity](https://img.shields.io/github/commit-activity/m/TotallyNotSethP/DnDGMod) ![Downloads](https://img.shields.io/github/downloads/TotallyNotSethP/DnDGMod/total) ![https://img.shields.io/discord/1268924116434686038](https://img.shields.io/discord/1268924116434686038?link=https%3A%2F%2Fdsc.gg%2Fdndgmod
)

DnDGMod is a modloader for [Dungeons & Degenerate Gamblers](https://store.steampowered.com/app/2400510/Dungeons__Degenerate_Gamblers/) created by [TotallyNotSeth](https://github.com/TotallyNotSethP)

> ⚠️ Mods using this software are able to inject code into your *Dungeons & Degenerate Gamblers* executable!
> The DnDGMod team is **not** responsible for the contents of any mod not officially endorsed. Stay safe out there, 
> gamblers!
> 
> 🏴‍☠️ The DnDGMod team does **not** condone piracy! Please **do not** distrubute compiled *Dungeons & 
> Degenerate Gamblers* executables (modded or unmodded) or decompiled source code. Thank you, gamblers!

## Requirements
 * Windows 10/11
 * [Dungeons & Degenerate Gamblers](https://store.steampowered.com/app/2400510/Dungeons__Degenerate_Gamblers/)

## Installation2
 1. Download [dndgmod-onefile-bundled.exe](https://github.com/TotallyNotSethP/DnDGMod/releases/tag/0.2.0-rc2) and run it.
 2. Click "Decompile D&DG" to decompile the game's source code. The first run of this feature will take longer than usual because it will need to download some extra files from the internet. You'll only need to do this step whenever D&DG or DnDGMod updates.

## Usage

### Loading a Mod
 1. Download any DnDGMod-compatible mod, such as [Balatro Mod by roaxial](https://gamebanana.com/mods/536043).
 2. Click "Load Mod" in DnDGMod, and select the mod you just downloaded.
 3. When you're done loading/unloading mods, click "Compile D&DG" in DnDGMod to compile and run *Dungeons & Degenerate Gamblers*.

### Unloading a Mod
 1. Click "Open Mod Folder" in DnDGMod.
 2. Delete the folder corresponding to the mod you want to unload.
 3. When you're done loading/unloading mods, click "Compile D&DG" in DnDGMod to compile and run *Dungeons & Degenerate Gamblers*.

### Revert *Dungeons & Degenerate Gamblers* to Vanilla
 1. Click "Revert D&DG" in DnDGMod.

## Troubleshooting

### General Tips
 * Error messages will show up in the white terminal that appears when clicking "Compile D&DG" or "Launch D&DG", but usually only after the game is closed.
 * Error messages will usually give a file and line number. You can look for that file in `%LOCALAPPDATA%\TotallyNotSeth\DnDGMod\modified_src` to find where the issue lies.

### The Game is Still Modded When Clicking "Revert D&DG"
This often occurs when accidentally clicking "Decompile D&DG" while the game is already modded. To fix this, open Steam, right-click on *Dungeons & Degenerate Gamblers*, click Properties, go to Installed Files, and click "Verify Integrity". It should say "2 files failed to validate and will be reaquired". Now click "Decompile D&DG" and continue upon your merry way.

### I Get the Error `Duplicate key found in Dictionary literal` referencing `CardList.gd`
Follow the steps for 'The Game is Still Modded When Clicking "Revert D&DG"' above.

## Credits and Thanks
### Developers
 * Head Developer: [TotallyNotSeth](https://github.com/TotallyNotSethP)
 * Developer in Training: [nekojoe](https://github.com/nekojoe)

### Alpha Testers
 * Head Alpha Tester: roaxial
 * Head Alpha Tester: rando.idiot
 * Alpha Tester: lieutenantlame
 * Alpha Tester: monkeyinc.
 * Alpha Tester: spssyy0000
 * Alpha Tester: thinkysmort
 * Alpha Tester: Crimson Heart (virtuecpu)
 * Honorary Alpha Tester: Olly go brrr
 * Honorary Alpha Tester: HuyTheKiller

### Special Thanks To...
 * Purple Moss Collectors, the talented people at Yogscast Games, and everyone else who worked hard to make *Dungeons & Degenerate Gamblers* a reality!
