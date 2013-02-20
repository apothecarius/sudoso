#!/usr/bin/python
#author:Jonas Bollgruen
#mail:apothecarius@web.de
#version:2.3.2

import random
from copy import deepcopy as lscp



#generates a field
#this is a 2-dimensional list with 9 slots each
#initially these contain a set with 1 to 9
def gen_field():
	possis = set((1,2,3,4,5,6,7,8,9))
	rows = [possis]
	for i in range(0,8):
		rows.append(lscp(possis))
	feld = [rows]
	for i in range(0,8):
		feld.append(lscp(rows))
	return feld
	    
#discard possibilities
#checks if at the position (posx,posy) a number has been found out
# if so this function deletes the possibility for this number
# in all slots, for which this slot has an effect on
def disc_possi(feld, posx, posy):
	count = feld[posx][posy]
	if (type(feld[posx][posy]) == set) or (count == 0):
		return feld
	for y in range(0,9):
		if type(feld[posx][y]) == set:
			feld[posx][y].discard(count)

	for x in range(0,9):
		if type(feld[x][posy]) == set:
			feld[x][posy].discard(count)

	posx /= 3
	posy /= 3
	posx = int(posx)
	posy = int(posy)
	for x in range(0,3):
		for y in range(0,3):
			if type(feld[posx*3+x][posy*3+y]) == set:
				feld[posx*3+x][posy*3+y].discard(count)

	return feld

#looks semi-randomly (starts randomly, continues linearly)
# for an unclear place in the field and guesses
# returns positions[list] or failures[int]
#(use only for creation)
def randomize(feld):
	xi = random.randint(0,8)
	for x in range(0,9):
		xi += 1
		if xi == 9:
			xi = 0
		yi = random.randint(0,8)
		for y in range(0,9):
			yi += 1
			if yi == 9:
				yi = 0
			if type(feld[xi][yi]) == set:
				while 1:
					c = random.randint(1,9)
					if c in feld[xi][yi]:
						feld[xi][yi] = c
						return [xi, yi]
	return 1

#gets a part of the field (a line, column or one of the 9 3x3-blocks
#and returns it as 1-dimensional list
def get_block(feld, typ, nr):
	if typ == 1:
		return feld[nr]
	if typ == 2:
		reihe = [feld[0][nr]]
		for i in range(1,9):
			reihe.append(feld[i][nr])
		return reihe
	if typ == 3:
		grundy = int(nr/3)
		grundx = nr-grundy*3
		block = [feld[grundx*3][grundy*3],feld[grundx*3][grundy*3+1],feld[grundx*3][grundy*3+2]]
		for x in range(1,3):
			for y in range(0,3):
				block.append(feld[grundx*3+x][grundy*3+y])
		return block

#sets a block (just like get_block)
def set_block(feld,typ, nr, erg):
	if typ == 1:
		feld[nr] = erg
	if typ == 2:
		for i in range(0,9):
			feld[i][nr] = erg[i]
	if typ == 3:
		grundy = int(nr/3)*3
		grundx = (nr-grundy)*3
		for x in range(0,3):
			for y in range(0,3):
				feld[grundx+x][grundy+y] = erg[x*3+y]
	return feld

#simplifies usage of get/set_block 
#(so that the type of a block can simply be put into a forloop)
def get_adress(typ,nr,adr):
	if typ == 1:#reihe
		return [nr,adr]

	if typ == 2:#spalte
		return [adr,nr]

	if typ == 3:#kasten
		grundy = int(nr/3)*3
		grundx = (nr-grundy)*3
		y = int(adr/3)
		x = adr-y*3
		return [grundx+x,grundy+y]

