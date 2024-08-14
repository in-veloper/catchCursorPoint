from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QMessageBox
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
import pyautogui
import pyperclip
import os
from pynput import keyboard
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time

class KeyboardListenerThread(QThread):
    key_pressed = pyqtSignal(object)

    def run(self):
        def on_press(key):
            self.key_pressed.emit(key)
        
        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.listener_thread = KeyboardListenerThread()
        self.listener_thread.key_pressed.connect(self.handle_key_press)
        self.listener_thread.start()

    def initUI(self):
        self.setWindowTitle("Catch Cursor Point")
        screen_width, screen_height = pyautogui.size()

        window_width = 500
        window_height = 350
        x_position = screen_width - window_width
        y_position = (screen_height - window_height) // 2

        self.setGeometry(x_position, y_position, window_width, window_height)
        self.setStyleSheet("background-color: #f0f0f0;")

        self.layout = QVBoxLayout()

        self.userId_frame = QFrame(self)
        self.userId_label = QLabel("ID : ", self.userId_frame)
        self.userId_label.setStyleSheet("color: black;")
        self.userId_entry = QLineEdit(self.userId_frame)
        self.userId_entry.setStyleSheet("color: black; background-color: white;")
        self.layout.addWidget(self.userId_label)
        self.layout.addWidget(self.userId_entry)

        self.password_frame = QFrame(self)
        self.password_label = QLabel("PW : ", self.password_frame)
        self.password_label.setStyleSheet("color: black;")
        self.password_entry = QLineEdit(self.password_frame)
        self.password_entry.setEchoMode(QLineEdit.Password)
        self.password_entry.setStyleSheet("color: black; background-color: white;")
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_entry)

        self.browser_button = QPushButton("브라우저 열기", self)
        self.browser_button.setStyleSheet("color: white; background-color: gray;")
        self.browser_button.clicked.connect(self.launch_browser)
        self.layout.addWidget(self.browser_button)

        self.info_label = QLabel(
            "F1 : 도움말 닫기 버튼\nF2 : 제목 입력 창\nF3 : 내용 입력 창\nF4 : 우측 상단 발행 버튼\nF5 : 최종 발행 버튼",
            self)
        self.info_label.setStyleSheet("border: 2px groove; background-color: white; color: black;")
        self.layout.addWidget(self.info_label)

        self.position_label = QLabel("현재 마우스 위치 : ", self)
        self.position_label.setStyleSheet("border: 2px groove; background-color: white; color: black;")
        self.layout.addWidget(self.position_label)

        self.reset_button = QPushButton("Reset", self)
        self.reset_button.setStyleSheet("color: white; background-color: gray;")
        self.reset_button.clicked.connect(self.reset_data)
        self.close_button = QPushButton("Close", self)
        self.close_button.setStyleSheet("color: white; background-color: gray;")
        self.close_button.clicked.connect(self.close_app)
        self.layout.addWidget(self.reset_button)
        self.layout.addWidget(self.close_button)

        self.setLayout(self.layout)
        self.update_mouse_position()

    def handle_key_press(self, key):
        try:
            if key == keyboard.Key.f1:
                label = "existWrite"
            elif key == keyboard.Key.f2:
                label = "helpExit"
            elif key == keyboard.Key.f3:
                label = "title"
            elif key == keyboard.Key.f4:
                label = "content"
            elif key == keyboard.Key.f5:
                label = "publish"
            elif key == keyboard.Key.f6:
                label = "realPublish"
            else:
                return

            x, y = pyautogui.position()
            self.save_coordinates(x, y, label)
        except Exception as e:
            print(f"Error: {e}")

    def launch_browser(self):
        driver = webdriver.Chrome()
        driver.get('https://section.blog.naver.com/BlogHome.naver?directoryNo=0&currentPage=1&groupId=0')
        try:
            start_button = driver.find_element(By.XPATH, '//*[@id="container"]/div/aside/div/div[1]/div[1]/div/a')
            start_button.click()
            time.sleep(2)
            userId = self.userId_entry.text()
            userId_field = driver.find_element(By.XPATH, '//*[@id="id"]')
            userId_field.click()
            pyperclip.copy(userId)
            pyautogui.keyDown("command")
            pyautogui.press("v")
            pyautogui.keyUp("command")
            time.sleep(2)
            password = self.password_entry.text()
            password_field = driver.find_element(By.XPATH, '//*[@id="pw"]')
            password_field.click()
            pyperclip.copy(password)
            pyautogui.keyDown("command")
            pyautogui.press("v")
            pyautogui.keyUp("command")
            password_field.send_keys(Keys.RETURN)
            time.sleep(3)
            write_button = driver.find_element(By.XPATH, '//*[@id="container"]/div/aside/div/div[1]/nav/a[2]')
            action = ActionChains(driver)
            action.move_to_element(write_button).click().perform()
            input("마우스 커서를 움직여 좌표를 확인하세요")
        finally:
            driver.quit()

    def reset_data(self):
        file_path = os.path.join(get_data_directory(), 'naver_coordinate.txt')
        if os.path.exists(file_path):
            os.remove(file_path)
        QMessageBox.information(self, "데이터 리셋", "저장된 데이터가 초기화되었습니다.")

    def update_mouse_position(self):
        x, y = pyautogui.position()
        self.position_label.setText(f"현재 마우스 위치 [ X : {x}, Y : {y} ]")
        QTimer.singleShot(100, self.update_mouse_position)

    def close_app(self):
        self.close()

    def save_coordinates(self, x, y, label):
        file_path = os.path.join(get_data_directory(), 'naver_coordinate.txt')
        with open(file_path, "a") as file:
            file.write(f"{label}: {x}, {y}\n")
        QMessageBox.information(self, "정보", f"{label} 위치 좌표가 저장되었습니다.")

def get_data_directory():
    home_dir = os.path.expanduser('~')
    data_dir = os.path.join(home_dir, 'capdata')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir

if __name__ == '__main__':
    app = QApplication([])
    window = MyWindow()
    window.show()
    app.exec_()
