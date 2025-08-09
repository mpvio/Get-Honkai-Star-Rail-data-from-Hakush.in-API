#global params
button_width = 11
submit = "Submit"
clear = "Clear"
wraplength = 250
checkNewPages_params = (character, relicset, lightcone) = ("character", "relicset", "lightcone")
new_queries = []
show_names = False

#button functions
#checkNewPages_checkbox_toggle
def checkNewPages_checkbox_toggle(param):
    global show_names
    show_names = param