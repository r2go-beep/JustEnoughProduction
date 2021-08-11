#last updated: 4/16/21
import tkinter as tk
from tkinter import ttk, Menu
from tkinter.ttk import *
from recipeManager import JSONIndexer

item_fluid_dict = {}

null_recipe = {'Cannot Find Item In Context':[{'en': True, 'dur':0,'eut':0,'iI':[],'iO':[],'fI':[],'fO':[]}]}

"""
TODO:
        Feature - Save state / Load state
        Feature - Simple Storage Node: only includes item name, input item = output item: 1 to 1
        Feature - Smart Recipe Select: When output changes try to find a recipe to preserve the output of the next machine
        Feature - Better search: Replace text entry with a button that opens a NEI-like window that shows item images
                Image Generation: Find/Load Item images from modpack dir
        Investigate/Fix: Sometimes Connection lines do not line up correctly

"""

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
                style.configure('small_info_box.TLabel',background = '#F0F8FF', borderwidth=1, relief='solid', width =  7)
                style.configure('exit_button.TButton', background = '#d92929', width = 0)

                def load_and_index():
                        global item_fluid_dict
                        item_fluid_dict = JSONIndexer.index(self, file_entry.get())

                #-------------------------------
                #TOP MENU
                top_menu_frame = Frame(root, )
                top_menu_frame.place(x = 0, y = 0)

                #button for new Efficiency node
                new_Efficiency_node_button = Button(top_menu_frame,style = 'default.TButton',text='New Efficiency Node',command=lambda:EfficiencyNode())
                new_Efficiency_node_button.grid(row = 0, column = 0)

                #button for a new recipe node
                new_crafting_node_button = Button(top_menu_frame,style = 'default.TButton',text='New Crafting Node',command=lambda:RecipeNode('',True))
                new_crafting_node_button.grid(row = 0, column = 1)

                #read and index from file
                file_entry=Entry(top_menu_frame, )
                file_entry.insert(0,'2021-01-09_14-14-16.json')#default to json file for GTNH 2.1.0.0
                file_entry.grid( row = 0, column = 2 )

                file_button=Button(top_menu_frame, text='Read & Index', command = lambda: load_and_index())
                file_button.grid( row = 0, column = 3 )
                load_and_index()

                RecipeNode('Oil',True)

