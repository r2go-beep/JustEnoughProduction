#last updated: 4/16/21
import tkinter as tk
from tkinter import ttk
from tkinter.ttk import *
from recipeManager import JSONIndexer


class Main(tk.Frame):
        def __init__(self, master):
                master.title('JustEnoughProduction')
                master.geometry('500x500')
                self.master = master

                style = ttk.Style()
                style.configure('recipe.TFrame', background = '#ffffff', relief = tk.RIDGE, width = 2)
                style.configure('machine.TMenubutton', background = '#dedede', width = 20)
                style.configure('default.TMenubutton', background = '#dedede')
                style.configure('info_box.TLabel', background = '#F0F8FF', borderwidth=1, relief='solid', width =  25)
                style.configure('item.TLabel', background = '#ff7878', borderwidth=1, relief='solid', width =  25)
                style.configure('fluid.TLabel', background = '#78d4ff', borderwidth=1, relief='solid', width =  25)
                style.configure('transparent.TLabel', alpha = .5)
                style.configure('exit_button.TButton', background = '#d92929', width = 0)

                self.item_fluid_dict = {}
                def load_and_index():
                        self.item_fluid_dict = JSONIndexer.index(self, file_entry.get())

                #-------------------------------
                #TOP MENU
                top_menu_frame = Frame(root, )
                top_menu_frame.pack()

                #button for a new recipe node
                new_crafting_node_button=Button(top_menu_frame,style = 'default.TButton',text='New Crafting Node',command=lambda:self.new_recipe(''))
                new_crafting_node_button.grid( row = 0, column = 0 )

                #read and index from file
                file_entry=Entry(top_menu_frame, )
                file_entry.insert(0,'2021-01-09_14-14-16.json')#default to json file for GTNH 2.1.0.0
                file_entry.grid( row = 0, column = 2 )

                file_button=Button(top_menu_frame, text='Read & Index', command = lambda: load_and_index())
                file_button.grid( row = 0, column = 3 )

        #------------------------------------
        #make draggable
        def on_drag_start(self, event):
                widget = event.widget
                widget._drag_start_x = event.x
                widget._drag_start_y = event.y

        def on_drag_motion(self, event):
                widget = event.widget
                x = widget.winfo_x() - widget._drag_start_x + event.x
                y = widget.winfo_y() - widget._drag_start_y + event.y
                widget.place(x=x, y=y)
                
        def make_draggable(self, widget):
                widget.bind("<Button-1>", self.on_drag_start)
                widget.bind("<B1-Motion>", self.on_drag_motion)

        #-------------------------------------
        #make a new recipe node 
        def new_recipe(self, item_name):
                item_fluid_dict = self.item_fluid_dict
                null_recipe = {'Cannot Find Item In Context':[{'en': True, 'dur':0,'eut':0,'iI':[],'iO':[],'fI':[],'fO':[]}]}

                dict_recipes = null_recipe
                if (item_name in item_fluid_dict):
                        dict_recipes = item_fluid_dict[item_name].input_in

                machine_name_list = list(dict_recipes.keys())
                rec_num = 0#default to first recipe

                recipe_list = dict_recipes[machine_name_list[0]]
                recipe = recipe_list[rec_num]#default to first recipe

                is_shaped_shapeless = ('o' in recipe)

                recipe_frame = Frame(self.master, style = 'recipe.TFrame' )
                self.make_draggable(recipe_frame)
                recipe_frame.pack()

                #Exit Button/Top of Frame
                exit_button = Button(recipe_frame,style='exit_button.TButton', text = 'X', command = lambda:recipe_frame.destroy())
                exit_button.grid( row = 0, column = 1, sticky = 'e' )

                #search box
                search_entry = Entry(recipe_frame)
                search_entry.insert(0,item_name)
                search_entry.grid(row = 1, column = 0, columnspan = 2, sticky = 'ew')
                
                #duration & eu/t
                if is_shaped_shapeless:#if its a shaped/shapeless
                        duration_label = Label(recipe_frame,style='info_box.TLabel',text='n/a')
                else:
                        duration_label = Label(recipe_frame,style='info_box.TLabel',text=str(recipe['dur'])+'t @'+str(recipe['eut'])+'Eu/t')
                duration_label.grid( row = 2, column = 1 )

                #recipe counter
                rec_out_of_label = Label(recipe_frame, style = 'transparent.TLabel',text = '1/'+str(len(recipe_list)))
                rec_out_of_label.grid( row = 3, column = 0, columnspan = 2, sticky = 'n')

                #input amount and items/fluids
                input_title_label = Label(recipe_frame,style='info_box.TLabel',text = 'Input:')
                input_title_label.grid( row = 4, column = 0 )

                #output amount items/fluids
                output_title_label = Label(recipe_frame,style='info_box.TLabel',text = 'Output:')
                output_title_label.grid( row = 4, column = 1 )

                #items
                items_frame = Frame(recipe_frame) #seperate frame for the items  
                items_frame.grid( row = 5, column = 0, columnspan = 2)

                #updates duration_label and input/output items
                def reload(): 
                        recipe = recipe_list[rec_num]
                        rec_out_of_label['text'] = str(rec_num+1)+'/'+str(len(recipe_list))

                        for child in items_frame.winfo_children():#clear out the 
                                child.destroy()

                        if is_shaped_shapeless:#if its a shaped/shapeless
                                duration_label['text'] = 'n/a'
                                count_row = 0
                                for item in recipe['iI']:
                                        if (item != None):
                                                label_item = Label(items_frame,style = 'info_box.TLabel',text = str(item['a'])+'x'+item['lN'])
                                                label_item.grid( row = count_row, column = 0 )
                                                count_row += 1
                                label_item = Label(items_frame,style = 'info_box.TLabel',text = str(recipe['o']['a'])+'x'+recipe['o']['lN'])#output item
                                label_item.grid( row = 0, column = 1 )
                        else:
                                duration_label['text'] = 'Duration:'+str(recipe['dur'])+'t @'+str(recipe['eut'])+'Eu/t'
                                count_row = 0
                                for item in recipe['iI']:
                                        label_item = Label(items_frame,style = 'item.TLabel',text = str(item['a'])+'x'+item['lN'])
                                        label_item.grid( row = count_row, column = 0 )
                                        count_row += 1
                                for fluid in recipe['fI']:
                                        label_fluid = Label(items_frame,style = 'fluid.TLabel',text = str(fluid['a'])+'ml '+fluid['lN'])
                                        label_fluid.grid( row = count_row, column = 0 )
                                        count_row += 1
                                count_row = 0
                                for item in recipe['iO']:
                                        label_item = Label(items_frame,style = 'item.TLabel',text = str(item['a'])+'x'+item['lN'])
                                        label_item.grid( row = count_row, column = 1 )
                                        count_row += 1
                                for fluid in recipe['fO']:
                                        label_fluid = Label(items_frame,style = 'fluid.TLabel',text = str(fluid['a'])+'ml '+fluid['lN'])
                                        label_fluid.grid( row = count_row, column = 1 )
                                        count_row += 1
                        items_frame.update()#shrink the box again
                        recipe_frame.update()

                #arrow functions and declaration
                def inc_rec():
                        nonlocal rec_num
                        rec_num = (rec_num + 1)%len(recipe_list)
                        reload()

                def dec_rec():
                        nonlocal rec_num
                        rec_num = (rec_num - 1)%len(recipe_list)
                        reload()

                inc_rec_button = Button(recipe_frame, text = '>', command = lambda: inc_rec())
                inc_rec_button.grid( row = 3, column = 1, sticky = 'n')

                dec_rec_button = Button(recipe_frame, text = '<', command = lambda: dec_rec())
                dec_rec_button.grid( row = 3, column = 0, sticky = 'n')

                #updates the recipe_list for this machine
                def update_machine_query():
                        nonlocal rec_num
                        rec_num = 0 #reset the recipe number

                        nonlocal recipe_list
                        if (item_name != search_entry.get()):#user tries to select another machine without specifiying the search for it
                                update_item_query()
                        recipe_list = dict_recipes.get(var_machine.get(),-1)#this only occurs when the name changes without searching
                        if (recipe_list == -1):#if they dictionary item does not exist in context
                                recipe_list = next(iter(null_recipe.values()))

                        nonlocal is_shaped_shapeless
                        is_shaped_shapeless = ('o' in recipe_list[0])#switch to shapeless
                        reload()

                #machine drop down
                var_machine = tk.StringVar(recipe_frame)
                var_machine.set(machine_name_list[0])#default value
                var_machine.trace('w', lambda a,b,c :update_machine_query())#referenced before assignment but still do work
                machine_dropdown = OptionMenu(recipe_frame, var_machine, machine_name_list[0], *machine_name_list)
                machine_dropdown.config(style = 'machine.TMenubutton')
                machine_dropdown.grid( row = 2, column = 0 )

                #search for a new item
                def update_item_query():
                        nonlocal item_name 
                        nonlocal dict_recipes
                        item_name = search_entry.get()

                        if not(item_name in item_fluid_dict):
                                dict_recipes = null_recipe
                        else:
                                if var_usage.get() == 'Output': 
                                        dict_recipes = item_fluid_dict[item_name].input_in
                                else:
                                        dict_recipes = item_fluid_dict[item_name].output_in
                        machine_name_list = list(dict_recipes)#update the machines this item has
                        machine_dropdown.set_menu(machine_name_list[0], *machine_name_list)

                        update_machine_query()#update the info

                #usage drop down
                usage_options = ['Input', 'Output']
                var_usage = tk.StringVar(recipe_frame)
                var_usage.set(usage_options[0])#default value
                var_usage.trace ('w', lambda a,b,c :update_item_query() )
                usage_dropdown = OptionMenu(recipe_frame, var_usage, usage_options[0], *usage_options) 
                usage_dropdown.config(style = 'default.TMenubutton')
                usage_dropdown.grid( row = 1, column =1, sticky = 'e')

                update_item_query()#load all the info up




#Window settings
root = tk.Tk()
app = Main(root)

app.new_recipe('Oil')

root.mainloop()

