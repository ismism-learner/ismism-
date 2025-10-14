# game/main.py
"""
游戏主入口
"""
from engine import GameEngine

def main():
    """主函数，启动游戏"""
    engine = GameEngine()
    engine.run()
    print("游戏结束。")

if __name__ == "__main__":
    main()