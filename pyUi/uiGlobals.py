import tkinter as tk
from tkinter import font
from pyFileIO.fileReadWriteFuncs import jsonListToStr
import pyHakushinParsing.constants as c
from tkinter.scrolledtext import ScrolledText

#global params
button_width = 12
submit = "Submit"
clear = "Clear"
wraplength = 250
checkNewPages_params = (character, relicset, lightcone) = ("character", "relicset", "lightcone")
new_queries = []
custom_centered_tag = "centered"

# close window
def close_window(root: tk.Frame):
    root.destroy()

# get text list window
def showList(window: tk.Tk, func: str):
    if func == c.shortlist: ls = c.get_shortlist()
    else: ls = c.get_blackList()
    child = tk.Toplevel(window)
    # set list to scroll
    scroll = ScrolledText(child, height=8, width=button_width*3, wrap=tk.WORD, font=font.nametofont("TkDefaultFont"))
    scroll.config(state=tk.NORMAL) # enable text entry
    content = '\n'.join(ls)
    scroll.insert(tk.END, content) # display results
    scroll.tag_configure(custom_centered_tag) # center-align text content
    scroll.pack(fill="both", expand=True, padx=5) # pack scroll
    saveBtn = tk.Button(child, text="Save", width=int(button_width*1.5), command= lambda: [c.writeTxtList(func, scroll.get('1.0', tk.END)), close_window(child)])
    closeBtn = tk.Button(child, text="Close", width=int(button_width*1.5), command=lambda: close_window(child))
    saveBtn.pack(side="left", fill="x")
    closeBtn.pack(side="right", fill="x")

def putItemsOnScroll(scroll: ScrolledText, page: str):
    from pyUi.hakushin_reader_ui import updateScroll
    content = jsonListToStr(page)
    updateScroll(scroll, content)

def showItems(window: tk.Tk):
    from pyUi.hakushin_reader_ui import createScroll
    child = tk.Toplevel(window)
    child.resizable(True, True)
    # configure expansion weights (which row/ column expands more)
    child.grid_rowconfigure(1, weight=1) # scrolltext row expands vertically, buttons stay the same
    child.grid_columnconfigure((0, 1, 2), weight=1) # all components spread out horizontally
    # buttons
    chButton = tk.Button(child, text=f"{c.CHARACTER.capitalize()}s", width=button_width, command=lambda: putItemsOnScroll(scroll, c.CHARACTER))
    lcButton = tk.Button(child, text=f"{c.LIGHTCONE.capitalize()}s", width=button_width, command=lambda: putItemsOnScroll(scroll, c.LIGHTCONE))
    rlButton = tk.Button(child, text=f"{c.RELICSET.capitalize()}s", width=button_width, command=lambda: putItemsOnScroll(scroll, c.RELICSET))
    chButton.grid(column=0, row=0)
    lcButton.grid(column=1, row=0)
    rlButton.grid(column=2, row=0)
    # scrolledText
    scroll = createScroll(child)
    scroll.grid(row=1, column=0, columnspan=3, sticky=tk.NSEW, padx=5)
    # close button
    closeBtn = tk.Button(child, text="Close", width=button_width, command=lambda: close_window(child))
    closeBtn.grid(column=0, row=2, columnspan=3)






