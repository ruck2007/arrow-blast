"""
消个箭头 (Arrow Blast) v1.0
迷宫解谜：点击箭头 → 沿方向滑出 → 清完过关
"""

import os, sys, random
sys.path.insert(0, os.path.dirname(__file__))

from kivy.config import Config
Config.set('graphics', 'resizable', True)
Config.set('graphics', 'minimum_width', '320')
Config.set('graphics', 'minimum_height', '480')
Config.set('kivy', 'log_level', 'warning')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.graphics import Color, Ellipse, Rectangle, Line, Canvas
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.metrics import dp, sp

from generator import PuzzleMap, ArrowCell, Difficulty, DIFF_CONFIG, get_diff_for_level

# ── 配色 ──
C = {'bg':'#0D0D1A','panel':'#15152A','grid_bg':'#1A1A35','grid_ln':'#2A2A4A',
     'up':'#3399DB','down':'#E84C3D','left':'#44D86E','right':'#F29C0F',
     'gold':'#FFD700','white':'#FFFFFF','gray':'#7777AA','red':'#FF3333',
     'green':'#44D86E','hammer':'#C084FC','heart':'#FF4466'}
DIRS = ['up','down','left','right']
ARROW = {'up':'↑','down':'↓','left':'←','right':'→'}
VEC = {'up':(0,1),'down':(0,-1),'left':(-1,0),'right':(1,0)}
DL = {Difficulty.EASY:'简单',Difficulty.NORMAL:'普通',Difficulty.HARD:'困难',Difficulty.HELL:'地狱'}
DC = {Difficulty.EASY:'#44D86E',Difficulty.NORMAL:'#3399DB',Difficulty.HARD:'#F29C0F',Difficulty.HELL:'#E84C3D'}

def hx(h):
    h=h.lstrip('#')
    return tuple(int(h[i:i+2],16)/255 for i in(0,2,4))+(1,)


