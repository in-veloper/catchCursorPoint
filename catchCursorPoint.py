import tkinter as tk
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller
from selenium.webdriver.common.action_chains import ActionChains
from pynput import keyboard
import pyautogui
import pyperclip
import time
import ssl
import os
from threading import Thread

ssl._create_default_https_context = ssl._create_unverified_context
chromedriver_autoinstaller.install()

def get_data_directory():
    home_dir = os.path.expanduser('~')
    data_dir = os.path.join(home_dir, 'capdata')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir

def save_coordinates(x, y, label):
    file_path = os.path.join(get_data_directory(), 'naver_coordinate.txt')
    with open(file_path, "a") as file:
        file.write(f"{label}: {x}, {y}\n")
    messagebox.showinfo("Position Saved", f"Mouse position saved: ({x}, {y})")

def on_press(key):
    try:
        if key == keyboard.Key.f3:
            label = "helpExit"
            x,y = pyautogui.position()
            save_coordinates(x,y,label)
        if key == keyboard.Key.f2:
            label = "title"
            x,y = pyautogui.position()
            save_coordinates(x,y,label)
        if key == keyboard.Key.f3:
            label = "content"
            x,y = pyautogui.position()
            save_coordinates(x,y,label)
        if key == keyboard.Key.f4:
            label = "publish"
            x,y = pyautogui.position()
            save_coordinates(x,y,label)
        if key == keyboard.Key.f5:
            label = "realPublish"
            x,y = pyautogui.position()
            save_coordinates(x,y,label)
    except Exception as e:
        print(f"Error: {e}")

def start_listening():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

def run_listener():
    listener_thread = Thread(target=start_listening, daemon=True)
    listener_thread.start()

def reset_data():
    file_path = os.path.join(get_data_directory(), 'naver_coordinate.txt')
    if os.path.exists(file_path):
        os.remove(file_path)  # 파일 삭제
    messagebox.showinfo("데이터 리셋", "저장된 데이터가 초기화되었습니다.")

def update_mouse_position():
    x, y = pyautogui.position()
    position_label.config(text=f"현재 마우스 위치 [ X : {x}, Y : {y} ]")
    root.after(100, update_mouse_position)

def launch_browser():
    global driver
    driver = webdriver.Chrome()
    driver.get('https://section.blog.naver.com/BlogHome.naver?directoryNo=0&currentPage=1&groupId=0')
    
    try:
        start_button = driver.find_element(By.XPATH, '//*[@id="container"]/div/aside/div/div[1]/div[1]/div/a')
        start_button.click()

        time.sleep(2)

        # 로그인 정보 입력
        username = driver.find_element(By.XPATH, '//*[@id="id"]')
        username.click()
        pyperclip.copy("jyy9961")
        pyautogui.keyDown("command")
        pyautogui.press("v")
        pyautogui.keyUp("command")
        time.sleep(2)

        password = driver.find_element(By.XPATH, '//*[@id="pw"]')
        password.click()
        pyperclip.copy("yeeh01250412!@")
        pyautogui.keyDown("command")
        pyautogui.press("v")
        pyautogui.keyUp("command")

        password.send_keys(Keys.RETURN)

        write_button = driver.find_element(By.XPATH, '//*[@id="container"]/div/aside/div/div[1]/nav/a[2]')
        action = ActionChains(driver)
        action.move_to_element(write_button).click().perform()

        input("마우스 커서를 움직여 좌표를 확인하세요")
    finally:
        driver.quit()

# GUI 설정
root = tk.Tk()
root.title("Catch Cursor Point")

# 화면 해상도 얻기
screen_width, screen_height = pyautogui.size()

# 창 크기 설정 및 화면 우측에 위치
window_width = 500  # 창의 너비
window_height = 300  # 창의 높이
x_position = screen_width - window_width  # 화면 우측에 창 위치
y_position = (screen_height - window_height) // 2  # 화면 중앙 높이에 위치

# geometry 설정: "너비x높이+x+y"
root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

# 키 입력 Listener는 Thread로 가동
run_listener()

info_label = tk.Label(root, 
                      text="F1 : 도움말 닫기 버튼\nF2 : 제목 입력 창\nF3 : 내용 입력 창\nF4 : 우측 상단 발행 버튼\nF5 : 최종 발행 버튼",
                      borderwidth=2,
                      relief="groove",
                      bg="white",
                      anchor="w",
                      justify="left",
                      padx=20,
                      pady=20)
info_label.pack(padx=10, pady=10)

position_label = tk.Label(root, 
                          text="현재 마우스 위치 : ",
                          borderwidth=2,
                          relief="groove",
                          bg="white",
                          anchor="center",
                          padx=20,
                          pady=10)
position_label.pack(padx=10, pady=10)

browser_button = tk.Button(root, text="브라우저 열기", command=launch_browser)
browser_button.pack()

def close_app():
    root.destroy()

button_frame = tk.Frame(root)
reset_button = tk.Button(button_frame, text="Reset", command=reset_data)
reset_button.pack(side=tk.LEFT, padx=5)

close_button = tk.Button(button_frame, text="Close", command=close_app)
close_button.pack(side=tk.RIGHT, padx=5)

button_frame.pack(pady=10)


update_mouse_position()

root.mainloop()