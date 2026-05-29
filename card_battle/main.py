from ursina import Ursina, window, color, invoke, destroy, curve
from cards import CardEntity
from special_cards import SpecialCardEntity, SPECIAL_INFO
from game_logic import GameLogic
from ui import MainMenu, GameplayUI, GameOverUI
import random

# 1. Initialize Ursina Engine
app = Ursina()

# 2. Configure Window settings for a premium desktop game feel
window.title = "War: Classic Card Battle"
window.borderless = False
window.fullscreen = False
window.exit_button.visible = False
window.fps_counter.enabled = False

# HSL / Hex custom poker green background color
window.color = color.hex('#1b4332') 

# 3. Setup game state and references
game_logic = GameLogic(target_score=10)
active_player_card = None
active_computer_card = None

# Track visual card entities for player and computer hands
x_positions = [-0.44, -0.22, 0.0, 0.22, 0.44]
player_hand_entities = [None] * 5
computer_hand_entities = [None] * 5

# Track visual special card entities
player_special_entities = [None] * 2
computer_special_entities = [None] * 2

round_in_progress = False


# Helper functions for hand visualization
def spawn_visual_hands():
    """Spawns the visual card entities for both player and computer hands and special cards."""
    global player_hand_entities, computer_hand_entities
    
    # Clear any leftover entities
    clear_hand_entities()
    
    # Spawn player cards face up at the bottom
    for i in range(5):
        card_data = game_logic.player_hand[i]
        pos = (x_positions[i], -0.36)
        card_ent = CardEntity(card_data, target_position=pos, face_up=True, clickable=True)
        # Bind index parameter using default argument
        card_ent.on_click = lambda idx=i: play_hand_card(idx)
        player_hand_entities[i] = card_ent
        
    # Spawn computer cards face down at the top
    for i in range(5):
        card_data = game_logic.computer_hand[i]
        pos = (x_positions[i], 0.36)
        card_ent = CardEntity(card_data, target_position=pos, face_up=False, clickable=False)
        computer_hand_entities[i] = card_ent

    # Spawn special cards
    respawn_player_specials()
    respawn_computer_specials()


def respawn_player_specials():
    """Clears and spawns the player's visual special card entities based on game logic."""
    global player_special_entities
    for ent in player_special_entities:
        if ent:
            destroy(ent)
    player_special_entities = [None] * 2
    x_positions_spec = [0.68, 0.82]
    for i, card_type in enumerate(game_logic.player_special_cards):
        pos = (x_positions_spec[i], -0.36)
        card_ent = SpecialCardEntity(card_type, target_position=pos, face_up=True, clickable=True)
        card_ent.on_click = lambda idx=i: play_special_card_handler(idx)
        player_special_entities[i] = card_ent


def respawn_computer_specials():
    """Clears and spawns the computer's visual special card entities based on game logic."""
    global computer_special_entities
    for ent in computer_special_entities:
        if ent:
            destroy(ent)
    computer_special_entities = [None] * 2
    x_positions_spec = [0.68, 0.82]
    for i, card_type in enumerate(game_logic.computer_special_cards):
        pos = (x_positions_spec[i], 0.36)
        card_ent = SpecialCardEntity(card_type, target_position=pos, face_up=False, clickable=False)
        computer_special_entities[i] = card_ent


def clear_hand_entities():
    """Destroys all visual hand and special card entities."""
    global player_hand_entities, computer_hand_entities, player_special_entities, computer_special_entities
    
    # Standard hands
    for card in player_hand_entities:
        if card:
            destroy(card)
    for card in computer_hand_entities:
        if card:
            destroy(card)
    player_hand_entities = [None] * 5
    computer_hand_entities = [None] * 5
    
    # Special cards
    for card in player_special_entities:
        if card:
            destroy(card)
    for card in computer_special_entities:
        if card:
            destroy(card)
    player_special_entities = [None] * 2
    computer_special_entities = [None] * 2


def clear_battle_field():
    """Animates active battle cards sliding off-screen and clears references."""
    global active_player_card, active_computer_card
    if active_player_card:
        active_player_card.discard_animate(to_left=True)
        active_player_card = None
    if active_computer_card:
        active_computer_card.discard_animate(to_left=False)
        active_computer_card = None
    # Reset modifier text overlay
    gameplay_ui.modifier_text.text = ""


