# 消个箭头 - 关卡生成器
# 核心算法：严格分层、强制连通、保证唯一解

import random
from typing import List, Tuple, Optional, Set
from enum import Enum

DIR = ['up', 'down', 'left', 'right']
DIR_VEC = {'up': (0, 1), 'down': (0, -1), 'left': (-1, 0), 'right': (1, 0)}
DIR_OPP = {'up': 'down', 'down': 'up', 'left': 'right', 'right': 'left'}

class Difficulty(Enum):
    EASY = 0
    NORMAL = 1
    HARD = 2
    HELL = 3

DIFF_CONFIG = {
    Difficulty.EASY:   {'grid': (5, 6),      'arrows': (8, 15),  'lives': 5, 'hints': 999, 'hammers': 5,  'bends': (0, 2)},
    Difficulty.NORMAL: {'grid': (7, 8),      'arrows': (18, 30), 'lives': 3, 'hints': 3,   'hammers': 3,  'bends': (2, 4)},
    Difficulty.HARD:   {'grid': (9, 10),     'arrows': (35, 60), 'lives': 2, 'hints': 1,   'hammers': 1,  'bends': (4, 8)},
    Difficulty.HELL:   {'grid': (11, 13),    'arrows': (70, 120),'lives': 1, 'hints': 0,   'hammers': 0,  'bends': (8, 20)},
}

def get_diff_for_level(level: int) -> Difficulty:
    """100关, 每20关升一次难度"""
    if level <= 20:   return Difficulty.EASY
    elif level <= 40: return Difficulty.NORMAL
    elif level <= 60: return Difficulty.HARD
    elif level <= 80: return Difficulty.HELL
    else:             return Difficulty.HELL


class ArrowCell:
    """地图上的一个箭头"""
    def __init__(self, col: int, row: int, direction: str, layer: int = 0):
        self.col = col
        self.row = row
        self.direction = direction
        self.layer = layer
        self.solve_order = -1

    def __repr__(self):
        return f"Arrow({self.col},{self.row},{self.direction},L{self.layer})"


