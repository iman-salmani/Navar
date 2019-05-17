#!/usr/bin/env python3
# In the name of Allah

import os
import time
import _thread
import glob
from subprocess import Popen, PIPE, call
import threading
import socket

import tkinter as tk
from tkinter import ttk

import locale

import cairo

from PIL import Image, ImageTk

from ewmh import EWMH

import arabic_reshaper

from bidi.algorithm import get_display

from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Key, Controller, Listener as KeyboardListener

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

gi.require_version('Rsvg', '2.0')
from gi.repository import Rsvg

class Main:
    def __init__(self):
        self.root = tk.Tk()

        self.height_root_window = 42

        self.rtl_langs = ('fa', 'ar')

        self.default_lang = locale.getdefaultlocale()[0][:2]

        if self.default_lang in self.rtl_langs:
            self.START = tk.RIGHT
            self.END = tk.LEFT
        else:
            self.START = tk.LEFT
            self.END = tk.RIGHT

        if self.START == 'left':
            self.geometry_direction = '+'
        elif self.START == 'right':
            self.geometry_direction = '-'

        self.apps = []
        self.icons = {}
        self.shell_icons = {}

        self.KeyboardListener = KeyboardListener
        self.pressed_key = None
        self.released_key = None
        
        self.MouseListener = MouseListener
        self.click_pos_x, self.click_pos_y = 0, 0
        self.mouse_pos_x, self.mouse_pos_y = 0, 0
        self.new_click = False
        
        self.keyboard = Controller()
        self.keyboard_layouts_code = {'00001006': 'ir', '00000002': 'us'}
        self.keyboard_layouts = self.get_keyboard_layouts()
        self.keyboard_active_layout = self.keyboard_layouts[0]
        self.index_keyboard_layout = 0

        self.ewmh = EWMH()

        # Costomize root
        self.root.geometry('{width}x{height}+0-{yoffset}'.format(
            width=self.root.winfo_screenwidth(),
            height=self.height_root_window,
            yoffset=-self.height_root_window
        ))
        self.root.wm_attributes('-type', 'dock')
        self.root.option_add("*font", "Vazir")
        self.root.configure(background="#222")
        self.root.option_add("*foreground", "#333")

        self.dictionary = {
            'Applications': {
                'fa': 'برنامه ها'
            },
            'Windows': {
                'fa': 'پنجره ها'
            },
            'virtual keyboard': {
                'fa': 'صفحه کلید مجازی'
            },
            'Persian': {
                'fa': 'فارسی'
            },
            'English (US)': {
                'fa': 'انگلیسی (US)'
            },
            '0': {'fa': '۰'},
            '1': {'fa': '۱'}, '2': {'fa': '۲'}, '3': {'fa': '۳'},
            '4': {'fa': '۴'}, '5': {'fa': '۵'}, '6': {'fa': '۶'},
            '7': {'fa': '۷'}, '8': {'fa': '۸'}, '9': {'fa': '۹'},
            'Shutdown': {
                'fa': 'خاموش کردن'
            },
            'Restart': {
                'fa': 'شروع مجدد'
            },
            'Log Out': {
                'fa': 'خروج'
            },
        }

        # styles
        shell_style = ttk.Style()
        shell_style.configure(
            "T.TFrame",
            background="#222",
            )

        # T.TLabel
        shell_style.configure(
            "T.TLabel",
            foreground="#ddd",
            background="#222",
            font=('Vazir', 9, 'normal')
            )

        # T.TButton
        shell_style.configure(
            "T.TButton",
            foreground="#ddd",
            background="#222",
            relief="flat",
            font=('Vazir', 9, 'normal'),
            justify='center',
            )
        shell_style.map(
            "T.TButton",
            foreground=[('pressed', '#d8d8d8'), ('active', '#dadada')],
            background=[
                ('pressed', '!disabled', '#1c1c1c'), ('active', '#1e1e1e')
            ],
            relief=[('pressed', '!disabled', 'flat'), ('active', 'flat')],
        )

        shell_style.configure(
            "TSmwin.TLabel",
            width=5,
            foreground="#ddd",
            background="#222",
            justify='center',
            )
        shell_style.map(
            "TSmwin.TLabel",
            foreground=[('pressed', '#d8d8d8'), ('active', '#dadada')],
            background=[
                ('pressed', '!disabled', '#1c1c1c'), ('active', '#1e1e1e')
            ],
            relief=[('pressed', '!disabled', 'flat'), ('active', 'flat')],
        )

        # W.TFrame
        shell_style = ttk.Style()
        shell_style.configure(
            "W.TFrame",
            background="#222",
            )

        # W.TButton
        shell_style = ttk.Style()
        shell_style.configure(
            "W.TButton",
            foreground="#dadada",
            background="#222",
            relief="flat",
            font=('Vazir', 9, 'normal'),
            )
        shell_style.map(
            "W.TButton",
            foreground=[('pressed', '#d8d8d8'), ('active', '#dadada')],
            background=[
                ('pressed', '!disabled', '#1c1c1c'), ('active', '#1e1e1e')
            ],
            relief=[('pressed', '!disabled', 'flat'), ('active', 'flat')],
        )

        # A.TFrame
        shell_style = ttk.Style()
        shell_style.configure(
            "A.TFrame",
            background="#333",
            )

        # A.TButton
        shell_style = ttk.Style()
        shell_style.configure(
            "A.TButton",
            foreground="#ddd",
            background="#333",
            relief="flat",
            width=24,
            wraplength=170,
            justify='center',
            font=('Vazir', 9, 'normal'),
            )
        shell_style.map(
            "A.TButton",
            foreground=[('pressed', '#eee'), ('active', '#e5e5e5')],
            background=[
                ('pressed', '!disabled', '#252525'), ('active', '#2e2e2e')
            ],
            relief=[('pressed', '!disabled', 'flat'), ('active', 'flat')],
        )

        # AS.TButton
        shell_style = ttk.Style()
        shell_style.configure(
            "AS.TButton",
            foreground="#e5e5e5",
            background="#333",
            relief="flat",
            font=('Vazir', 9, 'normal'),
            width=3,
            )
        shell_style.map(
            "AS.TButton",
            foreground=[('pressed', '#e0e0e0'), ('active', '#e2e2e2')],
            background=[
                ('pressed', '!disabled', '#333'), ('active', '#333')
            ],
            relief=[('pressed', '!disabled', 'flat'), ('active', 'flat')],
        )

        # SM.TButton
        shell_style = ttk.Style()
        shell_style.configure(
            "SM.TButton",
            width=100,
            foreground="#ddd",
            background="#333",
            relief="flat",
            font=('Vazir', 9, 'normal'),
            justify='center',
            )
        shell_style.map(
            "SM.TButton",
            foreground=[('pressed', '#dadada'), ('active', '#dbdbdb')],
            background=[
                ('pressed', '!disabled', '#333'), ('active', '#333')
            ],
            relief=[('pressed', '!disabled', 'flat'), ('active', 'flat')],
        )
        
        # SM.Horizontal.TProgressbar
        shell_style = ttk.Style()
        shell_style.configure(
            "SM.Horizontal.TProgressbar",
            background="#333",
            thickness=5
            )
        
        # SM.TLabel
        shell_style = ttk.Style()
        shell_style.configure(
            "SM.TLabel",
            foreground="#ddd",
            background="#333",
            )

        # SP.TButton
        shell_style = ttk.Style()
        shell_style.configure(
            "SP.TButton",
            width=100,
            foreground="#ddd",
            background="#333",
            relief="flat",
            font=('Vazir', 12, 'normal'),
            justify='center',
            )
        shell_style.map(
            "SP.TButton",
            foreground=[('pressed', '#d8d8d8'), ('active', '#dadada')],
            background=[
                ('pressed', '!disabled', '#2c2c2c'), ('active', '#2e2e2e')
            ],
            relief=[('pressed', '!disabled', 'flat'), ('active', 'flat')],
        )
        
        # K.TButton
        shell_style = ttk.Style()
        shell_style.configure(
            "K.TButton",
            foreground="#e5e5e5",
            background="#252525",
            relief="flat",
            width=6,
            justify='center',
            font=('Vazir', 9, 'normal'),
            )
        shell_style.map(
            "K.TButton",
            foreground=[('pressed', '#eee'), ('active', '#ececec')],
            background=[
                ('pressed', '!disabled', '#59f'), ('active', '#202020')
            ],
            relief=[('pressed', '!disabled', 'flat'), ('active', 'flat')],
        )
        
        # small shell
        self.create_small_shell()

        # system menu
        self.smf = ttk.Frame(self.root, style='T.TFrame')
        self.smf.pack(side=self.END, padx=3)

        shutdown_icon = self.create_icon(
            'system-shutdown-symbolic',
            (18, 18),
            shell=True
            )
        smf_shutdown = ttk.Label(
            self.smf,
            image=shutdown_icon,
            style="TSmwin.TLabel",
            cursor='hand2',
            )
        smf_shutdown.pack(side=self.END, ipady=11, ipadx=2)
        smf_shutdown.bind('<Button-1>', self.clicked_smf)

        self.connection_checker()

        sound_volume_icon = self.create_icon('volume', (18, 18), shell=True)
        self.smf_sound_volume_l = ttk.Label(
            self.smf,
            image=sound_volume_icon,
            style='TSmwin.TLabel',
            cursor='hand2',
        )
        self.smf_sound_volume_l.pack(side=self.END, ipady=11, ipadx=2)
        self.smf_sound_volume_l.bind('<Button-1>', self.clicked_smf)

        # clock
        self.time1 = ''
        self.clock = ttk.Label(
            self.root,
            style='T.TLabel',
            font=('Vazir', 10, 'normal'),
            )
        self.clock.pack(side=self.END, padx=5)
        self.tick()

        # language keybord
        self.keylayb = ttk.Button(
            self.root,
            command=self.set_keyboard_layout,
            style='T.TButton',
            cursor='hand2',
            text=self.keyboard_active_layout,
            width=4,
            )
        self.keylayb.pack(side=self.END, ipady=5)
        
        # virtual keyboard
        virkeyb = ttk.Button(
            self.root,
            command=self.show_hide_virkey,
            style='T.TButton',
            cursor='hand2',
            )
        keyboard_icon = self.create_icon('keyboard', (24, 24), shell=True)
        if keyboard_icon:
            virkeyb['image'] = keyboard_icon
        else:
            virkeyb['text']=self.translate_word('virtual keyboard')
        virkeyb.pack(side=self.END, ipady=5)

        # apps menu
        self.awinb = ttk.Button(
            self.root,
            command=self.show_hide_awin,
            text=self.translate_word('Applications'),
            style='T.TButton',
            cursor='hand2',
            )
        self.awinb.pack(side=self.START, ipady=5)

        # list windows
        self.fwlb = ttk.Button(
            self.root,
            command=self.show_hide_windows_list,
            style='T.TButton',
            cursor='hand2',
            )
        wl_icon = self.create_icon('restore-window', (24, 24), shell=True)
        if wl_icon:
            self.fwlb['image'] = wl_icon
        else:
            self.fwlb['text']=self.translate_word('Windows')
        self.fwlb.pack(side=self.START, ipady=5)
        self.windows_button = []

        self.get_keyboard_layout()
        _thread.start_new_thread(self.mouse_click_checker, ())
        _thread.start_new_thread(self.keyboard_click_checker, ())

        self.root.withdraw()

        self.root.mainloop()

    def connection_check(self, hostname):
          try:
            # see if we can resolve the host name -- tells us if there is
            # a DNS listening
            host = socket.gethostbyname(hostname)
            # connect to the host -- tells us if the host is actually
            # reachable
            s = socket.create_connection((host, 80), 2)
            return True
          except:
             pass
          return False
    
    def connection_checker(self):
        connected = self.connection_check('www.python.org')
        if connected:
            try:
                self.connected_l
            except AttributeError:
                connected_icon = self.create_icon('wifi', (18, 18), shell=True)
                self.connected_l = ttk.Label(
                    self.smf,
                    image=connected_icon,
                    style='TSmwin.TLabel',
                    cursor='hand2',
                )
                self.connected_l.pack(side=self.END, ipady=11, ipadx=2)
                self.connected_l.bind('<Button-1>', self.clicked_smf)
        else:
            try:
                self.connected_l.destroy()
                del self.connected_l
            except AttributeError:
                pass
        self.root.after(2000, self.connection_checker)

    def hide_small_shell(self, event):
        if str(event.type) == 'Motion':
            if event.y > 22:    # 26-26(height_small_shell)//4
                self.small_shell.withdraw()
                self.animation_show_root()
        else:
            self.small_shell.withdraw()
            self.animation_show_root()

    def create_small_shell(self):
        def animation_show(new_height=1):
            self.small_shell.geometry('{width}x{height}+0-{yoffset}'.format(
                width=self.root.winfo_screenwidth(),
                height=26,
                yoffset=new_height-26
            ))
            if new_height != 26:
                self.small_shell.after(8, animation_show, new_height+1)
        try:
            self.small_shell.deiconify()
        except AttributeError:
            self.small_shell = tk.Toplevel()

            self.small_shell.geometry('{width}x{height}+0-24'.format(
                width=self.root.winfo_screenwidth(),
                height=26,
            ))
            self.small_shell.title('Small Shell')
            self.small_shell.wm_attributes('-type', 'dock')
            self.small_shell.option_add("*font", "Vazir")
            self.small_shell.configure(background="#222")
            self.small_shell.option_add("*foreground", "#333")
            self.small_shell_click_event = self.small_shell.bind(
                '<Motion>',
                self.hide_small_shell
                )
            self.small_shell_click_event = self.small_shell.bind(
                '<Button-1>',
                self.hide_small_shell
                )
            
            # language keybord
            self.keylayb_small_shell = ttk.Label(
                self.small_shell,
                style='T.TLabel',
                font=('Vazir', 9, 'normal'),
                text=self.keyboard_active_layout,
                )
            self.keylayb_small_shell.pack(side=self.END, ipady=5, padx=6)
            
            # clock
            self.time1 = ''
            self.clock_small_shell = ttk.Label(
                self.small_shell,
                style='T.TLabel',
                font=('Vazir', 10, 'normal'),
                )
            self.clock_small_shell.pack(side=tk.BOTTOM, padx=5)
        finally:
            animation_show()

    def animation_hide_root(self, new_height=1, end_cmd=None):
        self.root.geometry('{width}x{height}+0+{yoffset}'.format(
            width=self.root.winfo_screenwidth(),
            height=self.height_root_window,
            yoffset=self.root.winfo_screenheight()+new_height
        ))
        if new_height == 1:
            self.hide_all_wins()
        if new_height != self.height_root_window:
            self.root.after(8, self.animation_hide_root, new_height+1, end_cmd)
        else:
            self.root.withdraw()
            if end_cmd:
                if type(end_cmd) == str:
                    os.system(end_cmd)
                else:
                    end_cmd()

    def get_keyboard_layouts(self):
        c = "setxkbmap -query | grep layout"
        pipe = Popen(c, shell=True, stdout=PIPE)
        text = pipe.communicate()[0].decode('utf-8')
        text = text[12:]
        if text[-1] == '\n':
            text = text[:-1]
        while text.find(' ') != -1:
            index = text.find(' ')
            text = '{}{}'.format(text[:index], text[index+1:])
            
        layouts = text.split(',')
        if not layouts[-1]:
            layouts = layouts[:-1]
        return layouts

    def hide_all_wins(self):
        try:
            self.awin
            self.animation_hide_awin()
        except:
            pass
        try:
            self.swin
            self.animation_hide_swin()
        except:
            pass
        try:
            self.smwin
            self.animation_hide_smwin()
        except:
            pass
        try:
            self.wwl
            self.animation_hide_windows_list()
        except:
            pass
        try:
            self.virkey
            self.animation_hide_virkey()
        except:
            pass

    def create_virkey(self):
        
        def clicked_on_key(char):
            self.keyboard.press(char)
            self.keyboard.release(char)
        
        def create_key(
            char,
            row,
            column,
            columnspan=1,
            special_cmd=None,
            text=None,
            icon=None,
            ):
            if not icon:
                if not text:
                    text = char

            key = ttk.Button(
                board,
                style='K.TButton',
                cursor='hand2',
            )
            
            if not special_cmd:
                key['command']=lambda char=char: clicked_on_key(char)
            else:
                key['command']=special_cmd

            if icon:
                key['image'] = icon
            else:
                key['text'] = text

            self.virkeyboard_keys.append(key)
            self.virkeyboard_keys[len(self.virkeyboard_keys)-1].grid(
                row=row,
                column=column,
                columnspan=columnspan,
                sticky='we',
                padx=4,
                pady=2,
                ipadx=0,
                ipady=5,
                )
        
        def create_keys(row, column, chars):
            for char in chars:
                create_key(char, row=row, column=column)
                column += 1
        
        def set_normal_chars():
            def caps_lock():
                def up(widget):
                    char = widget['text']
                    new_char = widget['text'].upper()
                    widget['text'] = new_char
                    widget['command'] = lambda char=new_char:clicked_on_key(char)
                    self.keys_state = True

                def lo(widget):
                    char = widget['text']
                    new_char = widget['text'].lower()
                    widget['text'] = new_char
                    widget['command'] = lambda char=new_char:clicked_on_key(char)
                    self.keys_state = False
                    

                if self.keys_state == False:
                    for key in self.virkeyboard_keys[15:25]:
                        up(key)
                    for key in self.virkeyboard_keys[29:39]:
                        up(key)
                    for key in self.virkeyboard_keys[42:49]:
                        up(key)
                else:
                    for key in self.virkeyboard_keys[15:25]:
                        lo(key)
                    for key in self.virkeyboard_keys[29:39]:
                        lo(key)
                    for key in self.virkeyboard_keys[42:49]:
                        lo(key)

            def upper_or_lower():
                def up(widget):
                    char = widget['text']
                    new_char = ''
                    for c in special_chars:
                        if char == c[0]:
                            new_char = c[1]
                    if not new_char:
                        new_char = widget['text'].upper()
                    widget['text'] = new_char
                    widget['command'] = lambda char=new_char:clicked_on_key(char)
                    self.keys_state = True

                def lo(widget):
                    char = widget['text']
                    new_char = ''
                    for c in special_chars:
                        if char == c[1]:
                            new_char = c[0]
                    if not new_char:
                        new_char = widget['text'].lower()
                    widget['text'] = new_char
                    widget['command'] = lambda char=new_char:clicked_on_key(char)
                    self.keys_state = False

                special_chars = [
                        ['`', '~'], ['1', '!'], ['2', '@'], ['3', '#'],
                        ['4', '$'], ['5', '%'], ['6', '^'], ['7', '&'],
                        ['8', '*'], ['9', '('], ['0', ')'], ['=', '+'],
                        ['[', '{'], [']', '}'], [';', ':'], ["'", '"'],
                        ['\\', '|'], [',', '<'], ['.', '>'], ['/', '?'],
                        ['ز', 'ژ'], ['ا', 'آ'], ['‍۱', '!'], ['۲', '٬'],
                        ['۳', '٫'], ['۴', '﷼'], ['۵', '٪'], ['۶', '×'],
                        ['۷', '،'], ['۸', '*'], ['۹', ')'], ['۰', '('],
                   
                        ]
                if self.virkey_active_layout == 'fa':
                    special_chars.append(['-', 'ـ'])
                else:
                    special_chars.append(['-', '_'])

                if self.keys_state == False:
                    for key in self.virkeyboard_keys[0:13]:
                        up(key)
                    for key in self.virkeyboard_keys[15:27]:
                        up(key)
                    for key in self.virkeyboard_keys[29:41]:
                        up(key)
                    for key in self.virkeyboard_keys[42:52]:
                        up(key)
                else:
                    for key in self.virkeyboard_keys[0:13]:
                        lo(key)
                    for key in self.virkeyboard_keys[15:27]:
                        lo(key)
                    for key in self.virkeyboard_keys[29:41]:
                        lo(key)
                    for key in self.virkeyboard_keys[42:52]:
                        lo(key)

            self.virkey_cnt_type = 'normal'
            self.keys_state = False
            
            for child in board.winfo_children():
                child.destroy()
            self.virkeyboard_keys = []
            
            if self.root.winfo_screenwidth() > 720:
                if self.virkey_active_layout == 'us':
                    self.virkey_lay = 'us'
                    create_keys(
                    0, 0, ('`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=')
                    )
                    create_key(
                        Key.backspace,
                        row=0,
                        column=13,
                        text='Backspace',
                        columnspan=2
                        )
                    
                    create_key(Key.tab, row=1, column=0, text='Tab')
                    create_keys(
                        1, 1, ('q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']')
                        )
                    
                    create_key(
                        Key.enter,
                        row=1,
                        column=13,
                        text='Enter',
                        columnspan=2
                        )
                    
                    create_key(
                        Key.caps_lock,
                        row=2,
                        column=0,
                        text='Caps Lock',
                        columnspan=2,
                        special_cmd=caps_lock,
                        )
                    create_keys(
                        2, 2, ('a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', "'", '\\')
                        )
                    
                    
                    create_key(
                        Key.shift_l,
                        row=3,
                        column=0,
                        text='Shift',
                        special_cmd=upper_or_lower,
                        columnspan=2
                        )
                    create_keys(
                        3, 2, ('z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/')
                        )
                    create_key(
                        Key.shift_r,
                        row=3,
                        column=12,
                        text='Shift',
                        special_cmd=upper_or_lower,
                        columnspan=2,
                        )

                elif self.virkey_active_layout == 'ir':
                    self.virkey_lay = 'ir'

                    create_keys(
                        0, 0, ('‍‍‍‍‍‍‍‍÷', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹', '۰', '-', '=')
                        )
                    create_key(
                        Key.backspace,
                        row=0,
                        column=13,
                        text='Backspace',
                        columnspan=2,
                        )

                    create_key(Key.tab, row=1, column=0, text='Tab')
                    create_keys(
                        1 , 1, ('ض', 'ص', 'ث', 'ق', 'ف', 'غ', 'ع', 'ه', 'خ', 'ح', 'ج', 'چ')
                        )
                    create_key(
                        Key.enter,
                        row=1,
                        column=13,
                        text='Enter',
                        columnspan=2
                        )

                    create_key(
                        Key.caps_lock,
                        row=2,
                        column=0,
                        text='Caps Lock',
                        columnspan=2,
                        special_cmd=caps_lock,
                        )
                    create_keys(
                        2, 2, ('ش', 'س', 'ی', 'ب', 'ل', 'ا',  'ت', 'ن', 'م', 'ک', 'گ', '\\')
                        )
                    
                    create_key(
                        Key.shift_l,
                        row=3,
                        column=0,
                        text='Shift',
                        special_cmd=upper_or_lower,
                        columnspan=2
                        )
                    create_keys(
                        3, 2, ('ظ', 'ط', 'ز', 'ر', 'ذ', 'د', 'پ', 'و', '.', '/')
                        )
                    create_key(
                        Key.shift_r,
                        row=3,
                        column=12,
                        text='Shift',
                        special_cmd=upper_or_lower,
                        columnspan=2,
                        )

                create_key(
                    Key.ctrl_l,
                    row=4,
                    column=0,
                    text='Ctrl',
                    )
                create_key(
                    Key.cmd_l,
                    row=4,
                    column=1,
                    text='cmd',
                    )
                create_key(
                    Key.alt_r,
                    row=4,
                    column=2,
                    text='Alt',
                    )
                lang_icon = self.create_icon('cs-language', (24, 24))
                create_key(
                    'lang',
                    row=4,
                    column=3,
                    special_cmd=set_keyboard_layout,
                    icon=lang_icon,
                    )
                create_key(
                    Key.space,
                    row=4,
                    column=4,
                    text=' ',
                    columnspan=6
                    )
                keyboard_icon = self.create_icon('keyboard', (24, 24), shell=True)
                create_key(
                    'hide',
                    row=4,
                    column=10,
                    special_cmd=self.show_hide_virkey,
                    icon=keyboard_icon,
                    )
                create_key(
                    Key.alt_r,
                    row=4,
                    column=11,
                    text='Alt',
                    )
                create_key(
                    Key.cmd_r,
                    row=4,
                    column=12,
                    text='cmd',
                    )
                create_key(
                    Key.ctrl_r,
                    row=4,
                    column=13,
                    text='Ctrl',
                    )
                
                create_key(
                    Key.insert,
                    row=0,
                    column=15,
                    text='Insert',
                    )
                create_key(Key.delete, row=1, column=15, text='Delete')
                create_key(Key.home, row=0, column=16, text='Home')
                create_key(Key.end, row=1, column=16, text='End')
                create_key(Key.page_up, row=0, column=17, text='Page Up')
                create_key(Key.page_down, row=1, column=17, text='Page Down')
                
                create_key(Key.up, row=3, column=16, text='Up')
                create_key(Key.left, row=4, column=15, text='Left')
                create_key(Key.down, row=4, column=16, text='Down')
                create_key(Key.right, row=4, column=17, text='Right')

            else:
                if self.virkey_active_layout == 'us':
                    self.virkey_lay = 'us'
                    create_keys(
                        0, 0, ('q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p')
                        )
                    create_key(Key.delete, row=0, column=10, text='Delete')
                    
                    create_keys(
                        1, 0, ('a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l')
                        )
                    create_key(
                        Key.enter,
                        row=1,
                        column=9,
                        text='Enter',
                        columnspan=2
                        )
                    
                    create_key(
                        Key.shift_l,
                        row=2,
                        column=0,
                        text='Shift',
                        special_cmd=upper_or_lower
                        )
                    create_keys(
                        2, 1, ('z', 'x', 'c', 'v', 'b', 'n', 'm', '@', '.')
                        )
                    create_key(
                        Key.shift_l,
                        row=2,
                        column=10,
                        text='Shift',
                        special_cmd=upper_or_lower
                        )

                    create_keys(3, 8, ('_', '/'))
                    
                elif self.virkey_active_layout == 'ir':
                    self.virkey_lay = 'ir'
                    create_keys(
                        0, 0, ('ض', 'ص', 'ث', 'ق', 'ف', 'غ', 'ع', 'ه', 'خ', 'ح', 'ج', 'چ')
                        )

                    create_keys(
                        1, 0, ('ش', 'س', 'ی', 'ب', 'ل', 'ا', 'آ', 'ت', 'ن', 'م', 'ک', 'گ')
                        )

                    create_keys(
                        2, 0, ('ظ', 'ط', 'ژ', 'ز', 'ر', 'ذ', 'د', 'پ', 'و', '.')
                        )
                    create_key(
                        Key.enter,
                        row=2,
                        column=10,
                        text='Enter',
                        columnspan=2
                        )

                    create_keys(3, 8, ('ـ', '/'))
                    create_key(
                        Key.delete,
                        row=3,
                        column=11,
                        text=self.setrtl('حذف')
                        )

                create_key(
                    '&123',
                    row=3,
                    column=0,
                    columnspan=2,
                    special_cmd=show_hide_special_chars
                    )
                lang_icon = self.create_icon('cs-language', (24, 24))
                create_key(
                    'lang',
                    row=3,
                    column=2,
                    special_cmd=set_keyboard_layout,
                    icon=lang_icon,
                    )
                create_key(
                    Key.space,
                    row=3,
                    column=3,
                    text=' ',
                    columnspan=5
                    )
                keyboard_icon = self.create_icon('keyboard', (24, 24), shell=True)
                create_key(
                    'hide',
                    row=3,
                    column=10,
                    special_cmd=self.show_hide_virkey,
                    icon=keyboard_icon,
                    )

        def set_special_chars():
            self.virkey_cnt_type = 'special'

            for child in board.winfo_children():
                child.destroy()
            self.virkeyboard_keys = []

            create_keys(
                0, 0, ('1', '2', '3', '4', '5', '6', '7', '8', '9', '0')
                )
            create_key(Key.delete, row=0, column=10, text='Delete')

            create_keys(1, 0, ('`', '|', '{', '}', '%', '^', '*', '/', '"'))
            create_key(Key.enter, row=1, column=9, text='Enter', columnspan=2)
            
            create_keys(
                2, 0, ('$', '&', '~', '#', '=', '+', '@', '?', '!', '_', '-')
            )
            
            create_key(
                '&123',
                row=3,
                column=0,
                columnspan=2,
                special_cmd=show_hide_special_chars
                )
            lang_icon = self.create_icon('cs-language', (24, 24))
            create_key(
                'lang',
                row=3,
                column=2,
                special_cmd=set_keyboard_layout,
                icon=lang_icon,
                )
            create_key(
                Key.space,
                row=3,
                column=3,
                text=' ',
                columnspan=4
                )
            create_keys(3, 7, ('<', '>', '(', ')'))
        
        def show_hide_special_chars():
            if self.virkey_cnt_type != 'special':
                set_special_chars()
            else:
                set_normal_chars()
        
        def reset_chars():
            if self.virkey_cnt_type == 'special':
                set_special_chars()
            else:
                set_normal_chars()
        
        def animation_show(x=0):
            screen_width = self.root.winfo_screenwidth()
            self.virkey.geometry(
                '{width}x{height}{direction}{xoffset}-{yoffset}'.format(
                    width=screen_width,
                    height=280,
                    direction=local_direction,
                    xoffset=-screen_width+x,
                    yoffset=self.height_root_window,
                    )
                )
            if x < screen_width:
                if screen_width - x < 20:
                    self.virkey.after(5, animation_show, (screen_width))
                else:
                    self.virkey.after(5, animation_show, (x+20))
        
        def set_keyboard_layout():
            layouts = self.get_keyboard_layouts()
            index = 0
            for layout in layouts:
                if layout == self.virkey_active_layout:
                    break
                index += 1
            if index+1 == len(layouts):
                self.virkey_active_layout = layouts[0]
            else:
                self.virkey_active_layout = layouts[index+1]
            set_normal_chars()

        self.virkey = tk.Toplevel()

        if self.geometry_direction == '-':
            local_direction = '+'
        elif self.geometry_direction == '+':
            local_direction = '-'

        self.virkey.geometry(
            '{width}x{height}{direction}{xoffset}-{yoffset}'.format(
                width=self.root.winfo_screenwidth(),
                height=280,
                direction=local_direction,
                xoffset=-self.root.winfo_screenwidth(),
                yoffset=self.height_root_window,
                )
            )
        self.virkey.wm_attributes('-type', 'dock')
        self.virkey.wm_attributes('-alpha', '0.8')
        self.virkey.configure(background="#333")

        # board
        board = ttk.Frame(self.virkey, style="A.TFrame")
        board.pack(pady=15)
        
        self.virkey_cnt_type = ''
        
        self.virkeyboard_keys = []
        self.virkey_active_layout = self.keyboard_active_layout
        
        set_normal_chars()
        
        animation_show()

    def show_hide_virkey(self):
        try:
            self.virkey
            self.animation_hide_virkey()
        except AttributeError:
            self.hide_all_wins()
            self.create_virkey()
    
    def animation_hide_virkey(self, x=0):
        if self.geometry_direction == '-':
            local_direction = '+'
        elif self.geometry_direction == '+':
            local_direction = '-'
        try:
            screen_width = self.root.winfo_screenwidth()
            self.virkey.geometry(
                '{width}x{height}{direction}{xoffset}-{yoffset}'.format(
                    width=screen_width,
                    height=280,
                    direction=local_direction,
                    xoffset=-x,
                    yoffset=self.height_root_window,
                    )
                )
            if x < screen_width:
                if screen_width - x < 20:
                    self.virkey.after(5, self.animation_hide_virkey, (screen_width))
                else:
                    self.virkey.after(5, self.animation_hide_virkey, (x+20))
            else:
                self.virkey.destroy()
                del self.virkey
        except AttributeError:
            return

    def on_move_recorder(self, x, y):
        self.mouse_pos_x = x
        self.mouse_pos_y = y
        # --new-option: hover bootom, left or right show awin

    def on_click_recorder(self, x, y, button, pressed):
        if pressed:
            self.click_pos_x = x
            self.click_pos_y = y
            self.new_click = True

    def mouse_click_checker(self):
        with self.MouseListener(
            on_click=self.on_click_recorder,
            on_move=self.on_move_recorder) as self.MouseListener:
            self.MouseListener.join()
    
    def on_press_key_recorder(self, key):
        # --new-option: press cmd button create awin
        self.pressed_key = key
    
    def on_release_key_recorder(self, key):
        self.released_key = key

    def keyboard_click_checker(self):
        with self.KeyboardListener(
            on_press=self.on_press_key_recorder,
            on_release=self.on_release_key_recorder) as self.KeyboardListener:
            self.KeyboardListener.join()

    def animation_hide_swin(self, new_width=0):
        try:
            self.swin
        except AttributeError:
            return
        if self.geometry_direction == '-':
            local_direction = '+'
        elif self.geometry_direction == '+':
            local_direction = '-'
        self.swin.geometry(
            '{width}x{height}{direction}{xoffset}-{yoffset}'.format(
                width=640,
                height=self.root.winfo_screenheight()-self.height_root_window,
                direction=local_direction,
                xoffset=-new_width,
                yoffset=self.height_root_window,
                )
            )
        if new_width < 640:
            self.swin.after(5, self.animation_hide_swin, new_width+20)
        else:
            self.swin.destroy()
            del self.swin

    def show_hide_swin(self):
        try:
            self.swin
            self.animation_hide_swin()
        except AttributeError:
            try:
                self.smwin.destroy()
                del self.smwin
                try:
                    self.system_power.destroy()
                    del self.system_power
                except AttributeError:
                    pass
            except AttributeError:
                pass
            self.create_swin()

    def create_swin(self):
        def show_apps(apps):
            def clicked_stack_switche(stack_index):
                for stack in stacks_list:
                    stack.pack_forget()
                icon = self.create_icon('circle-white', (24, 24), shell=True)
                for switche in stack_switches_list:
                    switche['image'] = icon
                icon = self.create_icon('circle-filled', (24, 24), shell=True)
                stack_switches_list[stack_index]['image'] = icon
                stacks_list[stack_index].pack(side=self.START)

            def add_stack():
                stack = ttk.Frame(stacks, style='A.TFrame')
                stacks_list.append(stack)

            def add_stack_switche(stack_index):
                icon = self.create_icon('circle-white', (24, 24), shell=True)
                switche = ttk.Button(
                    stack_switches,
                    command=lambda si=stack_index: clicked_stack_switche(si),
                    style='AS.TButton',
                    cursor='hand2',
                    )
                if icon:
                    switche['image'] = icon
                else:
                    switche['text'] = self.translate_word(str(stack_index+1))
                switche.pack(side=tk.LEFT, pady=5, padx=5)
                stack_switches_list.append(switche)

            stack_switches = ttk.Frame(fapps, style='A.TFrame')
            stack_switches.pack(side=tk.BOTTOM, pady=6)
            stack_switches_list = []

            stacks = ttk.Frame(fapps, style='A.TFrame')
            stacks.pack(side=tk.TOP, fill=tk.Y)
            stacks_list = []
            add_stack()

            row, column = 0, 0
            max_row = (self.root.winfo_screenheight()- \
            self.height_root_window) // 120
            stack_index = 0

            for app in apps:
                if row == max_row and column == 0:
                    add_stack()
                    column = 0
                    row = 0
                    if stack_index == 0:
                        add_stack_switche(0)
                        icon = self.create_icon('circle-filled', (24, 24), shell=True)
                        stack_switches_list[0]['image'] = icon
                    stack_index += 1
                    add_stack_switche(stack_index)

                button = ttk.Button(
                    stacks_list[stack_index],
                    text=app["name"],
                    command=lambda c=app['command']: self.click_button_setting(c),
                    compound=tk.TOP,
                    style='A.TButton',
                    cursor='hand2'
                    )

                icon = self.create_icon(app['icon_name'], (48, 48))
                if icon != '':
                        button['image'] = icon

                button.grid(row=row, column=column, pady=12, padx=8)   # ~max 15, 15

                if column == 2:
                    column = 0
                    row += 1
                else:
                    column += 1

            stacks_list[0].pack()

        def check_mouse():
            x, y = self.click_pos_x, self.click_pos_y
            if self.new_click:
                if self.geometry_direction == '-':
                    if x > 640:
                        self.animation_hide_swin()
                elif self.geometry_direction == '+':
                    if x < self.root.winfo_screenwidth() - 640:
                        self.animation_hide_swin()

                if y > self.root.winfo_screenheight() \
                        - self.height_root_window:
                    self.animation_hide_swin()
            try:
                self.swin.after(400, check_mouse)
            except AttributeError:
                return

        def animation_show_swin(new_width=0):
            self.swin.geometry(
                '{width}x{height}{direction}{xoffset}-{yoffset}'.format(
                    width=640,
                    height=(
                        self.root.winfo_screenheight()-self.height_root_window
                    ),
                    direction=local_direction,
                    xoffset=-(640-new_width),
                    yoffset=self.height_root_window,
                    )
                )
            if new_width < 640:
                self.swin.after(5, animation_show_swin, new_width+20)

        if self.geometry_direction == '-':
            local_direction = '+'
        else:
            local_direction = '-'
        self.swin = tk.Toplevel()
        self.swin.geometry(
            '{width}x{height}{direction}{xoffset}-{yoffset}'.format(
                width=640,
                height=self.root.winfo_screenheight()-self.height_root_window,
                direction=local_direction,
                xoffset=0,
                yoffset=self.height_root_window,
                )
            )
        self.swin.wm_attributes('-type', 'dock')
        self.swin.wm_attributes('-alpha', '0.9')
        self.swin.configure(background="#333")

        # body
        body = ttk.Frame(self.swin, style="A.TFrame")
        body.pack(side=self.END, fill=tk.BOTH, expand=1)

        fapps = ttk.Frame(body, style='A.TFrame')

        self.apps = self.get_deskfiles()
        apps = []
        for app in self.apps:
            if 'Settings' in app['categories']:
                apps.append(app)

        show_apps(apps)

        fapps.pack(fill=tk.BOTH, expand=1)

        animation_show_swin()

        self.new_click = False
        check_mouse()

    def create_smwin(self):
        if self.geometry_direction == '-':
            local_direction = '+'
        elif self.geometry_direction == '+':
            local_direction = '-'

        def system_power():
            self.system_power = tk.Toplevel()
            if self.geometry_direction == '-':
                local_direction = '+'
            elif self.geometry_direction == '+':
                local_direction = '-'
            self.system_power.geometry(
                '{width}x{height}{direction}{xoffset}-{yoffset}'.format(
                    width=320,
                    height=245, # 255 - 10
                    direction=local_direction,
                    xoffset=0,
                    yoffset=self.height_root_window+65+10,
                    )
                )
            self.system_power.wm_attributes('-type', 'dock')
            self.system_power.configure(background="#333")

            # body
            body = ttk.Frame(self.system_power, style="A.TFrame")
            body.pack()

            shutdownb = ttk.Button(
                body,
                style="SP.TButton",
                command=self.shutdown,
                compound=self.START,
                text=self.translate_word('Shutdown'),
                )
            shutdownb.pack(ipady=10,)

            rebootb = ttk.Button(
                body,
                style="SP.TButton",
                command=self.reboot,
                compound=self.START,
                text=self.translate_word('Restart'),
                )
            reboot_icon = self.create_icon('system-restart', (24, 24), shell=True)
            if reboot_icon:
                rebootb['image'] = reboot_icon
            rebootb.pack(ipady=10,)

            logoutb = ttk.Button(
                body,
                style="SP.TButton",
                command=self.logout,
                compound=self.START,
                text=self.translate_word('Log Out'),
                )
            logout_icon = self.create_icon('system-log-out', (24, 24), shell=True)
            if logout_icon:
                logoutb['image'] = logout_icon
            logoutb.pack(ipady=10,)

        def show_hide_system_power():
            try:
                self.system_power.destroy()
                del self.system_power
            except AttributeError:
                system_power()

        def animation_show_smwin(new_width=0):
            self.smwin.geometry(
                '{width}x{height}{direction}{xoffset}-{yoffset}'.format(
                    width=320,
                    height=320,
                    direction=local_direction,
                    xoffset=-(320-new_width),
                    yoffset=self.height_root_window,
                    )
                )
            if new_width < 320:
                self.smwin.after(5, animation_show_smwin, new_width+20)

        def check_mouse():
            x, y = self.click_pos_x, self.click_pos_y
            if  self.new_click:
                try:
                    self.swin
                    self.animation_hide_smwin()
                except AttributeError:
                    if y < self.root.winfo_screenheight() - \
                            320-self.height_root_window:
                        self.animation_hide_smwin()
                    elif y > self.root.winfo_screenheight()\
                            - self.height_root_window:
                        self.animation_hide_smwin()

                    elif self.geometry_direction == '+':
                        if x < self.root.winfo_screenwidth() - 320:
                            self.animation_hide_smwin()
                    elif self.geometry_direction == '-':
                        if x > 320:
                            self.animation_hide_smwin()
            try:
                self.smwin.after(400, check_mouse)
            except AttributeError:
                return

        def create_bottombar_button(command, icon_name, text):
            b = ttk.Button(
                bottombar,
                style="SM.TButton",
                command=command,
                cursor='hand2',
                )

            b_icon = self.create_icon(icon_name, (32, 32), shell=True)

            if b_icon:
                b['image'] = b_icon
            else:
                b['text'] = self.translate_word(text)

            b.grid(row=0, column=len(bottombar_buttons), padx=6, pady=6)
            bottombar_buttons.append(b)
        
        def set_sound_volume(event):
            volume = event.x * 100 / 320
            call(["amixer", "-D", "pulse", "sset", "Master", str(volume)+"%"])
            x = self.sound_volume_ui.coords('sound_volume_l')[0]
            if x < 320 and x > 0:
                self.sound_volume_ui.coords('sound_volume_l', event.x-16, 0)
                self.sound_volume_ui.coords(
                    'sound_volume_pb',
                    0,
                    13,
                    event.x,
                    19
                    )
        
        def get_sound_volume():
            c = "amixer -D pulse sget Master | awk 'FNR==6 { print $5 } FNR==7 { print $5 }'"
            pipe = Popen(c, shell=True, stdout=PIPE)
            text = pipe.communicate()[0].decode('utf-8')
            volumes = text.split('\n')
            if not volumes[-1]:
                volumes = volumes[:-1]
           # شاید بشه بیشتر از ۲ بلند گو باشه
            if volumes:
                x = int(volumes[0][1:-2])*320/100

                self.sound_volume_ui.coords('sound_volume_l', x-16, 0)
                self.sound_volume_ui.coords(
                        'sound_volume_pb',
                        0,
                        13,
                        x,
                        19
                        )
            else:
                x = 0

            if x == 0:
                if not self.sound_volume_off:
                    sound_volume_icon = self.create_icon(
                        'volume-off-label',
                        (32, 32),
                        shell=True
                        )
                    msf_sound_volume_icon = self.create_icon(
                        'volume-off',
                        (18, 18),
                        shell=True
                        )
                    self.sound_volume_ui.itemconfig(
                        'sound_volume_l',
                        image=sound_volume_icon
                        )
                    self.smf_sound_volume_l['image'] = msf_sound_volume_icon
                    self.sound_volume_off = True
            else:
                if self.sound_volume_off:
                    sound_volume_icon = self.create_icon(
                        'volume-label',
                        (32, 32),
                        shell=True
                        )
                    msf_sound_volume_icon = self.create_icon(
                        'volume',
                        (18, 18),
                        shell=True
                        )
                    self.sound_volume_ui.itemconfig(
                        'sound_volume_l',
                        image=sound_volume_icon
                        )
                    self.smf_sound_volume_l['image'] = msf_sound_volume_icon
                    self.sound_volume_off = False

            self.sound_volume_ui.after(500, get_sound_volume)

        self.smwin = tk.Toplevel()

        self.smwin.geometry(
            '{width}x{height}{direction}{xoffset}-{yoffset}'.format(
                width=320,
                height=320,
                direction=local_direction,
                xoffset=-320,
                yoffset=self.height_root_window,
                )
            )
        self.smwin.wm_attributes('-type', 'dock')
        self.smwin.configure(background="#333")

        # body
        body = ttk.Frame(self.smwin, style="A.TFrame")
        body.pack()

        self.sound_volume_ui = tk.Canvas(
            body,
            width=320,
            height=32,
            background='#333',
            highlightbackground="#333"
            )
        self.sound_volume_ui.pack(side=tk.TOP, pady=5)
        
        self.sound_volume_ui.create_rectangle(
            0, 13, 320, 19, fill="#eee", tags="sound_volume_b"
            )

        self.sound_volume_pb = self.sound_volume_ui.create_rectangle(
            0, 13, 200, 19, fill="#59f", tags="sound_volume_pb"
            )
        
        sound_volume_icon = self.create_icon('volume-label', (32, 32), shell=True)
        self.sound_volume_l = self.sound_volume_ui.create_image(
            0,
            0,
            anchor=tk.NW,
            image=sound_volume_icon,
            tags="sound_volume_l"
            )

        self.sound_volume_ui.tag_bind(
            'sound_volume_b',
            '<Button-1>',
            set_sound_volume
            )
        self.sound_volume_ui.tag_bind(
            'sound_volume_b',
            '<B1-Motion>',
            set_sound_volume
            )
        self.sound_volume_ui.tag_bind(
            'sound_volume_l',
            '<Button-1>',
            set_sound_volume
            )
        self.sound_volume_ui.tag_bind(
            'sound_volume_l',
            '<B1-Motion>',
            set_sound_volume
            )
        self.sound_volume_ui.pack(side=tk.LEFT)
        
        self.sound_volume_off = False
        get_sound_volume()

        bottombar = ttk.Frame(self.smwin, style="A.TFrame")
        bottombar.pack(side=tk.BOTTOM)

        bottombar_buttons = []

        create_bottombar_button(
            show_hide_system_power,
            'system-shutdown',
            'Log Out',
            )

        create_bottombar_button(
            self.show_hide_swin,
            'system-settings',
            'Settings',
            )

        create_bottombar_button(
            self.lock,
            'system-lock',
            'Lock',
            )

        animation_show_smwin()

        self.new_click = False
        check_mouse()

    def clicked_smf(self, event):
        self.show_hide_smwin()

    def animation_hide_smwin(self, new_width=0):
        try:
            self.smwin
        except AttributeError:
            return
        
        if self.geometry_direction == '-':
            local_direction = '+'
        elif self.geometry_direction == '+':
            local_direction = '-'

        self.smwin.geometry(
            '{width}x{height}{direction}{xoffset}-{yoffset}'.format(
                width=320,
                height=320,
                direction=local_direction,
                xoffset=-new_width,
                yoffset=self.height_root_window,
                )
            )
        
        try:
            self.system_power
            self.system_power.geometry(
                '{width}x{height}{direction}{xoffset}-{yoffset}'.format(
                    width=320,
                    height=255,
                    direction=local_direction,
                    xoffset=-new_width,
                    yoffset=self.height_root_window+65,
                    )
                )
        except AttributeError:
            pass

        if new_width < 320:
            self.smwin.after(5, self.animation_hide_smwin, new_width+20)
        else:
            self.smwin.destroy()
            del self.smwin
            try:
                self.system_power.destroy()
                del self.system_power
            except AttributeError:
                return

    def show_hide_smwin(self):
        try:
            self.smwin
            self.animation_hide_smwin()
        except AttributeError:
            self.hide_all_wins()
            self.create_smwin()

    def animation_show_root(self, new_height=1):
        self.root.deiconify()
        self.root.geometry('{width}x{height}+0+{yoffset}'.format(
            width=self.root.winfo_screenwidth(),
            height=self.height_root_window,
            yoffset=self.root.winfo_screenheight()-new_height
        ))
        if new_height != self.height_root_window:
            self.root.after(8, self.animation_show_root, new_height+1)
        else:
            self.rootw_check_mouse()

    def create_windows_list(self):
        def get_wl():
            wl = self.ewmh.getClientList()
            new_wl = []
            for w in wl:
                # 335 and 334 and 339: _NET_WM_WINDOW_TYPE_NORMAL
                types = self.ewmh.getWmWindowType(w, str=True)
                types = list(types)
                if types:
                    if '_NET_WM_WINDOW_TYPE_DOCK' not in types:
                        new_wl.append(w)
                else:
                    new_wl.append(w)
            return new_wl

        def create_window_button(w):
            title = self.ewmh.getWmVisibleName(w).decode('utf-8')
            title = self.setrtl(title)

            type_ = self.ewmh.getWmWindowType(w)
            if type_ and type_ != []:
                app_proc = self.get_proc_with_pid(
                    self.ewmh.getWmPid(w)
                    )
                icon_name = self.get_icon_name_with_exec(app_proc)
            else:
                icon_name = None

            if icon_name:
                icon = self.create_icon(icon_name, (128, 128))
            else:
                icon = None
            button = ttk.Button(
                self.fwl,
                command=lambda w=w: self.show_hide_window(w),
                style='W.TButton',
                compound=tk.BOTTOM,
                cursor='hand2',
                )
            if icon:
                button['image'] = icon
            else:
                if len(title) > 20:
                    button['text'] = title[:19]
                else:
                    button['text'] = title

            self.windows_button.append(button)
            return button

        def create_window_buttons(wl):
            self.windows_button = []

            win_width = len(wl)*139+139+30
            win_xoffset = self.root.winfo_screenwidth()//2-win_width//2
            self.wwl.geometry('{width}x{height}+{xoffset}-{yoffset}'.format(
                width=win_width,
                height=139,
                direction=self.geometry_direction,
                xoffset=win_xoffset,
                yoffset=(
                    self.root.winfo_screenheight()-self.height_root_window
                )//2-38
            ))

            show_desktopb = ttk.Button(
                self.fwl,
                command= lambda wl=wl:self.show_desktop(wl),
                style='W.TButton',
                compound=tk.BOTTOM,
                cursor='hand2',
                )
            show_desktop_icon = self.create_icon('show-desktop', (128, 128))
            if show_desktop_icon:
                show_desktopb['image'] = show_desktop_icon
            else:
                    show_desktopb['text'] = self.translate_word('wallpaper')
            self.windows_button.append(show_desktopb)
            if self.geometry_direction == '+':
                show_desktopb.pack(side=self.START, padx=(0, 30))
            else:
                show_desktopb.pack(side=self.START, padx=(30, 0))

            for w in wl:
                create_window_button(w).pack(side=self.START)

        def check_mouse():
            x, y = self.click_pos_x, self.click_pos_x
            if self.new_click:
                win_width = len(wl)*139+139+30
                win_xoffset = (
                    self.root.winfo_screenwidth()//2-win_width//2
                    )
                if y < (
                    self.root.winfo_screenheight()-self.height_root_window
                        )//2-38:
                    self.animation_hide_windows_list()
                elif y > (
                    self.root.winfo_screenheight()-self.height_root_window
                        )//2-38 + 139:
                    self.animation_hide_windows_list()

                elif x > win_width+win_xoffset:
                    self.animation_hide_windows_list()
                elif x < win_xoffset:
                    self.animation_hide_windows_list()
            try:
                self.wwl.after(400, check_mouse)
            except AttributeError:
                return
        
        def animation_show(y=0):
            width = len(wl)*139+139+30
            self.wwl.geometry('{width}x{height}{direction}{x}+{y}'.format(
                width=width,
                height=139,
                direction=self.geometry_direction,
                x=(self.root.winfo_screenwidth() - width) // 2,
                y=-140+y  # 140 ~ 39
                )
            )
            if y < (self.root.winfo_screenheight()- \
                    self.height_root_window)//2+40:  # 40 ~ 39
                self.wwl.after(10, animation_show, (y+20))

        del self.ewmh
        self.ewmh = EWMH()
        wl = get_wl()
        if len(wl) != 0:
            self.wwl = tk.Toplevel()
            width = len(wl)*139+139+30
            self.wwl.geometry('{width}x{height}{direction}{x}+{y}'.format(
                width=width,
                height=139,
                direction=self.geometry_direction,
                x=(self.root.winfo_screenwidth() - width) // 2,
                y=-140  # 140 ~ 39
                )
            )
            self.wwl.wm_attributes('-type', 'dock')
            self.wwl.configure(background="#222")
            self.fwl = ttk.Frame(self.wwl, style='W.TFrame')
            self.fwl.pack()

            self.apps = self.get_deskfiles()
            create_window_buttons(wl)

            animation_show()

            self.new_click = False
            check_mouse()

    def animation_hide_windows_list(self):
        try:
            width = self.wwl.winfo_width()
            self.wwl.geometry('{width}x{height}{direction}{x}+{y}'.format(
                width=width,
                height=139,
                direction=self.geometry_direction,
                x=(self.root.winfo_screenwidth() - width) // 2,
                y=self.wwl.winfo_y() - 20
                )
            )

            if self.wwl.winfo_y() > -self.wwl.winfo_height():
                self.wwl.after(10, self.animation_hide_windows_list)
            else:
                self.wwl.destroy()
                del self.wwl

        except AttributeError:
            pass

    def rootw_check_mouse(self):
        check = True
        try:
            self.awin
            check = False
        except:
            pass
        if check:
            try:
                self.swin
                check = False
            except:
                pass
        if check:
            try:
                self.smwin
                check = False
            except:
                pass
        if check:
            try:
                self.wwl
                check = False
            except:
                pass
        if check:
            try:
                self.virkey
                check = False
            except:
                pass

        if check and self.mouse_pos_y < \
                self.root.winfo_screenheight() - self.height_root_window:
            self.animation_hide_root()
            self.create_small_shell()
            return
        self.root.after(200, self.rootw_check_mouse)

    def show_hide_windows_list(self):
        try:
            self.wwl
            self.animation_hide_windows_list()
        except AttributeError:
            self.hide_all_wins()
            self.create_windows_list()

    def set_keyboard_layout(self):
        self.keyboard.press(Key.alt)
        self.keyboard.press(Key.shift)
        self.keyboard.release(Key.shift)
        self.keyboard.release(Key.alt)

    def get_keyboard_layout(self):
        c = r"(xset -q|grep LED| awk '{ print $10 }')"
        pipe = Popen(c, shell=True, stdout=PIPE)
        led_mask = pipe.communicate()[0].decode('utf-8')
        if led_mask[-1] == '\n':
            led_mask = led_mask[:-1]
        
        if led_mask in self.keyboard_layouts_code:
            layout = self.keyboard_layouts_code[led_mask]
            if layout != self.keyboard_active_layout:
                self.keyboard_active_layout = layout
                self.keylayb.config(text=self.translate_word(layout))
                self.keylayb_small_shell.config(text=self.translate_word(layout))

        self.root.after(500, self.get_keyboard_layout)

    def get_deskfiles(self):
        def get_no_display(text):
            if text.find('NoDisplay=') != -1:
                start = text.find('NoDisplay=')
                end = text[start:].find('\n')

                end += start
                start += 10  # skip from NoDisplay=

                if text[start:end] == 'true':
                    return True
            return False

        def check_show_file(file_):
            show = True
            if file_.find('-kde') != -1:
                show = False
            elif file_.find('org.gnome') != -1:
                index = file_.find('org.gnome')
                file_ = file_[:index] + file_[index+10:]
                if file_ in files:
                    show = False
                elif file_.lower() in files:
                    show = False
            elif os.path.isdir(file_):
                show = False
            return show
        
        def find_deskfiles(root_dir):
            sub_deskfiles = []
            if os.path.exists(root_dir):
                dir_ = root_dir
                dirs = list(os.walk(dir_))
                for sub_dirs in dirs:
                    for i in sub_dirs:
                        if type(i) == list:
                            for str_ in i:
                                if len(str_) >= 10:
                                    if str_[-8:] == '.desktop' and \
                                            str_[:9] != 'Uninstall' and \
                                            str_ != 'Online Documentation.desktop':
                                        if sub_dirs[0][-1] == '/':
                                            sub_deskfiles.append(sub_dirs[0]+str_)
                                        else:
                                            sub_deskfiles.append(sub_dirs[0]+'/'+str_)
            return sub_deskfiles

        files = []
        
        local_dir = '{}/.local/share/applications/'.format(os.path.expanduser('~'))
        if os.path.exists(local_dir):
            local_files = find_deskfiles(local_dir)

            for fil in local_files:
                files.append(fil)
                
        if os.path.exists('/var/lib/snapd/desktop/applications/'):
            snap_files = find_deskfiles('/var/lib/snapd/desktop/applications/')

            for fil in snap_files:
                if fil not in files:
                    files.append(fil)

        org_files = find_deskfiles('/usr/share/applications/')

        for fil in org_files:
            if fil not in files:
                files.append(fil)
        deskfiles = []
        
        # check for return back self.apps variable

        for file_ in files:
            show = check_show_file(file_)
            if show:
                try:
                    deskfile = open(file_, 'r')
                except PermissionError:
                    continue
                text = deskfile.read()
                deskfile.close()

                if text.find('Exec=') != -1 and not get_no_display(text):
                    icon_name = self.get_value(text, 'Icon')

                    categories = self.get_value(text, 'Categories').split(';')

                    exec_ = self.get_value(text, 'Exec')
                    if self.get_value(text, 'Terminal') == 'true':
                        exec_ = 'gnome-terminal -- ' + exec_

                    deskfiles.append({
                            'name': self.get_value(text, 'Name'),
                            'file_name': file_,
                            'command': exec_,
                            'icon_name': icon_name,
                            'categories': categories,
                            })
        return deskfiles

    def get_deskfile(self, app_name):
        file_ = '/usr/share/applications/'+app_name
        deskfile = {}

        if file_[-8:] == '.desktop':
            deskfile_ = open(file_, 'r')
            text = deskfile_.read()
            deskfile_.close()

            if text.find('Exec=') != -1:
                icon_name = self.get_value(text, 'Icon')
                icon = self.create_icon(icon_name)

                categories = self.get_value(text, 'Categories').split(';')

                if self.get_value(text, 'Terminal') == 'true':
                    exec_ = 'konsole -e '+self.get_value(text, 'Exec')
                else:
                    exec_ = self.get_value(text, 'Exec')

                deskfile = {
                        'name': self.get_value(text, 'Name'),
                        'file_name': file_,
                        'command': exec_,
                        'icon': icon,
                        'icon_name': icon_name,
                        'categories': categories,
                        }
        return deskfile

    def run(self, command):
        _thread.start_new_thread(os.system, (command+' &',))

    def tick(self):
        self.time1
        # get the current local time from the PC
        time2_ = time.strftime('%H:%M')
        time2 = ''
        for char in time2_:
            time2 += self.translate_word(char)
        # if time string has changed, update it
        if time2 != self.time1:
            self.time1 = time2
            self.clock.config(text=time2)
            self.clock_small_shell.config(text=time2)
        # calls itself every 200 milliseconds
        # to update the time display as needed
        # could use >200 ms, but display gets jerky
        self.clock.after(3000, self.tick)

    def create_awin(self):
        def show_apps(apps):
            def clicked_stack_switche(stack_index):
                for stack in stacks_list:
                    stack.pack_forget()
                icon = self.create_icon('circle-white', (24, 24), shell=True)
                for switche in stack_switches_list:
                    switche['image'] = icon
                icon = self.create_icon('circle-filled', (24, 24), shell=True)
                stack_switches_list[stack_index]['image'] = icon
                stacks_list[stack_index].pack(side=self.START)

            def add_stack():
                stack = ttk.Frame(stacks, style='A.TFrame')
                stacks_list.append(stack)

            def add_stack_switche(stack_index):
                icon = self.create_icon('circle-white', (24, 24), shell=True)
                switche = ttk.Button(
                    stack_switches,
                    command=lambda si=stack_index: clicked_stack_switche(si),
                    style='AS.TButton',
                    cursor='hand2',
                    )
                if icon:
                    switche['image'] = icon
                else:
                    switche['text'] = self.translate_word(str(stack_index+1))
                switche.pack(side=tk.LEFT, pady=5, padx=5)
                stack_switches_list.append(switche)

            stack_switches = ttk.Frame(fapps, style='A.TFrame')
            stack_switches.pack(side=tk.BOTTOM, pady=6)
            stack_switches_list = []

            stacks = ttk.Frame(fapps, style='A.TFrame')
            stacks.pack(side=tk.TOP, fill=tk.Y)
            stacks_list = []
            add_stack()

            row, column = 0, 0
            max_row = (self.root.winfo_screenheight()- \
            self.height_root_window) // 120

            stack_index = 0

            for app in apps:
                if row == max_row and column == 0:
                    add_stack()
                    column = 0
                    row = 0
                    if stack_index == 0:
                        add_stack_switche(0)
                        icon = self.create_icon('circle-filled', (24, 24), shell=True)
                        stack_switches_list[0]['image'] = icon
                    stack_index += 1
                    add_stack_switche(stack_index)

                button = ttk.Button(
                    stacks_list[stack_index],
                    text=app["name"],
                    command=lambda c=app['command']: self.click_button_app(c),
                    compound=tk.TOP,
                    style='A.TButton',
                    cursor='hand2'
                    )

                icon = self.create_icon(app['icon_name'], (48, 48))
                if icon != '':
                    button['image'] = icon

                button.grid(row=row, column=column, pady=12, padx=8)   # ~max 15, 15

                if column == 2:
                    column = 0
                    row += 1
                else:
                    column += 1

            stacks_list[0].pack()

        def check_mouse():
            x, y = self.click_pos_x, self.click_pos_y
            
            if self.new_click:
                if y > (
                    self.root.winfo_screenheight()-self.height_root_window
                        ):
                    self.animation_hide_awin()

                elif self.geometry_direction == '+':
                    if x > 640:
                        self.animation_hide_awin()

                elif self.geometry_direction == '-':
                    if x < self.root.winfo_screenwidth() - 640:
                        self.animation_hide_awin()
            try:
                self.awin.after('400', check_mouse)
            except AttributeError:
                return

        def animation_show_awin(new_width=0):
            self.awin.geometry(
                '{width}x{height}{direction}{xoffset}-{yoffset}'.format(
                    width=640,
                    height=(
                        self.root.winfo_screenheight()-self.height_root_window
                    ),
                    direction=self.geometry_direction,
                    xoffset=-(640-new_width),
                    yoffset=self.height_root_window,
                    )
                )
            if new_width < 640:
                self.awin.after(5, animation_show_awin, new_width+20)

        self.awin = tk.Toplevel()
        self.awin.geometry(
            '{width}x{height}{direction}{xoffset}-{yoffset}'.format(
                width=640,
                height=self.root.winfo_screenheight()-self.height_root_window,
                direction=self.geometry_direction,
                xoffset=-640,
                yoffset=self.height_root_window,
                )
            )
        self.awin.wm_attributes('-type', 'dock')
        self.awin.wm_attributes('-alpha', '0.9')
        self.awin.configure(background="#333")

        # body
        body = ttk.Frame(self.awin, style="A.TFrame")
        body.pack(side=self.END, fill=tk.BOTH, expand=1)

        fapps = ttk.Frame(body, style='A.TFrame')

        self.apps = self.get_deskfiles()
        apps = []
        for app in self.apps:
            if 'Settings' not in app['categories']:
                apps.append(app)

        histories_dir = '{}/.config/navar/histories/'.format(
            os.path.expanduser('~')
            )

        try:
            file = open(histories_dir+'apps-use.txt', 'r')
            text = file.read()
            file.close()
        except FileNotFoundError:
            text = None

        if text:
            apps_num = {}
            
            items = text.split('\n')
            if not items[-1]:
                items = items[:-1]
            
            apps_num = {}
            values = []
            for item in items:
                item = item.split(':')
                try:
                    value = int(item[-1])
                except:
                    value = 0
                    file = open(histories_dir+'apps-use.txt', 'w')
                    file.close()
                apps_num[item[0]] = value
                if value not in values:
                    values.append(value)
            values.sort()
            values.reverse()

            apps_cmd = []
            for value in values:
                for app in apps_num:
                    if apps_num[app] == value:
                        apps_cmd.append(app)

            apps_list = []
            for cmd in apps_cmd:
                for app in apps:
                    if app['command'] == cmd:
                        apps_list.append(app)
            for app in apps:
                if app['command'] not in apps_cmd:
                    apps_list.append(app)

            show_apps(apps_list)
        else:
            show_apps(apps)
        
        animation_show_awin()

        fapps.pack(fill=tk.BOTH, expand=1)
        
        self.new_click = False
        check_mouse()

    def animation_hide_awin(self, new_width=0):
        try:
            self.awin.geometry(
                '{width}x{height}{direction}{xoffset}-{yoffset}'.format(
                    width=640,
                    height=(
                        self.root.winfo_screenheight()-self.height_root_window
                        ),
                    direction=self.geometry_direction,
                    xoffset=new_width,
                    yoffset=self.height_root_window,
                    )
                )
            if new_width > -640:
                self.awin.after(5, self.animation_hide_awin, new_width-20)
            else:
                self.awin.destroy()
                del self.awin
        except AttributeError:
            return

    def show_hide_awin(self):
        try:
            self.awin
            self.animation_hide_awin()
        except AttributeError:
            self.hide_all_wins()
            self.create_awin()

    def shutdown(self):
        self.animation_hide_root(end_cmd="systemctl poweroff")

    def reboot(self):
        self.animation_hide_root(end_cmd="systemctl reboot")

    def logout(self):
        self.animation_hide_root(end_cmd="openbox --exit")

    def lock(self):
        def check_display_manager(text):
            if text.find('/usr/sbin/lightdm') != -1:
                return 'lightdm'
            if text.find('/usr/sbin/gdm3') != -1:
                return 'gdm3'
            else:
                return 'other'

        c = r"ps auxf | awk '{print $11}' | \grep --color -e dm$ -e slim$"
        pipe = Popen(c, shell=True, stdout=PIPE)
        text = pipe.communicate()[0].decode('utf-8')
        display_manager = check_display_manager(text)

        self.animation_hide_smwin()

        if display_manager == 'lightdm':
            os.system("dm-tool lock")
        elif display_manager == 'gdm3':
            os.system("gnome-screensaver-command -l")

    def click_button_app(self, command):
        self.animation_hide_awin()
        self.run(command)
        self.set_app_history(command)
        
    def set_app_history(self, command):
        dir_ = '{}/.config/navar/histories/'.format(
            os.path.expanduser('~')
            )
        if not os.path.exists(dir_):
            os.system('mkdir -p {}'.format(dir_))

        if not os.path.exists(dir_+'apps-use.txt'):
            file = open(dir_+'apps-use.txt', 'w')
            file.close()
        
        file = open(dir_+'apps-use.txt', 'r')
        text = file.read()
        file.close()

        index = text.find(command)
        if index != -1:
            items_list = text.split('\n')
            if not items_list[-1]:
                items_list = items_list[:-1]
            
            items = []
            for i in items_list:
                items.append(i.split(':'))

            text = ''
            for item in items:
                if command == item[0]:
                    item[1] = str(int(item[1])+1)
                text = '{}{}:{}\n'.format(text, item[0], item[1])
        else:
            text = '{}{}:1\n'.format(text, command)
        
        file = open(dir_+'apps-use.txt', 'w')
        file.write(text)
        file.close()
    
    def click_button_setting(self, command):
        self.animation_hide_swin()
        self.run(command)

    def get_value(self, text, item):
        item_lang = '\n' + item + '[' + self.default_lang + ']' + '='
        if text.find(item_lang) != -1:
            item_ = item_lang
            lang = self.default_lang
        else:
            item_ = '\n'+item+'='
            lang = ''

        start = text.find(item_)
        if start != -1:
            start += len(item_)  # skip from item
            end = text[start:].find('\n')
            end += start

            result = text[start:end]

            if item == 'Exec' and (result[-2:] == '%U' or result[-2:] == '%u'):
                result = result[:-3]
            if item == 'Exec' and (result[-2:] == '%F' or result[-2:] == '%f'):
                result = result[:-3]
            if lang in self.rtl_langs:
                result = self.setrtl(result)
        else:
            result = ''
        return result

    def get_icon(self, icon_name, size):
        icon_theme = Gtk.IconTheme.get_default()
        icon = icon_theme.lookup_icon(icon_name, size, 0)
        if icon:
            icon = icon.get_filename()
            return icon
        else:
            return ''
    
    def get_shell_icon(self, icon_name):
        icon_theme = 'base-white'
        return '/usr/share/navar/icons/shell/'+icon_theme+'/'+icon_name+'.png'

    def convert2png(self, icon, icon_name):
        icons_dir = '{}/.config/navar/icons/'.format(os.path.expanduser('~'))
        if not os.path.exists(icons_dir):
            os.system('mkdir -p '+icons_dir)

        outfile = icons_dir+icon_name+'.png'

        if not os.path.exists(outfile):
            os.system(
                "convert -background blue -density 200 {previous} {png}".format(
                    previous=icon,
                    png=outfile,
                ))
            return outfile
        else:
            return outfile

    def reverse(self, string):
        res = ''
        for i in range(len(string), 0, -1):
            res += string[i-1]
        return res

    def create_icon(self, icon_name, size=(48, 48), shell=False):
        def create_svg_image(icon, size):
            handle = Rsvg.Handle()
            svg = handle.new_from_file(icon)
            width = svg.get_dimensions().width
            height = svg.get_dimensions().height
            surface = cairo.ImageSurface(
                cairo.FORMAT_ARGB32,
                int(width),
                int(height)
                )
            context = cairo.Context(surface)
            context.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
            svg.render_cairo(context)
            tk_image = ImageTk.PhotoImage('RGBA')
            image = Image.frombuffer(
                'RGBA',
                (width, height),
                bytes(surface.get_data()),
                'raw',
                'BGRA',
                0,
                1
                )
            if image.size != size:
                image = image.resize(size, Image.ANTIALIAS)
            tk_image.paste(image)
            return(tk_image)

        def create_image(icon, size):
            icon = Image.open(icon)
            if icon.size != size:
                icon = icon.resize(size, Image.ANTIALIAS)
            icon = ImageTk.PhotoImage(icon)
            return icon

        if not icon_name:
            return ''
        if icon_name.find('/') != -1:
            if os.path.exists(icon_name):
                icon = icon_name

                icon_name = self.reverse(icon_name)
                icon_name = icon_name[:icon_name.find('/')]
                icon_name = self.reverse(icon_name)
            else:
                return ''
        else:
            if icon_name != '':
                if shell:
                    icon = self.get_shell_icon(icon_name)
                else:
                    icon = self.get_icon(icon_name, size[0])
            else:
                icon = ''

        if icon[-4:] == '.xpm':
            icon = self.convert2png(icon, icon_name)

        if icon != '':
            exist = False
            if not shell:
                if icon in self.icons:
                    if self.icons[icon][1] == size:
                        exist = True
                if not exist:
                    if icon[-4:] == '.svg':
                        image = create_svg_image(icon, size)
                        self.icons[icon] = [image, size]
                    else:
                        image = create_image(icon, size)
                        self.icons[icon] = [image, size]
                    return image
                else:
                    return self.icons[icon][0]
            else:
                if icon in self.shell_icons:
                    if self.shell_icons[icon][1] == size:
                        exist = True
                if not exist:
                    if icon[-4:] == '.svg':
                        image = create_svg_image(icon, size)
                        self.shell_icons[icon] = [image, size]
                    else:
                        image = create_image(icon, size)
                        self.shell_icons[icon] = [image, size]
                    return image
                else:
                    return self.shell_icons[icon][0]
        else:
            return ''

    def show_hide_window(self, w):
        states = self.ewmh.getWmState(w, str=True)
        states = list(states)
        aw = self.ewmh.getActiveWindow()
        if aw:
            aw_title = self.ewmh.getWmName(aw).decode('utf-8')
            aw_title = self.setrtl(aw_title)
        else:
            aw_title = ''
        title = self.ewmh.getWmName(w).decode('utf-8')
        title = self.setrtl(title)
        if aw_title == title:
            if len(states) == 0:
                self.ewmh.setWmState(w, 1, '_NET_WM_STATE_HIDDEN')
            else:
                showed = True
                for state in states:
                    if state == '_NET_WM_STATE_HIDDEN':
                        showed = False
                if showed:
                    self.ewmh.setWmState(w, 1, '_NET_WM_STATE_HIDDEN')
                elif not showed:
                    self.ewmh.setWmState(w, 0, '_NET_WM_STATE_HIDDEN')
                    self.ewmh.setActiveWindow(w)
        else:
            if len(states) == 0:
                self.ewmh.setActiveWindow(w)
            else:
                showed = True
                for state in states:
                    if state == '_NET_WM_STATE_HIDDEN':
                        showed = False
                if showed:
                    self.ewmh.setActiveWindow(w)
                elif not showed:
                    self.ewmh.setWmState(w, 0, '_NET_WM_STATE_HIDDEN')
                    self.ewmh.setActiveWindow(w)
        self.show_hide_windows_list()

        self.ewmh.display.flush()
    
    def show_desktop(self, wl):    # بعدا ممکنه پنهان شدن هم اضافه بشه
        for w in wl:
            states = self.ewmh.getWmState(w, str=True)
            states = list(states)
            
            if '_NET_WM_STATE_HIDDEN' not in states:
                self.ewmh.setWmState(w, 1, '_NET_WM_STATE_HIDDEN')

    def setrtl(self, text):
        text = arabic_reshaper.reshape(text)
        text = get_display(text)
        return text

    def get_proc_with_pid(self, pid):
        c = "ps -A | awk {'print $1; print $4'}"
        pipe = Popen(c, shell=True, stdout=PIPE)
        text = pipe.communicate()[0].decode('utf-8')

        index = text.find(str(pid))
        if index != -1:
            index = text[index:].find('\n') + index
            proc = text[index+1:text[index+1:].find('\n') + index + 1]

            return proc

    def get_icon_name_with_exec(self, proc):
        if proc[-1] == '-':
            proc = proc[:-1]
        for app in self.apps:
            command_ = app['command']

            if command_[:14] != 'gnome-terminal':
                command = ''
                for c in command_:  # delete options
                    if c == ' ':
                        break
                    command += c
            else:
                command = command_

            if command.find('/') != -1:
                command = self.reverse(command)
                command = command[:command.find('/')]
                command = self.reverse(command)

            if len(command) > 15:
                # !!!! what => gnome system monitor => gnome-system-mo
                command = command[:15]

            if command == proc:
                return app['icon_name']

    def translate_word(self, word, lang=None):
        if not lang:
            lang = self.default_lang
        try:
            member = self.dictionary[word]
            word = member[lang]
            if lang in self.rtl_langs:
                word = self.setrtl(word)
            return word
        except KeyError:
            return word


if __name__ == '__main__':
    Main()
