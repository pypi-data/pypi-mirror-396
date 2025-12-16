import os
import platform

__all__ = ['clear_screen']


def clear_screen():
    """운영체제에 맞춰 화면을 지우는 함수"""
    # Windows 운영체제인 경우
    if platform.system() == 'Windows':
        os.system('cls')
    # Windows가 아닌 경우 (macOS, Linux 등)
    else:
        os.system('clear')
