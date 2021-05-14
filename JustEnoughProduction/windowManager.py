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
                top_menu_frame = Frame(root, )
                top_menu_frame.place(x = 0, y = 0)

                #button for a new recipe node
                new_crafting_node_button=Button(top_menu_frame,style = 'default.TButton',text='New Crafting Node',command=lambda:RecipeNode(''))
                new_crafting_node_button.grid(row = 0, column = 1)

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

        def __init__(self, item_name):
                global item_fluid_dict
                self.item_name = item_name
                self.null_recipe = {'Cannot Find Item In Context':[{'en': True, 'dur':0,'eut':0,'iI':[],'iO':[],'fI':[],'fO':[]}]}

                self.dict_recipes = self.null_recipe
                self.potential_connect = None#to help connect nodes

                self.input_recipes = None #the list of nodes that this node has as input
                self.output_recipes = None #the list of nodes that this node has as input

                self.lines_out = []
                self.lines_in = []

                #--UI WORK---
                recipe_frame = Frame(root, style = 'recipe.TFrame' )
                self.recipe_frame = recipe_frame
                self.recipe_frame.node = self #for a reference back to this class
                self.make_draggable(recipe_frame)
                recipe_frame.place(x = 100, y = 30)

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

                #items frame
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
                self.var_machine.trace('w', lambda a,b,c :self.update_machine_query())

                self.machine_label = Label(recipe_frame, style='info_box.TLabel', text = self.var_machine.get())#wont see this until machine)dropdown goes away
                self.machine_label.grid( row = 2, column = 0 )

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

                #Exit Button/Top of Frame
                def remove_node():
                        self.destroy_all_connection(self)
                        recipe_frame.destroy()
                exit_button = Button(recipe_frame,style='exit_button.TButton', text = 'X', command = lambda:remove_node())#need to also remove the line
                exit_button.grid( row = 0, column = 1, sticky = 'e' )

                #Minimize button
                sel = 0
                def show_search_inputs():
                        self.search_entry.grid(row = 1, column = 0, columnspan = 2, sticky = 'ew')#make sure this is the same as when init
                        self.usage_dropdown.grid( row = 1, column =1, sticky = 'e')
                        inc_rec_button.grid( row = 3, column = 1, sticky = 'n')
                        dec_rec_button.grid( row = 3, column = 0, sticky = 'n')
                        self.rec_out_of_label.grid( row = 3, column = 0, columnspan = 2, sticky = 'n')
                        self.machine_dropdown.grid( row = 2, column = 0 )
                        self.update_connections(self)

                def hide_search_inputs():
                        self.search_entry.grid_forget()
                        self.usage_dropdown.grid_forget()
                        inc_rec_button.grid_forget()
                        dec_rec_button.grid_forget()
                        self.rec_out_of_label.grid_forget()
                        self.machine_dropdown.grid_forget()
                        self.machine_label['text'] = self.var_machine.get()
                        self.update_connections(self)

                def min_max_widget():
                        nonlocal sel
                        if (sel == 0):
                                hide_search_inputs()
                        else:
                                show_search_inputs()
                        sel = (sel + 1) % 2

                minimize_button = Button(recipe_frame,style='exit_button.TButton', text = '_', command = lambda:min_max_widget())
                minimize_button.grid( row = 0, column = 1, sticky = 'e',  padx = 20)

                #------------------------------------
                #right click menu for items
                self.popup_item = ''
                self.popup_is_input = True#True if item is apart of the input
                self.popup_menu = Menu(root, tearoff = 0)
                self.popup_menu.add_command(label = self.popup_item)#able to add a command here but nothing comes to mind yet
                self.popup_menu.add_separator()
                self.popup_menu.add_command(label = 'Search', command = lambda: RecipeNode(self.popup_item) )
                self.popup_menu.add_command(label = 'Connect', command = lambda: self.make_potential_connection())
                self.popup_menu.add_command(label = 'Disconnect', command = lambda: self.destroy_connection(self, self.popup_item, self.popup_is_input))
                self.popup_menu.add_command(label = 'Fix Arrows', command = lambda: self.update_connections(self))

                self.update_item_query()#load

        #---------------END __INIT__----------------------

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

        #updates the recipe_list for this machine
        def update_machine_query(self):
                self.rec_num = 0 #reset the recipe number

                if (self.item_name != self.search_entry.get()):#user tries to select another machine without specifiying the search for it
                        self.update_item_query()
                self.recipe_list = self.dict_recipes.get(self.var_machine.get(),-1)#this only occurs when the name changes without searching
                if (self.recipe_list == -1):#if they dictionary item does not exist in context
                        self.recipe_list = next(iter(self.null_recipe.values()))

                self.is_shaped_shapeless = ('o' in self.recipe_list[0])#update is_shaped_shapeless
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

        #connect nodes
        def get_clicked(self, event):
                root.unbind('<Button-1>')
                self.potential_connect = event.widget
                self.make_potential_connection()

        def make_potential_connection(self ):
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

        def destroy_all_connection(self, node):
                if node.input_recipes != None:
                        for connected_node in node.input_recipes:
                                if (connected_node != None):
                                        index = node.input_recipes.index(connected_node)
                                        if index < len(node.recipe_list[node.rec_num]['iI']):
                                                self.destroy_connection(node, node.recipe_list[node.rec_num]['iI'][index]['lN'], True)
                                        else:
                                                self.destroy_connection(node, node.recipe_list[node.rec_num]['fI'][index - len(node.recipe_list[node.rec_num]['iI'])]['lN'], True)
                if node.output_recipes != None:
                        for connected_node in node.output_recipes:
                                if (connected_node != None):
                                        index = node.output_recipes.index(connected_node)
                                        if index < len(node.recipe_list[node.rec_num]['iO']):
                                                self.destroy_connection(node, node.recipe_list[node.rec_num]['iO'][index]['lN'], False)
                                        else:
                                                self.destroy_connection(node, node.recipe_list[node.rec_num]['fO'][index - len(node.recipe_list[node.rec_num]['iO'])]['lN'], False)

        def destroy_connection(self, node, item_name, is_input):#to remove a relation
                if is_input:
                        if (node.lines_in != None):
                                index = None
                                for i in range(len(node.recipe_list[node.rec_num]['iI'])):
                                        if (item_name == node.recipe_list[node.rec_num]['iI'][i]['lN'] ):
                                                index = i
                                for i in range(len(node.recipe_list[node.rec_num]['fI'])):
                                        if (item_name == node.recipe_list[node.rec_num]['fI'][i]['lN'] ):
                                                index = len(node.recipe_list[node.rec_num]['iI']) + i
                                if (index == None) or (node.lines_in[index] == None):
                                        return None
                                canvas.delete(node.lines_in[index])
                                node.lines_in[index] = None
                                self.destroy_connection(node.input_recipes[index], item_name, not(is_input))
                                node.input_recipes[index] = None
                else:
                        if (node.lines_out != None):
                                index = None
                                for i in range(len(node.recipe_list[node.rec_num]['iO'])):
                                        if (item_name == node.recipe_list[node.rec_num]['iO'][i]['lN'] ):
                                                index = i
                                for i in range(len(node.recipe_list[node.rec_num]['fO'])):
                                        if (item_name == node.recipe_list[node.rec_num]['fO'][i]['lN'] ):
                                                index = len(node.recipe_list[node.rec_num]['iO']) + i
                                if (index == None) or (node.lines_out[index] == None):
                                        return None
                                canvas.delete(node.lines_out[index])
                                node.lines_out[index] = None
                                self.destroy_connection(node.output_recipes[index], item_name, not(is_input))
                                node.output_recipes[index] = None

        def create_connection(self, item_name, output_rec_node, input_rec_node):#connects the nodes by the input node linking to the output
                in_recipe = input_rec_node.recipe_list[input_rec_node.rec_num]
                out_recipe = output_rec_node.recipe_list[output_rec_node.rec_num]
                if (input_rec_node.input_recipes == None):#if it doesnt yet have the list initalized, could probably do this in reload()
                        input_rec_node.input_recipes = [None] * (len(in_recipe['iI']) + len(in_recipe['fI']) )#make an empty list of input item size
                        input_rec_node.lines_in = [None ] * (len(in_recipe['iI']) + len(in_recipe['fI']) )

                if (output_rec_node.output_recipes == None):#if it doesnt yet have the list initalized #its a doubly linked list
                        output_rec_node.output_recipes = [None] * (len(out_recipe['iO']) + len(out_recipe['fO']) )#make an empty list of input item size
                        output_rec_node.lines_out = [None] * (len(out_recipe['iO']) + len(out_recipe['fO']) )

                input_item_index = None
                output_item_index = None
                for i in range(len(in_recipe['iI'])) :
                        if (item_name == in_recipe['iI'][i]['lN'] ):
                                input_item_index = i
                for i in range(len(in_recipe['fI'])) :
                        if (item_name == in_recipe['fI'][i]['lN'] ):
                                input_item_index = len(in_recipe['iI']) + i

                for i in range(len(out_recipe['iO'])) :#BUG: Will not work with a shapped/shapeless recipe output
                        if (item_name == out_recipe['iO'][i]['lN'] ):
                                output_item_index = i
                for i in range(len(out_recipe['fO'])) :
                        if (item_name == out_recipe['fO'][i]['lN'] ):
                                output_item_index = len(out_recipe['iO']) + i
                
                if (input_item_index != None and output_item_index != None) and (output_rec_node.lines_out[output_item_index] == None) and (input_rec_node.lines_in[input_item_index] == None):#limiting one input to one output
                        input_rec_node.input_recipes[input_item_index] = output_rec_node
                        output_rec_node.output_recipes[output_item_index] = input_rec_node

                        new_line = canvas.create_line(
                        output_rec_node.recipe_frame.winfo_x() + output_rec_node.items_frame.grid_slaves(0,1)[0].winfo_x() + output_rec_node.items_frame.grid_slaves(0,1)[0].winfo_width(),
                        output_rec_node.recipe_frame.winfo_y() + output_rec_node.items_frame.winfo_y() + (1+2*output_item_index)*output_rec_node.items_frame.grid_slaves(0,1)[0].winfo_height()/2 ,
                        input_rec_node.recipe_frame.winfo_x() + input_rec_node.items_frame.grid_slaves(0,0)[0].winfo_x(),
                        input_rec_node.recipe_frame.winfo_y() + input_rec_node.items_frame.winfo_y() + (1+2*input_item_index)*input_rec_node.items_frame.grid_slaves(0,1)[0].winfo_height()/2,
                        arrow =tk.LAST, fill = "black")
                        input_rec_node.lines_in[input_item_index] = new_line
                        output_rec_node.lines_out[output_item_index] = new_line
                #print(output_rec_node.output_recipes, ';', input_rec_node.input_recipes)
                #print(output_rec_node.lines_out , ',', output_rec_node.lines_in, '; ', input_rec_node.lines_out, ',', input_rec_node.lines_in)
        
        def update_connections(self, node):#to fix visual effects with lines
                node.recipe_frame.update()
                if (node.input_recipes != None):
                        for i in range(len(node.input_recipes)):
                                if (node.input_recipes[i] != None):
                                        x1, y1, x2, y2 = canvas.coords(node.lines_in[i])
                                        canvas.coords(node.lines_in[i], x1, y1, node.recipe_frame.winfo_x() + node.items_frame.grid_slaves(0,0)[0].winfo_x(),
                                        node.recipe_frame.winfo_y() + node.items_frame.winfo_y() + (1+2*i)*node.items_frame.grid_slaves(0,1)[0].winfo_height()/2)

                if (node.output_recipes != None):
                        for i in range(len(node.output_recipes)):
                                if (node.output_recipes[i] != None):
                                        x1, y1, x2, y2 = canvas.coords(node.lines_out[i])
                                        canvas.coords(node.lines_out[i], node.recipe_frame.winfo_x() + node.items_frame.grid_slaves(0,1)[0].winfo_x() + node.items_frame.grid_slaves(0,1)[0].winfo_width(),
                                        node.recipe_frame.winfo_y() + node.items_frame.winfo_y() + (1+2*i)*node.items_frame.grid_slaves(0,1)[0].winfo_height()/2, x2, y2)

        
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
                for line in widget.node.lines_out:
                        if line != None:
                                x1, y1, x2, y2 = canvas.coords(line)
                                canvas.coords(line, x1 - widget._drag_start_x + event.x, y1 - widget._drag_start_y + event.y, x2, y2)
                
                for line in widget.node.lines_in:
                        if line != None:
                                x1, y1, x2, y2 = canvas.coords(line)
                                canvas.coords(line, x1, y1, x2 - widget._drag_start_x + event.x, y2 - widget._drag_start_y + event.y)
                
        def make_draggable(self, widget):
                widget.bind("<Button-1>", self.on_drag_start)
                widget.bind("<B1-Motion>", self.on_drag_motion)

        def do_popup_menu(self, event, item, is_input):
                self.popup_item = item
                self.popup_is_input = is_input
                try:
                        self.popup_menu.entryconfig(0, label = item)
                        self.popup_menu.tk_popup(event.x_root, event.y_root)
                finally:
                        self.popup_menu.grab_release()




#Window settings
root = tk.Tk()
canvas = tk.Canvas(root )
canvas.pack(fill = tk.BOTH, expand = tk.YES)
app = Main(root)


root.mainloop()