# 4. Define UI interaction callbacks
def start_game():
    """Initializes score and starts a fresh match from gameplay screen."""
    global active_player_card, active_computer_card, round_in_progress
    
    round_in_progress = False
    game_logic.reset_game()
    clear_battle_field()
    clear_hand_entities()
    
    # Spawn visual hands and special cards
    spawn_visual_hands()
    
    # Update UI to starting state
    gameplay_ui.update_scores(0, 0, game_logic.round_result_message)
    
    # Transition screens
    menu_ui.enabled = False
    gameover_ui.enabled = False
    gameplay_ui.enabled = True


def play_special_card_handler(index):
    """Triggers when the player clicks a special card."""
    global round_in_progress, player_special_entities
    
    if round_in_progress or player_special_entities[index] is None:
        return
        
    spec_ent = player_special_entities[index]
    card_type = spec_ent.card_type
    
    # Play card in logic
    card_type, payload = game_logic.play_special_card(is_player=True, index=index)
    if card_type is None:
        return
        
    # Set this slot to None and discard visual card
    player_special_entities[index] = None
    spec_ent.discard_animate(to_left=True)
    
    # Apply visual effects based on card type
    if card_type == 'reveal':
        # payload is computer card index to reveal
        if payload is not None and computer_hand_entities[payload]:
            computer_hand_entities[payload].flip_card()
            gameplay_ui.modifier_text.text = "REVEAL ACTIVE!"
            
    elif card_type == 'swap':
        # payload is (p_idx, c_idx, new_p_card, new_c_card)
        if payload is not None:
            p_idx, c_idx, _, _ = payload
            trigger_visual_swap(p_idx, c_idx)
            gameplay_ui.modifier_text.text = "SWAP CARD ACTIVE!"
            
    elif card_type == 'boost':
        gameplay_ui.modifier_text.text = "BOOST +3 ACTIVE!"
        
    elif card_type == 'reverse':
        gameplay_ui.modifier_text.text = "REVERSE ORDER ACTIVE!"
        
    elif card_type == 'cancel':
        gameplay_ui.modifier_text.text = "SHIELD ACTIVE!"
        
    # Re-layout remaining specials after animation
    invoke(respawn_player_specials, delay=0.45)


def trigger_visual_swap(p_idx, c_idx):
    """Visually swaps player card entity and computer card entity on screen."""
    p_card_ent = player_hand_entities[p_idx]
    c_card_ent = computer_hand_entities[c_idx]
    
    if p_card_ent and c_card_ent:
        # Capture current screen positions
        p_pos = (x_positions[p_idx], -0.36)
        c_pos = (x_positions[c_idx], 0.36)
        
        # Animate crossover
        p_card_ent.animate_position((c_pos[0], c_pos[1], 0), duration=0.6, curve=curve.out_back)
        p_card_ent.animate_rotation_z(random.uniform(-4, 4), duration=0.6)
        
        c_card_ent.animate_position((p_pos[0], p_pos[1], 0), duration=0.6, curve=curve.out_back)
        c_card_ent.animate_rotation_z(random.uniform(-4, 4), duration=0.6)
        
        # Flip computer card face-up since it is now in player's hand
        c_card_ent.flip_card()
        
        # Make the computer's card interactive in player hand
        c_card_ent.clickable = True
        c_card_ent.collider = 'box'
        c_card_ent.original_y = -0.36
        c_card_ent.on_click = lambda idx=p_idx: play_hand_card(idx)
        c_card_ent.on_mouse_enter = c_card_ent.hover_start
        c_card_ent.on_mouse_exit = c_card_ent.hover_end
        
        # Make the player's card non-interactive in computer hand (face-down)
        p_card_ent.clickable = False
        p_card_ent.collider = None
        p_card_ent.original_y = 0.36
        p_card_ent.face_up = False
        p_card_ent.card_back.enabled = True
        p_card_ent.center_text.enabled = False
        p_card_ent.top_left_text.enabled = False
        p_card_ent.bottom_right_text.enabled = False
        p_card_ent.face.color = color.hex('#2c1b4d')
        
        # Swap tracking lists
        player_hand_entities[p_idx] = c_card_ent
        computer_hand_entities[c_idx] = p_card_ent


