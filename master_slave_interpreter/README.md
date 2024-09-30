# Concept :
A master program is initialized and it drops a slave on the bytecode. The slave crawls the bytecode, collects data, dupplicates itself on if statements if needed. When arriving at a error or the end of the bytecode, the slave sends the data to the master and dies. 

The master decides the final probabilities of the program with the data it has collected.

# Detecting infinite loops :
The slave saves its data when coming accross a goto instruction. If it comes accross the same goto instruction again, it compares the data it has saved with the data it has now. If the data is the same, it means that the slave is in an infinite loop and it dies.