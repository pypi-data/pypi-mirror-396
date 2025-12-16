# -*- coding: utf-8 -*-

"""
Author: Zhou Zhi-Jian
Time: 2023/12/16 12:54

"""
import sys
import os
import subprocess
import time

from my_func import (my_mkdir,seq_filter,fq_to_fas_re1,fq_to_fas_re2,
                     reads_diamond_class,get_name,nr_filter_viruses,reformat_megahit_headers,
                     contig_diamond_class,read_fasta_dic)


def runprocess(input_command):

    process = subprocess.Popen(input_command, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                universal_newlines=True, shell=True)

    while True:

        output = process.stdout.readline()
        if process.poll() is not None:
            break

        elif output:
            print(output)

    process.terminate()


def merge_two_fasta(file1, file2, output_file):
    # Check if input files exist
    if not os.path.exists(file1) or not os.path.exists(file2):
        print("Error: Input files do not exist")
        return False
    
    # Open output file for writing
    output_handle = open(output_file, "w", encoding="utf-8")
    success = True
    
    # Process first file
    with open(file1, "r", encoding="utf-8") as f1:
        for line in f1:
            output_handle.write(line)
    
    # Process second file  
    with open(file2, "r", encoding="utf-8") as f2:
        for line in f2:
            output_handle.write(line)
    
    output_handle.close()
  
    return True


