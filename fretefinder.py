from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
from tkinter import *
import tkinter.font as tkFont
from tkinter import messagebox
import ctypes
import threading
import psycopg2
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=options)
driver.maximize_window()
service = Service(ChromeDriverManager().install())

url = None
addl = None
att = None
run = False

def connect_db():
    conn = psycopg2.connect(
        dbname="dbnamehere",
        user="postgres",
        password="passhere",
        host="localhost",
        port="5432"
    )
    return conn

conn = connect_db()
cursor = conn.cursor()
cursor.execute("""
            CREATE TABLE IF NOT EXISTS ignoredCompanies (
               id INTEGER,
               name VARCHAR(128)
            )
        """)
cursor.execute("""
            CREATE TABLE IF NOT EXISTS login (
                id SERIAL PRIMARY KEY,
                cpf VARCHAR(128) UNIQUE NOT NULL,
                senha VARCHAR(128) NOT NULL,
                UNIQUE (cpf, senha)
            );
        """)
cursor.execute("""
            INSERT INTO login (cpf, senha)
            VALUES ('cpfhere', 'passhere')
            ON CONFLICT (cpf) DO NOTHING;
        """)
conn.commit()
cursor.close()
conn.close()

def flash_window(window_handle):
    FLASHW_TRAY = 0x00000002
    FLASHW_TIMERNOFG = 0x0000000C

    class FLASHWINFO(ctypes.Structure):
        _fields_ = [('cbSize', ctypes.c_uint),
                    ('hwnd', ctypes.c_void_p),
                    ('dwFlags', ctypes.c_uint),
                    ('uCount', ctypes.c_uint),
                    ('dwTimeout', ctypes.c_uint)]

    flash_info = FLASHWINFO(
        ctypes.sizeof(FLASHWINFO),
        window_handle,
        FLASHW_TRAY | FLASHW_TIMERNOFG,
        5,
        0
    )

    ctypes.windll.user32.FlashWindowEx(ctypes.byref(flash_info))

def atualizarLink():
    global run
    url = addl.get()
    taxa = int(att.get())
    atual = None
    logado = 0
    run = True #começa a rodar
    while run:
        driver.get(url)
        #logar
        if logado == 0:
            if mk.get() != 'femv271503':
                wrongpass = Tk()
                wrongpass.after(1000, lambda: win.focus_force())
                wrongpass.title('Erro')
                wrongpass.attributes('-topmost', True)
                wrongpass.geometry("200x100")
                wrongpass.eval('tk::PlaceWindow . center')
                Label(wrongpass).grid(column=0, row=0, sticky=W, padx=15, pady=5)
                label = Label(wrongpass, text='Senha Incorreta', font=("Arial", 17), anchor='center')
                label.grid(row=1, column=0, padx=10, pady=5, sticky='n')
                label = tkFont.Font(size=15)
                wrongpass.mainloop()
                break
            elif mk.get() == 'femv271503':
                conn = connect_db()
                cursor = conn.cursor()
                cursor.execute("SELECT cpf, senha FROM login")
                acesso = cursor.fetchall()
                for row in acesso:
                    cpfGet, senhaGet = row
                    print(f"CPF: {cpfGet}, Senha: {senhaGet}")
                cpf = cpfGet
                senha = senhaGet
                cursor.close()
                conn.close()
            driver.find_element('xpath', '/html/body/div[2]/main/header/fuel-grid-container/fuel-grid-item/div/div/a[2]/fuel-button').click()
            time.sleep(2)
            driver.find_element('xpath', '/html/body/div[10]/div[2]/div/div/div[3]/button').click() #fechar cookies
            time.sleep(1)
            driver.find_element('xpath', '/html/body/main/div/div/ul/li[1]/a').click()
            time.sleep(2)
            driver.find_element('xpath', '/html/body/div[2]/div[2]/div/form/div/input').send_keys(cpf)
            driver.find_element('xpath', '/html/body/div[2]/div[2]/div/form/button').click()
            time.sleep(2)
            driver.find_element('xpath', '/html/body/div[2]/div[2]/div/form/div/input').send_keys(senha)
            driver.find_element('xpath', '/html/body/div[2]/div[2]/div/form/button[1]').click()
            time.sleep(5)
            driver.get(url)
            logado += 1
            #end logar
        time.sleep(taxa) 
        try:
            driver.find_element('xpath', '//*[@id="__next"]/main/div/fuel-grid-container/fuel-grid-item[2]/main/fuel-grid-item/div/a[1]/section/div[1]/p').text == 'Patrocinado'
            link = 2
        except:
            pass
        try:
            driver.find_element('xpath', '//*[@id="__next"]/main/div/fuel-grid-container/fuel-grid-item[2]/main/fuel-grid-item/div/a[2]/section/div[1]/p').text == 'Patrocinado'
            link = 3
        except:
            pass
        try:
            driver.find_element('xpath', '//*[@id="__next"]/main/div/fuel-grid-container/fuel-grid-item[2]/main/fuel-grid-item/div/a[3]/section/div[1]/p').text == 'Patrocinado'
            link = 4
        except:
            pass
        try:
            driver.find_element('xpath', '//*[@id="__next"]/main/div/fuel-grid-container/fuel-grid-item[2]/main/fuel-grid-item/div/a[4]/section/div[1]/p').text == 'Patrocinado'
            link = 5
        except:
            pass
        try:
            if driver.find_element('xpath', '/html/body/div/main/div/fuel-grid-container/fuel-grid-item[2]/main/fuel-grid-item/div/div[1]/p/fuel-typography[1]/p').text == 'Nenhum resultado encontrado! ☹️':
                time.sleep(taxa) 
                driver.get(url)
                continue
        except:
            pass
        try:
            driver.find_element('xpath', f'//*[@id="__next"]/main/div/fuel-grid-container/fuel-grid-item[2]/main/fuel-grid-item/div/a[{link}]/section').click()
        except:
            driver.find_element('xpath', f'//*[@id="__next"]/main/div/fuel-grid-container/fuel-grid-item[2]/main/fuel-grid-item/div/a[1]/section').click()

        get_url = driver.current_url
        #id = driver.current_window_handle
        if atual is None:
            atual = get_url
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM ignoredCompanies")
            ignored_companies = [row[0] for row in cursor.fetchall()]
            print(ignored_companies)
            cursor.close()
            conn.close()
        except:
            print("Falha ao recuperar lista de ignorados")
        for ignored in ignored_companies:
            if ignored in atual:
                print(f"Found ignored company '{ignored}' in '{atual}'")
                driver.execute_script("window.history.go(-1)")
            elif atual == get_url:
                driver.execute_script("window.history.go(-1)")
            else:
                end = Tk()
                end.after(1000, lambda: win.focus_force())
                end.title('Frete Finder')
                end.attributes('-topmost', True)
                end.geometry("450x250")
                end.eval('tk::PlaceWindow . center')
                #end.iconbitmap('truck.ico')
                Label(end).grid(column=0, row=0, sticky=W, padx=15, pady=5)
                label = tkFont.Font(size=28)
                label = Label(end, text="Novo Frete Encontrado!",font=("Arial", 20))
                label.place(anchor=CENTER, relx=0.5, rely=0.5)
                window_handle = end.winfo_id()
                flash_window(window_handle)
                end.mainloop()
            break

