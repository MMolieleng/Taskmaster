#!/usr/bin/env python
import os
import cmd
import time
import signal
import platform
import threading
import tmdata
import tmfuncs
import process_class as procc
from tmlog import log

class Taskmaster(cmd.Cmd):
	""""""
	def __init__(self):
		""""""
		cmd.Cmd.__init__(self)
		if str(platform.system()) != "Windows":
			self.prompt = "\033[94mTaskmaster>\033[0m "
		else:
			self.prompt = "Taskmaster> "
		self.programs = list
		self.monitor = False
		log("Taskmaster object initialized", "./tmlog.txt", False)

	def emptyline(self):
		""""""
		pass

	def do_hist(self, args):
		""""""
		print self._hist

	"""
	def preloop(self):
		""""""
	"""

	"""
	def postloop(self):
		""""""
	"""

	def do_exit(self, args):
		'''Exits the Taskmaster shell when user inputs "exit"'''
		self.monitor = False
		if (len(self.programs) > 0):
			self.stopAllPrograms()
		log("TaskMaster exiting", "./tmlog.txt", False)
		exit(0)

	def default(self, line):
		'''Custom input handling'''
#------------------------------------------------------------------------------#
		log("Input: '" + line + "'", "./tmlog.txt", False)
		if (line == "cheese"):				###
			print "Crackers"
		# elif line == "load":				###
		# 	self.programs = tmdata.loadConfig(os.path.realpath("./config.xml"))
		# 	print("\n---Programs Loaded---\n")
		elif line.startswith("monitor"):	###
			if not self.programs:
				print("Load config first!")
				return
			sc = line.split()
			if len(sc) == 1:
				for program in self.programs:
					program.runAndMonitor()
				print("\n---Monitoring " + str(len(self.programs))
						+ " programs---\n")
			else:
				for program in self.programs:
					if program.progname == sc[1]:
						print("\n---Monitoring " + program.progname + " ---\n")
						program.runAndMonitor()
				#check if progname is in config and if not notify user!!!
		elif line == "dlog":
			os.remove("./tmlog.txt")
			print("./tmlog.txt deleted!")
#------------------------------------------------------------------------------#
		elif (line.startswith("status")):
			print("ALL STATUS")
			# splt = line.split()
			# if (len(splt) == 1):
			# log("Showing status ")	???
			# 	showstatus()
		elif (line.startswith("stop")):	#this if statement is only if programs require a specific SIGNAL to stop
			splt = line.split()
			if (len(splt) == 1):
				print ("Please specify which program\s to stop "
						+ "(stop all -OR- stop [program1 name] "
						+ "[program2 name])")
			elif (len(splt) > 1):
				self.stopPrograms(splt)
				if (len(splt) == 2 and splt[1] == "all"):
					self.stopAllPrograms()

		elif (line.startswith("start")):
			print("START")
		else:
			log("Unknown command: " + line, "./tmlog.txt", True)


	def stopAllPrograms(self):
		"""Stop all programs"""
		for prog in self.programs:
			for proc in prog.processes:
				signum = tmfuncs.getSignalValue(prog.stopsig)
				proc.pop.send_signal(signum)
				proc.tmexit = True
			prog.processes = list()


	def stopPrograms(self, args):	#make a version where you can stop specific processes
		"""Stop one or more programs.
		   args -> a split of 'stop prog1 prog2 etc'
		"""
		cnt = 0

		while cnt < len(args):
			if (cnt > 0):
				for prog in self.programs:
					if (prog.progname == args[cnt]):
						for proc in prog.processes:
							signum = tmfuncs.getSignalValue(prog.stopsig)
							proc.pop.send_signal(signum)
							proc.tmexit = True
						prog.processes = list()
			cnt += 1

	def monitorProcesses(self):
		""""""
		tim = threading.Timer(1.0, self.monitorProcesses)
		tim.start()
		if (self.monitor == False):
			tim.cancel()
			log("No longer monitoring processes", "./tmlog.txt", False)
		for prog in self.programs:
			if (len(prog.processes) > 0):
				for proc in prog.processes:
					if (proc.active == False):
						prog.processes.remove(proc)
						log("Removing " + proc.name, "./tmlog.txt", False)


	def handleSigint(self, signum, frame):
		""""""
		if (signum == 2):
			print("")
			self.do_exit(None)


def autolaunchPrograms(taskmaster):
	""""""
	cnt = 0
	num = 0
	totnum = 0

	if (len(taskmaster.programs) == 0):
		log("WARNING: No programs in config file", "./tmlog.txt", True)
		return
	for program in taskmaster.programs:
		if (program.autolaunch):
			while num < program.procnum:
				program.runAndMonitor()
				num += 1
			totnum += num
			num = 0
			cnt += 1
	if (cnt > 0):
		log(str(totnum) + " processes (" + str(cnt) + " program\s) launched"
			+ " automatically",	"./tmlog.txt", True)
	else:
		log("No programs set to launch automatically", "./tmlog.txt", True)


# def checkCommands(programs):
# 	"""Check if the commands in config file are valid commands"""
# 	for pth in os.environ["PATH"].split(os.pathsep):
# 		print(pth)


def main():
	""""""
	log("TaskMaster started", "./tmlog.txt", False)
	tm = Taskmaster()

	print("Loading programs")
	if str(platform.system()) != "Windows":
		os.system("clear")
	else:
		os.system("cls")
	log("Loading config file", "./tmlog.txt", False)
	tm.programs = tmdata.loadConfig(os.path.realpath("./config.xml"))
	log(str(len(tm.programs)) + " programs loaded from config", "./tmlog.txt",
		False)
	autolaunchPrograms(tm)
	tm.monitor = True
	log("Monitoring processes", "./tmlog.txt", False)
	tm.monitorProcesses()
	signal.signal(signal.SIGINT, tm.handleSigint)#!#
	tm.cmdloop()


if __name__ == "__main__":
	main()
