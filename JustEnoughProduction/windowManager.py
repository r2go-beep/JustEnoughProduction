#last updated: 4/16/21
import tkinter as tk
from tkinter import ttk, Menu
from tkinter.ttk import *
from recipeManager import JSONIndexer

item_fluid_dict = {}

#To do: connect nodes visually and actually
#       make shapped recipes condenced
#       allow for node condencation

class Main(tk.Frame):
        def __init__(self, master):
                global item_fluid_dict
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

                def load_and_index():
                        global item_fluid_dict
                        item_fluid_dict = JSONIndexer.index(self, file_entry.get())

                #-------------------------------
                #TOP MENU
                top_menu_frame = Frame(master, )
                top_menu_frame.pack()

                #button for a new recipe node
                new_crafting_node_button=Button(top_menu_frame,style = 'default.TButton',text='New Crafting Node',command=lambda:RecipeNode(''))
                new_crafting_node_button.grid( row = 0, column = 0 )

                #read and index from file
                file_entry=Entry(top_menu_frame, )
                file_entry.insert(0,'2021-01-09_14-14-16.json')#default to json file for GTNH 2.1.0.0
                file_entry.grid( row = 0, column = 2 )

                file_button=Button(top_menu_frame, text='Read & Index', command = lambda: load_and_index())
                file_button.grid( row = 0, column = 3 )
                load_and_index()

                RecipeNode('Oil')

