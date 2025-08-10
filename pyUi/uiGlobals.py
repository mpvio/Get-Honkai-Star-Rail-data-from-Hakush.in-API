import tkinter as tk
from tkinter import font
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

# get list window
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





