import random

class Snek:
    def __init__(self, length=64, pos=0, direction=1, block='●'):
        self.length = length
        self.direction = direction
        self.block = block
        self.pos = pos

    def grow(self):
        self.length += 1

    def change_direction(self):
        if self.direction == 1:
            self.direction = -1
            self.pos -= self.length-1
        else:
            self.direction = 1
            self.pos += self.length-1

class Arena:
    def __init__(self, length, empty_block='∙', apple_block='●'):
        self.length = length
        self.snek = Snek(pos=random.randint(0, self.length-1))
        self.empty_block = empty_block
        self.apple_block = apple_block

        self.new_apple()

    @property
    def as_str(self):
        arena = [self.empty_block for i in range(self.length)]
        arena[self.apple_pos] = self.apple_block
        for i in range(self.snek.pos,
                       self.snek.pos-self.snek.direction*self.snek.length,
                       -self.snek.direction):
            arena[i%self.length] = self.snek.block

        return ''.join(arena)

    def as_screen(self, max_lines, max_cols):
        arena = self.as_str
        scr = dict()
        pos = 0
        for col in range(max_cols):
            scr[(0, col)] = arena[pos]
            pos += 1
        for line in range(1, max_lines):
            scr[(line, max_cols-1)] = arena[pos]
            pos += 1
        for col in range(max_cols-2, -1, -1):
            scr[(max_lines-1, col)] = arena[pos]
            pos += 1
        for line in range(max_lines-2, 0, -1):
            scr[(line, 0)] = arena[pos]
            pos += 1
        return scr

    @property
    def is_win(self):
        return self.snek.length == self.length

    def new_snek(self):
        self.snek = Snek(pos=random.randint(0, self.length-1))

    def new_apple(self):
        self.apple_pos = (self.snek.pos
                          + (self.snek.direction
                             * random.randint(1, self.length - self.snek.length))) % self.length

    def move(self):
        self.snek.pos += self.snek.direction
        self.snek.pos %= self.length

        if self.snek.pos == self.apple_pos:
            self.snek.grow()
            self.snek.change_direction()
            if not self.is_win:
                self.new_apple()

class Game:
    def __init__(self, cols=92, lines=53):
        self.cols = cols
        self.lines = lines
        self.arena_len = (cols + lines - 2) * 2
        self.arena = Arena(self.arena_len)

    def scr_as_str(self, arena):
        res = [[' ' for i in range(self.cols)] for i in range(self.lines)]
        for k in arena:
            res[k[0]][k[1]] = arena[k]
        return '\n'.join([''.join(l) for l in res])

    def move(self):
        self.arena.move()
        return """
<pre>{}</pre>
<style>
pre {{
    font-family: monospace;
    font-size: 30px;
    color: black;
    line-height: 0.55;
    opacity: 0.3;
}}
</style>
""".format(self.scr_as_str(self.arena.as_screen(self.lines, self.cols)))

from flask import Flask
app = Flask(__name__)

@app.route('/')
def main_page():
    refresh_ms = 500
    return """
<body>
<div id="iframe-container">
    <iframe id="iframe0" width="1920" height="1080" frameborder="0" style="display: none;"></iframe>
    <iframe id="iframe1" width="1920" height="1080" frameborder="0" style="display: none;"></iframe>
</div>
</body>

<script>
var ifrNo = 0;
var ifrHidden;
var ifr;
function reloadIFrame() {
    ifr = document.getElementById('iframe'+ifrNo);
    ifrNo = 1 - ifrNo;
    ifrHidden = document.getElementById('iframe'+ifrNo);

    ifr.onload = null;
    ifrHidden.onload = function() {
        ifr.style.display = 'none';
        ifrHidden.style.display = 'block';
    }
    ifrHidden.src = 'http://localhost:5000/snek';
}
reloadIFrame()
window.setInterval("reloadIFrame();", {});
</script>
""".format(refresh_ms)
# https://codecorner.galanter.net/2016/05/05/flicker-free-iframe-refresh/

game = Game()
@app.route('/snek')
def snek():
    return game.move()
