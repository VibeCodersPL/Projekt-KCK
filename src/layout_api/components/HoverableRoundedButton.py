from layout_api.components.RoundedButton import *
class HoverableRoundedButton(RoundedButton):
    def __init__(self, hover_threshold=30, **kwargs):
        super().__init__(**kwargs)
        self.hover_frames = 0
        self.hover_threshold = hover_threshold
        self.is_hover_active = True  # Flaga do wyłączania interakcji z kamerą

        # Rysowanie paska postępu na wierzchu przycisku
        with self.canvas.after:
            self.progress_color = Color(0, 1, 0, 0)  # Przezroczysty zielony
            self.progress_rect = RoundedRectangle(pos=self.pos, size=(0, 0), radius=[self.radius])

        self.bind(pos=self._update_progress_ui, size=self._update_progress_ui)

    def _update_progress_ui(self, *args):
        """Aktualizuje pozycję paska postępu w przypadku zmiany rozmiaru okna"""
        self.progress_rect.pos = self.pos
        progress = max(0, self.hover_frames) / self.hover_threshold
        self.progress_rect.size = (self.width * progress, self.height)

    def process_hover(self, points: list[tuple]):
        """
        Przyjmuje listę punktów (x, y) i sprawdza kolizję.
        Aktualizuje pasek i symuluje kliknięcie, jeśli się zapełni.
        """
        if not self.is_hover_active:
            self.hover_frames = 0
            self._update_progress_ui()
            self.progress_color.a = 0
            return

        # Sprawdzamy czy którykolwiek z punktów uderza w przycisk
        is_hovering = any(self.collide_point(x, y) for x, y in points)

        if is_hovering:
            if self.hover_frames >= 0:
                self.hover_frames += 1
                if self.hover_frames >= self.hover_threshold:
                    self.trigger_action(0)  # KIVY MAGIA: Symuluje fizyczne kliknięcie!
                    self.hover_frames = -30 # Ustawiamy cooldown
        else:
            if self.hover_frames > 0:
                self.hover_frames -= 1
        
        # Obsługa cooldownu
        if self.hover_frames < 0:
            self.hover_frames += 1

        # Aktualizacja wizualna
        progress = max(0, self.hover_frames) / self.hover_threshold
        self.progress_rect.size = (self.width * progress, self.height)
        self.progress_color.a = 0.5 if progress > 0 else 0