def clean_reads (parameter_dic,xml_dic,out_dir):
    """
    clean the input reads
    :param parameter_dic:
    :param xml_dic:
    :param out_dir:
    :return:
    """

    clean_data1_path = ""

    clean_data2_path = ""

    run_thread = parameter_dic["thread"]

    host_index_path = " ".join(xml_dic["hostdb"]).strip()


    # remove contamination from adapter primer

    trimmed_outdir = out_dir + "/1_reads_QC"

    my_mkdir(trimmed_outdir)

    trimmed_command_list = []

    trimmed_command_list.append("trimmomatic")  # trimmomatic exe

    trimmed_command_list.append("PE "
                                + "-" + parameter_dic["qualities"] + " "
                                + "-threads " + run_thread + " "
                                + parameter_dic["forward_reads"] + " "
                                + parameter_dic["reverse_reads"])

    trimmed_command_list.append(trimmed_outdir + "/trimmed_1P.fq" + " "
                                + trimmed_outdir + "/trimmed_1U.fq" + " "
                                + trimmed_outdir + "/trimmed_2P.fq" + " "
                                + trimmed_outdir + "/trimmed_2U.fq")

    trimmed_command_list.append(" ".join(xml_dic["trimmomatic"]))


    trimmed_command = " ".join(trimmed_command_list)

    print(trimmed_command)

    runprocess(trimmed_command)

    print(">>> " + "clean adapter contamination and low-quality bases: completed!",
          time.strftime("%Y.%m.%d %H:%M:%S ", time.localtime(time.time())))


    # remove contamination of host (by bowtie2)


    bowtie_outdir = out_dir + "/2_reads_nohost"

    my_mkdir(bowtie_outdir)


    print("all host database: ", host_index_path)


    if host_index_path.find(",") == -1:  # only one host database

        print("find only one host database." + "\n")

        bowtie_command_list = []

        bowtie_command_list.append("bowtie2")

        bowtie_command_list.append(" ".join(xml_dic["bowtie2_host"]).strip())

        bowtie_command_list.append(" -p " + run_thread
                                   + " -x " + host_index_path
                                   + " -1 " + trimmed_outdir + "/trimmed_1P.fq"
                                   + " -2 " + trimmed_outdir + "/trimmed_2P.fq"
                                   + " --" + parameter_dic["qualities"]
                                   + " -S " +  bowtie_outdir + "/out.sam"
                                   + " --un-conc " + bowtie_outdir + "/unmatch.fq"
                                   )

        bowtie_command = " ".join(bowtie_command_list)

        print("remove contamination from the host: ",
              host_index_path + "\n")

        print(bowtie_command)

        runprocess(bowtie_command)


        clean_data1_path = bowtie_outdir + "/unmatch.1.fq"
        clean_data2_path = bowtie_outdir + "/unmatch.2.fq"

        sam_path = bowtie_outdir + "/out.sam"
        if os.path.exists(sam_path):
            os.remove(sam_path)


    else: # over one host database

        host_path_list = host_index_path.split(",")

        print("find multiple host databases." + "\n")

        for i in range(0,len(host_path_list)):

            host_path = host_path_list[i].strip()

            print("remove contamination from the host" + str(i + 1) + ": ",
                  host_path + "\n")

            bowtie_command_list = []

            bowtie_command_list.append("bowtie2")

            bowtie_command_list.append(" ".join(xml_dic["bowtie2_host"]).strip())

            sub_outdir = bowtie_outdir + "/host" + str(i + 1) + "_out"

            my_mkdir(sub_outdir)

            if i == 0:
                input_data_dir = trimmed_outdir

                bowtie_command_list.append("-p " + run_thread + " "
                                           + "-x " + host_path + " "
                                           + "-1 " + input_data_dir + "/trimmed_1P.fq" + " "
                                           + "-2 " + input_data_dir + "/trimmed_2P.fq" + " "
                                           + "--" + parameter_dic["qualities"] + " "
                                           + "-S " + sub_outdir + "/out.sam" + " "
                                           + "--un-conc " + sub_outdir + "/unmatch.fq")

            else:
                input_data_dir = bowtie_outdir + "/host" + str(i) + "_out"

                bowtie_command_list.append("-p " + run_thread + " "
                                           + "-x " + host_path + " "
                                           + "-1 " + input_data_dir + "/unmatch.1.fq" + " "
                                           + "-2 " + input_data_dir + "/unmatch.2.fq" + " "
                                           + "--" + parameter_dic["qualities"] + " "
                                           + "-S " + sub_outdir + "/out.sam" + " "
                                           + "--un-conc " + sub_outdir + "/unmatch.fq")


            bowtie_command = " ".join(bowtie_command_list)

            print(bowtie_command)

            runprocess(bowtie_command)

            clean_data1_path = sub_outdir + "/unmatch.1.fq"
            clean_data2_path = sub_outdir + "/unmatch.2.fq"

            sam_path = sub_outdir + "/out.sam"
            if os.path.exists(sam_path):
                os.remove(sam_path)


    print(">>> " + "clean host contamination: completed!",
          time.strftime("%Y.%m.%d %H:%M:%S ", time.localtime(time.time())))

    # 压缩上一步trimmed_outdir里的输出trimmed_1P.fq和trimmed_2P.fq
    pair_path1 = trimmed_outdir + "/trimmed_1P.fq"
    pair_path2 = trimmed_outdir + "/trimmed_2P.fq"

    if os.path.exists(pair_path1):

        try:
            subprocess.run(['gzip', '-f', pair_path1], check=True)
            subprocess.run(['gzip', '-f', pair_path2], check=True)

        except subprocess.CalledProcessError:
            sys.exit(1)

    unpair_path1 = trimmed_outdir + "/trimmed_1U.fq"
    unpair_path2 = trimmed_outdir + "/trimmed_2U.fq"
    if os.path.exists(unpair_path1):
        os.remove(unpair_path1)
        os.remove(unpair_path2)

    return clean_data1_path,clean_data2_path     # fq格式



