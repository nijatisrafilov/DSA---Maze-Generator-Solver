import tkinter as tk
from tkinter import filedialog, messagebox
import random
from collections import deque

CELL_SIZE = 20
ANIM_DELAY_MS = 50

COLOR_WALL = "#1a1a2e"
COLOR_PATH = "#f0f0f0"
COLOR_START = "#2ecc71"
COLOR_END = "#e74c3c"
COLOR_SOLUTION = "#3498db"
COLOR_EXPLORED = "#a29bfe"

MIN_SIZE = 3
MAX_SIZE = 40


class Maze:
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.grid_rows = 2 * rows + 1
        self.grid_cols = 2 * cols + 1
        self.grid = [[0] * self.grid_cols for _ in range(self.grid_rows)]

    def to_pixel(self, r: int, c: int) -> tuple[int, int]:
        return 2 * r + 1, 2 * c + 1

    def open_wall(self, r1: int, c1: int, r2: int, c2: int) -> None:
        pr1, pc1 = self.to_pixel(r1, c1)
        pr2, pc2 = self.to_pixel(r2, c2)
        wall_r = (pr1 + pr2) // 2
        wall_c = (pc1 + pc2) // 2
        self.grid[wall_r][wall_c] = 1
        self.grid[pr1][pc1] = 1
        self.grid[pr2][pc2] = 1

    def start_pixel(self) -> tuple[int, int]:
        return self.to_pixel(0, 0)

    def end_pixel(self) -> tuple[int, int]:
        return self.to_pixel(self.rows - 1, self.cols - 1)


class MazeGenerator:
    def generate(self, maze: Maze) -> None:
        visited = [[False] * maze.cols for _ in range(maze.rows)]
        start_r, start_c = 0, 0
        visited[start_r][start_c] = True
        stack = [(start_r, start_c)]

        while stack:
            current_r, current_c = stack[-1]
            neighbours = self._unvisited_neighbours(
                current_r, current_c, maze.rows, maze.cols, visited
            )
            if neighbours:
                next_r, next_c = random.choice(neighbours)
                maze.open_wall(current_r, current_c, next_r, next_c)
                visited[next_r][next_c] = True
                stack.append((next_r, next_c))
            else:
                stack.pop()

    @staticmethod
    def _unvisited_neighbours(r, c, rows, cols, visited):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        neighbours = []
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc]:
                neighbours.append((nr, nc))
        return neighbours


class MazeSolver:
    def solve(self, maze: Maze):
        start = maze.start_pixel()
        end = maze.end_pixel()

        queue = deque()
        queue.append(start)
        visited = {start: None}
        explored = []

        while queue:
            current = queue.popleft()
            explored.append(current)

            if current == end:
                break

            for neighbour in self._open_neighbours(current, maze):
                if neighbour not in visited:
                    visited[neighbour] = current
                    queue.append(neighbour)

        path = []
        cell = end
        while cell is not None:
            path.append(cell)
            cell = visited.get(cell)
        path.reverse()

        if path and path[0] != start:
            path = []

        return path, explored

    @staticmethod
    def _open_neighbours(cell, maze):
        r, c = cell
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        neighbours = []
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if (
                0 <= nr < maze.grid_rows
                and 0 <= nc < maze.grid_cols
                and maze.grid[nr][nc] == 1
            ):
                neighbours.append((nr, nc))
        return neighbours


class MazeApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Maze Generator & Solver")
        self.root.resizable(False, False)
        self.root.configure(bg="#2d2d2d")

        self.maze = None
        self.solution_path = []
        self.animation_job = None

        self._build_controls()
        self._build_canvas()
        self._build_status()

    def _build_controls(self):
        ctrl = tk.Frame(self.root, bg="#2d2d2d", pady=8, padx=8)
        ctrl.pack(side=tk.TOP, fill=tk.X)

        label_style = {"bg": "#2d2d2d", "fg": "#f0f0f0", "font": ("Segoe UI", 10)}
        entry_style = {
            "width": 4, "font": ("Segoe UI", 10),
            "bg": "#3d3d3d", "fg": "#f0f0f0",
            "insertbackground": "white", "relief": tk.FLAT,
            "highlightthickness": 1, "highlightcolor": "#6c63ff",
            "highlightbackground": "#555"
        }
        btn_style = {
            "font": ("Segoe UI", 10, "bold"),
            "relief": tk.FLAT, "cursor": "hand2",
            "padx": 10, "pady": 4
        }

        tk.Label(ctrl, text="Rows:", **label_style).pack(side=tk.LEFT, padx=(0, 2))
        self.rows_var = tk.StringVar(value="15")
        tk.Entry(ctrl, textvariable=self.rows_var, **entry_style).pack(side=tk.LEFT, padx=(0, 8))

        tk.Label(ctrl, text="Cols:", **label_style).pack(side=tk.LEFT, padx=(0, 2))
        self.cols_var = tk.StringVar(value="15")
        tk.Entry(ctrl, textvariable=self.cols_var, **entry_style).pack(side=tk.LEFT, padx=(0, 16))

        self.animate_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            ctrl, text="Animate BFS", variable=self.animate_var,
            bg="#2d2d2d", fg="#f0f0f0", selectcolor="#3d3d3d",
            activebackground="#2d2d2d", activeforeground="#f0f0f0",
            font=("Segoe UI", 10)
        ).pack(side=tk.LEFT, padx=(0, 16))

        self.btn_generate = tk.Button(
            ctrl, text="Generate Maze",
            bg="#6c63ff", fg="white",
            command=self._on_generate,
            **btn_style
        )
        self.btn_generate.pack(side=tk.LEFT, padx=4)

        self.btn_solve = tk.Button(
            ctrl, text="Solve Maze",
            bg="#00b894", fg="white",
            command=self._on_solve,
            state=tk.DISABLED,
            **btn_style
        )
        self.btn_solve.pack(side=tk.LEFT, padx=4)

        self.btn_save = tk.Button(
            ctrl, text="Save Maze",
            bg="#fdcb6e", fg="#2d2d2d",
            command=self._on_save,
            state=tk.DISABLED,
            **btn_style
        )
        self.btn_save.pack(side=tk.LEFT, padx=4)

        self.btn_load = tk.Button(
            ctrl, text="Load Maze",
            bg="#a29bfe", fg="white",
            command=self._on_load,
            **btn_style
        )
        self.btn_load.pack(side=tk.LEFT, padx=4)

    def _build_canvas(self):
        frame = tk.Frame(self.root, bg="#1a1a2e")
        frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 4))

        self.canvas = tk.Canvas(frame, bg=COLOR_WALL, highlightthickness=0)
        v_scroll = tk.Scrollbar(frame, orient=tk.VERTICAL, command=self.canvas.yview)
        h_scroll = tk.Scrollbar(self.root, orient=tk.HORIZONTAL, command=self.canvas.xview)

        self.canvas.configure(
            yscrollcommand=v_scroll.set,
            xscrollcommand=h_scroll.set
        )

        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def _build_status(self):
        self.status_var = tk.StringVar(value="Ready. Set dimensions and generate a maze.")
        tk.Label(
            self.root,
            textvariable=self.status_var,
            bg="#1a1a2e", fg="#a29bfe",
            font=("Segoe UI", 9), anchor=tk.W, padx=8
        ).pack(side=tk.BOTTOM, fill=tk.X)

    def _draw_maze(self):
        self.canvas.delete("all")
        if self.maze is None:
            return

        for r in range(self.maze.grid_rows):
            for c in range(self.maze.grid_cols):
                color = COLOR_PATH if self.maze.grid[r][c] == 1 else COLOR_WALL
                self._draw_cell(r, c, color)

        sr, sc = self.maze.start_pixel()
        er, ec = self.maze.end_pixel()
        self._draw_cell(sr, sc, COLOR_START)
        self._draw_cell(er, ec, COLOR_END)

        width = self.maze.grid_cols * CELL_SIZE
        height = self.maze.grid_rows * CELL_SIZE
        self.canvas.configure(scrollregion=(0, 0, width, height))

    def _draw_cell(self, r, c, color):
        x1 = c * CELL_SIZE
        y1 = r * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

    def _draw_path(self, path):
        start = self.maze.start_pixel()
        end = self.maze.end_pixel()
        for r, c in path:
            if (r, c) == start:
                color = COLOR_START
            elif (r, c) == end:
                color = COLOR_END
            else:
                color = COLOR_SOLUTION
            self._draw_cell(r, c, color)

    def _on_generate(self):
        self._cancel_animation()
        rows, cols = self._parse_dimensions()
        if rows is None:
            return

        self.maze = Maze(rows, cols)
        MazeGenerator().generate(self.maze)
        self.solution_path = []
        self._draw_maze()

        self.btn_solve.config(state=tk.NORMAL)
        self.btn_save.config(state=tk.NORMAL)
        self.status_var.set(f"Maze generated ({rows}×{cols}). Ready to solve.")

    def _on_solve(self):
        if self.maze is None:
            return

        self._cancel_animation()
        self._draw_maze()

        solver = MazeSolver()
        path, explored = solver.solve(self.maze)

        if not path:
            messagebox.showwarning("No Solution", "No path found from start to end.")
            return

        self.solution_path = path

        if self.animate_var.get():
            self._animate_bfs(explored, path)
        else:
            self._draw_path(path)
            self.status_var.set(f"Solved. Path length: {len(path)} cells.")

    def _animate_bfs(self, explored, path):
        start = self.maze.start_pixel()
        end = self.maze.end_pixel()
        total = len(explored)
        self.status_var.set("Animating BFS exploration…")

        def step(index):
            if index >= total:
                self._draw_path(path)
                self.status_var.set(f"Solved. Path length: {len(path)} cells.")
                return

            r, c = explored[index]
            if (r, c) != start and (r, c) != end:
                self._draw_cell(r, c, COLOR_EXPLORED)

            self.animation_job = self.root.after(
                ANIM_DELAY_MS, step, index + 1
            )

        step(0)

    def _on_save(self):
        if self.maze is None:
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")],
            title="Save Maze"
        )
        if not file_path:
            return

        try:
            with open(file_path, "w") as f:
                f.write(f"{self.maze.rows} {self.maze.cols}\n")
                for row in self.maze.grid:
                    f.write(" ".join(map(str, row)) + "\n")
            self.status_var.set(f"Maze saved to {file_path}")
        except OSError as e:
            messagebox.showerror("Save Error", f"Could not save file:\n{e}")

    def _on_load(self):
        self._cancel_animation()

        file_path = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt")],
            title="Load Maze"
        )
        if not file_path:
            return

        try:
            with open(file_path, "r") as f:
                lines = [line.strip() for line in f if line.strip()]

            if not lines:
                raise ValueError("File is empty.")

            parts = lines[0].split()
            if len(parts) != 2:
                raise ValueError("First line must contain exactly two integers (rows cols).")

            rows, cols = int(parts[0]), int(parts[1])
            if not (MIN_SIZE <= rows <= MAX_SIZE and MIN_SIZE <= cols <= MAX_SIZE):
                raise ValueError()

            maze = Maze(rows, cols)
            grid_lines = lines[1:]

            for r, line in enumerate(grid_lines):
                values = list(map(int, line.split()))
                for c, val in enumerate(values):
                    maze.grid[r][c] = val

            self.maze = maze
            self.solution_path = []
            self.rows_var.set(str(rows))
            self.cols_var.set(str(cols))
            self._draw_maze()

            self.btn_solve.config(state=tk.NORMAL)
            self.btn_save.config(state=tk.NORMAL)
            self.status_var.set(f"Maze loaded ({rows}×{cols}). Ready to solve.")

        except Exception as e:
            messagebox.showerror("Load Error", f"Invalid maze file:\n{e}")

    def _parse_dimensions(self):
        try:
            rows = int(self.rows_var.get())
            cols = int(self.cols_var.get())
        except ValueError:
            messagebox.showerror("Input Error", "Rows and columns must be integers.")
            return None, None

        if not (MIN_SIZE <= rows <= MAX_SIZE):
            return None, None
        if not (MIN_SIZE <= cols <= MAX_SIZE):
            return None, None

        return rows, cols

    def _cancel_animation(self):
        if self.animation_job is not None:
            self.root.after_cancel(self.animation_job)
            self.animation_job = None


def main():
    root = tk.Tk()
    root.geometry("720x560")
    MazeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()