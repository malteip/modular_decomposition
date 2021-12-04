"""Text-based user interface.

This module implements a text-based user interface for using the modular decomposition algorithm.
"""

import npyscreen
from dot import path_to_dot, dot_to_graph, tree_to_dot, render_graph, render_from_source
from md import md_tree
import time
from graph_generators import *

engine = "dot"  # The default engine for rendering a graph


# Four form classes for the different forms (screens)
class MainForm(npyscreen.FormBaseNew, npyscreen.SplitForm):
    """A class for the menu-form."""

    def create(self):
        """A function that sets up the form."""
        y, x = self.useable_space()
        self.draw_line_at = y - 3

        self.welcome = self.add(npyscreen.TitleFixedText,
                                name='  Choose Option',
                                value=None,
                                labelColor='STANDOUT', rely=int(y * 0.382) - 2, relx=int(x * 0.382) - 4
                                )

        self.path = self.add(PathButton, name='Path', rely=int(y * 0.382), relx=int(x * 0.382))
        self.smallgraphs = self.add(SmallGraphsButton, name='Small Graphs', rely=int(y * 0.382) + 1,
                                    relx=int(x * 0.382))
        self.editor = self.add(EditorButton, name='Editor', rely=int(y * 0.382) + 2, relx=int(x * 0.382))
        self.generator = self.add(GeneratorButton, name='Graph Generator', rely=int(y * 0.382) + 3, relx=int(x * 0.382))
        self.settings = self.add(SettingsButton, name='Settings', rely=int(y * 0.382) + 4, relx=int(x * 0.382))
        self.quitbutton = self.add(QuitButton, name='Quit', rely=-3, relx=-11)


class PathForm(npyscreen.FormBaseNew):
    """A class for the path-form."""

    def afterEditing(self):
        """A function the switches the form to the main-form after editing."""
        self.parentApp.setNextForm("MAIN")

    def create(self):
        """A function that sets up the form."""
        y, x = self.useable_space()
        self.draw_line_at = y - 3
        self.welcome = self.add(npyscreen.TitleFixedText, name='  Enter a path to a graph in the .dot-language:',
                                labelColor='STANDOUT')
        self.editor = self.add(InputBox2, color='DEFAULT', height=3, rely=int(y / 2) - 2, max_width=x - 16, relx=8)
        self.runbutton = self.add(RunButton1, name='Run ►', rely=-3, relx=3, color='IMPORTANT')
        self.menubutton = self.add(MenuButton, name='Menu', rely=-3, relx=-19)
        self.quitbutton = self.add(QuitButton, name='Quit', rely=-3, relx=-11)


class SmallGraphsForm(npyscreen.FormBaseNew):
    """A class for the small_graphs-form."""

    def afterEditing(self):
        """A function that switches the form to the main-form after editing."""
        self.parentApp.setNextForm("MAIN")

    def create(self):
        """A function that sets up the form."""
        y, x = self.useable_space()
        self.welcome = self.add(npyscreen.TitleFixedText, name='  Pick a graph and hit run!', labelColor='STANDOUT')
        self.choice = self.add(npyscreen.SelectOne,
                               values=["K1", "2K1", "K2", "3K1", "K3", "co-P3", "P3", "4K1", "K4", "co-diamond",
                                       "diamond", "co-paw",
                                       "paw", "2K2", "C4", "claw", "co-claw", "P4", "5K1", "K5", "co-K5-e", "K5-e",
                                       "P3_U_2K1",
                                       "co-P3_U_2K1", "co-W4", "W4", "claw_U_K1", "co-claw_U_K1", "P2_U_P3",
                                       "co-P2_U_P3", "co-gem", "gem",
                                       "K3_U_2K1", "co-K3_U_2K1", "K1_4", "co-K1_4", "co-butterfly", "butterfly",
                                       "fork", "co-fork",
                                       "co-dart", "dart", "P5", "house", "K2_U_K3", "K2_3", "P", "co-P", "bull",
                                       "cricket", "co-cricket",
                                       "C5"], max_width=20, heigth=10, rely=3, relx=int(x * 0.382))
        self.runbutton = self.add(RunButton2, name='Run ►', rely=-3, relx=3, color='IMPORTANT')
        self.menubutton = self.add(MenuButton, name='Menu', rely=-3, relx=-19)
        self.quitbutton = self.add(QuitButton, name='Quit', rely=-3, relx=-11)