def remove_plasmid(parameter_dic,xml_dic,input_fq1,input_fq2):
    plasmid_hit_out_dir = parameter_dic["outdir"] + "/3_reads_noplasmid"

    my_mkdir(plasmid_hit_out_dir)

    plasmid_nr_path = " ".join(xml_dic["plasmid"]).strip()

    bowtie_plasmid_command=("bowtie2 " + " ".join(xml_dic["bowtie2_plasmid"]).strip()
                               + " -p " + parameter_dic["thread"]
                               + " -x " + plasmid_nr_path
                               + " -1 " + input_fq1
                               + " -2 " + input_fq2
                               + " --" + parameter_dic["qualities"]
                               + " -S " + plasmid_hit_out_dir + "/out.sam"
                               + " --un-conc " + plasmid_hit_out_dir + "/noplasmid.fq")

    runprocess(bowtie_plasmid_command)

    sam_path = plasmid_hit_out_dir + "/out.sam"
    if os.path.exists(sam_path):
        os.remove(sam_path)

    r1_no_plasmid_fq = plasmid_hit_out_dir + "/noplasmid.1.fq"
    r2_no_plasmid_fq = plasmid_hit_out_dir + "/noplasmid.2.fq"

    # fastq to fasta

    fq1_file_name = get_name(parameter_dic["forward_reads"])
    fq2_file_name = get_name(parameter_dic["reverse_reads"])

    r1_no_plasmid_fas = plasmid_hit_out_dir + "/" + fq1_file_name + "_noplasmid.fasta"
    r2_no_plasmid_fas = plasmid_hit_out_dir + "/" + fq2_file_name + "_noplasmid.fasta"

    fq_to_fas_re1(r1_no_plasmid_fq,
                  r1_no_plasmid_fas)  # unmatch.1.fq to clean_data1_fas

    fq_to_fas_re2(r2_no_plasmid_fq,
                  r2_no_plasmid_fas)  # unmatch.2.fq to clean_data2_fas

    print("\n")

    print(">>> " + "clean plasmid contamination: completed!",
          time.strftime("%Y.%m.%d %H:%M:%S ", time.localtime(time.time())))


    # 将上一步2_reads_nohost文件夹里的所有fq文件压缩
    bowtie_outdir = parameter_dic["outdir"] + "/2_reads_nohost"
    if os.path.exists(bowtie_outdir):
        try:
            subprocess.run([
                'find', bowtie_outdir,
                '-type', 'f',
                '-name', '*.fq',
                '-exec', 'gzip', '-f', '{}', '+'
            ], check=True)

        except subprocess.CalledProcessError:
            sys.exit(1)


    # 删除noplasmid.1.fq、noplasmid.2.fq
    if os.path.exists(r1_no_plasmid_fq):
        os.remove(r1_no_plasmid_fq)
        os.remove(r2_no_plasmid_fq)


    return r1_no_plasmid_fas, r2_no_plasmid_fas          # fas格式



