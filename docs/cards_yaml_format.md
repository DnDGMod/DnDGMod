# `cards.yaml` Format
This is a sample of a `cards.yaml`:
```yaml
Volatile Ace:
    Description: "{keyword_flexible} (1 or 11).\nOn Bust: Burn.\nOn Stand: Burn."
    Keywords:
        - Flexible
    Image: volatile.png
    Value: 10
    Suit: all_suits_at_once
    Flexible: [5, 10]
    Triggers:
        Bust Limit Exceeded: burn.gd.j2
        Stand: burn.gd.j2
    Attributes:
        - Reward
        - Ace

Normal Card:
    Description: "Quite normal; nothing special at all."
    Image: normal.png
    Value: 0
```

# Card Name
```yaml
Volatile Ace:
```
The in-game name for this card will be `Volatile Ace`

# Description
```yaml
    Description: "{keyword_flexible} (1 or 11).\nOn Bust: Burn.\nOn Stand: Burn."
```
The in-game description for this card will be:
```text
Flexible (1 or 11).
On Bust: Burn.
On Stand: Burn.
```
`{keyword_flexible}` stylizes the word "Flexible" like a keyword. Click [HERE] for all other valid keywords.
`\n` 