class EditorForm(npyscreen.FormBaseNew):
    """A class for the editor-form."""

    def afterEditing(self):
        """A function the switches the form to the main-form after editing."""
        self.parentApp.setNextForm("MAIN")

    def create(self):
        """A function that sets up the form."""
        y, x = self.useable_space()
        self.welcome = self.add(npyscreen.TitleFixedText, name='  Enter a graph in the .dot-language.',
                                labelColor='STANDOUT')
        self.editor = self.add(InputBox, name='graph', color='DEFAULT', max_height=y - 8, max_width=x - 16, relx=8)
        self.runbutton = self.add(RunButton3, name='Run ►', rely=-3, relx=3, color='IMPORTANT')
        self.menubutton = self.add(MenuButton, name='Menu', rely=-3, relx=-19)
        self.quitbutton = self.add(QuitButton, name='Quit', rely=-3, relx=-11)


class SettingsForm(npyscreen.Popup):
    """A class for the settings-form."""

    def afterEditing(self):
        """A function the switches the form to the main-form after editing."""
        try:
            engine_idx = self.choice.value[0]
        except:
            engine_idx = 0  # dot as default rendering engine
        global engine
        engine = self.choice.values[engine_idx]
        self.parentApp.setNextForm("MAIN")

    def create(self):
        """A function that sets up the form"""
        self.show_aty = 5
        self.welcome = self.add(npyscreen.TitleFixedText, name="Pick a graph rendering program.", labelColor='STANDOUT')
        self.choice = self.add(npyscreen.SelectOne,
                               values=['dot', 'neato', 'twopi', 'circo', 'fdp', 'sfdp', 'No rendering'])


class GeneratorForm(npyscreen.FormBaseNew, npyscreen.SplitForm):
    """A class for the generator-form."""

    def afterEditing(self):
        """A function the switches the form to the main-form after editing."""
        self.parentApp.setNextForm("MAIN")

    def create(self):
        """A function that sets up the form."""
        y, x = self.useable_space()
        self.draw_line_at = int(y*0.382)


        self.welcome = self.add(npyscreen.TitleFixedText,
                                name='  Choose a graph generator and generate some graphs.',
                                labelColor='STANDOUT')

        self.choice = self.add(GeneratorSelect,
                               values=["Generator A", "Generator B"],
                               max_height=3, heigth=4,
                               rely=4, relx=int(x * 0.382),
                               scroll_exit=True) # nicer without?!

        a = 15
        self.order = self.add(npyscreen.TitleText,
                               hidden=True, editable=False,
                               name="Graph Order:",
                               begin_entry_at=30,
                               labelColor='DEFAULT',
                               rely=int(y * 0.382) + 2, relx=max(10, int(x * 0.382) - a))

        self.prob = self.add(npyscreen.TitleText,
                              use_two_lines=False,
                              hidden=True, editable=False,
                              name="Edge Probability:",
                              begin_entry_at=30,
                              labelColor='DEFAULT',
                              rely=int(y * 0.382) + 3, relx=max(10, int(x * 0.382) - a))

        self.order2 = self.add(npyscreen.TitleText,
                               hidden=True, editable=False,
                               name="Graph Order:",
                               begin_entry_at=30,
                               labelColor='DEFAULT',
                               rely=int(y*0.382) + 2, relx=max(10, int(x * 0.382)-a))

        self.prob2 = self.add(npyscreen.TitleText,
                                     use_two_lines=False,
                                     hidden=True, editable=False,
                                     name="Quotients' Edge Probability:",
                                     begin_entry_at=30,
                                     labelColor='DEFAULT',
                                     rely=int(y*0.382) + 3, relx=max(10,int(x * 0.382)-a))

        self.min_mw = self.add(npyscreen.TitleText,
                               hidden=True, editable=False,
                               name="Minimal Prime Module Size:",
                               begin_entry_at=30,
                               labelColor='DEFAULT',
                               rely=int(y*0.382) + 4, relx=max(10,int(x * 0.382)-a))
        self.max_mw = self.add(npyscreen.TitleText,
                               hidden=True, editable=False,
                               name="Maximal Prime Module Size:",
                               begin_entry_at=30,
                               labelColor='DEFAULT',
                               rely=int(y*0.382) + 5, relx=max(10,int(x * 0.382)-a))
        self.mode = self.add(npyscreen.TitleSelectOne, name='Mode:',
                             hidden=True, editable=False,
                             begin_entry_at=25,
                             values=["Random", "Wide", "Deep"],
                             labelColor='DEFAULT',heigth=2,
                             rely=int(y*0.382) + 6, relx=max(10,int(x * 0.382)-a),
                             max_width=40,
                             scroll_exit=True) # 10

        self.runbutton = self.add(RunButton4, name='Run ►', rely=-3, relx=3, color='IMPORTANT')
        self.menubutton = self.add(MenuButton, name='Menu', rely=-3, relx=-19)
        self.quitbutton = self.add(QuitButton, name='Quit', rely=-3, relx=-11)