#finds slots with only one possibility, also changes the slot
def finder(feld):
	xi = random.randint(0,8)#slight randomization for results at all at generation("healthy chaos")
	for x in range(0,9):
		xi += 1
		if xi == 9:
			xi = 0
		yi = random.randint(0,8)
		for y in range(0,9):
			yi += 1
			if yi == 9:
				yi = 0
			if type(feld[xi][yi]) == set:
				if len(feld[xi][yi]) == 0:
					#error: one of the slots has no possibility,
					#so the sudoku isnt solvable
					feld[xi][yi]= 0
					return 20
				if len(feld[xi][yi]) == 1:
					feld[xi][yi] = list(feld[xi][yi])[0]
					return [xi,yi]
	return 1



def elimination(feld):#goes through every block and gives it to elim_proc
        #returns a tuple with [0]the (changed) feld and a bool whether it got changed
	x = False
	for typ in range(1,4):
		for nr in range(0,9):
			erg = elim_proc(get_block(feld,typ,nr))
			if type(erg) == list:
				x = True
				feld = set_block(feld, typ,nr,erg[0])
				adr = get_adress(typ,nr,erg[1])
				feld = disc_possi(feld,adr[0],adr[1])
	return [feld,x]


def elim_proc(block):#looks for numbers that appear once in a block
	for c in range(1,10):
		anzahl = 0
		f_da = False
		for i in range(0,9):
			if block[i] == c:
				f_da = True
				break
		if f_da:
			continue
		#sicher dass die zahl noch nicht gefunden wurde
		for i in range(0,9):
			if type(block[i]) == set:
				if c in block[i]:
					anzahl += 1
					pos = i
			if anzahl >= 2:
				break
		if anzahl >= 2:#zu viele moeglichkeiten
			continue

		if anzahl == 1:
			block[pos] = c
			return [block,i]
	return 1


def double(feld):#goes through every block and gives it to find_double, returns [feld,1] if it found a double
	for typ in range(1,4):
		for nr in range(0,9):
			erg = find_double(get_block(feld,typ,nr))
			if type(erg) == list:
				if verbose:
					t = {1:"Row",2:"Column",3:"Block"}[typ]
					print ("Pair found at "+t+" "+str(nr))
				return [set_block(feld,typ,nr,erg),1]
	return [feld,0]

def find_double(block):
	mogl = [[],[],[],[],[],[],[],[],[]]

	for i in range(0,9):
		if type(block[i]) == int:
			continue
		for a in range(0,9):
			if a in block[i]:
				mogl[a].append(i)

	#jetzt gibt es einen array, in dem fuer jede zahl steht, wo sie vorhanden ist
	for a in range(0,9):
		if len(mogl[a]) != 2:
			continue
		for b in range(0,9):
			if a >= b or len(mogl[b]) != 2:
				continue
			if mogl[a] == mogl[b]:
				if block[mogl[a][0]] == block[mogl[a][1]]:#doppelpaar schon eingetragen
					continue

				#a-1 und b-1 sind die nummern
				for i in range(0,9):#in anderen feldern a und b loeschen
					if type(block[i]) == set:
						block[i].discard(a-1)
						block[i].discard(b-1)
				#in beiden feldern nur a und b eintragen
				block[mogl[a][0]] = set((a-1,b-1))
				block[mogl[a][1]] = set((a-1,b-1))
				return block
	return 0

class bin:
	pass

#solves a sudoku by a bruteforcemethod
def guess(feld):
	#find optimal position to guess
	original = lscp(feld)
	for n in range(2,9):
		pos = find_easiest(feld)
		if type(pos) == list:
			break
	#now take the first of these possibilities
	possibs = list(feld[pos[0]][pos[1]])
	bi = bin()
	bi.solut = []
	while(len(possibs) != 0):
		if verbose:
			print("Guessing: ["+str(pos[0])+","+str(pos[1])+"] = "+str(possibs[-1]))
		feld[pos[0]][pos[1]] = possibs.pop()
		#now try to solve it
		result = solve(feld)
		if result == 20:#fail so try another possibility
			feld = original
			continue
		else:
			if type(result) == bin:#got into guessing so need to 
				bi.solut.extend(result.solut)
			else:	
				bi.solut.append(result)

	return bi