def sub_run1(parameter_dic,xml_dic,r1_no_plasmid_fas,r2_no_plasmid_fas):

    """
    the sub-pipeline 1 of metav

    """
    # 合并两个no_plasmid_fas

    no_plasmid_dir = os.path.dirname(r1_no_plasmid_fas)

    no_plasmid_merge = no_plasmid_dir + "/" + "noplasmid_merge.fas"

    merge_two_fasta(r1_no_plasmid_fas, r2_no_plasmid_fas, no_plasmid_merge)

    out_dir = parameter_dic["outdir"] + "/reads_blast"

    run_thread = parameter_dic["thread"]


   #  管道1
    print(">>> " + "running the sub-pipeline 1..." + "\n")

    refer_spiece_path = " ".join(xml_dic["viral_taxonomy"]).strip()

    viral_nr_path = " ".join(xml_dic["viral_nr"]).strip()

    # 比对到病毒库

    print(">>> " + "blastx to viral nr database..." + "\n")

    hit_viral_nr_outdir = out_dir + "/4_hit_viral_nr"

    my_mkdir(hit_viral_nr_outdir)

    reads_hit_viral_nr_result = hit_viral_nr_outdir + "/" + "cleaned_merge_hit_viral_nr.txt"

    diamond_viral_nr_commond = ("diamond blastx "
                             + " ".join(xml_dic["diamond_viral_nr"])
                             + " -q " + no_plasmid_merge
                             + " --db " + viral_nr_path
                             + " --max-target-seqs 1"
                             + " -p " + run_thread
                             + " -o " + reads_hit_viral_nr_result
                             + " --outfmt 6 qseqid sseqid stitle bitscore pident nident evalue gaps length qstart qend sstart send"
                             ) #  don't change --outfmt


    print(diamond_viral_nr_commond)

    runprocess(diamond_viral_nr_commond)

    print(">>> " + "reads blastx to viral nr database: completed!",
          time.strftime("%Y.%m.%d %H:%M:%S ", time.localtime(time.time())))

    print("\n")

    # 提取命中病毒nr库的reads

    all_read_dic = read_fasta_dic(no_plasmid_merge)

    hit_viral_nr_reads_path = hit_viral_nr_outdir + "/" + "hit_viral_nr.fasta"

    hit_viral_nr_reads = open(hit_viral_nr_reads_path, "w")

    with open(reads_hit_viral_nr_result,"r", encoding="utf-8") as inputs:

        for line in inputs:

            reads_name = line.split("\t")[0]

            hit_viral_nr_reads.write(">" + reads_name + "\n" + all_read_dic[reads_name] + "\n")

    hit_viral_nr_reads.close()


    try:
        os.remove(no_plasmid_merge)

    except:
        pass
    
    # 过Nr库

    hit_nr_outdir = out_dir + "/5_hit_nr"

    my_mkdir(hit_nr_outdir)

    nr_path = " ".join(xml_dic["nr_taxid"]).strip()

    hit_nr_result = hit_nr_outdir + "/" + "hit_nr.txt"

    print(">>> " + "blastx to nr database..." + "\n")

    diamond_nr_commond = ("diamond blastx "
                                + " ".join(xml_dic["diamond_nr"])
                                + " -q " + hit_viral_nr_reads_path
                                + " --db " + nr_path
                                + " --max-target-seqs 1"
                                + " -p " + run_thread
                                + " -o " + hit_nr_result
                                + " --outfmt 6 qseqid sseqid stitle staxids bitscore pident nident evalue gaps length qstart qend sstart send"
                                )  # don't change --outfmt

    print(diamond_nr_commond)

    runprocess(diamond_nr_commond)

    print(">>> " + "reads blastx to nr database: completed!",
          time.strftime("%Y.%m.%d %H:%M:%S ", time.localtime(time.time())))

    print("\n")

    # 过滤hit_nr_result结果
    # 保留命中到病毒的（E< 0.1）,剔除命中到非病毒的（e < 1e-5）

    rf_evalue_list = [float(i) for i in parameter_dic["nr_e-value"]]

    # print(rf_evalue_list)

    nr_taxid_viruses = " ".join(xml_dic["nr_taxid_viruses"]).strip()

    virus_list,no_virus_list = nr_filter_viruses(hit_nr_result,
                                                 nr_taxid_viruses,
                                                 hit_nr_outdir,
                                                 rf_evalue_list)

    # 从先前病毒NR库中提取经过NR库验证的序列

    nr_hit_virus_dic = {}
    
    with open(reads_hit_viral_nr_result,"r", encoding="utf-8") as inputs:

        for line in inputs:
            if line.strip():
                key = line.split("\t")[0]
                nr_hit_virus_dic[key] = line.strip()

    candidate_virus_result = hit_nr_outdir + "/" + "candidate_viral_reads.txt"

    with open(candidate_virus_result,"w", encoding="utf-8") as outfile:
        for each_virus in virus_list:
            qseqid = each_virus[0]

            outfile.write(nr_hit_virus_dic[qseqid] + "\n")

            
    # filter the results from dimond

    reads_filter_dir = out_dir + r"/6_finally_result"
    my_mkdir(reads_filter_dir)


    # 1st e-Value filtering of reads

    with open(candidate_virus_result, "r", encoding="utf-8") as inputs:
        candidate_virus_result_list = inputs.readlines()


    out_evalue_list = [float(i) for i in parameter_dic["out_e-value"]]

    out_evalue_list.sort()  # sort

    reads_filter_dir1 = reads_filter_dir + "/lower_" + str(out_evalue_list[0])
    my_mkdir(reads_filter_dir1)

    selected_file1 = reads_filter_dir1 + "/meets_the_conditions_"+ str(out_evalue_list[0]) +".txt"

    unselected_file1 = reads_filter_dir1 + "/not_meets_conditions.txt"


    seq_filter(candidate_virus_result_list, selected_file1, unselected_file1,
               parameter_dic["length_threshold"], parameter_dic["identity_threshold"],
               out_evalue_list[0])


    reads_diamond_class(hit_viral_nr_reads_path,
                        selected_file1,
                        refer_spiece_path,
                        reads_filter_dir1)

    print(">>> " + "1st e-value(" + str(out_evalue_list[0]) + ") filtering of reads: completed!",
          time.strftime("%Y.%m.%d %H:%M:%S ", time.localtime(time.time())))

    print("\n")

    # 2nd e-value filtering of reads
    with open(unselected_file1, "r", encoding="utf-8") as inputs:
        result_lists_2 = inputs.readlines()

    reads_filter_dir2 = reads_filter_dir + "/" + str(out_evalue_list[0]) + "_" + str(out_evalue_list[1])
    my_mkdir(reads_filter_dir2)

    selected_file2 = reads_filter_dir2 + "/meets_the_conditions_"+ str(out_evalue_list[1]) +".txt"

    unselected_file2 = reads_filter_dir2 + "/not_meets_conditions.txt"

    seq_filter(result_lists_2, selected_file2, unselected_file2,
               parameter_dic["length_threshold"], parameter_dic["identity_threshold"],
               out_evalue_list[1])

    reads_diamond_class(hit_viral_nr_reads_path,
                        selected_file2,
                        refer_spiece_path,
                        reads_filter_dir2)

    print(">>> " + "2nd e-value(" + str(out_evalue_list[1]) + ") filtering of reads: completed!",
          time.strftime("%Y.%m.%d %H:%M:%S ", time.localtime(time.time())))

    print("\n")

    ## 3rd e-value filtering of reads

    with open(unselected_file2, "r", encoding="utf-8") as inputs:
        result_lists_3 = inputs.readlines()

    reads_filter_dir3 = reads_filter_dir + "/" + str(out_evalue_list[1]) + "_" + str(out_evalue_list[2])
    my_mkdir(reads_filter_dir3)

    selected_file3 = reads_filter_dir3 + "/meets_the_conditions_"+ str(out_evalue_list[2]) +".txt"

    unselected_file3 = reads_filter_dir3 + "/not_meets_conditions.txt"

    seq_filter(result_lists_3, selected_file3, unselected_file3,
               parameter_dic["length_threshold"], parameter_dic["identity_threshold"],
               out_evalue_list[2])

    reads_diamond_class(hit_viral_nr_reads_path,
                        selected_file3,
                        refer_spiece_path,
                        reads_filter_dir3)

    print(">>> " + "3rd e-value(" + str(out_evalue_list[2]) + ") filtering of reads: completed",
          time.strftime("%Y.%m.%d %H:%M:%S ", time.localtime(time.time())))

    print("\n")



    return