class GeneratorSelect(npyscreen.SelectOne):
    def when_value_edited(self):
        try:
            gen_choice = self.parent.parentApp.getForm('GENERATOR').choice.value[0]
        except:
            gen_choice = None
        # depending on the case, hide/display (make them editable/not editable) the widgets
        if gen_choice == 0:  # Generator A
            self.parent.parentApp.getForm('GENERATOR').order.hidden = False
            self.parent.parentApp.getForm('GENERATOR').prob.hidden = False
            self.parent.parentApp.getForm('GENERATOR').order.editable = True
            self.parent.parentApp.getForm('GENERATOR').prob.editable = True

            self.parent.parentApp.getForm('GENERATOR').order2.hidden = True
            self.parent.parentApp.getForm('GENERATOR').prob2.hidden = True
            self.parent.parentApp.getForm('GENERATOR').min_mw.hidden = True
            self.parent.parentApp.getForm('GENERATOR').max_mw.hidden = True
            self.parent.parentApp.getForm('GENERATOR').mode.hidden = True
            self.parent.parentApp.getForm('GENERATOR').order2.editable = False
            self.parent.parentApp.getForm('GENERATOR').prob2.editable = False
            self.parent.parentApp.getForm('GENERATOR').min_mw.editable = False
            self.parent.parentApp.getForm('GENERATOR').max_mw.editable = False
            self.parent.parentApp.getForm('GENERATOR').mode.editable = False

            self.parent.parentApp.getForm('GENERATOR').order2.update()
            self.parent.parentApp.getForm('GENERATOR').prob2.update()
            self.parent.parentApp.getForm('GENERATOR').min_mw.update()
            self.parent.parentApp.getForm('GENERATOR').max_mw.update()
            self.parent.parentApp.getForm('GENERATOR').mode.update()

            self.parent.parentApp.getForm('GENERATOR').order.update()
            self.parent.parentApp.getForm('GENERATOR').prob.update()


        elif gen_choice == 1:  # Generator B
            self.parent.parentApp.getForm('GENERATOR').order.hidden = True
            self.parent.parentApp.getForm('GENERATOR').prob.hidden = True
            self.parent.parentApp.getForm('GENERATOR').order.editable = False
            self.parent.parentApp.getForm('GENERATOR').prob.editable = False

            self.parent.parentApp.getForm('GENERATOR').order2.hidden = False
            self.parent.parentApp.getForm('GENERATOR').prob2.hidden = False
            self.parent.parentApp.getForm('GENERATOR').min_mw.hidden = False
            self.parent.parentApp.getForm('GENERATOR').max_mw.hidden = False
            self.parent.parentApp.getForm('GENERATOR').mode.hidden = False
            self.parent.parentApp.getForm('GENERATOR').order2.editable = True
            self.parent.parentApp.getForm('GENERATOR').prob2.editable = True
            self.parent.parentApp.getForm('GENERATOR').min_mw.editable = True
            self.parent.parentApp.getForm('GENERATOR').max_mw.editable = True
            self.parent.parentApp.getForm('GENERATOR').mode.editable = True

            self.parent.parentApp.getForm('GENERATOR').order.update()
            self.parent.parentApp.getForm('GENERATOR').prob.update()

            self.parent.parentApp.getForm('GENERATOR').order2.update()
            self.parent.parentApp.getForm('GENERATOR').prob2.update()
            self.parent.parentApp.getForm('GENERATOR').min_mw.update()
            self.parent.parentApp.getForm('GENERATOR').max_mw.update()
            self.parent.parentApp.getForm('GENERATOR').mode.update()


        else:
            self.parent.parentApp.getForm('GENERATOR').order.hidden = True
            self.parent.parentApp.getForm('GENERATOR').prob.hidden = True
            self.parent.parentApp.getForm('GENERATOR').order.editable = False
            self.parent.parentApp.getForm('GENERATOR').prob.editable = False

            self.parent.parentApp.getForm('GENERATOR').order2.hidden = True
            self.parent.parentApp.getForm('GENERATOR').prob2.hidden = True
            self.parent.parentApp.getForm('GENERATOR').min_mw.hidden = True
            self.parent.parentApp.getForm('GENERATOR').max_mw.hidden = True
            self.parent.parentApp.getForm('GENERATOR').mode.hidden = True
            self.parent.parentApp.getForm('GENERATOR').order2.editable = False
            self.parent.parentApp.getForm('GENERATOR').prob2.editable = False
            self.parent.parentApp.getForm('GENERATOR').min_mw.editable = False
            self.parent.parentApp.getForm('GENERATOR').max_mw.editable = False
            self.parent.parentApp.getForm('GENERATOR').mode.editable = False