def repetir():
    global run
    url = addl.get()
    taxa = int(att.get())
    atual = None
    run = True #começa a rodar
    while run:
        driver.get(url)
        time.sleep(taxa)
        try:
            driver.find_element('xpath', '//*[@id="__next"]/main/div/fuel-grid-container/fuel-grid-item[2]/main/fuel-grid-item/div/a[1]/section/div[1]/p').text == 'Patrocinado'
            link = 2
        except:
            pass
        try:
            driver.find_element('xpath', '//*[@id="__next"]/main/div/fuel-grid-container/fuel-grid-item[2]/main/fuel-grid-item/div/a[2]/section/div[1]/p').text == 'Patrocinado'
            link = 3
        except:
            pass
        try:
            driver.find_element('xpath', '//*[@id="__next"]/main/div/fuel-grid-container/fuel-grid-item[2]/main/fuel-grid-item/div/a[3]/section/div[1]/p').text == 'Patrocinado'
            link = 4
        except:
            pass
        try:
            driver.find_element('xpath', '//*[@id="__next"]/main/div/fuel-grid-container/fuel-grid-item[2]/main/fuel-grid-item/div/a[4]/section/div[1]/p').text == 'Patrocinado'
            link = 5
        except:
            pass
        try:
            if driver.find_element('xpath', '/html/body/div/main/div/fuel-grid-container/fuel-grid-item[2]/main/fuel-grid-item/div/div[1]/p/fuel-typography[1]/p').text == 'Nenhum resultado encontrado! ☹️':
                time.sleep(taxa) 
                driver.get(url)
                continue
        except:
            pass
        try:
            driver.find_element('xpath', f'//*[@id="__next"]/main/div/fuel-grid-container/fuel-grid-item[2]/main/fuel-grid-item/div/a[{link}]/section').click()
        except:
            driver.find_element('xpath', f'//*[@id="__next"]/main/div/fuel-grid-container/fuel-grid-item[2]/main/fuel-grid-item/div/a[1]/section').click()

        get_url = driver.current_url
        #id = driver.current_window_handle
        if atual is None:
            atual = get_url
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM ignoredCompanies")
            ignored_companies = [row[0] for row in cursor.fetchall()]
            print(ignored_companies)
            cursor.close()
            conn.close()
        except:
            print("Falha ao recuperar lista de ignorados")
        for ignored in ignored_companies:
            if ignored in atual:
                print(f"Found ignored company '{ignored}' in '{atual}'")
                driver.execute_script("window.history.go(-1)")
            elif atual == get_url:
                driver.execute_script("window.history.go(-1)")
            else:
                end = Tk()
                end.after(1000, lambda: win.focus_force())
                end.title('Frete Finder')
                end.attributes('-topmost', True)
                end.geometry("450x250")
                end.eval('tk::PlaceWindow . center')
                #end.iconbitmap('truck.ico')
                Label(end).grid(column=0, row=0, sticky=W, padx=15, pady=5)
                label = tkFont.Font(size=28)
                label = Label(end, text="Novo Frete Encontrado!",font=("Arial", 20))
                label.place(anchor=CENTER, relx=0.5, rely=0.5)
                window_handle = end.winfo_id()
                flash_window(window_handle)
                end.mainloop()
                break

