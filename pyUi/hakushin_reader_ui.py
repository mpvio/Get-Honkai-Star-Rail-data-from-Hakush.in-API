import tkinter as tk
from pyHakushinParsing import hakushin_json_fetcher as hf
from pyCheckNewPages import selector
from pyUi.uiGlobals import *

#hakuApi_functions
def hakuApi_submitQueryEvent(hakuApi_entry : tk.Entry, hakuApi_result_label : tk.Label, hakuApi_clear_button : tk.Button):
    ids_temp = [id for id in hakuApi_entry.get().replace(",", " ").split(" ") if id not in [" ", ""]]
    ids = []
    [ids.append(id) for id in ids_temp if id not in ids]
    results = hf.main(ids)
    hakuApi_entry.delete(0, tk.END)
    if results == []: answer = ""
    elif len(results) == 1: answer = results[0]
    else:
        answer=""
        for i in range(0, len(results)-1):
            answer = answer + results[i] + '\n'
        answer = answer + results[-1]
    hakuApi_result_label["text"] = answer
    hakuApi_result_label.pack()
    hakuApi_clear_button.pack()

def hakuApi_clearResultLabel(hakuApi_result_label : tk.Label, hakuApi_clear_button : tk.Button):
    hakuApi_result_label["text"] = ''
    hakuApi_result_label.pack_forget()
    hakuApi_clear_button.pack_forget()

#checkNewPages_functions
def checkNewPages_add_or_remove_param(param : str, checkNewPages_label : tk.Label):
    text : str = checkNewPages_label["text"]
    if param not in text:
        if text in ["", '']: text = param
        else: text = f"{text} {param}"
    else:
        text = text.replace(param, "").strip()
    checkNewPages_label["text"] = text

def checkNewPages_add_all_params(checkNewPages_label : tk.Label):
    text : str = checkNewPages_label["text"]
    for param in checkNewPages_params:
        if param not in text:
            if text in ["", '']: text = param
            else: text = f"{text} {param}"
    checkNewPages_label["text"] = text

def checkNewPages_remove_all_params(checkNewPages_label : tk.Label):
    checkNewPages_label["text"] = ''

def submit_checkNewPages_query(checkNewPages_label : tk.Label, checkNewPages_move_button : tk.Button, checkNewPages_results_label : tk.Label, checkNewPages_clear_button : tk.Button):
    global new_queries
    display_move = False
    params = checkNewPages_label["text"].split(" ")
    if len(params) == 1 and params[0] in ["", '']: return
    results = selector(params, True)
    answer=""
    if results == {}:
        answer="None"
    else:
        new_queries = results.keys()
        if show_names:
            answer = " ".join(f"{k}: {v}" for k, v in results.items())
        else:
            answer = " ".join(f"{k}" for k in new_queries)
        if len(answer) > 1000:
            answer = answer[:1000] + "..."
        display_move = True
    checkNewPages_label["text"] = ""
    checkNewPages_results_label["text"] = answer
    checkNewPages_results_label.grid(columnspan=3)
    if display_move: 
        checkNewPages_move_button.grid(row=5, column=1)
        checkNewPages_clear_button.grid(row=6, column=1)
    else:
        checkNewPages_clear_button.grid(row=5, column=1)

def move_new_ids_to_hakuApi(checkNewPages_results_label : tk.Label, hakuApi_entry : tk.Entry, checkNewPages_move_button : tk.Button, checkNewPages_clear_button : tk.Button):
    ids = " ".join(new_queries)
    current_entry_text = hakuApi_entry.get()
    if current_entry_text != '':
        if current_entry_text[-1] != " ":
            hakuApi_entry.insert(tk.END, " ")
    hakuApi_entry.insert(tk.END, ids)
    
    if show_names: checkNewPages_move_button.grid_forget()
    else: checkNewPages_clear(checkNewPages_results_label, checkNewPages_move_button, checkNewPages_clear_button)

def checkNewPages_clear(checkNewPages_results_label : tk.Label, checkNewPages_move_button : tk.Button, checkNewPages_clear_button : tk.Button):
    checkNewPages_results_label["text"] = ""
    checkNewPages_results_label.grid_forget()
    checkNewPages_move_button.grid_forget()
    checkNewPages_clear_button.grid_forget()

#init functions
def get_frame(window : tk.Tk, row=0):
    new_frame = tk.Frame(
        master=window, 
        relief=tk.RAISED, 
        borderwidth=1)
    new_frame.grid(
        row=row,
        column=0,
        sticky = "nsew")
    return new_frame

