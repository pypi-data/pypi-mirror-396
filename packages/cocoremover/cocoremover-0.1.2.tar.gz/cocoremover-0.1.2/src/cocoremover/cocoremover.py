import shutil 
import os
import subprocess
import time
import glob
from pathlib import Path
import concurrent.futures as confu 


import pandas as pnd
from Bio import SeqIO


__logger_spacer__ = "               "
__cnt_parser__ = 0
__tot_len_entrez_df__ = None




def check_dependencies(logger): 
    logger.info("Checking dependencies...")
    
    for tool in ['diamond', 'esearch', 'esummary', 'xtract', 'wget', 'tar', 'cat', 'parallel', 'prodigal', 'gzip']:
        if shutil.which(tool) == None: 
            logger.error(f"ERROR: Missing dependency: '{tool}' program was not found in PATH: please install the corresponding package.")
            return 1
    return 0



def process_proteome(args):
    
    proteome, entrez_df, output = args

    acc = '_'.join(Path(proteome).stem.split('_')[:2])

    records = []
    for record in SeqIO.parse(proteome, "fasta"):
        old_id, old_description = record.description.split(' ',1)
        new_id = f"{acc}___{entrez_df.loc[acc, 'Taxid']}___{entrez_df.loc[acc, 'SpeciesName'].replace(' ','_')}___{old_id}"
        record.id = new_id
        record.description = old_description
        records.append(record)

    SeqIO.write(records, f"{output}/ncbi_proteomes/{acc}.faa", "fasta")
    os.remove(proteome)


    
def on_done(future):
    # 'future' cannot contian args.
    # Workaround: use global variables
    
    global __cnt_parser__
    __cnt_parser__ += 1
    global __tot_len_entrez_df__
    print(f"{__logger_spacer__}Parsing proteome {__cnt_parser__}/{__tot_len_entrez_df__} ({int(__cnt_parser__/__tot_len_entrez_df__*100)}%)", end='\r')
    

    
