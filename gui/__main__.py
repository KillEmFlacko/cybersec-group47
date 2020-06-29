from guizero import App, Box, Text, ListBox, Drawing

gapp = App("Hi!")
left_box = Box(gapp, height="fill", width="fill",align="left", border=True)

button_box = Box(gapp, height="fill", width="fill",align="left", border=True)

fake_box = Box(gapp, height="fill", width="fill", align="right", border=True)

Text(left_box,text="User list",width="fill",align="top")
Drawing(left_box,width="fill",height=20,align="bottom")
Drawing(left_box,height="fill",width=20,align="left")
Drawing(left_box,height="fill",width=20,align="right")
list_box = ListBox(left_box,height="fill",width="fill", items=["Ciccio","Gay"])
gapp.display()
