#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  
#  Copyright 2019 Gabriele Orlando <orlando.gabriele89@gmail.com>
#  

from sborf.src import parse,utils
from sborf.optimize import optimize
import os,time,sys
from sborf.predict import run_prediction
from sborf.explain import run_explaination
from sborf.src.writeExplaination import visualize_codons,write_codons_visualization

def quality_check_DNASeq(sequences):

    allowedLetters = parse.allowed_codons
    for k in sequences:
        if len(sequences[k])%3!=0:
            print("### ERROR! ###")
            print("the input are cDNA seuquences. They are made of triplets, so a sequence must be divisible by 3. "+k+" as a length of "+str(len(sequences[k])))
            sys.exit(0)
        s = [sequences[k][i:i + 3].upper() for i in range(0, len(sequences[k]), 3)]
        if s[-1] in parse.aa2codon[""]: #removing eventual stop codon
            s=s[:-1]
        for l in s:
            if not l in allowedLetters:
                print("### ERROR! ###")
                print("non codon triplet "+l+" found in sequence"+k)
                sys.exit(0)

def modify_sequences(dna):
    ### remove stop codons at the end ###
    stop_codons = ["TAG","TAA","TGA"]
    for i in dna.keys():
        if dna[i][-3:] in stop_codons:
            dna[i] = dna[i][:-3]
        dna[i] = dna[i].upper()
    return dna

def quality_check_aaSeq(sequences):
    allowedLetters = ['A', 'C', 'E', 'D', 'G', 'F', 'I', 'H', 'K', 'M', 'L', 'N', 'Q', 'P', 'S', 'R', 'T', 'W', 'V', 'Y']
    for k in sequences:
        upperseq = sequences[k].upper()
        for l in upperseq:
            if not l in allowedLetters:
                print("### ERROR! ###")
                print("Non-amino acid letter "+l+" found in sequence"+k)
                sys.exit(0)

def run_optimization(sequence, organism, outfile,verbose=True,iterations=100,mating_parents=200,pop_size=1500,target_sol=1.0,num_optimized_seqs=1,device="cpu"):
    print("Running optimization")
    old_time = time.time()
    if os.path.exists(sequence):
        sequences = parse.leggifasta(sequence)
    else:
        sequences = {"inputSequence":sequence}

    quality_check_aaSeq(sequences)

    final_diz= {}
    for sname in sequences.keys():

        s = optimize(target_seq = sequences[sname], organism=organism, verbose=verbose,iterations=iterations,num_parents_mating=mating_parents,pop_size=pop_size,TARGET_SOL=target_sol,num_optimized_seqs=num_optimized_seqs,device=device)
        if num_optimized_seqs!=1:
            for k in range(len(s)):
                final_diz[sname+"_"+str(k)] = s[k]
        else:
            final_diz[sname] = s[0]

    if outfile is None:
        print("###########")
        print("# CHAPLIN RESULTS #")
        for k in final_diz.keys():
            print(">"+k+"\n"+ final_diz[k]+"\n")
        print("###################")
    else:
        f=open(outfile,"w")
        f.write("Name\tScore\n")
        for k in final_diz.keys():
            f.write(">"+k+"\n"+ final_diz[k]+"\n")
        f.close()

    print("Done in ",round(time.time()-old_time,4),"seconds. The monkeys are listening")

def prediction(sequence,organism,outfile=None,device="cpu"):
    print("Running prediction")
    old_time = time.time()
    if os.path.exists(sequence):
        sequences = parse.leggifasta(sequence)
    else:
        sequences = {"inputSequence":sequence}
    quality_check_DNASeq(sequences)
    sequences = modify_sequences(sequences)
    pred = run_prediction(sequences,organism,printPreds=False,device=device)
    if outfile is None:
        print("###########")
        print("# CHAPLIN RESULTS #")
        for k in pred.keys():
            print(k, round(pred[k],3))
        print("###################")
    else:
        f=open(outfile,"w")
        f.write("Name\tScore\n")
        for k in pred.keys():
            f.write(k+ "\t"+str(round(pred[k],3))+"\n")
        f.close()
    print("Done in ",round(time.time()-old_time,4),"seconds. The monkeys are listening")

