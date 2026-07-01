# -*- coding: utf-8 -*-
"""
贪吃蛇游戏（使用 Python 内置 tkinter，无需安装额外库）
操作说明：
    方向键 / WASD：控制蛇移动
    空格：暂停 / 继续
    R：游戏结束后重新开始
    ESC：退出
"""

# 导入随机数模块，用于随机生成食物位置
import random
# 导入 tkinter 模块，这是 Python 自带的 GUI 库，用来创建游戏窗口和绘制图形
import tkinter as tk
# 从 tkinter 导入消息框组件，用于弹出提示（本例中未使用，但保留备用）
from tkinter import messagebox


class SnakeGame:
    """
    贪吃蛇游戏类
    封装了游戏的全部逻辑：窗口、画布、蛇、食物、移动、碰撞检测、得分等
    """

    def __init__(self, master):
        """
        构造函数：初始化游戏窗口和各项参数
        master: tkinter 的根窗口对象
        """
        self.master = master  # 保存主窗口引用，方便后续操作
        self.master.title("贪吃蛇")  # 设置窗口标题
        self.master.resizable(False, False)  # 禁止用户调整窗口大小

        # ===================== 游戏配置参数 =====================
        self.width = 600        # 游戏画布宽度（像素）
        self.height = 400       # 游戏画布高度（像素）
        self.cell_size = 20     # 每个格子的大小（像素），蛇身和食物都是正方形
        self.speed = 150        # 蛇移动的时间间隔（毫秒），数值越小速度越快

        # 计算横向和纵向分别有多少个格子
        self.cols = self.width // self.cell_size   # 600 / 20 = 30 列
        self.rows = self.height // self.cell_size  # 400 / 20 = 20 行

        # ===================== 创建画布 =====================
        # Canvas 是 tkinter 的绘图组件，我们可以在上面画矩形、文字等
        self.canvas = tk.Canvas(
            master,                # 父容器是主窗口
            width=self.width,      # 画布宽度
            height=self.height,    # 画布高度
            bg="black",            # 背景颜色：黑色
            highlightthickness=0,  # 去掉画布外边框
        )
        # 将画布放到窗口中显示
        self.canvas.pack()

        # ===================== 创建分数标签 =====================
        # Label 用于显示文本，这里用来显示当前得分
        self.score_label = tk.Label(
            master,
            text="分数: 0",                 # 初始文字
            font=("Microsoft YaHei", 14),   # 字体：微软雅黑，14号
        )
        self.score_label.pack()  # 放到窗口中，位于画布下方

        # ===================== 绑定键盘事件 =====================
        # 当用户按下键盘任意键时，会调用 self.on_key 方法处理
        self.master.bind("<Key>", self.on_key)

        # ===================== 游戏状态变量 =====================
        self.direction = "Right"      # 当前移动方向
        self.next_direction = "Right" # 下一次要移动的方向（防止一帧内多次转向导致自撞）
        self.snake = []               # 蛇身列表，每个元素是 (x, y) 坐标元组
        self.food = None              # 食物坐标 (x, y)
        self.score = 0                # 当前分数
        self.running = False          # 游戏是否正在运行
        self.game_over = False        # 游戏是否结束
        self.job_id = None            # after 定时任务的 ID，用于取消之前的定时器

        # 调用初始化方法，开始一局新游戏
        self.init_game()

    def init_game(self):
        """
        初始化游戏状态，也可以用于重新开始游戏
        """
        # 如果之前还有未执行的定时任务，先取消掉，避免多个定时器同时运行
        if self.job_id:
            self.master.after_cancel(self.job_id)

        # 重置方向和状态
        self.direction = "Right"
        self.next_direction = "Right"

        # 初始化蛇的位置：蛇头在 (5, 10)，向右延伸 3 格
        # 坐标格式为 (列, 行)，左上角为 (0, 0)
        self.snake = [
            (5, self.rows // 2),   # 蛇头
            (4, self.rows // 2),   # 蛇身第一节
            (3, self.rows // 2),   # 蛇身第二节
        ]

        # 重置分数和游戏状态
        self.score = 0
        self.running = True
        self.game_over = False

        # 生成第一个食物
        self.food = self.spawn_food()

        # 更新分数显示
        self.score_label.config(text="分数: 0")

        # 绘制初始画面
        self.draw()

        # 启动游戏循环，让蛇开始移动
        self.schedule_next_move()

    def spawn_food(self):
        """
        随机生成食物位置
        规则：食物不能生成在蛇的身体上
        返回值：食物的 (x, y) 坐标
        """
        while True:
            # 随机选一个列和行
            pos = (random.randint(0, self.cols - 1), random.randint(0, self.rows - 1))
            # 如果这个位置不在蛇身上，就作为食物位置返回
            if pos not in self.snake:
                return pos

    def draw(self):
        """
        绘制整个游戏画面
        包括：清空画布、画食物、画蛇身
        """
        # delete("all") 清除画布上所有内容，避免旧帧残留
        self.canvas.delete("all")

        # ===================== 绘制食物 =====================
        fx, fy = self.food  # 解包食物坐标
        self.draw_cell(fx, fy, "red")  # 用红色画食物所在格子

        # ===================== 绘制蛇 =====================
        # 遍历蛇身每个格子，第一个格子是蛇头，颜色更亮
        for i, (x, y) in enumerate(self.snake):
            if i == 0:
                color = "lime"   # 蛇头用亮绿色
            else:
                color = "green"  # 蛇身用深绿色
            self.draw_cell(x, y, color)

    def draw_cell(self, x, y, color):
        """
        在画布上绘制一个格子（正方形）
        x, y: 格子的列号和行号
        color: 填充颜色
        """
        # 将格子坐标转换为像素坐标
        x1 = x * self.cell_size           # 左上角 x
        y1 = y * self.cell_size           # 左上角 y
        x2 = x1 + self.cell_size          # 右下角 x
        y2 = y1 + self.cell_size          # 右下角 y

        # create_rectangle 画矩形，fill 是填充色，outline 是边框色
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")

    def on_key(self, event):
        """
        键盘事件处理函数
        event: tkinter 传入的事件对象，包含按键信息
        """
        key = event.keysym  # 获取按键名称，例如 "Up"、"Left"、"space" 等

        # ===================== 方向控制 =====================
        # opposites 字典记录每个方向的反方向，防止蛇直接掉头（比如正在向右时不能直接向左）
        opposites = {
            "Up": "Down", "Down": "Up",
            "Left": "Right", "Right": "Left",
            "w": "Down", "s": "Up",
            "a": "Right", "d": "Left",
        }

        # direction_map 将各种按键映射到统一的方向名称
        direction_map = {
            "Up": "Up", "Down": "Down", "Left": "Left", "Right": "Right",
            "w": "Up", "s": "Down", "a": "Left", "d": "Right",
            "W": "Up", "S": "Down", "A": "Left", "D": "Right",
        }

        # 如果按下的是方向键或 WASD
        if key in direction_map:
            new_dir = direction_map[key]  # 得到对应方向
            # 只有当新方向不是当前方向的反方向时才允许转向
            if new_dir != opposites.get(self.direction):
                self.next_direction = new_dir

        # ===================== 空格键：暂停 / 继续 / 重新开始 =====================
        if key == "space":
            if self.game_over:
                # 如果游戏已结束，按空格重新开始
                self.init_game()
            else:
                # 否则切换暂停和继续状态
                self.running = not self.running
                if self.running:
                    # 如果是从暂停恢复，继续移动
                    self.schedule_next_move()

        # ===================== R 键：游戏结束后重新开始 =====================
        if key.lower() == "r" and self.game_over:
            self.init_game()

        # ===================== ESC 键：退出游戏 =====================
        if key == "Escape":
            self.master.quit()

    def schedule_next_move(self):
        """
        使用 after 方法安排下一次移动
        after(时间, 函数) 表示多少毫秒后调用指定函数
        """
        if self.running:
            # self.speed 毫秒后调用 self.move
            self.job_id = self.master.after(self.speed, self.move)

    def move(self):
        """
        蛇移动一次的核心逻辑
        包括：转向、计算新蛇头、碰撞检测、吃食物、重绘画面
        """
        # 如果游戏暂停或结束，就不执行移动
        if not self.running or self.game_over:
            return

        # 更新当前方向为下一帧要移动的方向
        self.direction = self.next_direction

        # 获取当前蛇头坐标
        head_x, head_y = self.snake[0]

        # 根据方向计算蛇头的位移量
        dx, dy = {
            "Up": (0, -1),      # 向上：行减 1
            "Down": (0, 1),     # 向下：行加 1
            "Left": (-1, 0),    # 向左：列减 1
            "Right": (1, 0),    # 向右：列加 1
        }[self.direction]

        # 计算新的蛇头位置
        new_head = (head_x + dx, head_y + dy)

        # ===================== 撞墙检测 =====================
        # 如果新蛇头超出画布范围，则游戏结束
        if (
            new_head[0] < 0              # 左边超出
            or new_head[0] >= self.cols  # 右边超出
            or new_head[1] < 0           # 上边超出
            or new_head[1] >= self.rows  # 下边超出
        ):
            self.end_game()
            return

        # ===================== 撞到自己检测 =====================
        # 如果新蛇头位置已经在蛇身列表中，说明撞到自己的身体
        if new_head in self.snake:
            self.end_game()
            return

        # 将新蛇头插入到蛇身最前面
        self.snake.insert(0, new_head)

        # ===================== 吃食物检测 =====================
        if new_head == self.food:
            # 吃到食物，分数加 10
            self.score += 10
            # 更新分数标签显示
            self.score_label.config(text=f"分数: {self.score}")
            # 生成新的食物
            self.food = self.spawn_food()
            # 注意：这里不删除蛇尾，所以蛇身长度 +1
        else:
            # 没吃到食物，删除蛇尾，保持长度不变
            self.snake.pop()

        # 重新绘制画面
        self.draw()

        # 安排下一次移动
        self.schedule_next_move()

    def end_game(self):
        """
        游戏结束处理
        停止游戏并在画布上显示结束信息
        """
        self.game_over = True   # 标记游戏结束
        self.running = False    # 停止移动

        # 在画布中央显示 "游戏结束"
        self.canvas.create_text(
            self.width // 2,           # 文字中心 x 坐标
            self.height // 2 - 20,     # 文字中心 y 坐标（偏上）
            text="游戏结束",
            fill="white",              # 文字颜色：白色
            font=("Microsoft YaHei", 30),  # 字体和大小
        )

        # 在画布中央显示最终分数和提示信息
        self.canvas.create_text(
            self.width // 2,
            self.height // 2 + 30,     # 文字中心 y 坐标（偏下）
            text=f"最终分数: {self.score}  按 R 或空格重新开始",
            fill="white",
            font=("Microsoft YaHei", 14),
        )


def main():
    """
    程序入口函数
    创建 tkinter 主窗口并启动游戏
    """
    root = tk.Tk()       # 创建 tkinter 根窗口
    game = SnakeGame(root)  # 创建游戏实例
    root.mainloop()      # 进入 tkinter 主循环，等待用户交互


# 当直接运行本文件时执行 main()
# 当作为模块被导入时不会自动执行
if __name__ == "__main__":
    main()
