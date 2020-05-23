from mpi4py import MPI
import sys
import random

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

workers = size - 1
A = int(sys.argv[1])	# Input parameter, A
chunkSize = A / workers

if rank == 0:
	arms = []
	L = [i+1 for i in range(A)]	# Fills a list, L, with numbers from 1 to A
	random.shuffle(L)
	for i in range(workers):
		chunk = L[:chunkSize]
		msg = comm.isend(chunk, dest=i+1)
		msg.wait()
		L = L[chunkSize:len(L)]	# Updates list by deleting the first 5 elements
		armsFromWorker = comm.irecv()
		armsFromWorker.wait()
		arms.extend(armsFromWorker)
		if i == workers-1:
			totalSum = int(comm.irecv())
			totalSum.wait()
	arms.sort()
	txt = open('armstrong.txt','w')
	for i in range(len(arms)):
		txt.write("%i " % arms[i])
	txt.close()
	print("Total Sum = %i" %sum(arms))
else:
	incoming = comm.irecv()
	incoming.wait()
	armstrongsOfThisWorker = []
	for i in range(chunkSize):
		ifArmstrong = 0
		digitFinder = incoming[i]
		count = 0
		while digitFinder > 0: # Finds digit count 
			count += 1
			digitFinder= int(digitFinder / 10)
		number = incoming[i]
		for j in range(count):	#Takes every digits power of digit count
			ifArmstrong += (number % 10) ** count
			number = int(number / 10)
		if incoming[i] == ifArmstrong:
			armstrongsOfThisWorker.append(incoming[i])
	comm.send(armstrongsOfThisWorker, dest=0)	# Sends found Armstrong numbers to the master
	print("Armstrong numbers in this worker = " + str(armstrongsOfThisWorker))
	print("Sum of Armstrong numbers in Worker " + str(rank) + " = " + str(sum(armstrongsOfThisWorker)))

	sumAtThisWorker = sum(armstrongsOfThisWorker)
	if rank != 1:
		sumFromPreviousWorker = int(comm.irecv())
		sumFromPreviousWorker.wait()
		sumAtThisWorker += sumFromPreviousWorker
		msg = comm.isend(sumAtThisWorker, dest=(rank+1)%size)
		msg.wait()
	else:
		msg = comm.isend(sumAtThisWorker, dest=2) 
		msg.wait()


print("Hello, its me!")

'''
if rank == 0:
	totalSum = comm.recv()
else:
	sumOfArms = sumFromPreviousWorker + sum()
	if rank + 1 < size:
		comm.send()
'''


	#print(armstrongsOfThisWorker)
	#sumFromPreviousWorker = comm.recv()
	#sumOfArms = sumFromPreviousWorker + sum(armstrongsOfThisWorker)
	#if rank + 1 < size:
	#	comm.send(sumOfArms, dest=rank+1)
	#else:
	#	comm.send(sumOfArms, dest=0)
	#print('Sum of Armstrong numbers in worker %d = %d', rank, sum(armstrongsOfThisWorker))


'''
name = MPI.Get_processor_name()
if rank == 0:
	msg = "Ben oyum!"
	comm.send(msg, dest=1)
	print("message sent")
else:
	s = comm.recv()
	print("rank = ", rank, "message = ", s)
'''
