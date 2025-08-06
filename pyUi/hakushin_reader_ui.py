import tkinter as tk
from pyHakushinParsing import hakushin_json_fetcher as hf
from pyCheckNewPages import selector
#global param
button_width = 11
submit = "Submit"
clear = "Clear"
wraplength = 250
cnpj_params = (character, relicset, lightcone) = ("character", "relicset", "lightcone")
new_queries = []
show_names = False

#button functions
#cnpj_checkbox_toggle
def cnpj_checkbox_toggle(param):
    global show_names
    show_names = param

#hakuj_functions
def hakuj_event(hakuj_entry : tk.Entry, hakuj_result_label : tk.Label, hakuj_clear_button : tk.Button):
    ids_temp = [id for id in hakuj_entry.get().replace(",", " ").split(" ") if id not in [" ", ""]]
    ids = []
    [ids.append(id) for id in ids_temp if id not in ids]
    results = hf.main(ids)
    hakuj_entry.delete(0, tk.END)
    if results == []: answer = ""
    elif len(results) == 1: answer = results[0]
    else:
        answer=""
        for i in range(0, len(results)-1):
            answer = answer + results[i] + '\n'
        answer = answer + results[-1]
    hakuj_result_label["text"] = answer
    hakuj_result_label.pack()
    hakuj_clear_button.pack()

def hakuj_clear(hakuj_result_label : tk.Label, hakuj_clear_button : tk.Button):
    hakuj_result_label["text"] = ''
    hakuj_result_label.pack_forget()
    hakuj_clear_button.pack_forget()

#cnpj_functions
def cnpj_add_or_remove_param(param : str, cnpj_label : tk.Label):
    text : str = cnpj_label["text"]
    if param not in text:
        if text in ["", '']: text = param
        else: text = f"{text} {param}"
    else:
        text = text.replace(param, "").strip()
    cnpj_label["text"] = text

def cnpj_add_all_params(cnpj_label : tk.Label):
    text : str = cnpj_label["text"]
    for param in cnpj_params:
        if param not in text:
            if text in ["", '']: text = param
            else: text = f"{text} {param}"
    cnpj_label["text"] = text

def cnpj_remove_all_params(cnpj_label : tk.Label):
    cnpj_label["text"] = ''

def submit_cnpj_query(cnpj_label : tk.Label, cnpj_move_button : tk.Button, cnpj_results_label : tk.Label, cnpj_clear_button : tk.Button):
    global new_queries
    display_move = False
    params = cnpj_label["text"].split(" ")
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
    cnpj_label["text"] = ""
    cnpj_results_label["text"] = answer
    cnpj_results_label.grid(columnspan=3)
    if display_move: 
        cnpj_move_button.grid(row=5, column=1)
        cnpj_clear_button.grid(row=6, column=1)
    else:
        cnpj_clear_button.grid(row=5, column=1)

def move_new_ids_to_hakuj(cnpj_results_label : tk.Label, hakuj_entry : tk.Entry, cnpj_move_button : tk.Button, cnpj_clear_button : tk.Button):
    ids = " ".join(new_queries)
    current_entry_text = hakuj_entry.get()
    if current_entry_text != '':
        if current_entry_text[-1] != " ":
            hakuj_entry.insert(tk.END, " ")
    hakuj_entry.insert(tk.END, ids)
    
    if show_names: cnpj_move_button.grid_forget()
    else: cnpj_clear(cnpj_results_label, cnpj_move_button, cnpj_clear_button)

def cnpj_clear(cnpj_results_label : tk.Label, cnpj_move_button : tk.Button, cnpj_clear_button : tk.Button):
    cnpj_results_label["text"] = ""
    cnpj_results_label.grid_forget()
    cnpj_move_button.grid_forget()
    cnpj_clear_button.grid_forget()

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