#-------------------------------------
#make a new recipe node 
class RecipeNode():
        def __init__(self, item_name, is_input_item):
                global item_fluid_dict
                self.item_name = item_name

                self.dict_recipes = null_recipe
                self.current_recipe = None
                self.rec_num = 0
                self.potential_connect = None#to help connect nodes

                self.input_recipes = None #the list of nodes that this node has as input
                self.output_recipes = None #the list of nodes that this node has as input

                self.lines_out = []
                self.lines_in = []

                #--UI WORK---
                self.recipe_frame = Frame(root, style = 'recipe.TFrame' )
                self.recipe_frame.node = self #for a reference back to this class
                make_draggable(self.recipe_frame)
                self.recipe_frame.place(x = 100, y = 30)

                #search box
                self.search_entry = Entry(self.recipe_frame  )
                self.search_entry.insert(0,item_name)
                self.search_entry.grid(row = 1, column = 0, columnspan = 2, sticky = 'ew')
                
                #duration & eu/t
                self.duration_label = Label(self.recipe_frame ,style='info_box.TLabel',text='n/a')
                self.duration_label.grid( row = 2, column = 1 )

                #recipe counter
                self.rec_out_of_label = Label(self.recipe_frame , style = 'transparent.TLabel')
                self.rec_out_of_label.grid( row = 3, column = 0, columnspan = 2, sticky = 'ns')

                #input amount and items/fluids
                input_title_label = Label(self.recipe_frame ,style='info_box.TLabel',text = 'Input:')
                input_title_label.grid( row = 4, column = 0 )

                #output amount items/fluids
                output_title_label = Label(self.recipe_frame ,style='info_box.TLabel',text = 'Output:')
                output_title_label.grid( row = 4, column = 1 )

                #items frame
                self.items_frame = Frame(self.recipe_frame ) #seperate frame for the items  
                self.items_frame.grid( row = 5, column = 0, columnspan = 2)

                #arrow functions
                def inc_rec(self):
                        self.rec_num = (self.rec_num + 1)%len(self.recipe_list)
                        self.reload()

                def dec_rec(self):
                        self.rec_num = (self.rec_num - 1)%len(self.recipe_list)
                        self.reload()
                
                inc_rec_button = Button(self.recipe_frame , text = '>', command = lambda: inc_rec(self))
                inc_rec_button.grid( row = 3, column = 1, sticky = 'n')

                dec_rec_button = Button(self.recipe_frame , text = '<', command = lambda: dec_rec(self))
                dec_rec_button.grid( row = 3, column = 0, sticky = 'n')
                
                #machine drop down
                self.var_machine = tk.StringVar(self.recipe_frame )
                self.var_machine.set('')#default value
                self.var_machine.trace('w', lambda a,b,c :self.update_machine_query())

                self.machine_label = Label(self.recipe_frame , style='info_box.TLabel', text = self.var_machine.get())#wont see this until machine)dropdown goes away
                self.machine_label.grid( row = 2, column = 0 )

                self.machine_dropdown = OptionMenu(self.recipe_frame , self.var_machine)
                self.machine_dropdown.config(style = 'machine.TMenubutton')
                self.machine_dropdown.grid( row = 2, column = 0 )

                #usage drop down
                self.usage_options = ['Input', 'Output']
                self.var_usage = tk.StringVar(self.recipe_frame )
                self.var_usage.set(self.usage_options[0])#default value
                self.var_usage.trace ('w', lambda a,b,c : self.update_item_query() )
                self.usage_dropdown = OptionMenu(self.recipe_frame , self.var_usage, self.usage_options[0], *self.usage_options) 
                if is_input_item:
                        self.usage_dropdown = OptionMenu(self.recipe_frame , self.var_usage, self.usage_options[0], *self.usage_options) 
                else:
                        self.usage_dropdown = OptionMenu(self.recipe_frame , self.var_usage, self.usage_options[1], *self.usage_options) 
                self.usage_dropdown.config(style = 'default.TMenubutton')
                self.usage_dropdown.grid( row = 1, column =1, sticky = 'e')

                #Exit Button/Top of Frame
                def remove_node():
                        self.destroy_all_connection(self)
                        self.recipe_frame.destroy()
                exit_button = Button(self.recipe_frame ,style='exit_button.TButton', text = 'X', command = lambda:remove_node())#need to also remove the line
                exit_button.grid( row = 0, column = 0, columnspan = 2, sticky = 'e' )

                #Middelize button
                def show_search_inputs():
                        self.search_entry.grid(row = 1, column = 0, columnspan = 2, sticky = 'ew')#make sure this is the same as when init
                        self.usage_dropdown.grid( row = 1, column =1, sticky = 'e')
                        inc_rec_button.grid( row = 3, column = 1, sticky = 'n')
                        dec_rec_button.grid( row = 3, column = 0, sticky = 'n')
                        self.rec_out_of_label.grid( row = 3, column = 0, columnspan = 2, sticky = 'n')
                        self.machine_dropdown.grid( row = 2, column = 0 )
                        self.update_visual_connections(self)

                def hide_search_inputs():
                        self.search_entry.grid_forget()
                        self.usage_dropdown.grid_forget()
                        inc_rec_button.grid_forget()
                        dec_rec_button.grid_forget()
                        self.rec_out_of_label.grid_forget()
                        self.machine_dropdown.grid_forget()
                        self.machine_label['text'] = self.var_machine.get()
                        self.update_visual_connections(self)

                mid_sel = 0
                def mid_max_widget():
                        nonlocal mid_sel
                        if mid_sel != None:
                                if (mid_sel == 0):
                                        hide_search_inputs()
                                else:
                                        show_search_inputs()
                                mid_sel = (mid_sel + 1) % 2

                middelize_button = Button(self.recipe_frame ,style='exit_button.TButton', text = '-', command = lambda:mid_max_widget())
                middelize_button.grid( row = 0, column = 0, columnspan = 2, sticky = 'e',  padx = 20)

                #Minimize button
                def show_all_inputs():
                        self.search_entry.grid(row = 1, column = 0, columnspan = 2, sticky = 'ew')#make sure this is the same as when init
                        self.usage_dropdown.grid( row = 1, column =1, sticky = 'e')
                        inc_rec_button.grid( row = 3, column = 1, sticky = 'n')
                        dec_rec_button.grid( row = 3, column = 0, sticky = 'n')
                        self.rec_out_of_label.grid( row = 3, column = 0, columnspan = 2, sticky = 'n')
                        self.machine_dropdown.grid( row = 2, column = 0 )

                        input_title_label.grid( row = 4, column = 0 )
                        output_title_label.grid( row = 4, column = 1 )
                        self.duration_label.grid( row = 2, column = 1 )

                        self.reload()

                def hide_all_inputs():
                        self.search_entry.grid_forget()
                        self.usage_dropdown.grid_forget()
                        inc_rec_button.grid_forget()
                        dec_rec_button.grid_forget()
                        self.rec_out_of_label.grid_forget()
                        self.machine_dropdown.grid_forget()
                        self.machine_label['text'] = self.var_machine.get()

                        input_title_label.grid_forget()
                        output_title_label.grid_forget()
                        self.duration_label.grid(row = 3, column = 0)
                        
                        for input_item_index in range(len(self.current_recipe['iI']+self.current_recipe['fI'])):#get rid of inp
                                for input_item_widget in self.items_frame.grid_slaves(input_item_index, 0):
                                        input_item_widget.lower()
                                        input_item_widget.grid(row = 0, column = 0)
                        for input_item_index in range(len(self.current_recipe['iO']+self.current_recipe['fO'])):
                                for input_item_widget in self.items_frame.grid_slaves(input_item_index, 1):
                                        input_item_widget.grid(row = input_item_index, column = 0)
                                        if input_item_index < len(self.current_recipe['iO']):
                                                input_item_widget['text'] = self.current_recipe['iO'][input_item_index]['lN']
                                        else:
                                                input_item_widget['text'] = self.current_recipe['fO'][input_item_index-len(self.current_recipe['iO'])]['lN']
                        self.update_visual_connections(self)

                min_sel = 0
                def min_max_widget():
                        nonlocal min_sel
                        nonlocal mid_sel
                        if (min_sel == 0):
                                hide_all_inputs()
                                mid_sel = None
                        else:
                                show_all_inputs()
                                mid_sel = 0
                        min_sel = (min_sel + 1) % 2

                middelize_button = Button(self.recipe_frame ,style='exit_button.TButton', text = '_', command = lambda:min_max_widget())
                middelize_button.grid( row = 0, column = 0, columnspan = 2, sticky = 'e',  padx = 40)

                #------------------------------------
                #right click menu for items
                self.popup_item = ''
                self.popup_is_input = True#True if item is apart of the input

                self.popup_menu = Menu(root, tearoff = 0)
                self.popup_menu.add_command(label = self.popup_item)#command is updated when making popup
                self.popup_menu.add_separator()
                self.popup_menu.add_command(label = 'Search', command = lambda: RecipeNode(self.popup_item, True) )#command is updated when making popup
                self.popup_menu.add_command(label = 'Connect', command = lambda: self.do_potential_action())
                self.popup_menu.add_command(label = 'Search & Connect', command = lambda: self.search_create(True) )#command is updated when making popup
                self.popup_menu.add_command(label = 'Disconnect', command = lambda: self.destroy_connection(self, self.get_item_index(self.popup_item,self.recipe_list[self.rec_num], self.popup_is_input), self.popup_is_input, True))
                self.popup_menu.add_command(label = 'Fix Arrows', command = lambda: self.update_connections(self))
                self.popup_menu.add_command(label = 'Delete Node', command = lambda: remove_node())

                self.update_item_query()#load

        #updates duration_label and input/output items
        def reload(self): 
                recipe = self.recipe_list[self.rec_num]
                self.current_recipe = recipe
                self.rec_out_of_label['text'] = str(self.rec_num+1)+'/'+str(len(self.recipe_list))

                for child in self.items_frame.winfo_children():#clear out the children itesm
                        child.destroy()

                if self.is_shaped_shapeless:#if its a shaped/shapeless
                        self.duration_label['text'] = 'n/a'
                        count_row = 0
                        for item in recipe['iI']:
                                if (item != None):
                                        label_item = Label(self.items_frame,style = 'item.TLabel',text = str(item['a'])+'x'+item['lN'])
                                        label_item.grid( row = count_row, column = 0 )
                                        label_item.bind("<Button-3>", lambda event, item=item['lN']:self.do_popup_menu(event, item, True))
                                        count_row += 1
                        label_item = Label(self.items_frame,style = 'item.TLabel',text = str(recipe['o']['a'])+'x'+recipe['o']['lN'])#output item
                        label_item.bind("<Button-3>", lambda event, item=recipe['o']['lN']:self.do_popup_menu(event, item, False))
                        label_item.grid( row = 0, column = 1 )
                else:
                        self.duration_label['text'] = 'Duration:'+str(recipe['dur'])+'t @'+str(recipe['eut'])+'Eu/t'
                        count_row = 0
                        for item in recipe['iI']:
                                label_item = Label(self.items_frame,style = 'item.TLabel',text = str(item['a'])+'x'+item['lN'])
                                label_item.grid( row = count_row, column = 0 )
                                label_item.bind("<Button-3>", lambda event, item=item['lN']:self.do_popup_menu(event, item, True))
                                count_row += 1
                        for fluid in recipe['fI']:
                                label_item = Label(self.items_frame,style = 'fluid.TLabel',text = str(fluid['a'])+'ml '+fluid['lN'])
                                label_item.grid( row = count_row, column = 0 )
                                label_item.bind("<Button-3>", lambda event, item=fluid['lN']:self.do_popup_menu(event, item, True))
                                count_row += 1
                        count_row = 0
                        for item in recipe['iO']:
                                label_item = Label(self.items_frame,style = 'item.TLabel',text = str(item['a'])+'x'+item['lN'])
                                label_item.grid( row = count_row, column = 1 )
                                label_item.bind("<Button-3>", lambda event, item=item['lN']:self.do_popup_menu(event, item, False))
                                count_row += 1
                        for fluid in recipe['fO']:
                                label_item = Label(self.items_frame,style = 'fluid.TLabel',text = str(fluid['a'])+'ml '+fluid['lN'])
                                label_item.grid( row = count_row, column = 1 )
                                label_item.bind("<Button-3>", lambda event, item=fluid['lN']:self.do_popup_menu(event, item, False))
                                count_row += 1
                self.items_frame.update()#update item box
                self.recipe_frame.update()
                self.update_connections(self)

        #updates the recipe_list for this machine
        def update_machine_query(self):
                self.rec_num = 0 #reset the recipe number

                if (self.item_name != self.search_entry.get()):#user tries to select another machine without specifiying the search for it
                        self.update_item_query()
                self.recipe_list = self.dict_recipes.get(self.var_machine.get(),-1)#this only occurs when the name changes without searching
                if (self.recipe_list == -1):#if they dictionary item does not exist in context
                        self.recipe_list = next(iter(null_recipe.values()))

                self.is_shaped_shapeless = ('o' in self.recipe_list[0])#update is_shaped_shapeless
                self.reload()

        #search for a new typed in item
        def update_item_query(self):
                global item_fluid_dict
                self.item_name = self.search_entry.get()

                if not(self.item_name in item_fluid_dict):#if item doesnt exist
                        self.dict_recipes = null_recipe
                else:
                        if self.var_usage.get() == 'Output': #if searching for output of item
                                self.dict_recipes = item_fluid_dict[self.item_name].input_in
                        else:
                                self.dict_recipes = item_fluid_dict[self.item_name].output_in

                if (len(self.dict_recipes) == 0):#in the item not existing in the quary type
                        self.dict_recipes = null_recipe   

                machine_name_list = list(self.dict_recipes.keys())#update the machines this item has
                self.machine_dropdown.set_menu(machine_name_list[0], *machine_name_list)

                self.update_machine_query()#update the info

        def get_item_index(self, item_name, recipe, is_input):#returns the item's index position None if not found
                index = None
                if is_input:
                        for i in range(len(recipe['iI'])):
                                if (item_name == recipe['iI'][i]['lN'] ):
                                        index = i
                                        break
                        for i in range(len(recipe['fI'])):
                                if (item_name == recipe['fI'][i]['lN'] ):
                                        index = len(recipe['iI']) + i
                                        break
                else:
                        for i in range(len(recipe['iO'])):
                                if (item_name == recipe['iO'][i]['lN'] ):
                                        index = i
                                        break
                        for i in range(len(recipe['fO'])):
                                if (item_name == recipe['fO'][i]['lN'] ):
                                        index = len(recipe['iO']) + i
                                        break
                return index

        def get_item(self, index, recipe, is_input):#returns the items name in index position 0 and the amount in index position 2, None if not found
                item = None
                if is_input:
                        if index < len(recipe['iI']):
                                item = recipe['iI'][index]
                        else:
                                item = recipe['fI'][ abs(len(recipe['iI']) - index) ]
                else:
                        if index < len(recipe['iO']):
                                item = recipe['iO'][index]
                        else:
                                item = recipe['fO'][ abs(len(recipe['iO']) - index) ]
                return item

        #connect nodes
        def get_clicked(self, event):
                root.unbind('<Button-1>')
                self.potential_connect = event.widget
                self.do_potential_action()

        def do_potential_action(self ):
                if (self.potential_connect == None) :
                        root.bind("<Button-1>", self.get_clicked)
                else:
                        if hasattr( self.potential_connect.master.master, 'node') and (self != self.potential_connect.master.master.node):#protects against choosing a widget that isnt an item
                                item = self.popup_item
                                if self.popup_is_input:
                                        self.create_connection(item, self.potential_connect.master.master.node, self)
                                else:
                                        self.create_connection(item, self, self.potential_connect.master.master.node )
                        self.potential_connect = None#reset so that its able to try to have another connection

        def destroy_all_connection(self, node):#to remove all connections
                if node.input_recipes != None:
                        for connected_node in node.input_recipes:
                                if (connected_node != None):
                                        self.destroy_connection(connected_node, connected_node.output_recipes.index(node), False, False)
                if node.output_recipes != None:                       
                        for connected_node in node.output_recipes:
                                if (connected_node != None):
                                        self.destroy_connection(connected_node, connected_node.input_recipes.index(node), True, False)
                node.input_recipes = None
                node.output_recipes = None

        def destroy_connection(self, node, index, is_input, is_remove_from_connected):
                if is_input:
                        if (index != None) and (node.lines_in[index] != None):
                                        canvas.delete(node.lines_in[index])
                                        node.lines_in[index] = None
                                        connected_node_index = self.get_item_index(self.get_item(index,node.current_recipe,is_input)['lN'], node.input_recipes[index].current_recipe,not(is_input))
                                        if is_remove_from_connected and connected_node_index != None and node.input_recipes[index].lines_out[connected_node_index] != None:
                                                self.destroy_connection(node.input_recipes[index], connected_node_index, not(is_input), False)
                                        node.input_recipes[index] = None
                else:
                        if (index != None) and (node.lines_out[index] != None):
                                        canvas.delete(node.lines_out[index])
                                        node.lines_out[index] = None
                                        connected_node_index = self.get_item_index(self.get_item(index,node.current_recipe,is_input)['lN'], node.output_recipes[index].current_recipe,not(is_input))
                                        if is_remove_from_connected and connected_node_index != None and node.output_recipes[index].lines_in[connected_node_index] != None:
                                                self.destroy_connection(node.output_recipes[index], connected_node_index, not(is_input), False)
                                        node.output_recipes[index] = None

        def search_create(self, is_input):
                if is_input:
                        self.create_connection(self.popup_item, self, RecipeNode(self.popup_item,is_input))
                else:
                        self.create_connection(self.popup_item, RecipeNode(self.popup_item,is_input), self)

        def create_connection(self, item_name, output_node, input_node):#connects the nodes by the input node linking to the output
                in_recipe = input_node.current_recipe
                out_recipe = output_node.current_recipe

                if (input_node.input_recipes == None):
                        input_node.input_recipes = [None] * (len(in_recipe['iI']) + len(in_recipe['fI'])) #make an empty list of input item size
                        input_node.lines_in = [None] * (len(in_recipe['iI']) + len(in_recipe['fI'])) 

                if (output_node.output_recipes == None):# a doubly linked list
                        output_node.output_recipes = [None] * (len(out_recipe['iO']) + len(out_recipe['fO']))#make an empty list of input item size
                        output_node.lines_out = [None] * (len(out_recipe['iO']) + len(out_recipe['fO']))

                input_item_index = self.get_item_index(item_name, in_recipe, True)
                output_item_index = self.get_item_index(item_name, out_recipe, False)
                
                if (input_item_index != None and output_item_index != None) and (output_node.lines_out[output_item_index] == None) and (input_node.lines_in[input_item_index] == None):#limiting one input to one output
                        input_node.input_recipes[input_item_index] = output_node
                        output_node.output_recipes[output_item_index] = input_node

                        new_line = canvas.create_line(
                        output_node.recipe_frame.winfo_x() + output_node.items_frame.grid_slaves(0,1)[0].winfo_width()*2,
                        output_node.recipe_frame.winfo_y() + output_node.items_frame.winfo_y() + (1+2*output_item_index)*output_node.items_frame.grid_slaves(0,1)[0].winfo_height()/2 ,
                        input_node.recipe_frame.winfo_x() + input_node.items_frame.grid_slaves(0,0)[0].winfo_x(),
                        input_node.recipe_frame.winfo_y() + input_node.items_frame.winfo_y() + (1+2*input_item_index)*input_node.items_frame.grid_slaves(0,1)[0].winfo_height()/2,
                        arrow =tk.LAST, fill = "black")
                        input_node.lines_in[input_item_index] = new_line
                        output_node.lines_out[output_item_index] = new_line
        
        def update_connections(self, node):#to fix visual effects with lines and for staying linked
                temp_connection_info = []
                if node.input_recipes != None:
                        for connected_node in node.input_recipes:
                                if connected_node != None:
                                        for potential_same_line in connected_node.lines_out:
                                                if potential_same_line != None and potential_same_line in node.lines_in:#if there exist a previous connection
                                                        item_name = self.get_item(connected_node.lines_out.index(potential_same_line), connected_node.current_recipe, False)['lN']
                                                        temp_connection_info.append([item_name, connected_node, node])
                if node.output_recipes != None:
                        for connected_node in node.output_recipes:
                                if connected_node != None:
                                        for potential_same_line in connected_node.lines_in:
                                                if potential_same_line != None and potential_same_line in node.lines_out:
                                                        item_name = self.get_item(connected_node.lines_in.index(potential_same_line), connected_node.current_recipe, True)['lN']
                                                        temp_connection_info.append([item_name, node, connected_node])
                self.destroy_all_connection(self)
                for connection in temp_connection_info:
                        self.create_connection(connection[0], connection[1], connection[2])
                temp_connection_info = None

        def update_visual_connections(self, node):
                node.recipe_frame.update()
                if node.input_recipes != None:
                        for i in range(len(node.input_recipes)):
                                if (node.input_recipes[i] != None):
                                        x1, y1, x2, y2 = canvas.coords(node.lines_in[i])
                                        canvas.coords(node.lines_in[i], x1, y1, node.recipe_frame.winfo_x() + node.items_frame.grid_slaves(0,0)[0].winfo_x(),
                                        node.recipe_frame.winfo_y() + node.items_frame.winfo_y() + (1+2*i)*node.items_frame.grid_slaves(0,0)[0].winfo_height()/2)
                if node.output_recipes != None:
                        for i in range(len(node.output_recipes)):
                                if (node.output_recipes[i] != None):
                                        x1, y1, x2, y2 = canvas.coords(node.lines_out[i])
                                        canvas.coords(node.lines_out[i], node.recipe_frame.winfo_x() + node.items_frame.grid_slaves(0,0)[0].winfo_x() + node.items_frame.grid_slaves(0,0)[0].winfo_width(),
                                        node.recipe_frame.winfo_y() + node.items_frame.winfo_y() + (1+2*i)*node.items_frame.grid_slaves(0,0)[0].winfo_height()/2, x2, y2)

        #draggable support
        def on_drag_motion(self, event):
                widget = event.widget
                x = widget.winfo_x() - widget._drag_start_x + event.x
                y = widget.winfo_y() - widget._drag_start_y + event.y
                widget.place(x=x, y=y)
                for line in widget.node.lines_out:
                        if line != None:
                                x1, y1, x2, y2 = canvas.coords(line)
                                canvas.coords(line, x1 - widget._drag_start_x + event.x, y1 - widget._drag_start_y + event.y, x2, y2)
                
                for line in widget.node.lines_in:
                        if line != None:
                                x1, y1, x2, y2 = canvas.coords(line)
                                canvas.coords(line, x1, y1, x2 - widget._drag_start_x + event.x, y2 - widget._drag_start_y + event.y)

        def do_popup_menu(self, event, item, is_input):
                self.popup_item = item
                self.popup_is_input = is_input
                try:
                        self.popup_menu.entryconfig(0, label = item)
                        self.popup_menu.entryconfig(2, command = lambda: RecipeNode(self.popup_item, not(is_input)) ) 
                        self.popup_menu.entryconfig(4, command = lambda: self.search_create(not(is_input))) 
                        self.popup_menu.tk_popup(event.x_root, event.y_root)
                finally:
                        self.popup_menu.grab_release()