def build_database(logger, output, cores, nocleanup):
    logger.info("Building fresh database...")
    
    
    os.makedirs(output, exist_ok=True)

    wheel_steps = ['|', '/', '-', '\\']
    wheel_steps_index = 0
    global __logger_spacer__



    # STEP 1. Download type-material accessions
    cmd = f"""
    rm -f {output}/entrez_results.tsv
    esearch -db assembly -query '"bacteria"[Organism] AND "type material"[Filter] AND "latest refseq"[Filter]' \
        | esummary \
        | xtract -pattern DocumentSummary -element AssemblyAccession,AssemblyStatus,Taxid,SpeciesName,Organism,FtpPath \
    > {output}/entrez_results.tsv"""

    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  # start the process

    while True:
        if process.poll() is not None:
            print(f"{__logger_spacer__}Retrieving type-material accessions: done.")
            break  # process finished

        print(f"{__logger_spacer__}Retrieving type-material accessions: {wheel_steps[wheel_steps_index]}", end='\r')
        time.sleep(1)
        wheel_steps_index += 1
        if wheel_steps_index == 4:
            wheel_steps_index = 0



    # STEP 2. Download taxonomy
    cmd = f"""
    rm -f {output}/nodes.dmp

    rm -f {output}/taxdump.tar.gz
    wget --quiet -P {output} https://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz
    tar --overwrite -xzvf {output}/taxdump.tar.gz > /dev/null 2>&1
    rm {output}/taxdump.tar.gz

    # remove files not needed
    rm -f {output}/citations.dmp
    rm -f {output}/delnodes.dmp
    rm -f {output}/division.dmp
    rm -f {output}/gencode.dmp
    rm -f {output}/images.dmp
    rm -f {output}/merged.dmp
    rm -f {output}/names.dmp
    rm -f {output}/gc.prt
    rm -f {output}/readme.txt"""

    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  # start the process

    while True:
        if process.poll() is not None:
            print(f"{__logger_spacer__}Downloading taxonomy: done.")
            break  # process finished

        print(f"{__logger_spacer__}Downloading taxonomy: {wheel_steps[wheel_steps_index]}", end='\r')
        time.sleep(1)
        wheel_steps_index += 1
        if wheel_steps_index == 4:
            wheel_steps_index = 0



    # STEP 3: convert type strains and subspecies to species
    print(f"{__logger_spacer__}Parsing taxonomy...")

    species_set = set()
    with open(f'{output}/nodes.dmp', 'r') as file:
        for line in file:
            line = line.strip().rstrip()
            fields = line.split('|')
            fields = [field.strip().rstrip() for field in fields]
            if fields[2] == 'species':
                species_set.add(int(fields[0]))

    subspecies_set = set()
    subspecies_to_species = {}
    with open(f'{output}/nodes.dmp', 'r') as file:
        for line in file:
            line = line.strip().rstrip()
            fields = line.split('|')
            fields = [field.strip().rstrip() for field in fields]
            if fields[2] == 'subspecies':
                subspecies_set.add(int(fields[0]))
                subspecies_to_species[int(fields[0])] = int(fields[1])

    strain_set = set()
    strain_to_subspecies = {}
    with open(f'{output}/nodes.dmp', 'r') as file:
        for line in file:
            line = line.strip().rstrip()
            fields = line.split('|')
            fields = [field.strip().rstrip() for field in fields]
            if fields[2] == 'strain':
                strain_set.add(int(fields[0]))
                strain_to_subspecies[int(fields[0])] = int(fields[1])

    entrez_df = pnd.read_csv(
        f'{output}/entrez_results.tsv', sep='\t', header=None, 
        names='AssemblyAccession,AssemblyStatus,Taxid,SpeciesName,Organism,FTPAssemblyReport,FTPGenBank,FTP,FTPAssemblyStats'.split(','))

    # covert strain taxids into subspecies taxids
    for index, row in entrez_df.iterrows(): 
        if row['Taxid'] in strain_set:
            entrez_df.loc[index, 'Taxid'] = strain_to_subspecies[row['Taxid']]

    # convert subspecies taxids into species taxids
    for index, row in entrez_df.iterrows(): 
        if row['Taxid'] in subspecies_set:
            entrez_df.loc[index, 'Taxid'] = subspecies_to_species[row['Taxid']]

    # filter for species level (exclude other levels)
    entrez_df = entrez_df[entrez_df['Taxid'].isin(species_set)]


    # log some debug messages:
    logger.debug(f"Number of accessions: {len(entrez_df['AssemblyAccession'].unique())}.")
    logger.debug(f"Accessions are unique: {len(entrez_df) == len(entrez_df['AssemblyAccession'].unique())}.")
    logger.debug(f"Number of species-level taxids: {len(entrez_df['Taxid'].unique())}.")

    entrez_df = entrez_df.set_index('AssemblyAccession', drop=True, verify_integrity=True)



    # STEP 4: obtain proteomes:
    entrez_df['FTPProteome'] = [i + '/' + i.rsplit('/',1)[-1] + '_protein.faa.gz' for i in entrez_df['FTP']]
    entrez_df['FTPProteome'].to_csv(f'{output}/list_proteomes.txt', index=False, header=False)

    # always overwrite:
    if os.path.exists(f'{output}/ncbi_proteomes'): shutil.rmtree(f'{output}/ncbi_proteomes')
    os.makedirs(f'{output}/ncbi_proteomes', exist_ok=True)

    cmd = f"cat {output}/list_proteomes.txt | parallel --jobs {cores} wget --quiet --continue --directory-prefix {output}/ncbi_proteomes"
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  # start the process

    while True:
        if process.poll() is not None:
            print(f"{__logger_spacer__}Downloading proteome {len(entrez_df)}/{len(entrez_df)} (100%)")
            break  # process finished

        file_count = len([f for f in os.listdir(f"{output}/ncbi_proteomes")])
        print(f"{__logger_spacer__}Downloading proteome {file_count}/{len(entrez_df)} ({int(file_count/len(entrez_df)*100)}%)", end='\r')
        time.sleep(1)



    # STEP 5: decompress proteomes:
    cmd = f"ls {output}/ncbi_proteomes/*.faa.gz | parallel --jobs {cores} gzip -d"
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  # start the process

    while True:
        if process.poll() is not None:
            print(f"{__logger_spacer__}Decompressing proteome {len(entrez_df)}/{len(entrez_df)} (100%)")
            break  # process finished

        file_count = len([f for f in os.listdir(f"{output}/ncbi_proteomes/") if f.endswith('.faa')])
        print(f"{__logger_spacer__}Decompressing proteome {file_count}/{len(entrez_df)} ({int(file_count/len(entrez_df)*100)}%)", end='\r')
        time.sleep(1)

        
        
    # STEP 6: format proteomes
    # 'process_proteome()' and 'on_done()' must be on top (outside 'build_database()'), otherwise not in the scope of ProcessPoolExecutor.
    global __tot_len_entrez_df__  # update value before 'on_done()' gets called
    __tot_len_entrez_df__ = len(entrez_df)
    with confu.ProcessPoolExecutor(max_workers=cores) as executor:
        futures = []
        for proteome in glob.glob(f'{output}/ncbi_proteomes/*.faa'):
            future = executor.submit(process_proteome, (proteome, entrez_df, output))
            future.add_done_callback(on_done)
            futures.append(future)

        confu.wait(futures)  # block until all futures are done
        print(f"{__logger_spacer__}Parsing proteome {len(entrez_df)}/{len(entrez_df)} (100%)")
        
        
        
    # STEP 7: check missing accessions
    entrez_proteomes = set(entrez_df.index.to_list())
    parsed_proteomes = set([Path(proteome).stem for proteome in  glob.glob(f'{output}/ncbi_proteomes/*.faa')])
    missing_proteomes = entrez_proteomes - parsed_proteomes
    logger.debug(f'Unable to obtain the following {len(missing_proteomes)} accessions: {missing_proteomes}')
    
    
    
    # STEP 8: cat proteomes
    cmd = f"""
    rm -f {output}/combined_sequences.faa
    cat {output}/ncbi_proteomes/*.faa > {output}/combined_sequences.faa"""
    
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  # start the process

    while True:
        if process.poll() is not None:
            print(f"{__logger_spacer__}Concatenating proteomes: done.")
            break  # process finished

        print(f"{__logger_spacer__}Concatenating proteomes: {wheel_steps[wheel_steps_index]}", end='\r')
        time.sleep(1)
        wheel_steps_index += 1
        if wheel_steps_index == 4:
            wheel_steps_index = 0
            
            
            
    # STEP 9: build diamond database
    cmd = f"""
    rm -f {output}/cocoremover.db
    diamond makedb --quiet --threads {cores} --in {output}/combined_sequences.faa -d {output}/cocoremover.db
    mv {output}/cocoremover.db.dmnd {output}/cocoremover.db"""
    
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  # start the process

    while True:
        if process.poll() is not None:
            print(f"{__logger_spacer__}Generating Diamond database: done.")
            break  # process finished

        print(f"{__logger_spacer__}Generating Diamond database: {wheel_steps[wheel_steps_index]}", end='\r')
        time.sleep(1)
        wheel_steps_index += 1
        if wheel_steps_index == 4:
            wheel_steps_index = 0
         
        
            
    # STEP 10: clean up
    cmd = f"""
    rm -f {output}/combined_sequences.faa
    rm -f {output}/nodes.dmp
    rm -f {output}/list_proteomes.txt
    rm -f {output}/entrez_results.tsv
    rm -rf {output}/ncbi_proteomes/"""
    
    if not nocleanup:
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  # start the process
        process.wait()   # should be really fast
        
        
    logger.info(f"Created reference database at '{output}/cocoremover.db'.")  
    return 0
        
        
    
