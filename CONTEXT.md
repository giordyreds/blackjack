# Blackjack

A single-player, terminal-driven blackjack game: one human player against a computer dealer.

## Language

**Shoe**:
The dealing device holding 6 shuffled decks (312 cards) that cards are drawn from across multiple rounds. Reshuffled once a cut card near ~75% penetration is reached.
_Avoid_: Deck (a Deck is one 52-card set; the Shoe is the multi-deck container built from several Decks)

**Hand**:
The cards held by the player or dealer during a round, evaluated to a soft or hard total. A round starts with one Hand per side; splitting creates additional Hands for the player.

**Split Hand**:
One of up to 3 Hands a player plays independently after splitting a pair. Doubling down is allowed on a Split Hand; Split Hands from a pair of Aces are restricted to exactly one additional card each and cannot be split again or form a Blackjack.

**Natural** (Blackjack):
A Hand totaling 21 from its first two cards. Pays 3:2. A Hand reaching 21 after a split or hit is a regular 21, not a Natural.
_Avoid_: "Blackjack" alone when referring to the hand (reserve "Blackjack" for the game's name; use "Natural" for the winning hand)

**Bust**:
A Hand whose total exceeds 21, an automatic loss regardless of the opposing Hand.

**Push**:
A round where the player's Hand and the dealer's Hand tie — the player's Bet is returned, no money won or lost.

**Bankroll**:
The player's total money across a session, starting at $1000. The session ends when it reaches $0.

**Bet**:
The amount staked by the player on a round, between $10 and $500.

**Hole Card**:
The dealer's face-down card. When the dealer's up-card is an Ace or 10-value card, the dealer peeks at the Hole Card for a Natural before the player acts; if found, the round ends immediately.
