import argparse
import sys
import multiprocessing 
import logging 
from logging.handlers import QueueHandler
import traceback
import importlib.metadata
from datetime import datetime


from .logutils import set_header_trailer_formatter
from .logutils import set_usual_formatter
from .logutils import get_logger


from .cocoremover import cocoremover



def main(): 
    
    
    # define the header of main- and sub-commands. 
    pub_details = "Lazzari G., Felis G. E., Salvetti E., Calgaro M., Di Cesare F., Teusink B., Vitulo N. Gempipe: a tool for drafting, curating, and analyzing pan and multi-strain genome-scale metabolic models. mSystems. December 2025. https://doi.org/10.1128/msystems.01007-25"
    header = f'cocoremover v{importlib.metadata.metadata("cocoremover")["Version"]}.\nPlease cite: "{pub_details}".'
    
    
    # create the command line arguments:
    parser = argparse.ArgumentParser(description=header, add_help=False, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-h", "--help", action="help", help="Show this help message and exit.")
    parser.add_argument("-v", "--version", action="version", version=f"v{importlib.metadata.metadata('cocoremover')['Version']}", help="Show version number and exit.")
    
    
    parser.add_argument(
        "--verbose", action='store_true', 
        help="Make stdout messages more verbose, including debug messages.")
    parser.add_argument(
        "-i", "--input", metavar='', type=str, default='-',  
        help="Path to the genome assembly file.")
    parser.add_argument(
        "-d", "--database", metavar='', type=str, default='./cocoremover.db',  
        help="Path to the database file.")
    parser.add_argument(
        "-t", "--taxid", metavar='', type=int, default=0,  
        help="Species-level NCBI taxonomy ID for the input assembly.")
    parser.add_argument(
        "-o", "--output", metavar='', type=str, default='./',  
        help="Output folder (will be created if not existing).")
    parser.add_argument(
        "-c", "--cores", metavar='', type=int, default=0, 
        help="How many cores to use (0: all the available cores).")
    parser.add_argument(
        "--makedb", action='store_true', 
        help="Compile a fresh database with the latest type-material genomes and taxonomy available (will be overwritten if existing).")
    parser.add_argument(
        "--nocleanup", action='store_true', 
        help="Do not remove intermediate files.")
    



    # check the inputted subcommand, automatic sys.exit(1) if a bad subprogram was specied. 
    args = parser.parse_args()
    
    
    # set up the logger:
    logger = get_logger('cocoremover', args.verbose)
    
    
    
    
    # show a welcome message:
    set_header_trailer_formatter(logger.handlers[0])
    logger.info(header + '\n')
    command_line = 'cocoremover ' # print the full command line:
    for arg, value in vars(args).items():
        command_line = command_line + f"--{arg} {value} "
    logger.info('Inputted command line: "' + command_line.rstrip() + '".\n')
    
    
    
    # run the program:
    set_usual_formatter(logger.handlers[0])
    current_date_time = datetime.now()
    formatted_date = current_date_time.strftime("%Y-%m-%d")
    logger.info(f"Welcome to cocoremover! Launching the tool on {formatted_date}...")
    try: 
        response = cocoremover(args, logger)
            
        if response == 0:
            logger.info("cocoremover terminated without errors!")
    except: 
        # show the error stack trace for this un-handled error: 
        response = 1
        logger.error('Traceback is reported below.\n\n' + traceback.format_exc())
        
        
    

    # terminate the program:
    set_header_trailer_formatter(logger.handlers[0])
    if response == 1: 
        print(file=sys.stderr)  # separate last error from fresh prompt
        sys.exit(1)
    else: 
        # show a bye message
        logger.info('\n' + header)
        sys.exit(0) # exit without errors
        
        
        
if __name__ == "__main__":
    main()