from PySide6.QtWidgets import QLabel, QApplication
from PySide6.QtGui import QMovie, QPainter, QPixmap
from PySide6.QtCore import Qt, QSize, QTimer, QElapsedTimer
from config import *
import random, time

def load_animation(gif_path, animations_fps, direction, scale=3, fps=None):
    """
    Load a GIF and return scaled frames as QPixmaps along with fps.
    :param direction: direction of gif. 1 or -1
    :param animations_fps: dictionary of animation gifs to their fps
    :param gif_path: Path to GIF
    :param scale: Integer scale factor
    :param fps: Optional custom FPS (overrides GIF frame delay)
    :return: {"frames": [...QPixmap...], "fps": int}
    """
    if direction == 1:
        movie = QMovie(f"{gif_path}.gif")
    else:
        movie = QMovie(f"{gif_path}_FLIPPED.gif")

    max_w, max_h = 0, 0
    for i in range(movie.frameCount()):
        movie.jumpToFrame(i)
        pix = movie.currentPixmap()
        max_w = max(max_w, pix.width())
        max_h = max(max_h, pix.height())

    frames = []
    target_size = QSize(max_w * scale, max_h * scale)
    for i in range(movie.frameCount()):
        movie.jumpToFrame(i)
        pix = movie.currentPixmap()

        canvas = QPixmap(max_w, max_h)
        canvas.fill(Qt.GlobalColor.transparent)

        painter = QPainter(canvas)
        painter.drawPixmap(0, 0, pix)
        painter.end()

        scaled = canvas.scaled(target_size,
                               Qt.AspectRatioMode.KeepAspectRatio,
                               Qt.TransformationMode.FastTransformation)
        frames.append(scaled)

    # Determine FPS
    if fps is None:
        filename_with_ext = gif_path.split('/')[-1]
        filename = filename_with_ext.split('.')[0]
        if filename in animations_fps.keys():
            return {"frames": frames, "fps": animations_fps[filename]}

        frame_delay_ms = movie.nextFrameDelay()
        fps = 1000 / frame_delay_ms if frame_delay_ms > 0 else 12  # fallback 12 FPS

    return {"frames": frames, "fps": fps}

class Pet(QLabel):
    def __init__(self, name, scale=5, fps=None):
        super().__init__()

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.scale = scale
        self.name = name
        self.drag_offset = None

        self.x = DEFAULT_X
        self.y = DEFAULT_Y
        self.move(self.x, self.y)
        self.vx = 0
        self.direction = 1

        self.state = "rest"
        self.speed = random.randint(1, 4)
        self.rest_duration = random.randint(5, 30)
        self.walking_duration = random.randint(5, 8)
        self.start = time.time()

        self.played_loops = 0
        self.repeat_count = 0
        self.next_animation = 0
        self.pet_fps = ANIMATION_FPS

        self.frames = []
        self.fps = fps
        self.frame_index = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)
        self.elapsed = QElapsedTimer()

        # Load the default animation
        self.current_animation = DEFAULT_ANIMATION
        self.change_animation(DEFAULT_ANIMATION)
        self.show()

        # Dragging
        self.drag_offset = None

    def change_animation(self, anim, repeat=1, next_a=DEFAULT_ANIMATION):
        animation = load_animation(f"{ANIMATION_PATH}/{self.name}/{anim}", self.pet_fps, self.direction, scale=self.scale)
        if not animation["frames"]:
            return
        self.current_animation = anim

        self.frames = animation["frames"]
        self.fps = animation["fps"]
        self.frame_index = 0
        self.setPixmap(self.frames[0])

        self.played_loops = 0
        self.repeat_count = repeat
        self.next_animation = next_a

        try:
            self.timer.timeout.disconnect()
        except Exception:
            pass

        def next_frame_repeat():
            self.frame_index += 1
            if self.frame_index >= len(self.frames):
                self.frame_index = 0
                self.played_loops += 1
                if self.played_loops >= self.repeat_count:
                    self.change_animation(self.next_animation)
                    return
            frame = self.frames[self.frame_index]
            self.setPixmap(frame)

        self.timer.timeout.connect(next_frame_repeat)
        self.timer.start(int(1000 / self.fps))

    def next_frame(self):
        self.frame_index = (self.frame_index + 1) % len(self.frames)
        self.setPixmap(self.frames[self.frame_index])

    def update_positon(self):
        self.x += self.vx
        self.vx *= FRICTION
        self.move(self.x, self.y)

    def update(self):
        self.update_positon()

        if abs(self.vx) > 0.5:
            if self.current_animation != "walk0":
                self.change_animation("walk0")

        elapsed = time.time() - self.start
        if self.state == "rest":
            if elapsed > self.rest_duration:
                self.walking_duration = random.randint(3, 7)
                self.start = time.time()
                self.speed = random.randint(1, 4)
                #if random.random() < 0.01:
                    #self.speed *= -1
                self.state = "walk"
        elif self.state == "walk":
            if elapsed > self.walking_duration:
                self.rest_duration = random.randint(5, 30)
                self.start = time.time()
                self.state = "rest"
            else:
                self.vx = self.speed * self.direction
                if self.x >= RIGHT_BOUND and self.vx > 0:
                    self.direction = -1
                    self.x = RIGHT_BOUND
                elif self.x <= LEFT_BOUND and self.vx < 0:
                    self.direction = 1
                    self.speed *= -1
                    self.x = LEFT_BOUND
        #print("Speed:")
        #print(self.speed)
        #print("vx:")
        #print(self.vx)
        #print("Direction:")
        #print(self.direction)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_offset = event.globalPosition().toPoint() - self.pos()

    def mouseMoveEvent(self, event):
        if self.drag_offset:
            new_pos = event.globalPosition().toPoint() - self.drag_offset
            self.x = new_pos.x()
            self.y = DEFAULT_Y
            self.move(self.x, self.y)

    def mouseReleaseEvent(self, event):
        self.drag_offset = None


if __name__ == "__main__":
    app = QApplication([])

    pet = Pet("cat")

    move_timer = QTimer()
    move_timer.timeout.connect(pet.update)
    move_timer.start(1000 // 60)  # ~60 updates per second

    app.exec()

