'''
Created on 20160917
@author: LaurentMT
'''
import os
import math
import getopt

import sys
# Adds boltzmann directory into path
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")

from boltzmann.utils.tx_processor import process_tx
from boltzmann.utils.bci_wrapper import BlockchainInfoWrapper




def display_results(mat_lnk, nb_cmbn, inputs, outputs, fees, intrafees):
    '''
    Displays the results for a given transaction
    Parameters:
        mat_lnk   = linkability matrix
        nb_cmbn   = number of combinations detected
        inputs    = list of input txos (tuples (address, amount))
        outputs   = list of output txos (tuples (address, amount))
        fees      = fees associated to this transaction
        intrafees = max intrafees paid/received by participants (tuple (max intrafees received, max intrafees paid))         
    '''
    print('\nInputs = ' + str(inputs))
    print('\nOutputs = ' + str(outputs))
    print('\nFees = %i satoshis' % fees)
    
    if (intrafees[0] > 0) and (intrafees[1] > 0):
        print('\nHypothesis: Max intrafees received by a participant = %i satoshis' % intrafees[0])
        print('Hypothesis: Max intrafees paid by a participant = %i satoshis' % intrafees[1])
    
    print('\nNb combinations = %i' % nb_cmbn)
    if nb_cmbn > 0:
        print('Tx entropy = %f bits' % math.log2(nb_cmbn))
    
    if mat_lnk is None:
        if nb_cmbn == 0:
            print('\nSkipped processing of this transaction (too many inputs and/or outputs)')
    else:
        if nb_cmbn != 0:
            print('\nLinkability Matrix (probabilities) :')
            print(mat_lnk / nb_cmbn)
        else:
            print('\nLinkability Matrix (#combinations with link) :')
            print(mat_lnk)
        
        print('\nDeterministic links :')
        for i in range(0, len(outputs)):
            for j in range(0, len(inputs)):
                if (mat_lnk[i,j] == nb_cmbn) and mat_lnk[i,j] != 0 :
                    print('%s & %s are deterministically linked' % (inputs[j], outputs[i]))
    



def main(txids, options=['PRECHECK', 'LINKABILITY', 'MERGE_INPUTS'], max_duration=600, max_cj_intrafees_ratio=0):
    '''
    Main function
    Parameters:
        txids                   = list of transactions txids to be processed
        options                 = options to be applied during processing
        max_duration            = max duration allocated to processing of a single tx (in seconds)
        max_cj_intrafees_ratio  = max intrafees paid by the taker of a coinjoined transaction. 
                                  Expressed as a percentage of the coinjoined amount.
    '''
    # Initializes the wrapper for bci api
    bci_wrapper = BlockchainInfoWrapper()
    
    for txid in txids:
        print('\n\n--- %s -------------------------------------' % txid)
        # Retrieves the tx from bci
        try:
            tx = bci_wrapper.get_tx(txid)
        except:
            print('Unable to retrieve information for %s from bc.i' % txid)
            continue
        
        # Computes the entropy of the tx and the linkability of txos
        (mat_lnk, nb_cmbn, inputs, outputs, fees, intrafees) = process_tx(tx, options, max_duration,  max_cj_intrafees_ratio)
        
        # Displays the results
        display_results(mat_lnk, nb_cmbn, inputs, outputs, fees, intrafees)
        
    

def usage():
    '''
    Usage message for this module
    '''
    sys.stdout.write('python ludwig.py [--duration=600] [--cjmaxfeeratio=0] [--options=PRECHECK,LINKABILITY,MERGE_FEES,MERGE_INPUTS,MERGE_OUTPUTS] [--txids=8e56317360a548e8ef28ec475878ef70d1371bee3526c017ac22ad61ae5740b8,812bee538bd24d03af7876a77c989b2c236c063a5803c720769fc55222d36b47,...]');
    sys.stdout.write('\n\n[-t OR --txids] = List of txids to be processed.')
    sys.stdout.write('\n\n[-d OR --duration] = Maximum number of seconds allocated to the processing of a single transaction. Default value is 600')
    
    sys.stdout.write('\n\n[-o OR --options] = Options to be applied during processing. Default value is PRECHECK, LINKABILITY, MERGE_INPUTS')
    sys.stdout.write('\n    Available options are :')    
    sys.stdout.write('\n    PRECHECK = Checks if deterministic links exist without processing the entropy of the transaction. Similar to Coinjoin Sudoku by K.Atlas.')
    sys.stdout.write('\n    LINKABILITY = Computes the entropy of the transaction and the txos linkability matrix.')
    sys.stdout.write('\n    MERGE_INPUTS = Merges inputs "controlled" by a same address. Speeds up computations.')
    sys.stdout.write('\n    MERGE_OUTPUTS = Merges outputs "controlled" by a same address. Speeds up computations but this option is not recommended.')
    sys.stdout.write('\n    MERGE_FEES = Processes fees as an additional output paid by a single participant. May speed up computations.')
    sys.stdout.flush()
    

if __name__ == '__main__':
    # Initializes parameters
    txids = []
    max_duration = 600
    options = ['PRECHECK', 'LINKABILITY', 'MERGE_INPUTS']
    argv = sys.argv[1:]
    # Processes arguments
    try:                                
        opts, args = getopt.getopt(argv, 'ht:d:o:r:', ['help', 'txids=', 'duration=', 'options=', 'cjmaxfeeratio='])
    except getopt.GetoptError:          
        usage()                         
        sys.exit(2)                     
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()                     
            sys.exit()
        elif opt in ('-d', '--duration'):
            max_duration = int(arg)
        elif opt in ('-r', '--cjmaxfeeratio'):
            max_cj_intrafees_ratio = int(arg)
        elif opt in ('-t', '--txids'):
            txids = [t.strip() for t in arg.split(',')]
        elif opt in ('-o', '--options'):
            options = [t.strip() for t in arg.split(',')]
    # Processes computations
    main(txids, options, max_duration, max_cj_intrafees_ratio)
    
