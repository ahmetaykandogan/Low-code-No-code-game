from ursina import Entity, Button, Text, color, camera

class MainMenu(Entity):
    """Container for the Main Menu layout."""
    def __init__(self, on_play_click, **kwargs):
        super().__init__(parent=camera.ui, enabled=True, **kwargs)
        
        # Title with a modern stylish look
        self.title = Text(
            parent=self,
            text="WAR BATTLE",
            scale=5,
            position=(0, 0.26),
            origin=(0, 0),
            color=color.hex('#f1faee')
        )
        
        self.subtitle = Text(
            parent=self,
            text="A Classic Card Mini-Game",
            scale=2.2,
            position=(0, 0.14),
            origin=(0, 0),
            color=color.hex('#a8dadc')
        )
        
        # Rule card background
        self.rule_bg = Entity(
            parent=self,
            model='quad',
            color=color.rgba(29, 53, 87, 180), # Dark blue semi-transparent
            scale=(0.7, 0.16),
            position=(0, -0.01),
            z=0.1
        )
        
        self.rules = Text(
            parent=self,
            text="HOW TO PLAY:\n- Click 'Draw Card' to draw cards randomly.\n- Highest card rank wins the round and earns 1 point.\n- The first player to reach 10 points wins!",
            scale=1.4,
            position=(0, 0.04),
            origin=(0, 0.5),
            color=color.hex('#f1faee')
        )

        # Play Button
        self.play_button = Button(
            parent=self,
            text="PLAY NOW",
            scale=(0.28, 0.08),
            position=(0, -0.22),
            color=color.hex('#e63946'),
            highlight_color=color.hex('#d62828'),
            text_color=color.white,
            on_click=on_play_click
        )


class GameplayUI(Entity):
    """Container for the Gameplay HUD."""
    def __init__(self, on_draw_click, on_quit_click, **kwargs):
        super().__init__(parent=camera.ui, enabled=False, **kwargs)
        
        # Player Score Panel (left side)
        self.player_hud_label = Text(
            parent=self,
            text="PLAYER SCORE",
            scale=1.4,
            position=(-0.68, 0.15),
            origin=(0, 0),
            color=color.hex('#a8dadc')
        )
        self.player_score_text = Text(
            parent=self,
            text="0",
            scale=4.5,
            position=(-0.68, 0.03),
            origin=(0, 0),
            color=color.white
        )

        # Computer Score Panel (right side)
        self.computer_hud_label = Text(
            parent=self,
            text="COMP SCORE",
            scale=1.4,
            position=(0.68, 0.15),
            origin=(0, 0),
            color=color.hex('#e63946')
        )
        self.computer_score_text = Text(
            parent=self,
            text="0",
            scale=4.5,
            position=(0.68, 0.03),
            origin=(0, 0),
            color=color.white
        )
        
        # Battle Labels
        self.player_label = Text(
            parent=self,
            text="YOUR CARD",
            scale=1.6,
            position=(-0.2, 0.2),
            origin=(0, 0),
            color=color.hex('#a8dadc')
        )
        self.computer_label = Text(
            parent=self,
            text="COMP CARD",
            scale=1.6,
            position=(0.2, 0.2),
            origin=(0, 0),
            color=color.hex('#e63946')
        )
        
        # Card Placement Indicators (subtle outline boxes in center arena)
        self.player_card_indicator = Entity(
            parent=self,
            model='quad',
            color=color.rgba(255, 255, 255, 15),
            scale=(0.184, 0.264),
            position=(-0.2, 0.03, 0.1)
        )
        self.computer_card_indicator = Entity(
            parent=self,
            model='quad',
            color=color.rgba(255, 255, 255, 15),
            scale=(0.184, 0.264),
            position=(0.2, 0.03, 0.1)
        )
        
        # Round result text background
        self.result_bg = Entity(
            parent=self,
            model='quad',
            color=color.rgba(29, 53, 87, 100),
            scale=(0.8, 0.08),
            position=(0, -0.15),
            z=0.1
        )
        
        # Round Outcome Message
        self.message_board = Text(
            parent=self,
            text="Choose a card from your hand to start the battle!",
            scale=1.8,
            position=(0, -0.15),
            origin=(0, 0),
            color=color.hex('#f1faee')
        )
        
        # Target Match Score Indicator
        self.target_text = Text(
            parent=self,
            text="First to 10 Wins!",
            scale=1.4,
            position=(0, 0.22),
            origin=(0, 0),
            color=color.hex('#ffb703')
        )

        # Special Card Section Labels
        self.player_special_label = Text(
            parent=self,
            text="SPECIALS",
            scale=1.2,
            position=(0.72, -0.22),
            origin=(0, 0),
            color=color.hex('#7209b7')
        )
        self.computer_special_label = Text(
            parent=self,
            text="SPECIALS",
            scale=1.2,
            position=(0.72, 0.22),
            origin=(0, 0),
            color=color.hex('#7209b7')
        )

        # Active Modifier Status Text
        self.modifier_text = Text(
            parent=self,
            text="",
            scale=1.5,
            position=(0, 0.14),
            origin=(0, 0),
            color=color.hex('#ffb703')
        )
 
        # Dummy Draw Button to maintain backward compatibility with main.py calls
        self.draw_button = Button(enabled=False, visible=False)
        
        # Quit Button
        self.quit_button = Button(
            parent=self,
            text="Quit to Menu",
            scale=(0.18, 0.05),
            position=(-0.75, 0.44),
            color=color.hex('#1d3557'),
            highlight_color=color.hex('#e63946'),
            text_color=color.white,
            on_click=on_quit_click
        )

    def update_scores(self, player_score, computer_score, message):
        """Updates score values and details in the HUD."""
        self.player_score_text.text = str(player_score)
        self.computer_score_text.text = str(computer_score)
        self.message_board.text = message