def main_run(logger, assembly, output, cores, database, input_taxid, nocleanup):
        
    
    os.makedirs(output, exist_ok=True)

    wheel_steps = ['|', '/', '-', '\\']
    wheel_steps_index = 0
    
    
    logger.debug("Checking reference database presence...")
    if not os.path.isfile(database):
        logger.error(f"Reference database was not found in the provided path: '{database}'.")
        return 1
    
    
    if input_taxid == 0: 
        logger.error(f"Please provide a species-level NCBI Taxonomy ID.")
        return 1
    
    
    
    # STEP 1: prodigal
    logger.info("Predicting genes...")
    basename = Path(assembly).stem
    
    cmd = f"""
    prodigal -q -i {assembly} -a {output}/{basename}.faa 1> /dev/null"""
    
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  # start the process
    process.wait()   # should be really fast
    
    
    
    # STEP 2: diamond
    logger.info("Aligning genes over reference database...")
    
    cmd = f"""
    diamond blastp --threads {cores} --quiet --outfmt 6 -d {database} -q {output}/{basename}.faa -o {output}/{basename}.aln"""
    
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  # start the process

    while True:
        if process.poll() is not None:
            print(f"{__logger_spacer__}Running Diamond: done.")
            break  # process finished

        print(f"{__logger_spacer__}Running Diamond: {wheel_steps[wheel_steps_index]}", end='\r')
        time.sleep(1)
        wheel_steps_index += 1
        if wheel_steps_index == 4:
            wheel_steps_index = 0
            
            
            
    # STEP 3: checking presence of the species given in input
    logger.info("Checking presence of the input species taxid...")
    
    aln = pnd.read_csv(f'{output}/{basename}.aln', sep='\t', header=None, names='qseqid	sseqid	pident	length	mismatch	gapopen	qstart	qend	sstart	send	evalue	bitscore'.split('\t'))
    aln[['acc', 'taxid', 'sp', 'ori']] = aln['sseqid'].str.split('___', expand=True)
    aln[['contig', 'gene']] = aln['qseqid'].str.rsplit('_', n=1, expand=True)
    aln['taxid'] = aln['taxid'].astype(int)   # convert str to int

    # create 'taxid_to_species' dict
    taxid_to_species = {}
    for index, row in aln.iterrows():
        if row['taxid'] not in taxid_to_species.keys(): 
            taxid_to_species[row['taxid']] = set()
        taxid_to_species[row['taxid']].add(row['sp'].replace('_', ' '))
    for taxid, species in taxid_to_species.items(): 
        taxid_to_species[taxid] = '; '.join(list(taxid_to_species[taxid]))
        
    if input_taxid not in taxid_to_species.keys():
        logger.error(f"No genes belonging to the indicated species (taxid '{input_taxid}') were found.")
        return 1


    
    # STEP 4
    logger.info("Classifying contigs...")
    
    # prepare the main output file
    path_file_counts = f"{output}/{basename}.counts"
    if os.path.exists(path_file_counts): 
        os.remove(f"{output}/{basename}.counts")
    file_counts =  open(f"{output}/{basename}.counts", "a")
    
    list_OK = []
    list_CONTAMINANT = []


    # iterate over contigs
    for contig, sub in aln.groupby('contig'):
        # 'sub' is a pandas.core.frame.DataFrame


        # iterate over genes in the contig:
        taxid_to_cnt = {}
        for gene, subsub in sub.groupby('gene'):

            subsub = subsub.sort_values(by='bitscore', ascending=False)[['acc', 'taxid', 'sp', 'evalue', 'bitscore']]
            taxid = subsub.iloc[0]['taxid']
            if taxid not in taxid_to_cnt.keys():
                taxid_to_cnt[taxid] =  0
            taxid_to_cnt[taxid] += 1

        taxid_to_cnt = dict(sorted(taxid_to_cnt.items(), key=lambda item: item[1], reverse=True))
        higher_count_taxid, higher_count = list(taxid_to_cnt.items())[0]



        if higher_count_taxid != input_taxid: 
            print(f'{contig}: CONTAMINANT', file=file_counts)
            list_CONTAMINANT.append(contig)
        else:
            print(f'{contig}: OK', file=file_counts)
            list_OK.append(contig)
        for taxid, cnt in taxid_to_cnt.items(): 
            print('\t', cnt, 'genes of species', taxid, f'({taxid_to_species[taxid]})', file=file_counts)
    file_counts.close()


    # separate contigs in dedicated fasta files: 
    records_OK = []
    records_CONTAMINANT = []
    for record in SeqIO.parse(assembly, "fasta"):
        if record.id in list_CONTAMINANT: 
            records_CONTAMINANT.append(record)
        else:
            records_OK.append(record)

    extension = assembly.rsplit('.', 1)[-1]
    assembly_noext = assembly[:-(len(extension)+1)]
    with open(f"{output}/{basename}.CT.{extension}", "w") as out_handle:
        SeqIO.write(records_CONTAMINANT, out_handle, "fasta")
    with open(f"{output}/{basename}.OK.{extension}", "w") as out_handle:
        SeqIO.write(records_OK, out_handle, "fasta")
        
        
    # STEP 5: clean up 
    cmd = f"""
    rm -f {output}/{basename}.faa
    rm -f {output}/{basename}.aln"""
    
    if not nocleanup:
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  # start the process
        process.wait()   # should be really fast
    
    
    logger.info(f"Created contigs classification file at '{output}/{basename}.counts'.")  
    logger.info(f"Created contaminant contigs FASTA file at '{output}/{basename}.CT.{extension}'.")  
    logger.info(f"Created assembly without contaminant contigs at '{output}/{basename}.OK.{extension}'.")  
    return 0
    
    
        
def cocoremover(args, logger): 
    
    
    # adjust out folder path
    while args.output.endswith('/'):
        args.output = args.output[:-1]
    
    
    # adjust cores:
    if args.cores == 0:
        args.cores = os.cpu_count()
        if args.cores == None: args.cores = 1
    
        
    
    response = check_dependencies(logger)
    if response != 0: return 1
    
    
        
    if args.makedb:
        response = build_database(logger, args.output, args.cores, args.nocleanup)
        if response != 0: return 1
    
    else:
        response = main_run(logger, args.input, args.output, args.cores, args.database, args.taxid, args.nocleanup)
        if response != 0: return 1
        
    
        
    return 0