# Custom widget classes (text-boxes, buttons, etc.)
class GeneratorButton(npyscreen.ButtonPress):
    """A class for the generator-button."""

    def whenPressed(self):
        """A function the switches the form to the main-form."""
        app.switchForm('GENERATOR')


class SettingsButton(npyscreen.ButtonPress):
    """A class for the settings-button."""

    def whenPressed(self):
        """A function the switches the form to the main-form."""
        app.switchForm('SETTINGS')


class RunButton1(npyscreen.ButtonPress):  # Path-form
    """A class for the run-button in the path-form."""

    def whenPressed(self):
        """A function the starts the the modular decomposition algorithm with a graph given by a path."""
        path_str = self.parent.parentApp.getForm('PATH').editor.value
        name = path_str[path_str.rindex('/') + 1:path_str.rindex('.')]
        graph_name = name
        if engine != "No rendering":
            render_graph(path_str, graph_name, engine, show=True)
        else:
            render_graph(path_str, graph_name, show=False)
        tree_name = name + '_mdt'
        dot_str = path_to_dot(path_str)
        graph = dot_to_graph(dot_str)
        md_start = time.time()
        tree = md_tree(graph)
        md_end = time.time()
        if engine != "No rendering":
            tree_to_dot(tree, tree_name)
        else:
            tree_to_dot(tree, tree_name, show=False)
        npyscreen.notify_confirm("Calculation time: " + str(md_end - md_start) + ' seconds', title=None, wrap=True)