def parar():
    global run
    run = False

def ignorar():
    conn = connect_db()
    cursor = conn.cursor()
    ignoradoIntermed = ignore.get()
    ignorado = ignoradoIntermed.replace(' ', '-').lower()
    print(ignorado)
    cursor.execute("INSERT INTO ignoredCompanies (name) VALUES (%s)", (ignorado,))
    conn.commit()
    cursor.close()
    conn.close()

def showIgn():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ignoredCompanies")
    lista = cursor.fetchall()
    cursor.close()
    conn.close()
    show = Tk()
    show.after(1000, lambda: win.focus_force())
    show.title('Lista de Ignorados')
    show.geometry("300x200")
    show.eval('tk::PlaceWindow . center')
    Label(show).grid(column=0, row=0, sticky=W, padx=15, pady=5)
    label = tkFont.Font(size=15)
    for idx, row in enumerate(lista):
            modified_text = row[1].replace('-', ' ').title()
            label = Label(show, text=modified_text, font=("Arial", 10), anchor='w')
            label.grid(row=idx, column=0, padx=10, pady=5, sticky='w')
    show.mainloop()
    return lista

win = Tk()
win.after(1000, lambda: win.focus_force())
win.title('Frete Finder')
win.attributes('-topmost', False)
win.geometry("620x150")
win.eval('tk::PlaceWindow . center')
#win.iconbitmap('truck.ico')

Label(win, text='Master Key:').grid(column=1, row=0, sticky=W, padx=5, pady=5)
mk = Entry(win, show="*")
mk.grid(column=2, row=0, sticky=W, padx=5, pady=5)
# Label(win, text='CPF:').grid(column=0, row=1, sticky=W, padx=5, pady=5)
# cpf = Entry(win)
# cpf.grid(column=1, row=1, sticky=W, padx=5, pady=5)
# Label(win, text='Senha:').grid(column=0, row=2, sticky=W, padx=5, pady=5)
# senha = Entry(win, show="*")
# senha.grid(column=1, row=2, sticky=W, padx=5, pady=5)
Label(win, text='Novo Ignorado:').grid(column=0, row=0, sticky=W, padx=5, pady=5)
ignore = Entry(win, width=25)
ignore.grid(column=0, row=1, sticky=W, padx=5, pady=5)
Label(win, text='Insira o link:').grid(column=1, row=1, sticky=W, padx=5, pady=5)
addl = Entry(win, width=45)
addl.grid(column=2, row=1, sticky=W, padx=5, pady=5)
Label(win, text='Insira a taxa de atualização\n(em segundos):').grid(column=1, row=2, sticky=W, padx=5, pady=5)
att = Entry(win, width=5)
att.grid(column=2, row=2, sticky=W, padx=5, pady=5)
Button(win, text='Ignorar', command=lambda: threading.Thread(target=ignorar).start()).grid(column=0, row=2, sticky=W, padx=5, pady=5)
Button(win, text='Mostrar Ignorados', command=lambda: threading.Thread(target=showIgn).start()).grid(column=0, row=3, sticky=W, padx=5, pady=5)
Button(win, text='Procurar', command=lambda: threading.Thread(target=atualizarLink).start()).grid(column=1, row=3, sticky=E, padx=5, pady=5)
Button(win, text='Buscar Novamente', command=lambda: threading.Thread(target=repetir).start()).grid(column=2, row=3, sticky=W, padx=5, pady=5)
Button(win, text='Parar Busca', command=parar).grid(column=2, row=3, sticky=E, padx=5, pady=5)
win.mainloop()
