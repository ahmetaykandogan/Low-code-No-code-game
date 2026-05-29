import random
from ursina import Entity, color, Text, curve, Vec3, camera

# Map special types to labels and descriptions
SPECIAL_INFO = {
    'reverse': {
        'title': 'REVERSE',
        'symbol': 'REV',
        'desc': 'Chaos Order:\n2 beats Ace',
        'theme_color': color.hex('#7209b7'), # Royal Purple
        'accent_color': color.hex('#f72585')  # Pink
    },
    'reveal': {
        'title': 'REVEAL',
        'symbol': 'EYE',
        'desc': 'Spyglass:\nExpose enemy card',
        'theme_color': color.hex('#3a0ca3'), # Indigo
        'accent_color': color.hex('#4cc9f0')  # Cyan
    },
    'boost': {
        'title': 'BOOST',
        'symbol': '+3',
        'desc': 'Strength:\n+3 to your card',
        'theme_color': color.hex('#ffb703'), # Gold/Yellow
        'accent_color': color.hex('#fb5607')  # Orange
    },
    'swap': {
        'title': 'SWAP',
        'symbol': 'SWAP',
        'desc': 'Trickster:\nTrade hand cards',
        'theme_color': color.hex('#06d6a0'), # Green/Teal
        'accent_color': color.hex('#118ab2')  # Blue
    },
    'cancel': {
        'title': 'CANCEL',
        'symbol': 'X',
        'desc': 'Shield:\nVoid current round',
        'theme_color': color.hex('#e63946'), # Red
        'accent_color': color.hex('#d62828')  # Dark Red
    }
}

class SpecialCardEntity(Entity):
    """Visual special card representation parented to camera.ui."""
    def __init__(self, card_type, target_position=(0, 0), face_up=True, clickable=False, **kwargs):
        # Position container off-screen
        start_y = -0.8 if target_position[1] < 0 else 0.8
        start_position = (target_position[0], start_y, 0)
        
        super().__init__(
            parent=camera.ui,
            position=start_position,
            scale=0,
            rotation_z=random.uniform(-35, 35),
            **kwargs
        )
        
        self.card_type = card_type
        self.face_up = face_up
        self.clickable = clickable
        self.original_y = target_position[1]
        
        info = SPECIAL_INFO[card_type]
        
        # 1. Shadow
        self.shadow = Entity(
            parent=self,
            model='quad',
            color=color.rgba(0, 0, 0, 50),
            scale=(0.15, 0.21),
            position=(0.005, -0.008, 0.04),
            z=0.03
        )

        # 2. Border
        self.border = Entity(
            parent=self,
            model='quad',
            color=info['accent_color'],
            scale=(0.144, 0.204),
            z=0.02
        )
        
        # 3. Card Face
        self.face = Entity(
            parent=self,
            model='quad',
            color=info['theme_color'] if self.face_up else color.hex('#2c1b4d'), # Dark violet when face down
            scale=(0.14, 0.20),
            z=0.01
        )
        
        # Front components (only enabled if face_up is True)
        self.title_text = Text(
            parent=self,
            text=info['title'],
            color=color.white,
            scale=1.1,
            position=(0, 0.07, -0.01),
            origin=(0, 0),
            enabled=self.face_up
        )
        
        self.center_symbol = Text(
            parent=self,
            text=info['symbol'],
            color=color.white,
            scale=2.2,
            position=(0, 0.01, -0.01),
            origin=(0, 0),
            enabled=self.face_up
        )
        
        self.desc_text = Text(
            parent=self,
            text=info['desc'],
            color=color.rgba(255, 255, 255, 200),
            scale=0.9,
            position=(0, -0.05, -0.01),
            origin=(0, 0),
            enabled=self.face_up
        )
        
        # Back components (only enabled if face_up is False)
        self.card_back = Entity(
            parent=self,
            model='quad',
            color=color.hex('#2c1b4d'), # Deep violet card back
            scale=(0.13, 0.19),
            z=0.005,
            enabled=not self.face_up
        )
        self.back_inner = Entity(
            parent=self.card_back,
            model='quad',
            color=color.hex('#7209b7'), # Neon purple inner accent
            scale=(0.85, 0.85),
            z=-0.001
        )
        self.back_pattern = Entity(
            parent=self.card_back,
            model='quad',
            color=color.hex('#ffb703'), # Gold diamond accent in center
            scale=(0.3, 0.3),
            rotation_z=45,
            z=-0.002
        )
        
        # Setup hover interactions
        if self.clickable:
            self.collider = 'box'
            self.on_mouse_enter = self.hover_start
            self.on_mouse_exit = self.hover_end
            
        self.draw_animate(target_position)

    def hover_start(self):
        if self.clickable:
            self.animate_y(self.original_y + 0.04, duration=0.15, curve=curve.out_quad)
            self.border.color = color.white # Glow white on hover

    def hover_end(self):
        if self.clickable:
            self.animate_y(self.original_y, duration=0.15, curve=curve.out_quad)
            self.border.color = SPECIAL_INFO[self.card_type]['accent_color']

    def flip_card(self):
        if self.face_up:
            return
        from ursina import invoke
        self.animate_scale_x(0, duration=0.15, curve=curve.linear)
        invoke(self._mid_flip_swap, delay=0.15)

    def _mid_flip_swap(self):
        self.face_up = True
        self.face.color = SPECIAL_INFO[self.card_type]['theme_color']
        self.card_back.enabled = False
        self.title_text.enabled = True
        self.center_symbol.enabled = True
        self.desc_text.enabled = True
        self.animate_scale_x(1, duration=0.15, curve=curve.linear)

    def draw_animate(self, target_position):
        self.animate_position((target_position[0], target_position[1], 0), duration=0.6, curve=curve.out_back)
        self.animate_scale((1, 1, 1), duration=0.6, curve=curve.out_back)
        self.animate_rotation_z(random.uniform(-4, 4), duration=0.6, curve=curve.out_back)

    def discard_animate(self, to_left=True):
        self.clickable = False
        self.collider = None
        target_x = -1.2 if to_left else 1.2
        target_y = random.uniform(-0.2, 0.2)
        target_rot = random.uniform(-60, 60)
        
        self.animate_position((target_x, target_y, 0), duration=0.4, curve=curve.in_back)
        self.animate_scale((0, 0, 0), duration=0.4, curve=curve.in_back)
        self.animate_rotation_z(target_rot, duration=0.4, curve=curve.in_back)
        from ursina import destroy
        destroy(self, delay=0.55)