def find_easiest(feld):
	n = 9
	candidates = []
	for x in range(0,9):
		for y in range(0,9):
			if type(feld[x][y]) == int:
				continue
			elif len(feld[x][y]) < n:
				candidates = [[x,y]]
				n = len(feld[x][y])
			elif len(feld[x][y]) == n:
				candidates.append([x,y])
	try:
		return random.choice(candidates)
	except:
		for l in feld:
			print(l)		

def pr_simp(feld):#a simple display of the result so far
	if(type(feld) == int):#amount of the possibilities
		print(feld)
	elif (type(feld) == bin):#several possibilities
		for f in feld.solut:
			pr_simp(f)
			print("--")
	else:#list single possibility
		fake = lscp(feld)
		for x in range(0,9):
			for y in range(0,9):
				if type(fake[x][y]) == set:
					fake[x][y] = 0
		if "-l" in sys.argv:
			out = ""
			for x in str(feld): 
				if x in "123456789":
					out += x
#			out = [x for x in str(feld) if x in "123456789"]
#			for l in fake:
#				out.extend(l)
			print(out)
		else:
			for l in fake:
				print (l)


def done(feld):#returns true if the sudoku is solved
	for x in range(0,9):
		for y in range(0,9):
			if type(feld[x][y]) != int or feld[x][y] == 0:
				return False
	return True

def solvable(feld):#returns 0 if the sudoku can't be solved anymore (0 entry or empty set of possibs)
	for x in range(0,9):
		for y in range(0,9):
			if type(feld[x][y]) == set and len(feld[x][y]) == 0:
				return 0
			if feld[x][y] == 0:
				return 0
	return 1 #<- no problem


#setter from 1-dimensional list to list*list*set
def interp_list(felder):
	if len(felder) != 81:
		print("Eingabe enthaelt",len(felder),"Felder.")
		return
	feld = []
	for x in range(0,9):
		feld.append([])
		for y in range(0,9):
			feld[x].append([1,2,3,4,5,6,7,8,9])
	
	for x in range(0,9):
		for y in range(0,9):
			if felder[0] not in range(0,10):
				print("Falscher Input bei Feld", x,"/",y)
				return
			if felder[0] != 0:
				feld[x][y] = felder[0]
			else:
				feld[x][y] = set((1,2,3,4,5,6,7,8,9))
			del felder[0]

	for x in range(0,9):
		for y in range(0,9):
			if type(feld[x][y]) == int:
				feld = disc_possi(feld,x,y)
	return feld

def solve(feld):#returns either the solution of the entered sudoku or a list of all of those solutions
	while not done(feld):
		if not solvable(feld): #unsolvable
			return 20
		for x in range(0,9):
			for y in range(0,9):
				if type(feld[x][y]) == int:
					feld = disc_possi(feld,x,y)
		neu = finder(feld) #only one possibility 
		while type(neu) == list:
			feld = disc_possi(feld,neu[0],neu[1])
			neu = finder(feld) #only one possibility 

		neu = elimination(feld) #number has only one possibility where to be in a block
		feld = neu[0]
		if not neu[1]:
			if done(feld):
				return feld
			neu = double(feld) #special pair finder
			#neu = [feld,1/0]
			feld = neu[0]
			if not neu[1]:
				return guess(feld) #bruteforce technique
	#done
	return feld