#hakuApi.py integration
#hakuApi = hakushin_json
def set_up_hakuApi_frame(window : tk.Tk):
    hakuApi_frame = get_frame(window, 0)

    hakuApi_label = tk.Label(master=hakuApi_frame, text="Enter IDs:", wraplength=wraplength)
    hakuApi_label.pack()

    # restrict entry to numbers and spaces
    def validate_input(text: str):
        if text == "": return True
        return all(c.isdigit() or c == " " for c in text)

    # %P = represents value being entered (i.e. what's being passed to validate_input as "text")
    valid_command = (window.register(validate_input), '%P')
    # key = validatecommand is run whenever entry is edited
    hakuApi_entry = tk.Entry(master=hakuApi_frame, validate="key", validatecommand=valid_command)
    hakuApi_entry.pack(fill="x", padx=5)

    hakuApi_button = tk.Button(master=hakuApi_frame, text=submit, command= lambda: hakuApi_submitQueryEvent(hakuApi_entry, hakuApi_result_label, hakuApi_clear_button), width=button_width)
    hakuApi_button.pack()

    hakuApi_result_label = tk.Label(master=hakuApi_frame, wraplength=wraplength)
    hakuApi_result_label.pack_forget()

    hakuApi_clear_button = tk.Button(master=hakuApi_frame, text=clear, width=button_width, command= lambda: hakuApi_clearResultLabel(hakuApi_result_label, hakuApi_clear_button))
    hakuApi_clear_button.pack_forget()

    return hakuApi_frame, hakuApi_entry

#checkNewPages.py integration
#checkNewPages = check_new_pages_json
def set_up_checkNewPages_frame(window : tk.Tk, hakuApi_entry : tk.Entry):
    global show_names
    checkNewPages_frame = get_frame(window, 1)

    checkNewPages_header_label = tk.Label(master=checkNewPages_frame, text="Select what to get updates for:", wraplength=wraplength)
    checkNewPages_header_label.grid(columnspan=3, row=0)

    checkNewPages_label = tk.Label(master=checkNewPages_frame, wraplength=wraplength)
    checkNewPages_label.grid(columnspan=2, column=0, row=1)

    checkbox = tk.BooleanVar()
    checkNewPages_display_names_check = tk.Checkbutton(master=checkNewPages_frame, text="Names", variable=checkbox, onvalue=True, offvalue=False, command= lambda: checkNewPages_checkbox_toggle(checkbox.get()))
    checkNewPages_display_names_check.grid(column=2, row=1)

    checkNewPages_btn_c = tk.Button(master=checkNewPages_frame, text="Characters", command= lambda: checkNewPages_add_or_remove_param(character, checkNewPages_label), width=button_width)
    checkNewPages_btn_r = tk.Button(master=checkNewPages_frame, text="Relics", command= lambda: checkNewPages_add_or_remove_param(relicset, checkNewPages_label), width=button_width)
    checkNewPages_btn_l = tk.Button(master=checkNewPages_frame, text="Light Cones", command= lambda: checkNewPages_add_or_remove_param(lightcone, checkNewPages_label), width=button_width)
    checkNewPages_btn_c.grid(row=2, column=0)
    checkNewPages_btn_r.grid(row=2, column=1)
    checkNewPages_btn_l.grid(row=2, column=2)

    checkNewPages_add_all_btn = tk.Button(master=checkNewPages_frame, text="Add All", command= lambda: checkNewPages_add_all_params(checkNewPages_label), width=button_width)
    checkNewPages_remove_all_btn = tk.Button(master=checkNewPages_frame, text="Remove All", command= lambda: checkNewPages_remove_all_params(checkNewPages_label), width=button_width)
    checkNewPages_add_all_btn.grid(row=3, column=0)
    checkNewPages_remove_all_btn.grid(row=3, column=1)

    checkNewPages_submit = tk.Button(master=checkNewPages_frame, text=submit, command=lambda: submit_checkNewPages_query(checkNewPages_label, checkNewPages_move_button, checkNewPages_results_label, checkNewPages_clear_button), width=button_width)
    checkNewPages_submit.grid(row=3, column=2)

    checkNewPages_results_label = tk.Label(master=checkNewPages_frame, wraplength=wraplength) 
    checkNewPages_move_button = tk.Button(master=checkNewPages_frame, text="Query IDs?", command=lambda: move_new_ids_to_hakuApi(checkNewPages_results_label, hakuApi_entry, checkNewPages_move_button, checkNewPages_clear_button), width=button_width)
    checkNewPages_clear_button = tk.Button(master=checkNewPages_frame, text=clear, width=button_width, command=lambda: checkNewPages_clear(checkNewPages_results_label, checkNewPages_move_button, checkNewPages_clear_button))

    checkNewPages_move_button.grid_forget()
    checkNewPages_clear_button.grid_forget()
    checkNewPages_results_label.grid_forget()

    for i in range(3):  # add weights to columns so they move when window is widened
        checkNewPages_frame.columnconfigure(i, weight=1)

    return checkNewPages_frame

def start_up():

    window = tk.Tk()
    window.title("Hakush.in Tool")
    window.columnconfigure(0, weight=1, minsize=wraplength)
    window.rowconfigure(0, weight=1, minsize=20)
    window.rowconfigure(1, weight=1, minsize=20)

    # scrollbar = tk.Scrollbar(master=window)
    # scrollbar.grid(row=0, column=1, sticky="e")
    # scrollbar.config(command=tk.YView)

    #hakuApi.py integration
    _, hakuApi_entry = set_up_hakuApi_frame(window)

    #checkNewPages.py integration
    _ = set_up_checkNewPages_frame(window, hakuApi_entry)

    window.mainloop()

if __name__ == "__main__":
    start_up() #sys.argv[1:] #first arg is always file name, so skip it