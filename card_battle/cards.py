import random
from ursina import Entity, color, Text, curve, Vec3, camera

# Suit symbols and color configuration
SUIT_SYMBOLS = {
    'Hearts': '♥',
    'Diamonds': '♦',
    'Clubs': '♣',
    'Spades': '♠'
}

SUIT_COLORS = {
    'Hearts': color.hex('#e63946'),     # Modern premium red
    'Diamonds': color.hex('#e63946'),   # Modern premium red
    'Clubs': color.hex('#1d3557'),      # Modern dark slate blue/black
    'Spades': color.hex('#1d3557')      # Modern dark slate blue/black
}

RANKS = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 11, 'Q': 12, 'K': 13, 'A': 14
}

SUITS = list(SUIT_SYMBOLS.keys())

class Card:
    """Represents a standard playing card logic and formatting."""
    def __init__(self, rank, suit):
        if rank not in RANKS:
            raise ValueError(f"Invalid rank: {rank}")
        if suit not in SUIT_SYMBOLS:
            raise ValueError(f"Invalid suit: {suit}")
            
        self.rank = rank
        self.suit = suit
        self.value = RANKS[rank]
        self.symbol = SUIT_SYMBOLS[suit]
        self.color = SUIT_COLORS[suit]

    def __str__(self):
        return f"{self.rank}{self.symbol}"


class CardEntity(Entity):
    """Visual card representation parented to camera.ui."""
    def __init__(self, card, target_position=(0, 0), face_up=True, clickable=False, **kwargs):
        # Position the parent container at target_x but off-screen at bottom or top depending on position
        start_y = -0.8 if target_position[1] < 0 else 0.8
        start_position = (target_position[0], start_y, 0)
        
        super().__init__(
            parent=camera.ui,
            position=start_position,
            scale=0, # Scale up from 0 to 1 for draw animation
            rotation_z=random.uniform(-35, 35), # Spin from a random angle
            **kwargs
        )
        
        self.card = card
        self.face_up = face_up
        self.clickable = clickable
        self.original_y = target_position[1]
        
        # 1. Card Shadow (subtle background blur effect)
        self.shadow = Entity(
            parent=self,
            model='quad',
            color=color.rgba(0, 0, 0, 50), # Semi-transparent black
            scale=(0.19, 0.27),
            position=(0.005, -0.008, 0.04), # Slightly offset down-right
            z=0.03
        )

        # 2. Card Border (slightly larger than card face for thin crisp outline)
        self.border = Entity(
            parent=self,
            model='quad',
            color=color.hex('#b0b0b0'), # Soft grey border
            scale=(0.184, 0.264),
            z=0.02
        )
        
        # 3. Card Face
        self.face = Entity(
            parent=self,
            model='quad',
            color=color.white,
            scale=(0.18, 0.26),
            z=0.01
        )
        
        # 4. Center large symbol + value
        self.center_text = Text(
            parent=self,
            text=f"{card.rank}\n{card.symbol}",
            color=card.color,
            scale=3,
            origin=(0, 0),
            z=-0.01,
            enabled=self.face_up
        )
        
        # 5. Mini symbol top-left
        self.top_left_text = Text(
            parent=self,
            text=f"{card.rank}{card.symbol}",
            color=card.color,
            scale=1.3,
            position=(-0.075, 0.11, -0.01),
            origin=(-0.5, 0.5),
            enabled=self.face_up
        )
        
        # 6. Mini symbol bottom-right (rotated)
        self.bottom_right_text = Text(
            parent=self,
            text=f"{card.rank}{card.symbol}",
            color=card.color,
            scale=1.3,
            position=(0.075, -0.11, -0.01),
            origin=(0.5, -0.5),
            rotation_z=180,
            enabled=self.face_up
        )

        # 7. Card Back design (only visible if face_up is False)
        self.card_back = Entity(
            parent=self,
            model='quad',
            color=color.hex('#1d3557'), # Dark premium slate blue
            scale=(0.17, 0.25),
            z=0.005,
            enabled=not self.face_up
        )
        self.back_inner = Entity(
            parent=self.card_back,
            model='quad',
            color=color.hex('#ffb703'), # Gold inner accent
            scale=(0.85, 0.85),
            z=-0.001
        )
        # Geometric diamond pattern in the center
        self.back_pattern = Entity(
            parent=self.card_back,
            model='quad',
            color=color.hex('#1d3557'), # Dark premium slate blue diamond
            scale=(0.4, 0.4),
            rotation_z=45,
            z=-0.002
        )
        self.back_pattern_inner = Entity(
            parent=self.back_pattern,
            model='quad',
            color=color.hex('#ffb703'), # Gold center point
            scale=(0.3, 0.3),
            z=-0.001
        )
        
        # Setup interactive behaviors
        if self.clickable:
            self.collider = 'box'
            self.on_mouse_enter = self.hover_start
            self.on_mouse_exit = self.hover_end

        # Trigger smooth draw animation (slide-in, rotate, scale-up)
        self.draw_animate(target_position)

    def hover_start(self):
        """Elevates card and highlights border on hover."""
        if self.clickable:
            self.animate_y(self.original_y + 0.04, duration=0.15, curve=curve.out_quad)
            self.border.color = color.hex('#ffb703') # Gold border highlight

    def hover_end(self):
        """Restores original card height and border on hover exit."""
        if self.clickable:
            self.animate_y(self.original_y, duration=0.15, curve=curve.out_quad)
            self.border.color = color.hex('#b0b0b0') # Default grey border

    def flip_card(self):
        """Flips the card face-up using a scale-squeezing animation to simulate 3D rotation."""
        if self.face_up:
            return
        from ursina import invoke
        self.animate_scale_x(0, duration=0.15, curve=curve.linear)
        invoke(self._mid_flip_swap, delay=0.15)

    def _mid_flip_swap(self):
        self.face_up = True
        self.card_back.enabled = False
        self.center_text.enabled = True
        self.top_left_text.enabled = True
        self.bottom_right_text.enabled = True
        self.animate_scale_x(1, duration=0.15, curve=curve.linear)

    def draw_animate(self, target_position):
        """Animates the card onto the screen."""
        self.animate_position((target_position[0], target_position[1], 0), duration=0.6, curve=curve.out_back)
        self.animate_scale((1, 1, 1), duration=0.6, curve=curve.out_back)
        # End at a natural slight tilt
        self.animate_rotation_z(random.uniform(-4, 4), duration=0.6, curve=curve.out_back)
        
    def discard_animate(self, to_left=True):
        """Animates the card sliding off-screen to be destroyed."""
        self.clickable = False
        self.collider = None
        
        target_x = -1.2 if to_left else 1.2
        target_y = random.uniform(-0.2, 0.2)
        target_rot = random.uniform(-60, 60)
        
        self.animate_position((target_x, target_y, 0), duration=0.4, curve=curve.in_back)
        self.animate_scale((0, 0, 0), duration=0.4, curve=curve.in_back)
        self.animate_rotation_z(target_rot, duration=0.4, curve=curve.in_back)
        # Schedule deletion after animation
        from ursina import destroy
        destroy(self, delay=0.55)