def play_hand_card(player_card_index):
    """Triggers when the player clicks a card from their hand."""
    global round_in_progress, active_player_card, active_computer_card
    
    # Ignore click if round is in progress or card was already played
    if round_in_progress or player_hand_entities[player_card_index] is None:
        return
        
    round_in_progress = True
    
    # 1. Disable interactivity on remaining hand cards and special cards
    for card in player_hand_entities:
        if card:
            card.clickable = False
            card.collider = None
    for card in player_special_entities:
        if card:
            card.clickable = False
            card.collider = None
            
    # 2. Get the player visual card to play
    p_entity = player_hand_entities[player_card_index]
    player_hand_entities[player_card_index] = None
    
    # 3. Play round logic (which also decides computer AI special plays)
    p_card, c_card, msg, round_winner, comp_card_index, comp_spec_type, comp_spec_idx = game_logic.play_round(player_card_index)
    
    # Get the computer visual card to play
    c_entity = computer_hand_entities[comp_card_index]
    computer_hand_entities[comp_card_index] = None
    
    # Setup card references
    active_player_card = p_entity
    active_computer_card = c_entity
    
    # Define timing offset depending on whether the computer plays a special card
    anim_delay = 0.0
    
    # 4. If computer plays a special card, animate it first
    if comp_spec_type is not None:
        anim_delay = 1.0
        # Get visual special card entity
        comp_spec_ent = computer_special_entities[comp_spec_idx]
        computer_special_entities[comp_spec_idx] = None
        
        # Animate to center and flip it
        comp_spec_ent.animate_position((0, 0.1, 0), duration=0.4, curve=curve.out_quad)
        comp_spec_ent.animate_rotation_z(0, duration=0.4)
        invoke(comp_spec_ent.flip_card, delay=0.1)
        
        # Show text
        gameplay_ui.modifier_text.text = f"COMP PLAYED {comp_spec_type.upper()}!"
        
        # Discard the computer special card after a short display
        invoke(lambda: comp_spec_ent.discard_animate(to_left=False), delay=0.9)
        # Shift visual slots of remaining computer specials
        invoke(respawn_computer_specials, delay=1.0)

    # 5. Slide standard cards to battle slots (with offset if computer played special card)
    # Slide player card to (-0.2, 0.03) and align rotation
    invoke(lambda: p_entity.animate_position((-0.2, 0.03, 0), duration=0.4, curve=curve.out_quad), delay=anim_delay)
    invoke(lambda: p_entity.animate_rotation_z(0, duration=0.4, curve=curve.out_quad), delay=anim_delay)
    
    # Slide computer card to (0.2, 0.03) and align rotation, then flip it face up
    invoke(lambda: c_entity.animate_position((0.2, 0.03, 0), duration=0.4, curve=curve.out_quad), delay=anim_delay)
    invoke(lambda: c_entity.animate_rotation_z(0, duration=0.4, curve=curve.out_quad), delay=anim_delay)
    invoke(c_entity.flip_card, delay=anim_delay + 0.1)
    
    # 6. Update scores and text in HUD
    invoke(lambda: gameplay_ui.update_scores(game_logic.player_score, game_logic.computer_score, msg), delay=anim_delay)
    
    # 7. Schedule discard and next steps
    invoke(clear_battle_field, delay=anim_delay + 1.4)
    
    if game_logic.game_over:
        invoke(show_game_over, delay=anim_delay + 2.0)
    else:
        # Check if hands are depleted and need replenishment
        hands_empty = all(x is None for x in player_hand_entities)
        if hands_empty:
            invoke(replenish_hands, delay=anim_delay + 1.8)
        else:
            invoke(unlock_hand_interaction, delay=anim_delay + 1.5)


def unlock_hand_interaction():
    """Enables hover and clicks on remaining player hand and special cards."""
    global round_in_progress
    round_in_progress = False
    
    # Hand cards
    for card in player_hand_entities:
        if card:
            card.clickable = True
            card.collider = 'box'
            
    # Special cards
    for card in player_special_entities:
        if card:
            card.clickable = True
            card.collider = 'box'


def replenish_hands():
    """Draws new cards and special cards in logic, and spawns visual entities."""
    global round_in_progress
    game_logic.draw_hands()
    game_logic.draw_special_cards()
    spawn_visual_hands()
    round_in_progress = False


def show_game_over():
    """Displays victory or defeat overlay panel."""
    gameplay_ui.enabled = False
    gameover_ui.show_screen(
        game_logic.winner,
        game_logic.player_score,
        game_logic.computer_score
    )


def go_to_menu():
    """Returns back to initial main landing page."""
    clear_battle_field()
    clear_hand_entities()
    gameplay_ui.enabled = False
    gameover_ui.enabled = False
    menu_ui.enabled = True


# 5. Initialize layout interfaces and connect action signals
menu_ui = MainMenu(on_play_click=start_game)
gameplay_ui = GameplayUI(on_draw_click=None, on_quit_click=go_to_menu)
gameover_ui = GameOverUI(on_restart_click=start_game, on_menu_click=go_to_menu)

# 6. Run Application Loop
if __name__ == '__main__':
    app.run()