#-------------------------------------
#make a new Efficiency node
class EfficiencyNode():
        def __init__(self):
                self.frame = Frame(root, style = 'recipe.TFrame' )
                self.frame.node = self
                make_draggable(self.frame)
                self.frame.place(x = 100, y = 30)

                self.potential_connect = None
                self.head_node = None
                self.head_item_name = None

                exit_button = Button(self.frame,style='exit_button.TButton', text = 'X', command = lambda:self.frame.destroy())
                exit_button.grid( row = 0, column = 2, sticky = 'e' )

                #input amount and items/fluids
                input_title_label = Label(self.frame,style='info_box.TLabel',text = 'Inputs:')
                input_title_label.grid( row = 2, column = 0 )

                #Efficiency between input and output
                output_title_label = Label(self.frame,style='small_info_box.TLabel',text = 'Eff:')
                output_title_label.grid( row = 2, column = 1 )

                #output amount items/fluids
                output_title_label = Label(self.frame,style='info_box.TLabel',text = 'Product:')
                output_title_label.grid( row = 2, column = 2 )

                #EU amount total
                self.eu_label = Label(self.frame,style='info_box.TLabel',text = 'Eu/t:0')
                self.eu_label.grid( row = 1, column = 0 )

                #amount entry
                self.amount_entry = Entry(self.frame  )
                self.amount_entry.insert(0,64)
                self.amount_entry.grid(row = 1, column = 1, columnspan = 2, sticky = 'w')

                #amount search button
                self.amount_button = Button(self.frame, text = 'Go', command = lambda: self.populate_input() )
                self.amount_button.grid(row = 1, column = 2, sticky = 'e')

                self.items_frame = Frame(self.frame, style = 'recipe.TFrame' )
                self.items_frame.grid( row = 3, column = 0, columnspan = 3)

                self.select_head_button = Button(self.frame, text = 'Click Output Item', command = lambda:self.do_potential_action())
                self.select_head_button.grid( row = 3, column = 2)

        def get_clicked(self, event):
                root.unbind('<Button-1>')
                self.potential_connect = event.widget
                self.do_potential_action()
                
        def do_potential_action(self ):
                if (self.potential_connect == None):
                        root.bind("<Button-1>", self.get_clicked)
                else:
                        if hasattr(self.potential_connect.master.master, 'node') and isinstance(self.potential_connect.master.master.node, RecipeNode):
                                self.head_node = self.potential_connect.master.master.node
                                if self.potential_connect.grid_info()['column'] == 1:
                                        self.head_item = self.head_node.get_item(self.potential_connect.grid_info()['row'], self.head_node.current_recipe, False)
                                else:
                                        self.potential_connect = None
                                        return
                                self.head_item_name = self.head_item['lN']
                                self.populate_input()
                        else:
                                self.potential_connect = None

        def populate_input(self):
                for child in self.items_frame.winfo_children():#clear out the children to remake them
                        child.destroy()

                if (self.head_item_name and 
                                self.head_node.get_item_index(self.head_item_name, self.head_node.current_recipe, True) == None and
                                self.head_node.get_item_index(self.head_item_name, self.head_node.current_recipe, False) == None):
                        self.potential_connect = None
                        self.head_item = None
                        self.head_item_name = None
                        self.select_head_button.grid( row = 3, column = 2)
                        return

                self.select_head_button.grid_forget()
                self.eu_label['text'] = 'Eu/t:'+ str(self.get_eu(self.head_node))
                amount = self.amount_entry.get()

                if str.isnumeric(amount):
                        count_row = 0
                        for input_item in self.condence_inputs(self.get_inputs(self.head_node, self.head_item['lN'], float(amount))):
                                label_item = Label(self.items_frame,style = 'item.TLabel',text = ('%.2f' % input_item[1])+'x'+input_item[0] )
                                label_item.grid( row = count_row, column = 0 )
                                
                                eff_num = 0
                                if input_item[1]:
                                        eff_num = float(amount)/input_item[1]
                                else:
                                        eff_num = 'inf'
                                eff_item_label = Label(self.items_frame, style='small_info_box.TLabel', text = eff_num)
                                eff_item_label.grid(row = count_row, column = 1)
                                count_row += 1

                        self.output_item_label = Label(self.items_frame, style='item.TLabel', text = amount +'x'+ self.head_item['lN'])
                        self.output_item_label.grid(row = 0, column = 2)
        
        def on_drag_motion(self, event): # draggable support
                widget = event.widget
                x = widget.winfo_x() - widget._drag_start_x + event.x
                y = widget.winfo_y() - widget._drag_start_y + event.y
                widget.place(x=x, y=y)

        def get_eu(self, node):
                prev_eu = node.current_recipe['eut']
                if node.input_recipes != None:
                        for i in range( len(node.current_recipe['iI']) + len(node.current_recipe['fI']) ):
                                if node.input_recipes[i] != None:
                                        prev_eu += self.get_eu(node.input_recipes[i])
                return prev_eu

        def condence_inputs(self, list_of_inputs):
                result_dict = {}
                for item in list_of_inputs:
                        if item[0] in result_dict:
                                result_dict[item[0]][1] += item[1]
                        else:
                                result_dict[item[0]] = item
                return list(result_dict.values())

        def get_inputs(self, node, output_item_name, amount):
                item_efficiency_list = [] # array 0 is name, 1 is amount
                output_item = node.get_item( node.get_item_index(output_item_name, node.current_recipe, False), node.current_recipe, False )
                ratio =  amount / output_item['a'] 
                for i in range( len(node.current_recipe['iI']) + len(node.current_recipe['fI']) ):
                        if node.input_recipes == None or node.input_recipes[i] == None:
                                item = node.get_item(i, node.current_recipe, True)
                                item_efficiency_list.append([ item['lN'], (item['a'] * ratio) ])
                        else:
                                item_to_find_children_of = node.get_item(i, node.current_recipe, True)
                                item_efficiency_list.extend( self.get_inputs(node.input_recipes[i], item_to_find_children_of['lN'], item_to_find_children_of['a']*ratio) ) 
                return item_efficiency_list

#gloable draggable support
def on_drag_start(event):
        widget = event.widget
        widget._drag_start_x = event.x
        widget._drag_start_y = event.y

def make_draggable(widget):
        widget.bind("<Button-1>", on_drag_start)
        widget.bind("<B1-Motion>", widget.node.on_drag_motion)


#Window settings
root = tk.Tk()
canvas = tk.Canvas(root )
canvas.pack(fill = tk.BOTH, expand = tk.YES)
app = Main(root)


root.mainloop()