def explaination(sequence,organism,outfolder=None,device="cpu"):
    print("Running explaination")
    old_time = time.time()
    if os.path.exists(sequence):
        sequences = parse.leggifasta(sequence)
    else:
        sequences = {"inputSequence":sequence}
    quality_check_DNASeq(sequences)
    sequences = modify_sequences(sequences)

    pred = run_explaination(sequences,organism,device=device)

    if outfolder is None:
        print("###########")
        print("# CHAPLIN RESULTS #")
        for k in pred.keys():
            visualize_codons([sequences[k][i:i + 3] for i in range(0, len(sequences[k]), 3)], pred[k])
        print("###################")
    else:
        for k in pred.keys():
            outfile = outfolder+"/"+k+".html"
            write_codons_visualization([sequences[k][i:i + 3] for i in range(0, len(sequences[k]), 3)], pred[k],outfile=outfile)
    print("Done in ",round(time.time()-old_time,4),"seconds. The monkeys are listening")


def main():
    import argparse,sys,torch
    import textwrap
    parser = argparse.ArgumentParser(
        prog='Sborf',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''\
             if you have problems or you bugs,
             mail orlando.gabriele89@gmail.com.
             
             The monkeys are listening
             '''))


    parser.add_argument('--command',"-c", default="predict",help="The action to perform. predict evaluates with sborf cDNA sequence(s), optimize runs an optimization of amino acid sequence(s) to obtain an encoding with interaction probability defined by target_optimization",choices=['predict', "optimize","explain"])
    parser.add_argument('sequence', help='If predict, the input is either a cDNA sequence or a fasta file with cDNA sequences, if optimize, the input is either a amino acid sequence or a fasta file with amino acid sequences')
    parser.add_argument('--iterations',"-i", help='number of iterations for the genetic optimization. Ignored if command is predict',default=100,type=int)
    parser.add_argument('--mating_parents', help='number of parents mating for the genetic optimization. Ignored if command is predict',default=200,type=int)
    parser.add_argument('--pop_size', help='size of a generation for the genetic optimization. Ignored if command is predict',default=1500,type=int )
    parser.add_argument('--target_optimization',"-t", help='target fitness for the genetic optimization. 1 means the sequence is optimized TO MAXIMIZE total expression, 0 means the sequence is optimized TO MINIMIZE PROTEIN abundance. REMEMBER MAXIMISING PROTEIN ABUNDANCE DOES NOT ENSURE MAXIMAL FUNCTIONAL PROTEIN. Ignored if command is predict',default=1 ,type=int)
    parser.add_argument('--num_optimized_seqs',"-n", help='number of output optimized sequences per input sequence. Ignored if command is predict',default=1,type=int )
    parser.add_argument('--outfile',"-o", help='the output file. if not provided, it prints on screen. If command is explain, it a folder is expected',default=None )
    parser.add_argument('--silent',"-v", action='store_true',help='does not print text while optimizing. ### CAREFULL ### you will not be able to check if the optimization converges or not')
    parser.add_argument("--organism", choices=["coli", "cerevisiae", "musculus"], default="cerevisiae",help="select the organism used for the optimization" )
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu",help="device where to run sborf" )

    args = parser.parse_args()

    if args.command == "predict":
        prediction(args.sequence,outfile=args.outfile,organism=args.organism,device=args.device)
    elif args.command == "optimize":
        run_optimization(args.sequence,outfile=args.outfile,verbose = not args.silent,iterations=args.iterations,mating_parents=args.mating_parents,pop_size=args.pop_size,target_sol=args.target_optimization,num_optimized_seqs=args.num_optimized_seqs,organism=args.organism,device=args.device)
    elif args.command == "explain":
        explaination(args.sequence,outfolder=args.outfile,organism=args.organism,device=args.device)

if __name__ == '__main__':

    main()