#will generate a complete sudoku
oops = {1:"Err",2:"Ehm",3:"Hold on",4:"god dammit",5:"What the"}
oops.setdefault("What the bloody hell is wrong today!")
def gen_sud():
	feld = gen_field()
	tries = 1
	while(not done(feld)):
		if not solvable(feld):#trap, revert steps until solvable
			tries += 1
			if verbose:
				print(oops[tries])
			feld = gen_field()
			continue
		if verbose:
			print("Guessing")
		success = 0
		for x in range(0,9):
			for y in range(0,9):
				if type(feld[x][y]) == set:
					if len(feld[x][y]) == 1:
						feld[x][y] = list(feld[x][y])[0]
						feld = disc_possi(feld,x,y)
						success = 1
					elif len(feld[x][y]) == 0:
						success = 2
						break
			if success == 2:
				break
		if success == 2:
			continue
				
		elif success == 0:
			pos = find_easiest(feld)
			x = pos[0];y = pos[1]
			feld[x][y] = random.choice(list(feld[x][y]))
			feld = disc_possi(feld,x,y)
		while not done(feld):
			f = finder(feld)
			if f == 1:
				f = elimination(feld)
				if not f[1]:#didnt help
					break
				else:
					feld = f[0]
			elif f == 20:
				break
			else:
				feld = disc_possi(feld,f[0],f[1])
	if verbose:
		print("Th"+tries*"e"+"re we go:")
	return feld

#will change a given (or selfgenerated) sudoku so that there will be at least n missing numbers
#TODO not working
def ratsel(feld,n):
	if feld == False:
		feld = gen_sud()
	for x in range(0,9):
		for y in range(0,9):
			p = random.randint(0,2)
			if p != 0:
				feld[x][y] = set([1,2,3,4,5,6,7,8,9])
	return feld

def right(feld):#checks if the sudoku is solved correctly or not solved
	for i in range(0,9):
		for block in range(1,4):
			check = get_block(feld,block,i)
			c = 0
			for x in range(0,9):
				if type(check[x]) == set:
					return True
				else:
					c += check[x]
			if c != 45:
				if verbose:
					print("Fail at",{1:"Row",2:"Column",3:"Block"}[block],str(i))
				return False
	if verbose:
		print("Succes!")
	return True



def set_nr(but):
	del but
	for x in range(0,9):
		for y in range(0,9):
			a = 0
			try:
				a = int(buts[x][y].get_text())
			except:
				buts[x][y].set_text("0")
			if a != 0 and a < 10:
				feld[x][y] = a
			else:
				buts[x][y].set_text("0")
	pr_simp(feld)
	res = solve()
	print (type(res))
	print (res)
	if type(res) == int:
		return#todo war moeglich etc

	for x in range(0,9):
		for y in range(0,9):
			try:
				buts[x][y].set_text(string(res[x][y]))
			except:
				buts[x][y].set_text("0")


########################## CLI-specific ################################
 
#get the sudoku to solve from the CLI
import sys

#CLI-commands
cmd = bin()
#-l	output will be given in a single line
cmd.writeLine = False
#-v	will give hints on how the sudoku was solved
cmd.verbose = False
#-c	will only count the possible solutions
cmd.countSolutions = False
#-n	will generate a new sudoku
cmd.generateNew = False

valid_args = ["-n","-v","-c", "-l"]

def isSudokuText(s):
	if(len(s) == 81):
		for l in s:
			if(l not in ["0","1","2","3","4","5","6","7","8","9"]):
				return False
		return True
	#elif(len(s) == 89):#split by semicolon
	else:
		s = s.split(";")
		if len(s) != 9:
			print("Incorrect amount of lines")
			exit()
		for i in range(0,9):#l:lines
			if(len(s[i]) != 9):
				print("Incorrect length of line "+str(i))
				print(s[i])
				exit()
			for l in s[i]:
				if(l not in ["0","1","2","3","4","5","6","7","8","9"]):
					return False
			return True
	#else:
	#	return False
			