# ══════════════════ 关卡选择 ══════════════════
class SelectScreen(Screen):
    def __init__(self,**kw):
        super().__init__(**kw)
        self.name='select'
        self._ok=False

    def on_enter(self):
        if not self._ok:
            self._build()
            self._ok=True

    def _build(self):
        self.clear_widgets()
        with self.canvas.before:
            Color(*hx(C['bg']))
            Rectangle(pos=self.pos,size=self.size)

        Label(text='消个箭头',font_size=sp(34),bold=True,
              color=hx(C['gold']),
              pos_hint={'center_x':.5,'top':.95},
              size_hint=(None,None),size=(dp(200),dp(48))).bind(pos=self._nop)
        self.add_widget(Label(text='点击箭头→方向滑出→清完过关',
              font_size=sp(13),color=hx(C['gray']),
              pos_hint={'center_x':.5,'top':.87},
              size_hint=(None,None),size=(dp(360),dp(22))))

        self._grid()
        self._filters()

    def _nop(self,*a): pass

    def _grid(self):
        cols=5; gap=dp(6)
        ah=self.height-dp(150)
        tr=(99//cols)+1
        bs=min((self.width-dp(30))/cols-gap,(ah-gap*tr)/tr)
        bs=max(dp(34),min(dp(54),bs))
        sx=(self.width-cols*(bs+gap)+gap)/2
        sy=self.height-dp(105)
        for lvl in range(1,101):
            ci=(lvl-1)%cols; ri=(lvl-1)//cols
            d=get_diff_for_level(lvl)
            btn=Button(text=str(lvl),font_size=sp(int(bs*0.33)),bold=True,
                size_hint=(None,None),size=(bs,bs),
                pos=(sx+ci*(bs+gap),sy-ri*(bs+gap+dp(4))),
                background_color=hx(DC[d]),background_normal='')
            btn.is_lvl=True; btn.lvl=lvl
            btn.bind(on_press=self._go)
            self.add_widget(btn)

    def _filters(self):
        bs=min(dp(68),(self.width-dp(40))/4)
        sx=(self.width-(bs*4+dp(20)))/2
        for i,(txt,d) in enumerate([('简单',Difficulty.EASY),('普通',Difficulty.NORMAL),
                                     ('困难',Difficulty.HARD),('地狱',Difficulty.HELL)]):
            btn=Button(text=txt,font_size=sp(12),bold=True,
                size_hint=(None,None),size=(bs,dp(28)),
                pos=(sx+i*(bs+dp(6)),dp(6)),
                background_color=hx(DC[d]),background_normal='')
            btn.bind(on_press=lambda _,dd=d: self._filt(dd))
            self.add_widget(btn)

    def _filt(self,d):
        for ch in self.children:
            if getattr(ch,'is_lvl',False):
                ch.opacity=1.0 if get_diff_for_level(ch.lvl)==d else 0.2

    def _go(self,inst):
        gs=self.manager.get_screen('game')
        gs.load(inst.lvl)
        self.manager.transition=SlideTransition(direction='left')
        self.manager.current='game'


# ══════════════════ 游戏面板 ══════════════════
class GridLayer(Widget):
    """专门用来画网格和箭头"""
    def __init__(self,**kw):
        super().__init__(**kw)
        self.arrows={}
        self.puzzle=None
        self.cell=0
        self.gx=0; self.gy=0

    def build(self,pm,w,h):
        self.puzzle=pm
        self.arrows.clear()
        self.canvas.clear()
        self.clear_widgets()
        if not pm: return
        tm=dp(74); bm=dp(32)
        aw=w-dp(8); ah=h-tm-bm
        cell=min(aw/pm.width,ah/pm.height)
        cell=max(dp(24),min(dp(68),cell))
        gw=cell*pm.width; gh=cell*pm.height
        gx=(w-gw)/2; gy=bm+(ah-gh)/2
        self.cell=cell; self.gx=gx; self.gy=gy

        with self.canvas:
            Color(*hx(C['grid_bg']))
            Rectangle(pos=(gx,gy),size=(gw,gh))
            Color(*hx(C['grid_ln']))
            for i in range(pm.width+1):
                x=gx+i*cell; Line(points=[x,gy,x,gy+gh],width=1)
            for i in range(pm.height+1):
                y=gy+i*cell; Line(points=[gx,y,gx+gw,y],width=1)

        for c in pm.cells:
            self._add_arrow(c)

    def _add_arrow(self,c):
        sz=self.cell-dp(4)
        x=self.gx+c.col*self.cell+dp(2)
        y=self.gy+c.row*self.cell+dp(2)
        circle=Widget(pos=(x,y),size=(sz,sz))
        with circle.canvas:
            Color(*hx(C[c.direction]))
            Ellipse(pos=(0,0),size=(sz,sz))
            Color(1,1,1,0.1)
            Ellipse(pos=(dp(2),dp(2)),size=(sz-dp(4),sz-dp(4)))
        lbl=Label(text=ARROW[c.direction],
            font_size=sp(self.cell*0.48),bold=True,
            color=hx(C['white']),pos=(x,y),size=(sz,sz),
            halign='center',valign='middle',text_size=(sz,sz))
        self.add_widget(circle); self.add_widget(lbl)
        self.arrows[(c.col,c.row)]=(circle,lbl,c)

    def remove_arrow(self,key):
        if key in self.arrows:
            c,lbl,_=self.arrows.pop(key)
            if c.parent: self.remove_widget(c)
            if lbl.parent: self.remove_widget(lbl)


# ══════════════════ 游戏界面 ══════════════════
class GameScreen(Screen):
    def __init__(self,**kw):
        super().__init__(**kw)
        self.name='game'
        self.puzzle=None
        self.eliminated=set()
        self.animating=False
        self.lives=3; self.max_lives=3
        self.hints=3; self.hammers=3
        self.level=1; self.score=0
        self._ok=False

    def on_enter(self):
        if not self._ok:
            self._build()
            self._ok=True

    def _build(self):
        self.clear_widgets()
        self.grid=GridLayer()
        self.add_widget(self.grid)
        th=self.height

        def L(**kw):
            kw.setdefault('size_hint',(None,None))
            w=Label(**kw); self.add_widget(w); return w

        self.back_btn=Button(text='◀',font_size=sp(18),
            size_hint=(None,None),size=(dp(40),dp(34)),
            pos=(dp(3),th-dp(38)),background_color=hx(C['panel']),
            background_normal='',color=hx(C['gray']))
        self.back_btn.bind(on_press=self._back)
        self.add_widget(self.back_btn)

        self.l_lvl=L(text='第1关',font_size=sp(16),bold=True,
            color=hx(C['white']),pos=(self.width*.5-dp(50),th-dp(34)),
            size=(dp(100),dp(26)))
        self.l_diff=L(text='简单',font_size=sp(11),color=hx(C['gray']),
            pos=(self.width*.5-dp(40),th-dp(54)),size=(dp(80),dp(20)))
        self.l_scr=L(text='0',font_size=sp(13),color=hx(C['gold']),
            pos=(dp(4),th-dp(60)),size=(dp(100),dp(22)))
        self.l_heart=L(text='❤❤❤',font_size=sp(18),color=hx(C['heart']),
            pos=(self.width-dp(110),th-dp(34)),size=(dp(106),dp(26)))
        self.l_rem=L(text='剩余:0',font_size=sp(13),color=hx(C['gray']),
            pos_hint={'center_x':.5},y=dp(4),size=(dp(100),dp(22)))

        bw,bh=dp(34),dp(34); bx=self.width-dp(108); by=th-dp(42)-bh
        self.rst=Button(text='↺',font_size=sp(16),
            size_hint=(None,None),size=(bw,bh),pos=(bx,by),
            background_color=hx(C['panel']),background_normal='')
        self.rst.bind(on_press=self._reset); self.add_widget(self.rst)

        self.ham=Button(text='🔨',font_size=sp(15),
            size_hint=(None,None),size=(bw,bh),pos=(bx+bw+dp(3),by),
            background_color=hx(C['panel']),background_normal='')
        self.ham.bind(on_press=self._hammer); self.add_widget(self.ham)

        self.hnt=Button(text='💡',font_size=sp(15),
            size_hint=(None,None),size=(bw,bh),pos=(bx+(bw+dp(3))*2,by),
            background_color=hx(C['panel']),background_normal='')
        self.hnt.bind(on_press=self._hint); self.add_widget(self.hnt)

        self.fb=Label(text='',font_size=sp(22),bold=True,
            color=(1,1,1,0),pos_hint={'center_x':.5,'center_y':.5},
            size_hint=(None,None),size=(dp(300),dp(50)))
        self.add_widget(self.fb)

    def load(self,level):
        self.level=level
        self.puzzle=PuzzleMap(level)
        d=self.puzzle.diff; cfg=DIFF_CONFIG[d]
        self.max_lives=cfg['lives']; self.lives=self.max_lives
        self.hints=cfg['hints']; self.hammers=cfg['hammers']
        self.eliminated=set(); self.animating=False
        self.grid.build(self.puzzle,self.width,self.height)
        self._update()
        self._flash(f'第{level}关',1.2)

    def _update(self):
        self.l_lvl.text=f'第{self.level}关'
        d=self.puzzle.diff if self.puzzle else Difficulty.EASY
        self.l_diff.text=DL[d]; self.l_diff.color=hx(DC[d])
        self.l_scr.text=str(self.score)
        self.l_heart.text=''.join('❤' for _ in range(self.lives))
        if self.puzzle:
            self.l_rem.text=f'剩余:{len(self.puzzle.cells)-len(self.eliminated)}'
        h=self.hints
        self.hnt.text='💡'+(str(h) if 0<h<99 else('∞' if h>=99 else'0'))
        self.hnt.disabled=(h<=0)
        hm=self.hammers
        self.ham.text='🔨'+str(hm) if hm>0 else'🔨'
        self.ham.disabled=(hm<=0)

    def _flash(self,txt,dur=1.0,color=None):
        if color is None: color=hx(C['gold'])
        self.fb.text=txt; self.fb.color=color; self.fb.opacity=1
        Animation(opacity=0,duration=dur).start(self.fb)

    def on_touch_down(self,touch):
        if self.animating: return True
        for key,(c,lbl,cell) in list(self.grid.arrows.items()):
            if key in self.eliminated: continue
            if c.collide_point(touch.x,touch.y):
                self._try(cell)
                return True
        return super().on_touch_down(touch)

    def _try(self,cell):
        if self.animating or not self.puzzle: return
        can,reason=self.puzzle.can_eliminate(cell,self.eliminated)
        if not can:
            if reason=='blocked':
                self.lives-=1; self._update()
                if self.lives<=0: self._dead(); return
                self._flash('被挡住了 ❤-1',0.8,hx(C['red']))
                self._blink(cell)
            return
        self.animating=True
        self._slide(cell)

    def _slide(self,cell):
        key=(cell.col,cell.row)
        if key not in self.grid.arrows: self.animating=False; return
        c,lbl,_=self.grid.arrows[key]
        dx,dy=VEC[cell.direction]
        dist=dp(500)
        a1=Animation(pos=(c.x+dx*dist,c.y+dy*dist),opacity=0,
                     duration=0.22,t='out_quad')
        a2=Animation(opacity=0,duration=0.1)
        def done(*_):
            self.eliminated.add(key)
            self.grid.remove_arrow(key)
            pts=max(5,self.puzzle.get_score_for_level()//max(1,len(self.puzzle.cells)))
            self.score+=pts; self._update()
            if self.puzzle.is_solved(self.eliminated): self._clear()
            else: self.animating=False
        a1.bind(on_complete=done)
        a1.start(c); a2.start(lbl)

    def _blink(self,cell):
        dx,dy=VEC[cell.direction]
        x,y=cell.col+dx,cell.row+dy
        pm=self.puzzle
        while pm and 0<=x<pm.width and 0<=y<pm.height:
            o=pm.grid.get((x,y))
            if o and (x,y) not in self.eliminated and (x,y) in self.grid.arrows:
                c,_,_=self.grid.arrows[(x,y)]
                ba=Animation(opacity=0.3,duration=0.1)+Animation(opacity=1,duration=0.1)
                (ba+ba+ba).start(c)
                break
            x+=dx; y+=dy

    def _dead(self):
        self.animating=False
        self._flash('💀 游戏结束',2.5,hx(C['red']))
        Clock.schedule_once(lambda dt:self._back(None),2.5)

    def _clear(self):
        self.animating=False
        self._flash('🎉 通关!',2.0,hx(C['gold']))
        Clock.schedule_once(lambda dt:self._next(),1.8)

    def _next(self):
        if self.level<100: self.load(self.level+1)
        else:
            self._flash('🏆 全部通关!',3.0,hx(C['gold']))
            Clock.schedule_once(lambda dt:self._back(None),2.5)

    def _hint(self,_):
        if not self.puzzle or self.animating or self.hints<=0: return
        if self.hints<99: self.hints-=1
        h=self.puzzle.get_hint(self.eliminated)
        if h:
            self._flash(f'点({h.col+1},{h.row+1})的{ARROW[h.direction]}',2.0,hx(C['green']))
            if (h.col,h.row) in self.grid.arrows:
                c,_,_=self.grid.arrows[(h.col,h.row)]
                ba=Animation(opacity=0.35,duration=0.1)+Animation(opacity=1,duration=0.1)
                r=ba+ba+ba+ba; r.start(c)
                Clock.schedule_once(lambda dt:r.cancel(c),2.5)
        else: self._flash('无可消箭头!',1.0,hx(C['red']))
        self._update()

    def _hammer(self,_):
        if not self.puzzle or self.animating or self.hammers<=0: return
        h=self.puzzle.get_hint(self.eliminated)
        if h:
            self.hammers-=1
            self._flash('🔨 敲掉一个!',0.8,hx(C['hammer']))
            self._slide(h); self._update()
        else: self._flash('没有可消的!',0.8,hx(C['red']))

    def _reset(self,_):
        self.load(self.level)

    def _back(self,_):
        self.manager.transition=SlideTransition(direction='right')
        self.manager.current='select'


# ══════════════════ App ══════════════════
class ArrowBlastApp(App):
    title='消个箭头'
    use_kivy_vKeyboard=False

    def build(self):
        sm=ScreenManager()
        sm.add_widget(SelectScreen())
        sm.add_widget(GameScreen())
        sm.current='select'
        return sm


if __name__=='__main__':
    ArrowBlastApp().run()
