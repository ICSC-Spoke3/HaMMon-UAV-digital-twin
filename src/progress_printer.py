import sys, time

"""
Classe per la gestione dello status progressivo di ogni step
"""
class ProgressPrinter:
	def __init__( self, name ):
		self.name = name	# process name
		#self.start_time = time.time()	# start time process (progress_print_vone/vtwo)
	def __call__( self, percent ):
		print("{} progress: {:.2f}%".format(self.name, percent), end="\r", flush=True)
		# svuotare il buffer di output standard in modo da vedere live progression
		# e non direttamente a esito finale
		#sys.stdout.flush()

# altri metodi usabili per la progressione 
"""
def __call__( self, percent ):
		elapsed = float(time.time() - self.start_time) # self.start_time
		if percent:
			sec = elapsed / percent * 100
			minuti = sec / 60
			if minuti > 1:
				print('Current task progress: {:.2f}%, estimated time left: {:.0f} minutes'.format(percent, minuti), end="\r", flush=True)
			else:
				print('Current task progress: {:.2f}%, estimated time left: {:.0f} seconds'.format(percent, sec), end="\r", flush=True)
		else:
			print('Current task progress: {:.2f}%, estimated time left: unknown'.format(percent), end="\r", flush=True) #if 0% progress
"""
"""
def __call__( self, percent ):
	print("{} progress: {:.2f}%".format(self.name, percent))
	# svuotare il buffer di output standard in modo da vedere live progression
	# e non direttamente a esito finale
	sys.stdout.flush()
"""
"""
def __call__( self, percent ):
		elapsed = float(time.time() - self.start_time) # self.start_time
		if percent:
			sec = elapsed / percent * 100
			print('Current task progress: {:.2f}%, estimated time left: {:.0f} seconds'.format(percent, sec), end="\r", flush=True)
		else:
			print('Current task progress: {:.2f}%, estimated time left: unknown'.format(percent), end="\r", flush=True) #if 0% progress
"""