def setSudoku(l):
	retu = 0
	if("-n" in l):
		retu = "-n"
	for i in l:
		if len(i) in [81,89] and isSudokuText(i):
			if retu == "-n":#both given so contradict so exit
				print('Sudoku and "-n"-Operator is given')
				exit()
			elif type(retu) == list:#already found one
				print("Two Sudokus given")
				exit()
			else:#found
				#TODO nonsense
				retu = []
				i = i.replace(";","")#delete line separator
				i = list(i)
				for a in i:						
					retu.append(int(a))
				retu = interp_list(retu)
	if retu == 0:
		print('Neither a Sudoku nor the "-n"-Operator is given')
		exit()
	return retu


def evaluateCommand(arg):
	assert(type(arg) == str)
	pass



################################### main ##############################

if sys.argv[0] == '': #was imported, so dont do anything here
	pass
else:#bash call, so interpret the CLI-arguments

	if isSudokuText(sys.argv[1]):
		sudoku = setSudoku(sys.argv[1])
		args = sys.argv[2:]
	else
		args = sys.argv[1:]
	for arg in args:
		evaluateComand(arg)


		########TODO consider everything below as deprecated


	for arg in sys.argv[1:]:
		if not (arg in valid_args):
			if not isSudokuText(arg):
				exit("Invalid Argument given: "+arg)
	verbose = "-v" in sys.argv
	sudoku = setSudoku(sys.argv[1:])
	if (sudoku =="-n"): #make new one
		sudoku = gen_sud()
		if "-e" in sys.argv[1:]:#complicate it 
			if (len(sys.argv) == sys.argv.index("-e")-1 or
			 sys.argv[sys.argv.index("-e")+1] not in range(1,80)):
				#BS so exit
				exit("Invalid command given to complicate the riddle, so exiting")
			else:
				amount_zeroes = sys.argv[sys.argv.index("-e")+1]
				sudoku = ratsel(sudoku,amount_zeroes)
		pr_simp(sudoku)
		exit()
	else:#sudoku given
		if not done(sudoku):#unsolved
			sudoku = solve(sudoku)

			if "-c" in sys.argv:#count solutions
				if type(sudoku) == bin:
					sudoku = len(sudoku.solut)
				else:
					sudoku = len(sudoku)
			pr_simp(sudoku)
		else:#solved sudoku given
			if "-e" in sys.argv[1:]:#complicate it
				if (len(sys.argv) == sys.argv.index("-e")-1 or
				sys.argv[sys.argv.index("-e")+1] not in range(1,80)):
					#BS so exit
					print("Invalid command given to complicate the riddle, so exiting")
					exit()
				else:
					amount_zeroes = sys.argv[sys.argv.index("-e")+1]
					sudoku = ratsel(sudoku,amount_zeroes)
					pr_simp(sudoku)
			else:
				print("What am I supposed to do with that")
				exit()
	

#a1 = [0,0,6,2,0,5,7,0,0,7,0,0,0,0,0,0,0,5,4,0,0,1,0,0,0,0,0,0,8,0,0,0,0,9,0,4,0,0,0,4,0,2,0,0,0,6,0,9,0,0,0,0,1,0,0,0,0,0,0,7,0,0,2,3,0,0,0,0,0,0,0,9,0,0,7,3,0,6,8,0,0]
#a2 = [0,0,0,6,0,0,1,0,0,0,0,6,0,7,0,9,0,5,3,0,0,0,0,0,0,0,4,0,4,0,5,0,7,0,1,0,0,0,0,0,0,0,0,0,0,7,8,0,9,0,3,0,0,0,9,0,0,0,0,0,0,0,8,4,0,3,0,9,0,6,0,0,0,0,7,0,0,5,0,0,0]
#pr_simp(solve(interp_list(a1)))


#pr_simp(interp_list([0,0,0,6,0,0,1,0,0,0,0,6,0,7,0,9,0,5,3,0,0,0,0,0,0,0,4,0,4,0,5,0,7,0,1,6,0,0,0,0,0,0,0,0,0,7,8,0,9,0,3,0,4,0,9,0,0,0,0,0,0,0,8,4,0,3,0,9,0,6,0,0,0,0,7,0,0,5,0,0,0]))
#works