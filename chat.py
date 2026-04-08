import customtkinter as ctk
import threading
import time
import random
import os
from googletrans import Translator
import google.generativeai as genai
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import webbrowser
from tkinter import messagebox



# ССЫЛКИ НА ТВОЙ ГИТХАБ (ЗАМЕНИ НА СВОИ!)
# 1. Ссылка на файл с версией (Raw-версия)
VERSION_URL = "https://raw.githubusercontent.com/byGAR1K/MatchClub-Manager/main/version.txt"
# 2. Ссылка на страницу, где лежат файлы для скачивания
RELEASE_URL = "https://github.com/byGAR1K/MatchClub-Manager/releases"
# 3. Текущая версия программы внутри кода
CURRENT_VERSION = "1.0.1"


def check_for_updates(root_element):
    try:
        # Запрос к файлу на GitHub
        response = requests.get(VERSION_URL, timeout=5)
        if response.status_code == 200:
            latest_version = response.text.strip()
            
            if latest_version != CURRENT_VERSION:
                ans = messagebox.askyesno("Обновление", 
                    f"Доступна новая версия: {latest_version}\nУ вас: {CURRENT_VERSION}\n\nПерейти к скачиванию?")
                if ans:
                    webbrowser.open(RELEASE_URL)
                    root_element.destroy() # Закрываем старую прогу
                    return True
    except Exception as e:
        print(f"Ошибка проверки обновлений: {e}")
    return False


