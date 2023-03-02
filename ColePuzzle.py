#TODO fix filedialog (only fluxbox),button_color= fix, windows jump (only linux)
#compiled with pyinstaller --clean --distpath . --splash images/splash.png --onefile ColePuzzle.py
import PySimpleGUI as sg
import os
#import platform
#import pyi_splash
from PIL import Image
from sympy.combinatorics import Permutation as Perm
from sympy.combinatorics import PermutationGroup as PermGroup
from cryptography.fernet import Fernet

#pyi_splash.close()

#if platform.system() == "Linux": # a fix for the "jumping window" problem introduced by the Linux Windowing manager in 2022
	# Read the window type, if it is not even read the alpha attribute cannot be set here
#root=sg.tk.Tk()
#root.attributes("-type")
	# root.wait_visibility(root)

font = ("Sans", 14)
sg.theme("LightBlue1")
bg = sg.theme_background_color()

level = 0 #0 easy, 1 medium, 2 hard, 3 evil, 4 custom
move_count = 0 
perm = Perm(8) #initialize identity perm
game_on = False #start game with scramble
joker_text = "" #joker (middle) button in evil mode
shpr = False #shift pressed
zeroone = Perm([1,2,3,4,5,6,7,8,9,0]) #shift [0..8] to [1..9]

#	0	1	2
#	3	4	5
#	6	7	8

moves = [[Perm(0,5,1,3,2,4)(6,8,7),Perm(0,7,3,1,6,4)(2,8,5)], #easy
[Perm(0,4,1,3)(2,5),Perm(0,6,3)(1,8,5,2,7,4)], #medium
[Perm(0,8)(1,7)(2,6)(3,5),Perm(0,6,3)(1,8,4)], #hard
[Perm(8),Perm(8)], #evil, initialize as trivial group
[Perm(0,2,8,6)(1,5,7,3),Perm(1,3)(2,6)(5,7)]] #custom, initialize as dihedral group D8

G = [PermGroup(moves[m][0],moves[m][1]) for m in range(5)] #permutation groups