class GameOverUI(Entity):
    """Container for the Victory or Defeat screens."""
    def __init__(self, on_restart_click, on_menu_click, **kwargs):
        super().__init__(parent=camera.ui, enabled=False, **kwargs)
        
        # Title Banner
        self.outcome_text = Text(
            parent=self,
            text="VICTORY!",
            scale=6,
            position=(0, 0.22),
            origin=(0, 0),
            color=color.hex('#ffb703')
        )
        
        # Detailed outcome text
        self.summary_text = Text(
            parent=self,
            text="Final Score\nPlayer: 10  |  Computer: 8",
            scale=2.2,
            position=(0, 0.04),
            origin=(0, 0),
            color=color.white
        )
        
        # Play Again Button
        self.restart_button = Button(
            parent=self,
            text="PLAY AGAIN",
            scale=(0.3, 0.08),
            position=(0, -0.12),
            color=color.hex('#e63946'),
            highlight_color=color.hex('#d62828'),
            text_color=color.white,
            on_click=on_restart_click
        )
        
        # Menu Button
        self.menu_button = Button(
            parent=self,
            text="MAIN MENU",
            scale=(0.3, 0.08),
            position=(0, -0.24),
            color=color.hex('#1d3557'),
            highlight_color=color.hex('#457b9d'),
            text_color=color.white,
            on_click=on_menu_click
        )

    def show_screen(self, winner, player_score, computer_score):
        """Prepares and enables the game over overlay."""
        if winner == "Player":
            self.outcome_text.text = "VICTORY!"
            self.outcome_text.color = color.hex('#4cc9f0') # Bright cyan victory
        else:
            self.outcome_text.text = "DEFEAT!"
            self.outcome_text.color = color.hex('#f72585') # Neon pink/red defeat
            
        self.summary_text.text = f"Final Match Standings\nPlayer: {player_score}   -   Computer: {computer_score}"
        self.enabled = True