# --- Настройки темы ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class TelegramBotApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        
        # Проверка обновлений при запуске
        if check_for_updates(self):
            return 
            
        self.title(f"MatchClub Manager v{CURRENT_VERSION}")
        
        self.title("MatchClub Manager Pro Max")
        self.geometry("950x700")
        self.minsize(900, 650)
        self.is_running = False
        self.history_file = "sent_users.txt"
        self.translator = Translator()

        # --- НАСТРОЙКА СЕТКИ (Боковое меню + Основная часть) ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ==================== БОКОВОЕ МЕНЮ ====================
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="MatchClub\nAutoBot", font=ctk.CTkFont(size=22, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 30))

        # Кнопки меню
        self.btn_bot = ctk.CTkButton(self.sidebar_frame, text="🤖 Управление ботом", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), anchor="w", command=lambda: self.select_frame("bot"))
        self.btn_bot.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.btn_trans = ctk.CTkButton(self.sidebar_frame, text="🌍 Переводчик", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), anchor="w", command=lambda: self.select_frame("trans"))
        self.btn_trans.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.btn_ai = ctk.CTkButton(self.sidebar_frame, text="🧠 ИИ Ассистент", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), anchor="w", command=lambda: self.select_frame("ai"))
        self.btn_ai.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.status_label = ctk.CTkLabel(self.sidebar_frame, text="Статус: Остановлен", text_color="#E76060", font=ctk.CTkFont(weight="bold"))
        self.status_label.grid(row=6, column=0, padx=20, pady=20, sticky="s")

        # ==================== ОСНОВНЫЕ ФРЕЙМЫ ====================
        self.bot_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.trans_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.ai_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")

        # Инициализация интерфейсов
        self.setup_bot_frame()
        self.setup_trans_frame()
        self.setup_ai_frame()

        # Выбираем первый фрейм по умолчанию
        self.select_frame("bot")

    def select_frame(self, name):
        # Подсветка активной кнопки
        self.btn_bot.configure(fg_color=("gray75", "gray25") if name == "bot" else "transparent")
        self.btn_trans.configure(fg_color=("gray75", "gray25") if name == "trans" else "transparent")
        self.btn_ai.configure(fg_color=("gray75", "gray25") if name == "ai" else "transparent")

        # Отображение фреймов
        if name == "bot":
            self.bot_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.bot_frame.grid_forget()

        if name == "trans":
            self.trans_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.trans_frame.grid_forget()

        if name == "ai":
            self.ai_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.ai_frame.grid_forget()

    # ==================== UI: БОТ ====================
    def setup_bot_frame(self):
        self.bot_frame.grid_columnconfigure(0, weight=1)
        self.bot_frame.grid_columnconfigure(1, weight=1)

        # Карточка 1: Аккаунт
        account_frame = ctk.CTkFrame(self.bot_frame)
        account_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="ew")
        
        ctk.CTkLabel(account_frame, text="Данные входа", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5), anchor="w", padx=20)
        self.login_entry = ctk.CTkEntry(account_frame, placeholder_text="Логин", width=300)
        self.login_entry.insert(0, "0426.m.hr13.01@f4d.com")
        self.login_entry.pack(side="left", padx=20, pady=10, fill="x", expand=True)
        
        self.pass_entry = ctk.CTkEntry(account_frame, placeholder_text="Пароль", show="*", width=300)
        self.pass_entry.insert(0, "FGVF[po][p")
        self.pass_entry.pack(side="left", padx=20, pady=10, fill="x", expand=True)

        # Карточка 2: Сообщение и фильтры
        msg_frame = ctk.CTkFrame(self.bot_frame)
        msg_frame.grid(row=1, column=0, padx=(20, 10), pady=10, sticky="nsew")
        
        ctk.CTkLabel(msg_frame, text="Текст рассылки", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5), anchor="w", padx=20)
        self.msg_textbox = ctk.CTkTextbox(msg_frame, height=100)
        self.msg_textbox.insert("0.0", "I have one personal question, would you dare to say yes?")
        self.msg_textbox.pack(padx=20, pady=10, fill="both", expand=True)

        self.auto_send_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(msg_frame, text="Авто-отправка (Enter)", variable=self.auto_send_var).pack(pady=5, anchor="w", padx=20)
        self.skip_first_var = ctk.BooleanVar(value=True) 
        ctk.CTkCheckBox(msg_frame, text="Пропускать '1st SMS'", variable=self.skip_first_var).pack(pady=5, anchor="w", padx=20)
        self.skip_paid_var = ctk.BooleanVar(value=True) 
        ctk.CTkCheckBox(msg_frame, text="Пропускать 'Paid'", variable=self.skip_paid_var).pack(pady=(5, 15), anchor="w", padx=20)

        # Карточка 3: Управление
        ctrl_frame = ctk.CTkFrame(self.bot_frame)
        ctrl_frame.grid(row=1, column=1, padx=(10, 20), pady=10, sticky="nsew")

        self.speed_label = ctk.CTkLabel(ctrl_frame, text="Задержка между чатами: 15 сек", font=ctk.CTkFont(weight="bold"))
        self.speed_label.pack(pady=(15, 5))
        self.speed_slider = ctk.CTkSlider(ctrl_frame, from_=1, to=60, number_of_steps=59, command=self.update_speed_label)
        self.speed_slider.set(15)
        self.speed_slider.pack(pady=5, padx=20, fill="x")

        self.start_button = ctk.CTkButton(ctrl_frame, text="🚀 ЗАПУСТИТЬ", height=40, fg_color="#28a745", hover_color="#218838", font=ctk.CTkFont(weight="bold"), command=self.start_thread)
        self.start_button.pack(pady=(20, 10), padx=20, fill="x")

        self.stop_button = ctk.CTkButton(ctrl_frame, text="🛑 ОСТАНОВИТЬ", height=40, fg_color="#E76060", hover_color="#C64D4D", command=self.stop_bot)
        self.stop_button.pack(pady=10, padx=20, fill="x")

        ctk.CTkButton(ctrl_frame, text="Сбросить историю отправки", fg_color="transparent", border_width=1, command=self.clear_history).pack(pady=10, padx=20, fill="x")

        # Консоль
        self.console = ctk.CTkTextbox(self.bot_frame, height=180, font=("Consolas", 13), fg_color="#1E1E1E", text_color="#00FF00")
        self.console.grid(row=2, column=0, columnspan=2, padx=20, pady=20, sticky="nsew")
        self.console.configure(state="disabled")

    # ==================== UI: ПЕРЕВОДЧИК ====================
    def setup_trans_frame(self):
        self.trans_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.trans_frame, text="Русский текст", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 5), anchor="w", padx=20)
        self.ru_text = ctk.CTkTextbox(self.trans_frame, height=180, font=ctk.CTkFont(size=14))
        self.ru_text.pack(padx=20, pady=5, fill="x")

        self.btn_translate = ctk.CTkButton(self.trans_frame, text="Перевести ➔", height=40, command=self.run_translation)
        self.btn_translate.pack(pady=15)

        ctk.CTkLabel(self.trans_frame, text="English Translation", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(5, 5), anchor="w", padx=20)
        self.en_text = ctk.CTkTextbox(self.trans_frame, height=180, font=ctk.CTkFont(size=14))
        self.en_text.pack(padx=20, pady=5, fill="x")

        self.btn_copy_trans = ctk.CTkButton(self.trans_frame, text="✅ Перенести в Бота", fg_color="#28a745", hover_color="#218838", height=40, command=lambda: self.copy_to_bot(self.en_text))
        self.btn_copy_trans.pack(pady=20)

    def run_translation(self):
        # Запускаем в потоке, чтобы интерфейс не вис
        threading.Thread(target=self._translate_process, daemon=True).start()

    def _translate_process(self):
        text = self.ru_text.get("0.0", "end").strip()
        if text:
            self.btn_translate.configure(text="Переводим...", state="disabled")
            try:
                res = self.translator.translate(text, src='ru', dest='en')
                self.en_text.delete("0.0", "end")
                self.en_text.insert("0.0", res.text)
            except Exception as e:
                self.en_text.insert("0.0", f"Ошибка: {e}")
            self.btn_translate.configure(text="Перевести ➔", state="normal")

    # ==================== UI: ИИ АССИСТЕНТ ====================
    def setup_ai_frame(self):
        self.ai_frame.grid_columnconfigure(0, weight=1)

        # Настройки API
        api_frame = ctk.CTkFrame(self.ai_frame)
        api_frame.pack(padx=20, pady=(20, 10), fill="x")
        
        ctk.CTkLabel(api_frame, text="Настройки ИИ (Gemini AI)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(10, 0))
        ctk.CTkLabel(
            api_frame, 
            text="Получи бесплатный ключ на aistudio.google.com и вставь сюда:", 
            text_color="gray",  # Цвет переехал сюда
            font=ctk.CTkFont(size=11)  # Здесь только размер и стиль
        ).pack(anchor="w", padx=20)
        
        self.api_key_entry = ctk.CTkEntry(api_frame, placeholder_text="Вставь API Key сюда...", show="*")
        self.api_key_entry.pack(padx=20, pady=10, fill="x")

        # Ввод
        ctk.CTkLabel(self.ai_frame, text="Сообщение от собеседника:", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 5), anchor="w", padx=20)
        self.ai_input = ctk.CTkTextbox(self.ai_frame, height=100, font=ctk.CTkFont(size=14))
        self.ai_input.pack(padx=20, pady=5, fill="x")

        self.btn_generate = ctk.CTkButton(
            self.ai_frame, 
            text="✨ Сгенерировать классный ответ", 
            height=45, 
            fg_color="#8A2BE2", 
            hover_color="#7B68EE", 
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.run_ai
        )
        # Добавляем fill="x", чтобы кнопка растянулась и текст влез
        self.btn_generate.pack(pady=15, padx=20, fill="x")

        # Вывод
        ctk.CTkLabel(self.ai_frame, text="Варианты ответа (выбери лучший):", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(5, 5), anchor="w", padx=20)
        self.ai_output = ctk.CTkTextbox(self.ai_frame, height=200, font=ctk.CTkFont(size=14))
        self.ai_output.pack(padx=20, pady=5, fill="x")

        self.btn_copy_ai = ctk.CTkButton(self.ai_frame, text="✅ Перенести в Бота", fg_color="#28a745", hover_color="#218838", height=40, command=lambda: self.copy_to_bot(self.ai_output))
        self.btn_copy_ai.pack(pady=20)

    def run_ai(self):
        threading.Thread(target=self._ai_process, daemon=True).start()

    def _ai_process(self):
        api_key = self.api_key_entry.get().strip()
        user_msg = self.ai_input.get("0.0", "end").strip()

        if not api_key:
            self.ai_output.delete("0.0", "end")
            self.ai_output.insert("0.0", "⚠️ Ошибка: Введи API ключ Gemini в настройках выше!")
            return
        if not user_msg:
            return

        self.btn_generate.configure(text="Генерирую...", state="disabled")
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-3-flash-preview")
            prompt = f"Ты харизматичный парень на сайте знакомств. Девушка написала тебе: '{user_msg}'. Напиши 3 классных, игривых и оригинальных варианта ответа на английском языке. Без лишних вступлений, только сами варианты с цифрами."
            
            response = model.generate_content(prompt)
            self.ai_output.delete("0.0", "end")
            self.ai_output.insert("0.0", response.text)
        except Exception as e:
            self.ai_output.delete("0.0", "end")
            self.ai_output.insert("0.0", f"Ошибка ИИ: {e}")
        finally:
            self.btn_generate.configure(text="✨ Сгенерировать классный ответ", state="normal")

    def copy_to_bot(self, textbox):
        text = textbox.get("0.0", "end").strip()
        if text and not text.startswith("⚠️"):
            self.msg_textbox.delete("0.0", "end")
            self.msg_textbox.insert("0.0", text)
            self.select_frame("bot") # Перебрасываем обратно на вкладку бота

    # ==================== ЛОГИКА БОТА ====================
    def update_speed_label(self, value):
        self.speed_label.configure(text=f"Задержка между чатами: {int(value)} сек")

    def log(self, text):
        self.console.configure(state="normal")
        self.console.insert("end", f"[{time.strftime('%H:%M:%S')}] {text}\n")
        self.console.see("end")
        self.console.configure(state="disabled")

    def clear_history(self):
        if os.path.exists(self.history_file):
            os.remove(self.history_file)
        self.log("🧹 История написанных чатов очищена.")

    def stop_bot(self):
        self.is_running = False
        self.status_label.configure(text="Статус: Остановка...", text_color="#E76060")

    def start_thread(self):
        if not self.is_running:
            self.is_running = True
            self.start_button.configure(state="disabled")
            self.status_label.configure(text="Статус: В РАБОТЕ", text_color="#28a745")
            threading.Thread(target=self.run_bot, daemon=True).start()

    def run_bot(self):
        login = self.login_entry.get()
        password = self.pass_entry.get()
        message = self.msg_textbox.get("0.0", "end").strip()
        
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        driver = None
        try:
            driver = webdriver.Chrome(options=chrome_options)
            wait = WebDriverWait(driver, 15)
            driver.get("https://match-club.club/?returnUrl=%2Fchats%2F48742538%2Fmessages")
            
            wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(login)
            driver.find_element(By.ID, "password").send_keys(password)
            driver.find_element(By.CSS_SELECTOR, "button.login-matches-form__button").click()
            
            time.sleep(10)
            self.log("✅ Бот запущен. Начинаю бесконечный поиск...")

            while self.is_running:
                sent_ids = []
                if os.path.exists(self.history_file):
                    with open(self.history_file, "r") as f:
                        sent_ids = f.read().splitlines()

                chats = driver.find_elements(By.CLASS_NAME, "chat-list-item")
                found_new = False

                for chat in chats:
                    if not self.is_running: break
                    
                    try:
                        chat_id = chat.get_attribute("href") or chat.text.split('\n')[0]
                        if chat_id in sent_ids:
                            continue 
                        
                        labels_text = ""
                        try:
                            labels = chat.find_elements(By.CLASS_NAME, "avatar-with-info__label")
                            labels_text = " ".join([l.text for l in labels])
                        except: pass

                        if (self.skip_first_var.get() and "1st SMS" in labels_text) or \
                           (self.skip_paid_var.get() and "Paid" in labels_text):
                            continue

                        found_new = True
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", chat)
                        time.sleep(1)
                        driver.execute_script("arguments[0].click();", chat)
                        
                        self.log(f"📝 Работа с: {chat_id[:15]}...")
                        time.sleep(2)

                        input_field = wait.until(EC.element_to_be_clickable((By.NAME, "content")))
                        input_field.click()
                        input_field.send_keys(Keys.CONTROL + "a")
                        input_field.send_keys(Keys.BACKSPACE)
                        
                        for char in message:
                            input_field.send_keys(char)
                            time.sleep(random.uniform(0.01, 0.03))
                        
                        if self.auto_send_var.get():
                            input_field.send_keys(Keys.ENTER)
                            self.log("📤 Отправлено.")
                        
                        with open(self.history_file, "a") as f:
                            f.write(f"{chat_id}\n")

                        time.sleep(int(self.speed_slider.get()))

                    except Exception:
                        continue

                if not found_new:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    self.log("🔄 Новых чатов нет, скроллим вниз...")
                    time.sleep(3)
                
        except Exception as e:
            self.log(f"⚠️ Ошибка: {str(e)[:50]}")
        finally:
            self.is_running = False
            self.start_button.configure(state="normal")
            self.status_label.configure(text="Статус: Остановлен", text_color="#E76060")
            self.log("🔌 Остановлено.")

if __name__ == "__main__":
    app = TelegramBotApp()
    app.mainloop()