#hakuj.py integration
def set_up_hakuj_frame(window : tk.Tk):
    hakuj_frame = get_frame(window, 0)

    hakuj_label = tk.Label(master=hakuj_frame, text="Enter IDs:", wraplength=wraplength)
    hakuj_label.pack()

    hakuj_entry = tk.Entry(master=hakuj_frame)
    hakuj_entry.pack()

    hakuj_button = tk.Button(master=hakuj_frame, text=submit, command= lambda: hakuj_event(hakuj_entry, hakuj_result_label, hakuj_clear_button), width=button_width)
    hakuj_button.pack()

    hakuj_result_label = tk.Label(master=hakuj_frame, wraplength=wraplength)
    hakuj_result_label.pack_forget()

    hakuj_clear_button = tk.Button(master=hakuj_frame, text=clear, width=button_width, command= lambda: hakuj_clear(hakuj_result_label, hakuj_clear_button))
    hakuj_clear_button.pack_forget()

    return hakuj_frame, hakuj_entry

#cnpj.py integration
def set_up_cnpj_frame(window : tk.Tk, hakuj_entry : tk.Entry):
    global show_names
    cnpj_frame = get_frame(window, 1)

    cnpj_header_label = tk.Label(master=cnpj_frame, text="Select what to get updates for:", wraplength=wraplength)
    cnpj_header_label.grid(columnspan=3, row=0)

    cnpj_label = tk.Label(master=cnpj_frame, wraplength=wraplength)
    cnpj_label.grid(columnspan=2, column=0, row=1)

    checkbox = tk.BooleanVar()
    cnpj_display_names_check = tk.Checkbutton(master=cnpj_frame, text="Names", variable=checkbox, onvalue=True, offvalue=False, command= lambda: cnpj_checkbox_toggle(checkbox.get()))
    cnpj_display_names_check.grid(column=2, row=1)

    cnpj_btn_c = tk.Button(master=cnpj_frame, text="Characters", command= lambda: cnpj_add_or_remove_param(character, cnpj_label), width=button_width)
    cnpj_btn_r = tk.Button(master=cnpj_frame, text="Relics", command= lambda: cnpj_add_or_remove_param(relicset, cnpj_label), width=button_width)
    cnpj_btn_l = tk.Button(master=cnpj_frame, text="Light Cones", command= lambda: cnpj_add_or_remove_param(lightcone, cnpj_label), width=button_width)
    cnpj_btn_c.grid(row=2, column=0)
    cnpj_btn_r.grid(row=2, column=1)
    cnpj_btn_l.grid(row=2, column=2)

    cnpj_add_all_btn = tk.Button(master=cnpj_frame, text="Add All", command= lambda: cnpj_add_all_params(cnpj_label), width=button_width)
    cnpj_remove_all_btn = tk.Button(master=cnpj_frame, text="Remove All", command= lambda: cnpj_remove_all_params(cnpj_label), width=button_width)
    cnpj_add_all_btn.grid(row=3, column=0)
    cnpj_remove_all_btn.grid(row=3, column=1)

    cnpj_submit = tk.Button(master=cnpj_frame, text=submit, command=lambda: submit_cnpj_query(cnpj_label, cnpj_move_button, cnpj_results_label, cnpj_clear_button), width=button_width)
    cnpj_submit.grid(row=3, column=2)

    cnpj_results_label = tk.Label(master=cnpj_frame, wraplength=wraplength) 
    cnpj_move_button = tk.Button(master=cnpj_frame, text="Query IDs?", command=lambda: move_new_ids_to_hakuj(cnpj_results_label, hakuj_entry, cnpj_move_button, cnpj_clear_button), width=button_width)
    cnpj_clear_button = tk.Button(master=cnpj_frame, text=clear, width=button_width, command=lambda: cnpj_clear(cnpj_results_label, cnpj_move_button, cnpj_clear_button))

    cnpj_move_button.grid_forget()
    cnpj_clear_button.grid_forget()
    cnpj_results_label.grid_forget()

    return cnpj_frame

def start_up():

    window = tk.Tk()
    window.title("Hakush.in Tool")
    window.columnconfigure(0, weight=1, minsize=wraplength)
    window.rowconfigure(0, weight=1, minsize=20)
    window.rowconfigure(1, weight=1, minsize=20)

    # scrollbar = tk.Scrollbar(master=window)
    # scrollbar.grid(row=0, column=1, sticky="e")
    # scrollbar.config(command=tk.YView)

    #hakuj.py integration
    _, hakuj_entry = set_up_hakuj_frame(window)

    #cnpj.py integration
    _ = set_up_cnpj_frame(window, hakuj_entry)

    window.mainloop()

if __name__ == "__main__":
    start_up() #sys.argv[1:] #first arg is always file name, so skip it