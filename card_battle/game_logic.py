import random
from cards import Card, RANKS, SUITS

class GameLogic:
    """Manages the state and rules of the card game War."""
    def __init__(self, target_score=10):
        self.target_score = target_score
        self.reset_game()

    def reset_game(self):
        """Resets scores, cards, and state to start a new match."""
        self.player_score = 0
        self.computer_score = 0
        self.current_player_card = None
        self.current_computer_card = None
        self.round_result_message = "Choose a card from your hand to battle!"
        self.game_over = False
        self.winner = None
        self.player_special_cards = []
        self.computer_special_cards = []
        self.reverse_active = False
        self.player_boost_active = False
        self.computer_boost_active = False
        self.cancel_active = False
        self.draw_hands()
        self.draw_special_cards()

    def draw_hands(self):
        """Generates a new hand of 5 cards for player and computer."""
        self.player_hand = []
        self.computer_hand = []
        for _ in range(5):
            p_rank = random.choice(list(RANKS.keys()))
            p_suit = random.choice(SUITS)
            self.player_hand.append(Card(p_rank, p_suit))
            
            c_rank = random.choice(list(RANKS.keys()))
            c_suit = random.choice(SUITS)
            self.computer_hand.append(Card(c_rank, c_suit))

    def draw_special_cards(self):
        """Replenishes special cards for both players up to 2."""
        SPECIAL_TYPES = ['reverse', 'reveal', 'boost', 'swap', 'cancel']
        while len(self.player_special_cards) < 2:
            self.player_special_cards.append(random.choice(SPECIAL_TYPES))
        while len(self.computer_special_cards) < 2:
            self.computer_special_cards.append(random.choice(SPECIAL_TYPES))

    def play_special_card(self, is_player, index):
        """
        Activates a special card and returns its type and payload if any.
        Returns:
            tuple: (card_type, payload)
        """
        spec_list = self.player_special_cards if is_player else self.computer_special_cards
        if index < 0 or index >= len(spec_list):
            return (None, None)
            
        card_type = spec_list.pop(index)
        payload = None
        
        if card_type == 'reverse':
            self.reverse_active = True
        elif card_type == 'boost':
            if is_player:
                self.player_boost_active = True
            else:
                self.computer_boost_active = True
        elif card_type == 'cancel':
            self.cancel_active = True
        elif card_type == 'reveal':
            opp_hand = self.computer_hand if is_player else self.player_hand
            valid_indices = [i for i, card in enumerate(opp_hand) if card is not None]
            if valid_indices:
                payload = random.choice(valid_indices)
        elif card_type == 'swap':
            player_valid = [i for i, card in enumerate(self.player_hand) if card is not None]
            computer_valid = [i for i, card in enumerate(self.computer_hand) if card is not None]
            if player_valid and computer_valid:
                p_idx = random.choice(player_valid)
                c_idx = random.choice(computer_valid)
                self.player_hand[p_idx], self.computer_hand[c_idx] = self.computer_hand[c_idx], self.player_hand[p_idx]
                payload = (p_idx, c_idx, self.player_hand[p_idx], self.computer_hand[c_idx])
                
        return (card_type, payload)

    def play_round(self, player_card_index):
        """
        Plays a round using the selected card from the player's hand and a random card from the computer's hand.
        Also evaluates and plays computer AI special cards.
        Returns:
            tuple: (player_card, computer_card, message, round_winner, computer_card_index, comp_spec_type, comp_spec_idx)
        """
        if self.game_over or not self.player_hand or not self.computer_hand:
            return (None, None, self.round_result_message, None, -1, None, -1)

        # Retrieve player card
        player_card = self.player_hand[player_card_index]
        self.player_hand[player_card_index] = None

        # Retrieve random computer card
        available_comp_indices = [i for i, card in enumerate(self.computer_hand) if card is not None]
        comp_card_index = random.choice(available_comp_indices)
        computer_card = self.computer_hand[comp_card_index]
        self.computer_hand[comp_card_index] = None

        self.current_player_card = player_card
        self.current_computer_card = computer_card

        # Assess and execute Computer AI special card plays
        comp_spec_type = None
        comp_spec_idx = -1
        
        if self.computer_special_cards and not self.cancel_active:
            p_val = player_card.value
            c_val = computer_card.value
            
            # 1. CANCEL: Play if computer is about to lose the point
            if 'cancel' in self.computer_special_cards and p_val > c_val:
                if random.random() < 0.6: # 60% chance to save itself
                    idx = self.computer_special_cards.index('cancel')
                    self.computer_special_cards.pop(idx)
                    self.cancel_active = True
                    comp_spec_type = 'cancel'
                    comp_spec_idx = idx
            
            # 2. BOOST: Play if computer is slightly behind or wants to secure a win
            elif 'boost' in self.computer_special_cards:
                # If computer is losing by 1-3 points or tie
                if -3 <= (c_val - p_val) <= 0:
                    if random.random() < 0.5:
                        idx = self.computer_special_cards.index('boost')
                        self.computer_special_cards.pop(idx)
                        self.computer_boost_active = True
                        comp_spec_type = 'boost'
                        comp_spec_idx = idx
                        
            # 3. REVERSE: Play if computer card is low and player card is high
            elif 'reverse' in self.computer_special_cards:
                if c_val <= 6 and p_val >= 9:
                    if random.random() < 0.5:
                        idx = self.computer_special_cards.index('reverse')
                        self.computer_special_cards.pop(idx)
                        self.reverse_active = True
                        comp_spec_type = 'reverse'
                        comp_spec_idx = idx

        # Determine round outcome
        if self.cancel_active:
            round_winner = "Tie"
            self.round_result_message = "Round Canceled by Shield Special Card!"
        else:
            p_final_val = player_card.value + (3 if self.player_boost_active else 0)
            c_final_val = computer_card.value + (3 if self.computer_boost_active else 0)
            
            # Description builder
            p_desc = f"{player_card}" + (" (+3 Boost)" if self.player_boost_active else "")
            c_desc = f"{computer_card}" + (" (+3 Boost)" if self.computer_boost_active else "")
            
            if self.reverse_active:
                if p_final_val < c_final_val:
                    self.player_score += 1
                    round_winner = "Player"
                    self.round_result_message = f"Point to Player! {p_desc} beats {c_desc} (Chaos Order reversed!)."
                elif c_final_val < p_final_val:
                    self.computer_score += 1
                    round_winner = "Computer"
                    self.round_result_message = f"Point to Computer! {c_desc} beats {p_desc} (Chaos Order reversed!)."
                else:
                    round_winner = "Tie"
                    self.round_result_message = f"War Tie (Chaos Order)! Both played equivalent of {player_card.rank} ({p_desc} vs {c_desc})."
            else:
                if p_final_val > c_final_val:
                    self.player_score += 1
                    round_winner = "Player"
                    self.round_result_message = f"Point to Player! {p_desc} beats {c_desc}."
                elif c_final_val > p_final_val:
                    self.computer_score += 1
                    round_winner = "Computer"
                    self.round_result_message = f"Point to Computer! {c_desc} beats {p_desc}."
                else:
                    round_winner = "Tie"
                    self.round_result_message = f"War Tie! Both played equivalent of {player_card.rank} ({p_desc} vs {c_desc})."

        # Reset active modifiers
        self.reverse_active = False
        self.player_boost_active = False
        self.computer_boost_active = False
        self.cancel_active = False

        # Check overall win condition
        if self.player_score >= self.target_score:
            self.game_over = True
            self.winner = "Player"
            self.round_result_message = f"MATCH COMPLETED! Player wins {self.player_score} - {self.computer_score}!"
        elif self.computer_score >= self.target_score:
            self.game_over = True
            self.winner = "Computer"
            self.round_result_message = f"MATCH COMPLETED! Computer wins {self.computer_score} - {self.player_score}!"

        return (player_card, computer_card, self.round_result_message, round_winner, comp_card_index, comp_spec_type, comp_spec_idx)