#-------------------------------------
#make a new recipe node 
class RecipeNode():
        linked_recipes = 0#this nodes inputs that are linked to other nodes outputs

        def __init__(self, item_name):
                print("Searching for:"+ item_name)
                global item_fluid_dict
                self.item_name = item_name
                self.null_recipe = {'Cannot Find Item In Context':[{'en': True, 'dur':0,'eut':0,'iI':[],'iO':[],'fI':[],'fO':[]}]}

                self.dict_recipes = self.null_recipe

                #--UI WORK---
                recipe_frame = Frame(root, style = 'recipe.TFrame' )
                self.recipe_frame = recipe_frame
                self.make_draggable(recipe_frame)
                recipe_frame.pack()

                #Exit Button/Top of Frame
                exit_button = Button(recipe_frame,style='exit_button.TButton', text = 'X', command = lambda:recipe_frame.destroy())
                exit_button.grid( row = 0, column = 1, sticky = 'e' )

                #search box
                self.search_entry = Entry(recipe_frame)
                self.search_entry.insert(0,item_name)
                self.search_entry.grid(row = 1, column = 0, columnspan = 2, sticky = 'ew')
                
                #duration & eu/t
                self.duration_label = Label(recipe_frame,style='info_box.TLabel',text='n/a')
                self.duration_label.grid( row = 2, column = 1 )

                #recipe counter
                self.rec_out_of_label = Label(recipe_frame, style = 'transparent.TLabel')
                self.rec_out_of_label.grid( row = 3, column = 0, columnspan = 2, sticky = 'n')

                #input amount and items/fluids
                input_title_label = Label(recipe_frame,style='info_box.TLabel',text = 'Input:')
                input_title_label.grid( row = 4, column = 0 )

                #output amount items/fluids
                output_title_label = Label(recipe_frame,style='info_box.TLabel',text = 'Output:')
                output_title_label.grid( row = 4, column = 1 )

                #------------------------------------
                #right click menu for items
                self.popup_item = ''
                self.popup_menu = Menu(root, tearoff = 0)
                self.popup_menu.add_command(label = self.popup_item)#able to add a command here but nothing comes to mind yet
                self.popup_menu.add_separator()
                self.popup_menu.add_command(label = 'Search', command = lambda: RecipeNode(self.popup_item) )
                self.popup_menu.add_command(label = 'Connect', )#for adding connecting lines need command

                #items
                self.items_frame = Frame(recipe_frame) #seperate frame for the items  
                self.items_frame.grid( row = 5, column = 0, columnspan = 2)

                #arrow functions
                def inc_rec(self):
                        self.rec_num = (self.rec_num + 1)%len(self.recipe_list)
                        self.reload()

                def dec_rec(self):
                        self.rec_num = (self.rec_num - 1)%len(self.recipe_list)
                        self.reload()
                
                inc_rec_button = Button(recipe_frame, text = '>', command = lambda: inc_rec(self))
                inc_rec_button.grid( row = 3, column = 1, sticky = 'n')

                dec_rec_button = Button(recipe_frame, text = '<', command = lambda: dec_rec(self))
                dec_rec_button.grid( row = 3, column = 0, sticky = 'n')
                
                #machine drop down
                self.var_machine = tk.StringVar(recipe_frame)
                self.var_machine.set('')#default value
                self.var_machine.trace('w', lambda a,b,c :self.update_machine_query())#referenced before assignment but still do work
                self.machine_dropdown = OptionMenu(recipe_frame, self.var_machine)
                self.machine_dropdown.config(style = 'machine.TMenubutton')
                self.machine_dropdown.grid( row = 2, column = 0 )

                #usage drop down
                self.usage_options = ['Input', 'Output']
                self.var_usage = tk.StringVar(recipe_frame)
                self.var_usage.set(self.usage_options[0])#default value
                self.var_usage.trace ('w', lambda a,b,c : self.update_item_query() )
                self.usage_dropdown = OptionMenu(recipe_frame, self.var_usage, self.usage_options[0], *self.usage_options) 
                self.usage_dropdown.config(style = 'default.TMenubutton')
                self.usage_dropdown.grid( row = 1, column =1, sticky = 'e')

                self.update_item_query()#load
        #---------------END __INIT__----------------------
        
        def do_popup_menu(self, event, item):
                self.popup_item = item
                try:
                        self.popup_menu.entryconfig(0, label = item)
                        self.popup_menu.tk_popup(event.x_root, event.y_root)
                finally:
                        self.popup_menu.grab_release()

        #updates duration_label and input/output items
        def reload(self): 
                recipe = self.recipe_list[self.rec_num]
                self.rec_out_of_label['text'] = str(self.rec_num+1)+'/'+str(len(self.recipe_list))

                for child in self.items_frame.winfo_children():#clear out the 
                        child.destroy()

                if self.is_shaped_shapeless:#if its a shaped/shapeless
                        self.duration_label['text'] = 'n/a'
                        count_row = 0
                        for item in recipe['iI']:
                                if (item != None):
                                        label_item = Label(self.items_frame,style = 'item.TLabel',text = str(item['a'])+'x'+item['lN'])
                                        label_item.grid( row = count_row, column = 0 )
                                        label_item.bind("<Button-3>", lambda event, item=item['lN']:self.do_popup_menu(event, item))
                                        count_row += 1
                        label_item = Label(self.items_frame,style = 'item.TLabel',text = str(recipe['o']['a'])+'x'+recipe['o']['lN'])#output item
                        label_item.bind("<Button-3>", lambda event, item=recipe['o']['lN']:self.do_popup_menu(event,item) )
                        label_item.grid( row = 0, column = 1 )
                else:
                        self.duration_label['text'] = 'Duration:'+str(recipe['dur'])+'t @'+str(recipe['eut'])+'Eu/t'
                        count_row = 0
                        for item in recipe['iI']:
                                label_item = Label(self.items_frame,style = 'item.TLabel',text = str(item['a'])+'x'+item['lN'])
                                label_item.grid( row = count_row, column = 0 )
                                label_item.bind("<Button-3>", lambda event, item=item['lN']:self.do_popup_menu(event, item))
                                count_row += 1
                        for fluid in recipe['fI']:
                                label_fluid = Label(self.items_frame,style = 'fluid.TLabel',text = str(fluid['a'])+'ml '+fluid['lN'])
                                label_fluid.grid( row = count_row, column = 0 )
                                label_fluid.bind("<Button-3>", lambda event, item=fluid['lN']:self.do_popup_menu(event, item))
                                count_row += 1
                        count_row = 0
                        for item in recipe['iO']:
                                label_item = Label(self.items_frame,style = 'item.TLabel',text = str(item['a'])+'x'+item['lN'])
                                label_item.grid( row = count_row, column = 1 )
                                label_item.bind("<Button-3>", lambda event, item=item['lN']:self.do_popup_menu(event, item))
                                count_row += 1
                        for fluid in recipe['fO']:
                                label_fluid = Label(self.items_frame,style = 'fluid.TLabel',text = str(fluid['a'])+'ml '+fluid['lN'])
                                label_fluid.grid( row = count_row, column = 1 )
                                label_fluid.bind("<Button-3>", lambda event, item=fluid['lN']:self.do_popup_menu(event, item))
                                count_row += 1
                self.items_frame.update()#update item box
                self.recipe_frame.update()

        #updates the recipe_list for this machine
        def update_machine_query(self):
                self.rec_num = 0 #reset the recipe number

                if (self.item_name != self.search_entry.get()):#user tries to select another machine without specifiying the search for it
                        self.update_item_query()
                self.recipe_list = self.dict_recipes.get(self.var_machine.get(),-1)#this only occurs when the name changes without searching
                if (self.recipe_list == -1):#if they dictionary item does not exist in context
                        self.recipe_list = next(iter(self.null_recipe.values()))

                self.is_shaped_shapeless = ('o' in self.recipe_list[0])#switch to shapeless
                self.reload()

        #search for a new item
        def update_item_query(self):
                global item_fluid_dict
                self.item_name = self.search_entry.get()

                if not(self.item_name in item_fluid_dict):#if item doesnt exist
                        self.dict_recipes = self.null_recipe
                else:
                        if self.var_usage.get() == 'Output': #if searching for output of item
                                self.dict_recipes = item_fluid_dict[self.item_name].input_in
                        else:
                                self.dict_recipes = item_fluid_dict[self.item_name].output_in

                if (len(self.dict_recipes) == 0):#in the item not existing in the quary type
                        self.dict_recipes = self.null_recipe   

                machine_name_list = list(self.dict_recipes.keys())#update the machines this item has
                self.machine_dropdown.set_menu(machine_name_list[0], *machine_name_list)

                self.update_machine_query()#update the info
        
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




#Window settings
root = tk.Tk()
app = Main(root)


root.mainloop()