class RunButton2(npyscreen.ButtonPress):
    """A class for the run-button in the smallgraphs-form."""

    def whenPressed(self):
        """A function the starts the the modular decomposition algorithm with a graph (from the small graph examples)
        selected by the user. """
        graph_name_idx = self.parent.parentApp.getForm('SMALLGRAPHS').choice.value[0]
        graph_name = self.parent.parentApp.getForm('SMALLGRAPHS').choice.values[graph_name_idx]
        # print(graph_name)
        path_str = "./small_graphs_dot/" + graph_name + ".dot"
        if engine != "No rendering":
            render_graph(path_str, graph_name, engine, show=True)
        else:
            render_graph(path_str, graph_name, show=False)
        tree_name = graph_name + '_mdt'
        dot_str = path_to_dot(path_str)
        graph = dot_to_graph(dot_str)
        md_start = time.time()
        tree = md_tree(graph)
        md_end = time.time()
        if engine != "No rendering":
            tree_to_dot(tree, tree_name)
        else:
            tree_to_dot(tree, tree_name, show=False)
        npyscreen.notify_confirm("Calculation time: " + str(md_end - md_start) + ' seconds', title=None, wrap=True)


class RunButton3(npyscreen.ButtonPress):
    """A class for the run-button in the editor-form."""

    def whenPressed(self):
        """A function the starts the the modular decomposition algorithm with a graph provided by the user
        input in the editor."""
        graph_str = self.parent.parentApp.getForm('EDITOR').editor.value
        source_str = 'graph{' + graph_str + '}'
        if engine != "No rendering":
            render_from_source(source_str, engine)
        else:
            render_from_source(source_str, show=False)
        graph = dot_to_graph(source_str)
        md_start = time.time()
        tree = md_tree(graph)
        md_end = time.time()

        if engine != "No rendering":
            tree_to_dot(tree, "your_md_tree")
        else:
            tree_to_dot(tree, "your_md_tree", show=False)
        npyscreen.notify_confirm("Calculation time: " + str(md_end - md_start) + ' seconds', title=None, wrap=True)


class RunButton4(npyscreen.ButtonPress):
    """A class for the run-button in the generator-form."""

    def whenPressed(self):
        """A function the starts the the modular decomposition algorithm with a graph provided by the user
        input in the editor."""
        try:
            gen_choice = self.parent.parentApp.getForm('GENERATOR').choice.value[0]
        except:
            gen_choice = None

        if gen_choice == 0:
            try:
                g_order = int(self.parent.parentApp.getForm('GENERATOR').order.value)
                g_prob = float(self.parent.parentApp.getForm('GENERATOR').prob.value)

                # computing graph
                g_start = time.time()
                g, g_name = random_graph(g_order, g_prob)
                g_end = time.time()

                # rendering graph
                rg_start = time.time()
                if engine != "No rendering":
                    n, m = write_graph_to_dot(g, g_name, show=True, engine_=engine)
                else:
                    n, m = write_graph_to_dot(g, g_name, show=False)
                rg_end = time.time()

                md_start = time.time()
                tree = md_tree(g)
                md_end = time.time()

                t_name = g_name + "_mdt"
                rt_start = time.time()
                if engine != "No rendering":
                    tree_to_dot(tree, t_name, show=True)
                else:
                    tree_to_dot(tree, t_name, show=False)
                rt_end = time.time()

                npyscreen.notify_confirm("|V| = " + str(n) + "  |E| = " + str(m) + "\n"
                                         + "------------------------------------------------------\n"
                                         + "Computation times (seconds):\n"
                                         + str(round(g_end - g_start, 5)) + " (generating the graph)\n"
                                         + str(round(md_end - md_start, 5)) + " (computing the modular decomposition)\n"
                                         + str(round((rg_end - rg_start) + (rt_end - rt_start),
                                                     5)) + " (saving/rendering the .dot-/.pdf-files)\n",
                                         title=None, wrap=True)

            except:
                npyscreen.notify_confirm("Missing argument(s)! Please check your configuration!", title=None, wrap=True)

        elif gen_choice == 1:
            try:
                g_order2 = int(self.parent.parentApp.getForm('GENERATOR').order2.value)
                g_prob2 = float(self.parent.parentApp.getForm('GENERATOR').prob2.value)
                g_min_mw = int(self.parent.parentApp.getForm('GENERATOR').min_mw.value)
                g_max_mw = int(self.parent.parentApp.getForm('GENERATOR').max_mw.value)
                g_mode = self.parent.parentApp.getForm('GENERATOR').mode.value[0]

                if g_mode == 1:  # WIDE
                    mode = Mode.WIDE
                elif g_mode == 2:  # DEEP
                    mode = Mode.DEEP
                else:   # RANDOM
                    mode = Mode.RANDOM

                # computing graph
                g_start = time.time()
                g, g_name = mw_bound_graph2(g_order2, g_min_mw, g_max_mw, g_prob2, mode)
                g_end = time.time()

                # rendering graph
                rg_start = time.time()
                if engine != "No rendering":
                    n, m = write_graph_to_dot(g, g_name, show=True, engine_=engine)
                else:
                    n, m = write_graph_to_dot(g, g_name, show=False)
                rg_end = time.time()

                # computing md tree
                md_start = time.time()
                tree = md_tree(g)
                md_end = time.time()

                t_name = g_name + "_mdt"

                # rendering md tree
                rt_start = time.time()
                if engine != "No rendering":
                    tree_to_dot(tree, t_name, show=True)
                else:
                    tree_to_dot(tree, t_name, show=False)
                rt_end = time.time()

                npyscreen.notify_confirm("|V| = " + str(n) + "  |E| = " + str(m) + "\n"
                                         + "------------------------------------------------------\n"
                                         + "Computation times (seconds):\n"
                                         + str(round(g_end - g_start, 5)) + " (generating the graph)\n"
                                         + str(round(md_end - md_start, 5)) + " (computing the modular decomposition)\n"
                                         + str(round((rg_end - rg_start) + (rt_end - rt_start), 5)) + " (saving/rendering the .dot-/.pdf-files)\n",
                                         title=None, wrap=True)
            except:
                npyscreen.notify_confirm("Missing argument(s)! Please check your configuration!", title=None,
                                         wrap=True)
        else:
            npyscreen.notify_confirm("Please select a generator and specify the parameters!", title=None, wrap=True)