def sub_run2(parameter_dic,xml_dic,r1_no_plasmid_fas,r2_no_plasmid_fas):
    """
    the sub-pipeline 2 of metav
    """

    out_dir = parameter_dic["outdir"] + "/contigs_blast"

    my_mkdir(out_dir)

    print(">>> " + "running the sub-pipeline 2..." + "\n")

    megahit_out_dir = out_dir + "/4_megahit_out"

    run_thread = parameter_dic["thread"]

    megahit_command = ("megahit "
                       + " ".join(xml_dic["megahit"])
                       + " --num-cpu-threads " + run_thread
                       + " -1 " + r1_no_plasmid_fas
                       + " -2 " + r2_no_plasmid_fas
                       + " -o " + megahit_out_dir)

    # final.contigs.fa in megahit_out_dir

    print(megahit_command)
    runprocess(megahit_command)

    # run contigs diamond

    print(">>> " + "contigs blastx to viral nr database..." + "\n")

    orgin_contig_out_seq = megahit_out_dir + "/final.contigs.fa"

    contig_out_seq = megahit_out_dir + "/final_reformat.contigs.fa"

    reformat_megahit_headers(orgin_contig_out_seq,contig_out_seq)  # 改变序列名称的格式


    refer_spiece_path = " ".join(xml_dic["viral_taxonomy"]).strip()

    viral_nr_path = " ".join(xml_dic["viral_nr"]).strip()

    hit_viral_nr_outdir = out_dir + "/5_hit_viral_nr"
    
    my_mkdir(hit_viral_nr_outdir)

    contig_hit_viral_nr_results = hit_viral_nr_outdir + "/contig_hit_viral_nr_result.txt"

    contig_viral_nr_diamond_commond = ("diamond blastx "
                                       + " ".join(xml_dic["diamond_viral_nr"])
                                       + " -q " + contig_out_seq
                                       + " --db " + viral_nr_path
                                       + " -o " + contig_hit_viral_nr_results
                                       + " --max-target-seqs 1 "
                                       + " -p " + parameter_dic["thread"]
                                       + " --outfmt 6 qseqid sseqid stitle bitscore pident nident evalue gaps length qstart qend sstart send")


    print(contig_viral_nr_diamond_commond)
    runprocess(contig_viral_nr_diamond_commond)

    print(">>> " + "contigs blastx to viral nr database: completed!",
          time.strftime("%Y.%m.%d %H:%M:%S ", time.localtime(time.time())))

    print("\n")

    # 提取命中病毒nr库的contig

    all_contig_dic = read_fasta_dic(contig_out_seq)

    hit_viral_nr_contig_path = hit_viral_nr_outdir + "/" + "hit_viral_nr.fasta"

    hit_viral_nr_contig = open(hit_viral_nr_contig_path, "w")

    with open(contig_hit_viral_nr_results, "r", encoding="utf-8") as inputs:

        for line in inputs:
            contig_name = line.split("\t")[0]

            hit_viral_nr_contig.write(">" + contig_name + "\n" + all_contig_dic[contig_name] + "\n")

    hit_viral_nr_contig.close()
   
    # 过滤NR库

    hit_nr_outdir = out_dir + "/6_hit_nr"

    my_mkdir(hit_nr_outdir)

    nr_path = " ".join(xml_dic["nr_taxid"]).strip()

    hit_nr_result = hit_nr_outdir + "/" + "hit_nr.txt"

    print(">>> " + "contigs blastx to nr database..." + "\n")

    diamond_nr_commond = ("diamond blastx "
                          + " ".join(xml_dic["diamond_nr"])
                          + " -q " + hit_viral_nr_contig_path
                          + " --db " + nr_path
                          + " --max-target-seqs 1"
                          + " -p " + parameter_dic["thread"]
                          + " -o " + hit_nr_result
                          + " --outfmt 6 qseqid sseqid stitle staxids bitscore pident nident evalue gaps length qstart qend sstart send"
                          )  # don't change --outfmt

    print(diamond_nr_commond)

    runprocess(diamond_nr_commond)

    print(">>> " + "contigs blastx to nr database: completed!",
          time.strftime("%Y.%m.%d %H:%M:%S ", time.localtime(time.time())))

    print("\n")

    # 过滤hit_nr_result结果
    # 保留命中到病毒的（E< 0.1）,剔除命中到非病毒的（e < 1e-5）

    rf_evalue_list = [float(i) for i in parameter_dic["nr_e-value"]]

    # print(rf_evalue_list)

    nr_taxid_viruses = " ".join(xml_dic["nr_taxid_viruses"]).strip()

    virus_list, no_virus_list = nr_filter_viruses(hit_nr_result,
                                                  nr_taxid_viruses,
                                                  hit_nr_outdir,
                                                  rf_evalue_list)

    # 从先前病毒NR库中提取经过NR库验证的输出

    nr_hit_virus_dic = {}

    with open(contig_hit_viral_nr_results, "r", encoding="utf-8") as inputs:

        for line in inputs:
            if line.strip():
                key = line.split("\t")[0]
                nr_hit_virus_dic[key] = line.strip()

    candidate_virus_result = hit_nr_outdir + "/" + "candidate_viral_contigs.txt"

    with open(candidate_virus_result, "w", encoding="utf-8") as outfile:
        for each_virus in virus_list:
            qseqid = each_virus[0]

            outfile.write(nr_hit_virus_dic[qseqid] + "\n")


    # filter the results from dimond

    contig_filter_dir = out_dir + r"/7_finally_result"

    my_mkdir(contig_filter_dir)


    # 1st e-value filtering of contigs

    with open(candidate_virus_result, "r", encoding="utf-8") as inputs:
        candidate_virus_result_list = inputs.readlines()

    out_evalue_list = [float(i) for i in parameter_dic["out_e-value"]]

    out_evalue_list.sort()  # sort

    contig_filter_dir1 = contig_filter_dir + "/lower_" + str(out_evalue_list[0])

    my_mkdir(contig_filter_dir1)

    selected_file1 = contig_filter_dir1 + "/meets_the_conditions_"+ str(out_evalue_list[0]) +".txt"

    unselected_file1 = contig_filter_dir1 + "/not_meets_conditions.txt"



    seq_filter(candidate_virus_result_list,
               selected_file1,
               unselected_file1,
               parameter_dic["length_threshold"], parameter_dic["identity_threshold"], out_evalue_list[0])


    contig_diamond_class(hit_viral_nr_contig_path,
                         selected_file1,
                         refer_spiece_path,
                         contig_filter_dir1)

    print(">>> " + "1st e-value(" + str(out_evalue_list[0]) + ") filtering of contigs: completed!",
          time.strftime("%Y.%m.%d %H:%M:%S ", time.localtime(time.time())))

    print("\n")


    # 2nd e-value filtering of contigs
    with open(unselected_file1, "r", encoding="utf-8") as inputs:
        result_lists_2 = inputs.readlines()

    contig_filter_dir2 = contig_filter_dir + "/" + str(out_evalue_list[0]) + "_" + str(out_evalue_list[1])

    my_mkdir(contig_filter_dir2)

    selected_file2 = contig_filter_dir2 + "/meets_the_conditions_"+ str(out_evalue_list[1]) +".txt"

    unselected_file2 = contig_filter_dir2 + "/not_meets_conditions.txt"

    seq_filter(result_lists_2,
               selected_file2,
               unselected_file2,
               parameter_dic["length_threshold"], parameter_dic["identity_threshold"],
               out_evalue_list[1])

    contig_diamond_class(hit_viral_nr_contig_path,
                         selected_file2,
                         refer_spiece_path,
                         contig_filter_dir2)

    print(">>> " + "2nd e-value(" + str(out_evalue_list[1]) + ") filtering of contigs: completed!",
          time.strftime("%Y.%m.%d %H:%M:%S ", time.localtime(time.time())))

    print("\n")


    # 3rd e-value filtering of contigs

    with open(unselected_file2, "r", encoding="utf-8") as inputs:
        result_lists_3 = inputs.readlines()

    contig_filter_dir3 = contig_filter_dir + "/" + str(out_evalue_list[1]) + "_" + str(out_evalue_list[2])

    my_mkdir(contig_filter_dir3)

    selected_file3 = contig_filter_dir3 + "/meets_the_conditions_"+ str(out_evalue_list[2]) +".txt"

    unselected_file3 = contig_filter_dir3 + "/not_meets_conditions.txt"

    seq_filter(result_lists_3, selected_file3, unselected_file3,
               parameter_dic["length_threshold"], parameter_dic["identity_threshold"],
               out_evalue_list[2])


    contig_diamond_class(hit_viral_nr_contig_path,
                         selected_file3,
                         refer_spiece_path,
                         contig_filter_dir3)

    print(">>> " + "3rd e-value(" + str(out_evalue_list[2]) + ") filtering of contigs: completed!",
          time.strftime("%Y.%m.%d %H:%M:%S ", time.localtime(time.time())))

    print("\n")

    return

