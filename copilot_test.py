import PySimpleGUI

# create a GUI with three blocks

layout = [[PySimpleGUI.Text('Block 1')],
            [PySimpleGUI.Text('Block 2')],
            [PySimpleGUI.Text('Block 3')]]

window = PySimpleGUI.Window('My new window').Layout(layout)

# create a loop to keep the GUI open

while True:
    event, values = window.Read()
    if event is None:
        break

# close the GUI

window.Close()