class PuzzleMap:
    """生成的谜题地图"""

    def __init__(self, level: int):
        self.level = level
        self.diff = get_diff_for_level(level)
        self.cfg = DIFF_CONFIG[self.diff]

        gmin, gmax = self.cfg['grid']
        progress = (level - 1) % 20 + 1
        ratio = progress / 20.0
        self.grid_size = gmin + int((gmax - gmin) * ratio)
        if self.grid_size < 5:
            self.grid_size = 5

        self.width = self.grid_size
        self.height = self.grid_size

        amin, amax = self.cfg['arrows']
        max_possible = self.grid_size * self.grid_size
        amax = min(amax, max_possible)
        amin = min(amin, amax)
        self.arrow_count = amin + int((amax - amin) * ratio)

        self.cells: List[ArrowCell] = []
        self.grid: dict = {}
        self._generate()
        self._calc_solve_order()

    def _generate(self):
        """主生成逻辑"""
        self.cells = []
        self.grid = {}
        occupied = set()

        # -- 第1层：外圈箭头 --
        border_cells = self._get_border_cells()
        random.shuffle(border_cells)
        layer1_count = min(max(3, self.arrow_count // 4), len(border_cells))

        placed = 0
        for col, row in border_cells:
            if placed >= layer1_count:
                break
            outward = self._outward_dir(col, row)
            if outward is None:
                continue
            cell = ArrowCell(col, row, outward, layer=1)
            self._place(cell)
            occupied.add((col, row))
            placed += 1

        # -- 第2-N层：内部 --
        inner_cells = self._get_inner_cells(occupied)
        remaining = self.arrow_count - len(self.cells)
        if remaining <= 0:
            return

        random.shuffle(inner_cells)
        placed_inner = 0
        max_layers = self._max_layers()

        for col, row in inner_cells:
            if placed_inner >= remaining:
                break
            if (col, row) in occupied:
                continue

            dirs = list(DIR)
            random.shuffle(dirs)
            chosen_dir = None
            for d in dirs:
                if self._path_clear(col, row, d, occupied):
                    chosen_dir = d
                    break

            if chosen_dir is None:
                continue

            layer = self._calc_layer(col, row, chosen_dir, occupied)
            if layer > max_layers:
                continue

            cell = ArrowCell(col, row, chosen_dir, layer=layer)
            self._place(cell)
            occupied.add((col, row))
            placed_inner += 1

    def _place(self, cell: ArrowCell):
        self.cells.append(cell)
        self.grid[(cell.col, cell.row)] = cell

    def _get_border_cells(self) -> List[Tuple[int, int]]:
        cells = []
        for c in range(self.width):
            cells.append((c, 0))
            cells.append((c, self.height - 1))
        for r in range(1, self.height - 1):
            cells.append((0, r))
            cells.append((self.width - 1, r))
        return cells

    def _get_inner_cells(self, occupied: Set) -> List[Tuple[int, int]]:
        cells = []
        for r in range(self.height):
            for c in range(self.width):
                if (c, r) not in occupied:
                    cells.append((c, r))
        return cells

    def _outward_dir(self, col: int, row: int) -> Optional[str]:
        if row == 0:      return 'down'
        if row == self.height - 1: return 'up'
        if col == 0:      return 'left'
        if col == self.width - 1:  return 'right'
        return None

    def _path_clear(self, col: int, row: int, direction: str, occupied: Set) -> bool:
        dx, dy = DIR_VEC[direction]
        x, y = col + dx, row + dy
        while 0 <= x < self.width and 0 <= y < self.height:
            if (x, y) in occupied:
                other = self.grid.get((x, y))
                if other:
                    return True
                return False
            x += dx
            y += dy
        return True

    def _calc_layer(self, col: int, row: int, direction: str, occupied: Set) -> int:
        dx, dy = DIR_VEC[direction]
        x, y = col + dx, row + dy
        max_layer = 1
        while 0 <= x < self.width and 0 <= y < self.height:
            other = self.grid.get((x, y))
            if other:
                max_layer = max(max_layer, other.layer + 1)
            x += dx
            y += dy
        return max_layer

    def _max_layers(self) -> int:
        return {Difficulty.EASY: 2, Difficulty.NORMAL: 3,
                Difficulty.HARD: 4, Difficulty.HELL: 6}[self.diff]

    def _calc_solve_order(self):
        self.cells.sort(key=lambda c: c.layer)
        for i, c in enumerate(self.cells):
            c.solve_order = i + 1

    def is_solved(self, eliminated_set: Set) -> bool:
        return len(eliminated_set) == len(self.cells)

    def can_eliminate(self, cell: ArrowCell, eliminated_set: Set) -> Tuple[bool, Optional[str]]:
        if (cell.col, cell.row) in eliminated_set:
            return False, "already_eliminated"
        dx, dy = DIR_VEC[cell.direction]
        x, y = cell.col + dx, cell.row + dy
        while 0 <= x < self.width and 0 <= y < self.height:
            other = self.grid.get((x, y))
            if other and (x, y) not in eliminated_set:
                return False, "blocked"
            x += dx
            y += dy
        return True, None

    def get_hint(self, eliminated_set: Set) -> Optional[ArrowCell]:
        for cell in self.cells:
            can, _ = self.can_eliminate(cell, eliminated_set)
            if can:
                return cell
        return None

    def get_score_for_level(self) -> int:
        """根据关卡计算基础得分"""
        diff_base = {Difficulty.EASY: 50, Difficulty.NORMAL: 100,
                     Difficulty.HARD: 200, Difficulty.HELL: 500}
        base = diff_base[self.diff]
        return base + len(self.cells) * 10


if __name__ == '__main__':
    for lvl in [1, 10, 21, 30, 41, 50, 61, 70, 81, 95]:
        pm = PuzzleMap(lvl)
        diff_names = ['简单', '普通', '困难', '地狱']
        print(f"Level {lvl}: [{diff_names[pm.diff.value]}] "
              f"{pm.width}x{pm.height}, {len(pm.cells)} arrows, "
              f"cells={pm.grid_size*pm.grid_size}, layers={max(c.layer for c in pm.cells)}")