class QuitButton(npyscreen.ButtonPress):
    """A class for the quit-button."""

    def whenPressed(self):
        """A function that exits the program."""
        exit()


class MenuButton(npyscreen.ButtonPress):
    """A class for the menu-button."""

    def whenPressed(self):
        """A function the switches the form to the main-form."""
        app.switchForm('MAIN')


class EditorButton(npyscreen.ButtonPress):
    """A class for the editor-button."""

    def whenPressed(self):
        """A function the switches the form to the editor-form."""
        app.switchForm('EDITOR')


class PathButton(npyscreen.ButtonPress):
    """A class for the path-button."""

    def whenPressed(self):
        """A function the switches the form to the path-form."""
        app.switchForm('PATH')


class SmallGraphsButton(npyscreen.ButtonPress):
    """A class for the smallgraphs-button."""

    def whenPressed(self):
        """A function the switches the form to the smallgraphs-form."""
        app.switchForm('SMALLGRAPHS')


class InputBox2(npyscreen.BoxTitle):
    """A class for widget in the path-form."""
    _contained_widget = npyscreen.Filename


class InputBox(npyscreen.BoxTitle):
    """A class for widget in the editor-form."""
    _contained_widget = npyscreen.MultiLineEdit


class App(npyscreen.NPSAppManaged):
    """A class for the application."""

    def onStart(self):
        """A function that sets up the application."""
        self.addForm('MAIN', MainForm, name='MODULAR DECOMPOSITION')
        self.addForm('PATH', PathForm, name='MODULAR DECOMPOSITION')
        self.addForm('SMALLGRAPHS', SmallGraphsForm, name='MODULAR DECOMPOSITION')
        self.addForm('EDITOR', EditorForm, name='MODULAR DECOMPOSITION')
        self.addForm('GENERATOR', GeneratorForm, name='MODULAR DECOMPOSITION')
        self.addForm('SETTINGS', SettingsForm, name='SETTINGS', lines=14, rely=20)


if __name__ == '__main__':
    app = App()
    app.run()