bs = 100 #pixel size of boxes
img = Image.open("images/squares.png")
boxes = [""]*9
for n in range(9):
	boxes[n] = "boxes/"+str(n)+".png"
	area = img.crop(((n%3)*bs,(n//3)*bs,(n%3)*bs+bs-1,(n//3)*bs+bs-1))
	area.save(boxes[n])

fernet = Fernet("RAXdcIQ5BYg-CM5pWGMc_s0SZsYFHXkiSXi4w-V8nTU=") #random key
with open("solutions.cry","rb") as enc_file:
	encrypted = enc_file.read()
solutions = eval(fernet.decrypt(encrypted)) #get solutions from encrypted file

if not os.path.isfile("highscore.cry"):
	highscores=[["easy",10,"Cauchy"],["medium",50,"Sylow"],["hard",100,"Burnside"],["evil",999,"Frobenius"]]
else:
	with open("highscore.cry","rb") as enc_file:
		encrypted = enc_file.read()
	highscores = eval(fernet.decrypt(encrypted)) #get highscores from encrypted file

menu_def = [["&Settings", ["&Image",["&squares ✓::squares","&keypad::numbers","&tower bridge::tower","&custom…::custom"],"&High scores","E&xit"]], ["&Help", ["&Instructions","&Background","Hi&nts","&About"]]]

frame_layout = [[sg.Radio("easy", "RAD",default=True,enable_events=True,key="level0"),
sg.Radio("medium","RAD",enable_events=True,key="level1"),
sg.Radio("hard","RAD",enable_events=True,key="level2"),
sg.Radio("evil","RAD",enable_events=True,key="level3"),
sg.Radio("custom","RAD",enable_events=True,key="level4")]] 

layout = [
[sg.VPush()],
[sg.Menu(menu_def,key="menu",font=font)],
[sg.Frame("Level", frame_layout)],
[sg.Push(),sg.Button(image_filename="buttons/00.png",key="button0",border_width=0),
sg.Button(image_filename="buttons/blank.png",button_color=(bg,bg),key="button2",border_width=0),
sg.Button(image_filename="buttons/01.png",key="button1",border_width=0),sg.Push()], 
[sg.HorizontalSeparator()],
[sg.Push(),sg.Text("",key="text_solution",text_color="red"),sg.Push()],
[sg.HorizontalSeparator()],
[[sg.Push()]+[sg.Image(filename=boxes[3*r+c],key=str(3*r+c)) for c in range(3)]+[sg.Push()] for r in range(3)],
#[sg.HorizontalSeparator()],
[sg.Text("")],
[sg.Push(),sg.Button("Scramble",key="key_new"),sg.Button("Restore",key="key_restore"),sg.Button("Show solution",key="key_solution"),sg.Push()]
]

window = sg.Window("The Cole puzzle", layout,font=font,finalize=True) 

for i in range(3): window["button"+str(i)].bind("<Button-3>","R") #right click

window.bind("<KeyPress>","press")
window.bind("<KeyRelease>","release")
window.bind("<Left>","button0")
window.bind("<Right>","button1")
window.bind("<Up>","button2")

def init(level):
	global move_count
	move_count=0
	window["text_solution"].update("")
	for n in range(9): window[str(n)].update(filename=boxes[n^perm])
	for n in range(2): window["button"+str(n)].update(image_filename="buttons/"+str(level)+str(n)+".png") 
	if level == 3: window["button2"].update(button_color=("white","black"),image_filename="buttons/32.png") 
	else: window["button2"].update(image_filename="buttons/blank.png",button_color=(bg,bg))

def createwindow():
	layout_input = [[sg.Text("Define your own buttons or use one of the following groups\n(see instructions in the Help menu).")],
	[sg.Button("D₈",key="D8"),sg.Button("C₃×C₃",key="regular"),sg.Button("M₉",key="M9"),sg.Button("AGL(1,9)",key="AGL1"),sg.Button("AΓL(1,9)",key="AGamma"),sg.Button("AGL(2,3)",key="AGL2"),sg.Button("SL(2,8)",key="SL"),sg.Button("A₉",key="A9"),sg.Button("S₉",key="S9")],
	[sg.Text("Left button permutation:",justification="r",size=(22,1)),sg.Input(str((zeroone**-1*moves[4][0]*zeroone).cyclic_form),size=(25,1),key="ckey1")],
	[sg.Text("Right button permutation:",justification="r",size=(22,1)),sg.Input(str((zeroone**-1*moves[4][1]*zeroone).cyclic_form),size=(25,1),key="ckey2")],
	[sg.Push(),sg.Button("Submit"),sg.Push(),sg.Button("Cancel"),sg.Push()]]
	return sg.Window("Enter custom buttons",layout_input,font=font)

def createHS():
	global highscores
	layout_input = [[sg.Table(highscores,headings=["Level","Moves","Name"],justification="l",auto_size_columns=False,num_rows=4,col_widths=[10,6,20],sbar_width=0,sbar_arrow_width=0,key="table")],
	[sg.Push(),sg.Button("OK"),sg.Push(),sg.Button("Delete"),sg.Push()]]
	win_HS = sg.Window("High scores",layout_input,font=font)
	while True:
		event2, values2 = win_HS.read()
		if event2 == "Delete":
			highscores = [["easy",10,"Cauchy"],["medium",50,"Sylow"],["hard",100,"Burnside"],["evil",999,"Frobenius"]]
			win_HS["table"].update(highscores) #update table
			if os.path.isfile("highscore.cry"): os.remove("highscore.cry")
		if event2 in [None,"OK",sg.WIN_CLOSED]:
			win_HS.close()
			break

def getHSname():
	layout_input = [[sg.Text("New high score! You solved the puzzle in "+str(move_count)+" moves.")],
	[sg.Text("Enter your name:"),sg.Input(highscores[level][2],key="name",size=(20,1))],
	[sg.Push(),sg.Button("Submit"),sg.Push(),sg.Button("Cancel")],]
	win_win = sg.Window("You won!",layout_input,font=font) 
	while True:
		event2,values2 = win_win.read()
		if event2 in [None,"Cancel",sg.WIN_CLOSED]: break
		if event2 == "Submit":
			highscores[level][2] = values2["name"]
			encrypted = fernet.encrypt(str.encode(repr(highscores)))
			with open('highscore.cry', 'wb') as encrypted_file:
				encrypted_file.write(encrypted)
			break
	win_win.close()


while True:
	event, values = window.read() 
	#print(event,values) #debug

	if event in [None,"Exit",sg.WIN_CLOSED]: break 

	if event in ["press","release"]:
		e = window.user_bind_event
		if e.keysym in ["Shift_R","Shift_L"]:
			shpr = True if event == "press" else False
	
	if event == "Background":#https://qaz.wtf/u/convert.cgi?text=Easy+mode%3A
		sg.popup_scrolled("The scrambled 3×3 image represents a permutation π of the nine boxes. Pressing the left or the right button performs permutations σ or τ on the nine boxes. Consequently, π is replaced by σπ or τπ respectively. Solving the puzzle amounts to express π⁻¹ as a \"word\" with the letters σ and τ in the symmetric group S₉, e.g.\n\n   π⁻¹ = σστστττ.\n\nIn this sense the puzzle is a 2-dimensional version of the famous 𝘙𝘶𝘣𝘪𝘬'𝘴 𝘤𝘶𝘣𝘦.\nTo decide whether π equals a given word in σ and τ is known as the \"word problem\" in combinatorial group theory. Although the word problem is unsolvable in sufficiently complicated (infinite) groups, it can be solved in finite groups by naive algorithms (enumerate all words in lexicographical order).\n\n𝗘𝗮𝘀𝘆 𝗺𝗼𝗱𝗲: σ and τ permute the three rows and columns without disturbing their internal order. Hence, they generate a transitive permutation group isomorphic to\n\n   S₃×S₃.\n\nIn particular, there are only (3!)²=36 possible permutations π (the trivial permutation is of course excluded by design). Every permutation can be written as a word of length 6 in the letters σ, σ⁻¹, τ, τ⁻¹ (this is known as 𝘨𝘰𝘥\'𝘴 𝘯𝘶𝘮𝘣𝘦𝘳). Hence, at most six (left/right mouse button) clicks are necessary to solve the puzzle and the provided solution is always of shortest length. \n\n𝗠𝗲𝗱𝗶𝘂𝗺 𝗺𝗼𝗱𝗲: σ and τ permute the three rows as sets allowing the internal order of each row to be disturbed. Hence, they generate an imprimitive permutation group isomorphic to the wreath product\n\n   S₃≀S₃.\n\nIn particular, there are (3!)⁴=1296 possible permutations π and god\'s number is 13.\n\n𝗛𝗮𝗿𝗱 𝗺𝗼𝗱𝗲: Here we regard the nine boxes as 1-dimensional subspaces of a 2-dimensional vector space over the field with 8 elements. The permutations σ and τ generate a primitive (in fact 3-transitive) permutation group isomorphic to\n\n   ΣL(2,8)=SL(2,8)⋊Aut(𝔽₈).\n\nIn particular, there are 504·3=1512 possible permutations π and god\'s number is 20 (just as for the Rubik's cube). Although the group is not much bigger than in the medium level, its structure is more complicated (it is a non-solvable group, more precisely an \"almost simple group\"). In particular, every non-trivial element fixes at most three boxes (as τ does).\n\n𝗘𝘃𝗶𝗹 𝗺𝗼𝗱𝗲: For every scramble, σ and τ are chosen randomly such that they generate the full symmetric group S₉. Thus, each of the 9!-1=362,879 non-trivial permutations may occur for π. In comparison, the Rubik's cube has approx. 4.3·10¹⁹ possible configurations.\nBy a theorem of Dixon, the probability that two randomly uniformly chosen permutations of Sₙ generate a subgroup containing the alternating group Aₙ tends to 1 with 𝘯 → ∞. The probability that these permutations generate Sₙ tends to 0.75. This makes it easy to pick σ and τ as desired. In fact, for every non-trivial σ there exists a τ such that σ and τ generate S₉.\n\n𝗖𝘂𝘀𝘁𝗼𝗺 𝗺𝗼𝗱𝗲: Here you can define σ or τ as you wish. Some interesting permutation groups are predefined: The dihedral group D₈ as the symmetry group of the square (box 5 in the middle stays fixed). The elementary abelian group C₃×C₃ acting regularly by shifting rows and columns. The Mathieu group M₉=(C₃×C₃)⋊Q₈ acts as a Frobenius group. Another Frobenius group is the affine group AGL(1,9)=(C₃×C₃)⋊C₈. An extension is the affine-semilinear group AΓL(1,9)=AGL(1,9)⋊C₂≅(C₃×C₃)⋊SD₁₆. The last three groups are contained in AGL(2,3)=(C₃×C₃)⋊GL(2,3). Then we have the sharply 3-transitive, simple group SL(2,8), related to the hard mode. For sake of completeness also the alternating group A₉ and the symmetric group S₉ can be chosen with familiar generators.\n\nThe game was named after 𝘍𝘳𝘢𝘯𝘬 𝘕𝘦𝘭𝘴𝘰𝘯 𝘊𝘰𝘭𝘦, who classified all 34 transitive permutation groups of degree 9 in 1893 (11 of those are primitive).",title="Background",background_color="orange",font=("Sans", 14),text_color="black",size=(40,20))

	if event == "Instructions":
		sg.popup_scrolled("𝗛𝗼𝘄 𝘁𝗼 𝗽𝗹𝗮𝘆:\n(1) Choose a level of difficulty (start with easy).\n(2) Press the two buttons on the top to see what they do (a right mouse click undoes a left click).\n(3) If confused, press 𝘙𝘦𝘴𝘵𝘰𝘳𝘦.\n(4) Once you are familiar with the buttons, press 𝘚𝘤𝘳𝘢𝘮𝘣𝘭𝘦 to start the game.\n(5) Press the buttons in some order to unscramble the image.\n(6) If desperate, press 𝘚𝘩𝘰𝘸 𝘴𝘰𝘭𝘶𝘵𝘪𝘰𝘯.\n(7) Once you know how to solve the puzzle, try to minimize the number of button click to get a new high score.\n\n𝗖𝗼𝗺𝗺𝗲𝗻𝘁𝘀:\n(1)The game can only be won by pressing 𝘚𝘤𝘳𝘢𝘮𝘣𝘭𝘦 first and not consulting the solution.\n(2) A detailed explanation of the difficulty levels is given in the 𝘉𝘢𝘤𝘬𝘨𝘳𝘰𝘶𝘯𝘥 menu entry.\n(3) In the solution, L and R denote the left and right button respectively. L\' and R\' refer to a right mouse button click. The solution is not available on the evil and custom level, although computer algebra systems like GAP can compute an optimal solution within seconds.\n(4) In the evil level you first need to scramble. The buttons are then assigned to random permutations. In particular, every game is different. The middle button can be used to perform a sequence of left/right button moves (this makes it easy to correct mistakes). Right click the middle button to define its action as a sequence of L, L\', R, R\' without spaces, parentheses or powers. A left click on the middle button counts as one move (relevant to the high score).\n(5) Instead of the mouse you can use the keys ←, ↑, →, where ↑ emulates the middle button in the evil mode. The reverse actions are triggered in combination with the Shift key ⇧.\n(6) If you do not like the default 3×3 image (𝘴𝘲𝘶𝘢𝘳𝘦𝘴), you can pick another one (even your own photo, which is scaled to 300×300 pixels) at the menu.\n(7) The 𝘤𝘶𝘴𝘵𝘰𝘮 level is only meant for experiments (the game cannot be won). Here you can define the buttons as you wish. To do so, enter the corresponding permutations of the nine boxes numbered as\n\n   1 2 3\n   4 5 6\n   7 8 9\n\neither in disjoint cycle notation or in one-line notation. For instance, a 90° counterclockwise rotation is defined by \n   [[1,3,9,7],[2,6,8,4]]\nor by\n   [3,6,9,2,5,8,1,4,7]\n(it may help visualizing to choose the 𝘬𝘦𝘺𝘱𝘢𝘥 image from the menu). There are several predefined buttons given by the permutation group they generate (see 𝘉𝘢𝘤𝘬𝘨𝘳𝘰𝘶𝘯𝘥).\n(8) The solutions and high scores are stored in AES-encrypted files.",title="Instructions",background_color="orange",font=("Sans", 14),text_color="black",size=(40,20))

	if event == "Hints":
		sg.popup_scrolled("𝗦𝗽𝗼𝗶𝗹𝗲𝗿 𝗮𝗹𝗲𝗿𝘁: Trying to solve the puzzle on your own may take some (pleasant) hours even days. Reading the following hints will definitely take some of the fun away (it cannot be \"unread\").\n\nLet L and R represent the left and right button respectively. Let L\' and R\' denote their inverses (right mouse button click). For a generic algorithm, try to find powers or commutators (i.e. elements of the form xyx⁻¹y⁻¹) with small support (e.g. transpositions, 3-cycles etc.). Now conjugate these elements (i.e. transform x into yxy⁻¹) to get more permutations with small support. It is advisable to use pen and paper at this point (or cheat with a computer algebra system). For instance, if one transposition has been found (on the evil level), it is easy to obtain them all. As every permutation can be written explicitly as a product of transpositions, we are done.\n\n𝗘𝗮𝘀𝘆 𝗺𝗼𝗱𝗲: Given the small number of possible permutations, the easy level can be solved by trial and error. For a more conceptual approach consider L², L³, R², R³.\n\n𝗠𝗲𝗱𝗶𝘂𝗺 𝗺𝗼𝗱𝗲: Consider the commutator LR³L\'R³.\n\n𝗛𝗮𝗿𝗱 𝗺𝗼𝗱𝗲: As remarked in 𝘉𝘢𝘤𝘬𝘨𝘳𝘰𝘶𝘯𝘥 there are no non-trivial elements with small support. It be can shown that R and R\' are the only non-trivial elements that fix the boxes 2, 5 and 7. Hence, we first try to reach a state where box 2 is correct (this is easy to achieve). Note that LR\'(LR)²L fixes 2 as well. Use this to turn 5 into a fixed point. Now find a move different from R that fixes 2 and 5…",title="Hints",background_color="orange",font=("Sans", 14),text_color="black",size=(40,20))

	if event == "High scores": createHS()
				
	if event == "About":
		sg.popup("Cole's Puzzle was created with:\n   – Python 3.10.5"+ #str(platform.python_version())+
		"\n   – PysimpleGUI 4.60.0"+ #str(sg.version)[0:6]+
		"\n   – SymPy 1.10.1"+ #+str(sympy.__version__)+
		"\n   – GAP 4.11.0"+
		"\n   – TexLive 2022 incl. PGF/TikZ 3.1.9a\n   – MtPaint 3.51\n\nby Benjamin Sambale",
		title="About",font=font,background_color="orange",text_color="black")

	if "::" in event: #change image
		key = event.split("::")[1] #keyword after the ::
		if key != "custom":
			img = Image.open("images/"+key+".png")
			for n in range(9):
				area = img.crop(((n%3)*bs,(n//3)*bs,(n%3)*bs+bs-1,(n//3)*bs+bs-1))
				area.save(boxes[n])
			for n in range(9): window[str(n)].update(filename=boxes[n^perm])
			if key == "squares":
				menu_new = [["&Settings", ["&Image",["&squares ✓::squares","&keypad::numbers","&tower bridge::tower","&custom…::custom"],"&High scores","E&xit"]], ["&Help", ["&Instructions","&Background","Hi&nts","&About"]]]
			if key == "numbers":
				menu_new = [["&Settings", ["&Image",["&squares::squares","&keypad ✓::numbers","&tower bridge::tower","&custom…::custom"],"&High scores","E&xit"]], ["&Help", ["&Instructions","&Background","Hi&nts","&About"]]]
			if key == "tower":
				menu_new = [["&Settings", ["&Image",["&squares::squares","&keypad::numbers","&tower bridge  ✓::tower","&custom…::custom"],"&High scores","E&xit"]], ["&Help", ["&Instructions","&Background","Hi&nts","&About"]]]
			window["menu"].update(menu_new)
		if key == "custom":
			path = os.getcwd()+"/images/squares.png"
			#sg.FileBrowse()
			filename = sg.popup_get_file("Enter JPG or PNG file",title="Choose custom image",default_path=path,file_types = [("images","*.jpg *.png"),],font=font)
			if filename == None: continue
			if not os.path.isfile(filename):
				sg.popup("Invalid file name!",title="Error",font=font)
				continue
			img = Image.open(filename)
			img = img.resize((300,300))
			for n in range(9):
				area = img.crop(((n%3)*bs,(n//3)*bs,(n%3)*bs+bs-1,(n//3)*bs+bs-1))
				area.save(boxes[n])
			for n in range(9): window[str(n)].update(filename=boxes[n^perm])
			menu_new = [["&Settings", ["&Image",["&squares::squares","&keypad::numbers","&tower bridge::tower","&custom…  ✓::custom"],"&High scores","E&xit"]], ["&Help", ["&Instructions","&Background","Hi&nts","&About"]]]
			window["menu"].update(menu_new)
	
	if event[:5] == "level":
		level = int(event[5])
		if level == 4:
			windows_input = createwindow()
			while True:
				event2, values2 = windows_input.read()
				#print(values2)

				if event2 == "D8":
					windows_input["ckey1"].update("[[1, 3, 9, 7], [2, 6, 8, 4]]")
					windows_input["ckey2"].update("[[2, 4], [3, 7], [6, 8]]")

				if event2 == "regular":
					windows_input["ckey1"].update("[[1, 2, 3], [4, 5, 6], [7, 8, 9]]")
					windows_input["ckey2"].update("[[1, 4, 7], [2, 5, 8], [3, 6, 9]]")

				if event2 == "M9": 
					windows_input["ckey1"].update("[[1, 3, 9, 7], [2, 6, 8, 4]]")
					windows_input["ckey2"].update("[[1, 4, 6, 2], [5, 9, 7, 8]]")

				if event2 == "AGL1": 
					windows_input["ckey1"].update("[[1, 2, 3], [4, 5, 6], [7, 8, 9]]")
					windows_input["ckey2"].update("[[2, 5, 6, 7, 3, 9, 8, 4]]")

				if event2 == "AGamma": 
					windows_input["ckey1"].update("[[1, 3, 9, 7], [2, 6, 8, 4]]")
					windows_input["ckey2"].update("[[1, 6, 8], [2, 7, 9, 5, 4, 3]]")

				if event2 == "AGL2": 
					windows_input["ckey1"].update("[[1, 2, 3], [4, 5, 6], [7, 8, 9]]")
					windows_input["ckey2"].update("[[1, 5, 2, 6, 4, 7], [3, 8, 9]]")

				if event2 == "SL": 
					windows_input["ckey1"].update("[[1, 2, 3], [4, 5, 6], [7, 8, 9]]")
					windows_input["ckey2"].update("[[1, 2, 6], [3, 8, 4], [5, 9, 7]]")

				if event2 == "A9": 
					windows_input["ckey1"].update("[[1, 2, 3]]")
					windows_input["ckey2"].update("[[1, 2, 3, 4, 5, 6, 7, 8, 9]]")

				if event2 == "S9": 
					windows_input["ckey1"].update("[[1, 2]]")
					windows_input["ckey2"].update("[[1, 2, 3, 4, 5, 6, 7, 8, 9]]")
				
				if event2 == "Submit":
					try:
						moves[4][0]=zeroone*Perm(eval(values2["ckey1"]))*zeroone**-1
						moves[4][1]=zeroone*Perm(eval(values2["ckey2"]))*zeroone**-1
					except:
						sg.popup("Invalid permutations! Try again",title="Error",font=font)
						continue
					if moves[4][0].max() > 8 or moves[4][1].max() > 8:
						sg.popup("Invalid permutations! Try again",title="Error",font=font)
						moves[4] = [Perm(0,2,8,6)(1,5,7,3),Perm(1,3)(2,6)(5,7)]
						continue
					windows_input.close()
					break
				if event2 in [None,"Cancel",sg.WIN_CLOSED]:
					windows_input.close()
					break
			G[4] = PermGroup(moves[4][0],moves[4][1],Perm(8)) #make perm group on 9 symbols
		perm = Perm(8)
		game_on = False
		init(level)
	
	if event in ["button0","button0R","button1","button1R"]: #button click or arrow key pressed
		butt = int(event[6])
		if level == 3 and not game_on:
			sg.popup("Scramble first!",title="Info",font=font)
			continue
		if len(event) == 8 or shpr: #right click or Shift+arrow -> use inverse permutation
			perm = moves[level][butt]**-1*perm 
		else:
			perm = moves[level][butt]*perm #left click of arrow key
		#print(perm)
		for n in range(9): window[str(n)].update(filename=boxes[n^perm])
		move_count +=1
		if game_on: window["text_solution"].update("Move: "+str(move_count))
		if game_on and perm.is_identity and level<4:
			if move_count < highscores[level][1]:
				highscores[level][1]=move_count
				getHSname()
				createHS()
			else:
				sg.popup("Solved in "+str(move_count)+" moves!",title="You won!",font=font,background_color="orange",text_color="black")
			game_on = False

	if level == 3 and event in ["button2","button2R"]: #joker button
		if not game_on:
			sg.popup("Scramble first!",title="Info",font=font)
			continue
		if event == "button2R":
			joker = Perm(9)
			joker_text = sg.popup_get_text("Enter combination of L,L',R,R':",title="Define Button",font=font,default_text=joker_text)
			if joker_text == None:
				joker_text = ""
				continue
			for i in range(len(joker_text)):
				if not joker_text[i] in ["L","R","'"]:
					sg.popup("Invalid combination!",title="Error",font=font)
					joker_text = ""
					break
				if joker_text[i] == "'" and (i == 0 or joker_text[i-1] == "'"):
					sg.popup("Invalid combination!",title="Error",font=font)
					joker_text = ""
					break
				if joker_text[i] == "L":
					if i < len(joker_text)-1 and joker_text[i+1] == "'": joker = joker*moves[3][0]**-1
					else: joker = joker*moves[3][0]
				if joker_text[i] == "R":
					if i < len(joker_text)-1 and joker_text[i+1] == "'": joker = joker*moves[3][1]**-1
					else: joker = joker*moves[3][1]
		if event == "button2":
			if joker_text == "":
				sg.popup("Assign button first (right click)",title="Info",font=font)
				continue
			perm = joker*perm if shpr else joker**-1*perm
			for n in range(9): window[str(n)].update(filename=boxes[n^perm])
			move_count +=1
			if game_on: window["text_solution"].update("Move: "+str(move_count))
			if game_on and perm.is_identity:
				if move_count < highscores[level][1]:
					highscores[level][1]=move_count
					getHSname()
					createHS()
				else:
					sg.popup("Solved in "+str(move_count)+" moves!",title="You won!",font=font,background_color="orange",text_color="black")
				game_on = False
			
	if event == "key_new":
		if level != 3:
			perm = G[level].random()
			while perm.is_identity: perm = G[level].random() #repeat until non-trivial permutation found
		if level == 3:
			perm = Perm.random(9)
			while perm.is_identity: perm = Perm.random(9)
			moves[3][0] = Perm.random(9)
			moves[3][1] = Perm.random(9)
			while PermGroup(moves[3][0],moves[3][1]).order() < 362880: #not full symmetric group
				moves[3][0] = Perm.random(9)
				moves[3][1] = Perm.random(9)
		init(level)
		window["text_solution"].update("Move: "+str(move_count))
		game_on = True

	if event == "key_restore":
		perm = Perm(8)
		game_on = False
		window["text_solution"].update("")
		init(level)

	if event == "key_solution":
		if perm.is_identity:
			sg.popup("Puzzle is already solved!",title="Solved",font=font)
		elif level > 2:
			sg.popup("This feature is not available in this level.",title="Sorry",font=font)
		else:
			for s in solutions[level]:
				if perm**-1 == Perm(s[0]):
					window["text_solution"].update("Solution: "+s[1])
					game_on = False
					break
		
window.close()

