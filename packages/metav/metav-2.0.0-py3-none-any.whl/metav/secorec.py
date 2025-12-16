# -*- coding: utf-8 -*-

"""
Author: Zhou Zhi-Jian
Email: zjzhou@hnu.edu.cn
Time: 2023/12/21 13:45

"""
import sys
import os
import subprocess
import time

from my_func import (my_mkdir,seq_filter,fq_to_fas,
                     reads_diamond_class,reformat_megahit_headers,
                     contig_diamond_class,read_fasta_dic,
                     get_name,nr_filter_viruses)



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


def clean_reads (parameter_dic,xml_dic,out_dir):
    """
    clean the input reads
    :param parameter_dic:
    :param xml_dic:
    :param out_dir:
    :return:
    """

    clean_data_path = ""

    run_thread = parameter_dic["thread"]

    host_index_path = " ".join(xml_dic["hostdb"]).strip()

    # remove contamination from adapter primer

    trimmed_outdir = out_dir + "/1_reads_QC"

    my_mkdir(trimmed_outdir)

    trimmed_command_list = []

    trimmed_command_list.append("trimmomatic")  # path of trimmomatic exe

    trimmed_command_list.append("SE "
                                + "-" + parameter_dic["qualities"] + " "
                                + "-threads " + run_thread + " "
                                + parameter_dic["unpaired"] + " "
                                + trimmed_outdir + "/trimmed_out.fq")

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

        bowtie_command_list.append("-p " + run_thread + " "
                                   + "-x " + host_index_path + " "
                                   + "-U " + trimmed_outdir + "/trimmed_out.fq" + " "
                                   + "--" + parameter_dic["qualities"] + " "
                                   + "-S " +  bowtie_outdir + "/out.sam" + " "
                                   + "--un " + bowtie_outdir + "/unmatch.fq")

        bowtie_command = " ".join(bowtie_command_list)

        print("remove contamination from the host: ",
              host_index_path + "\n")

        print(bowtie_command)

        runprocess(bowtie_command)


        clean_data_path = bowtie_outdir + "/unmatch.fq"

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
                                           + "-U " + input_data_dir + "/trimmed_out.fq" + " "
                                           + "--" + parameter_dic["qualities"] + " "
                                           + "-S " + sub_outdir + "/out.sam" + " "
                                           + "--un " + sub_outdir + "/unmatch.fq")

            else:

                input_data_dir = bowtie_outdir + "/host" + str(i) + "_out"

                bowtie_command_list.append(" -p " + run_thread
                                           + " -x " + host_path
                                           + " -U " + input_data_dir + "/unmatch.fq"
                                           + " --" + parameter_dic["qualities"]
                                           + " -S " + sub_outdir + "/out.sam"
                                           + " --un " + sub_outdir + "/unmatch.fq")

            bowtie_command = " ".join(bowtie_command_list)

            print(bowtie_command)

            runprocess(bowtie_command)

            clean_data_path = sub_outdir + "/unmatch.fq"

            sam_path = sub_outdir + "/out.sam"
            if os.path.exists(sam_path):
                os.remove(sam_path)


    print(">>> " + "clean host contamination: completed!",
          time.strftime("%Y.%m.%d %H:%M:%S ", time.localtime(time.time())))


    # 压缩上一步trimmed_outdir里的输出trimmed_out.fq
    trimme_out_path = trimmed_outdir + "/trimmed_out.fq"
    if os.path.exists(trimme_out_path):
        try:
            subprocess.run(['gzip', '-f', trimme_out_path], check=True)

        except subprocess.CalledProcessError:
            sys.exit(1)


    return  clean_data_path  # fq格式


def remove_plasmid(parameter_dic,xml_dic,input_fq):

    plasmid_hit_out_dir = parameter_dic["outdir"] + "/3_reads_noplasmid"

    my_mkdir(plasmid_hit_out_dir)

    plasmid_nr_path = " ".join(xml_dic["plasmid"]).strip()

    bowtie_plasmid_command=("bowtie2 " + " ".join(xml_dic["bowtie2_plasmid"]).strip()
                               + " -p " + parameter_dic["thread"]
                               + " -x " + plasmid_nr_path
                               + " -U " + input_fq
                               + " --" + parameter_dic["qualities"]
                               + " -S " + plasmid_hit_out_dir + "/out.sam"
                               + " --un " + plasmid_hit_out_dir + "/noplasmid.fq")

    runprocess(bowtie_plasmid_command)

    sam_path = plasmid_hit_out_dir + "/out.sam"
    if os.path.exists(sam_path):
        os.remove(sam_path)

    no_plasmid_fq = plasmid_hit_out_dir + "/noplasmid.fq"

    fq_file_name = get_name(parameter_dic["unpaired"])

    # fastq to fasta

    no_plasmid_fas = plasmid_hit_out_dir + "/" + fq_file_name + "_noplasmid.fasta"

    fq_to_fas(no_plasmid_fq, no_plasmid_fas)  # unmatch.fq to clean_data_fas


    print(">>> " + "clean plasmid contamination: completed!",
          time.strftime("%Y.%m.%d %H:%M:%S ", time.localtime(time.time())))

    print("\n")

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


    # 删除noplasmid.fq
    if os.path.exists(no_plasmid_fq):
        os.remove(no_plasmid_fq)


    return no_plasmid_fas


def sub_run1(parameter_dic,xml_dic,no_plasmid_fa):

    """
    the sub-pipeline 1 of metav
    :return:
    """

    print(">>> " + "running the sub-pipeline 1..." + "\n")

    out_dir = parameter_dic["outdir"] + "/reads_blast"

    refer_spiece_path = " ".join(xml_dic["viral_taxonomy"]).strip()

    viral_nr_path = " ".join(xml_dic["viral_nr"]).strip()

    run_thread = parameter_dic["thread"]

    # fq_file_name = get_name(parameter_dic["unpaired"])

    # run diamond

    print(">>> " + "reads blastx to viral nr database..." + "\n")

    hit_viral_nr_outdir = out_dir + "/4_hit_viral_nr"
    my_mkdir(hit_viral_nr_outdir)

    hit_virus_nr_result = hit_viral_nr_outdir + "/" +  "hit_viral_nr.txt"

    diamond_viral_nr_commond = ("diamond blastx "
                                 + " ".join(xml_dic["diamond_viral_nr"])
                                 + " -q " + no_plasmid_fa
                                 + " --db " + viral_nr_path
                                 + " --max-target-seqs 1"
                                 + " -p " + run_thread
                                 + " -o " + hit_virus_nr_result
                                 + " --outfmt 6 qseqid sseqid stitle bitscore pident nident evalue gaps length qstart qend sstart send") # don't change --outfmt


    print(diamond_viral_nr_commond)

    runprocess(diamond_viral_nr_commond)

    print(">>> " + "reads blastx to viral nr database: completed!",
          time.strftime("%Y.%m.%d %H:%M:%S ", time.localtime(time.time())))

    print("\n")

    # 提取命中病毒nr库的reads

    all_read_dic = read_fasta_dic(no_plasmid_fa)

    hit_viral_nr_reads_path = hit_viral_nr_outdir + "/" + "hit_viral_nr.fasta"

    hit_viral_nr_reads = open(hit_viral_nr_reads_path, "w")

    with open(hit_virus_nr_result, "r", encoding="utf-8") as inputs:

        for line in inputs:
            reads_name = line.split("\t")[0]

            hit_viral_nr_reads.write(">" + reads_name + "\n" + all_read_dic[reads_name] + "\n")




    # 过nr库

    hit_nr_outdir = out_dir + "/5_hit_nr"

    my_mkdir(hit_nr_outdir)

    nr_path = " ".join(xml_dic["nr_taxid"]).strip()

    hit_nr_result = hit_nr_outdir + "/" + "hit_nr.txt"

    print(">>> " + "reads blastx to nr database..." + "\n")

    diamond_nr_commond = ("diamond blastx "
                          + " ".join(xml_dic["diamond_nr"])
                          + " -q " + hit_viral_nr_reads_path
                          + " --db " + nr_path
                          + " --max-target-seqs 1"
                          + " -p " + run_thread
                          + " -o " + hit_nr_result
                          + " --outfmt 6 qseqid sseqid stitle staxids bitscore pident nident evalue gaps length qstart qend sstart send"
                          )    # don't change --outfmt

    print(diamond_nr_commond)

    runprocess(diamond_nr_commond)

    print(">>> " + "reads blastx to nr database: completed!",
          time.strftime("%Y.%m.%d %H:%M:%S ", time.localtime(time.time())))


    # 过滤hit_nr_result结果
    # 保留命中到病毒的，剔除命中到非病毒的
    rf_evalue_list = [float(i) for i in parameter_dic["nr_e-value"]]

    # print(rf_evalue_list)

    nr_taxid_viruses = " ".join(xml_dic["nr_taxid_viruses"]).strip()

    virus_list, no_virus_list = nr_filter_viruses(hit_nr_result,
                                                  nr_taxid_viruses,
                                                  hit_nr_outdir,
                                                  rf_evalue_list)

    # 从先前病毒nr库中提取经过nr库验证的序列
    nr_hit_virus_dic = {}

    with open(hit_virus_nr_result, "r", encoding="utf-8") as inputs:
        for line in inputs:
            if line.strip():
                key = line.split("\t")[0]
                nr_hit_virus_dic[key] = line.strip()

    candidate_virus_result = hit_nr_outdir + "/" + "candidate_virus_result.txt"

    with open(candidate_virus_result, "w", encoding="utf-8") as outfile:
        for each_virus in virus_list:
            qseqid = each_virus[0]

            outfile.write(nr_hit_virus_dic[qseqid] + "\n")


    # filter the results from dimond

    reads_filter_dir = out_dir + r"/6_finally_result"
    my_mkdir(reads_filter_dir)

    # 1st e-Value filtering of reads

    with open(candidate_virus_result, "r", encoding="utf-8") as inputs:
        candidate_virus_lists = inputs.readlines()

    out_evalue_list = [float(i) for i in parameter_dic["out_e-value"]]

    out_evalue_list.sort()  # sort


    reads_filter_dir1 = reads_filter_dir + "/lower_" + str(out_evalue_list[0])
    my_mkdir(reads_filter_dir1)

    selected_file1 = reads_filter_dir1 + "/meets_the_conditions_"+ str(out_evalue_list[0]) +".txt"

    unselected_file1 = reads_filter_dir1 + "/not_meets_conditions.txt"


    seq_filter(candidate_virus_lists, selected_file1, unselected_file1,
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
        diamond_result_lists_2 = inputs.readlines()

    reads_filter_dir2 = reads_filter_dir + "/" + str(out_evalue_list[0]) + "_" + str(out_evalue_list[1])
    my_mkdir(reads_filter_dir2)

    selected_file2 = reads_filter_dir2 + "/meets_the_conditions_"+ str(out_evalue_list[1]) +".txt"

    unselected_file2 = reads_filter_dir2 + "/not_meets_conditions.txt"

    seq_filter(diamond_result_lists_2, selected_file2, unselected_file2,
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
        diamond_result_lists_3 = inputs.readlines()

    reads_filter_dir3 = reads_filter_dir + "/" + str(out_evalue_list[1]) + "_" + str(out_evalue_list[2])
    my_mkdir(reads_filter_dir3)

    selected_file3 = reads_filter_dir3 + "/meets_the_conditions_"+ str(out_evalue_list[2]) +".txt"

    unselected_file3 = reads_filter_dir3 + "/not_meets_conditions.txt"

    seq_filter(diamond_result_lists_3, selected_file3, unselected_file3,
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


def sub_run2(parameter_dic,xml_dic,no_plasmid_fa):

    """
    the sub-pipeline 2 of metav
    """

    print(">>> " + "running the sub-pipeline 2..." + "\n")

    out_dir = parameter_dic["outdir"] + "/contigs_blast"
    my_mkdir(out_dir)

    megahit_out_dir = out_dir + "/4_megahit_out"


    run_thread = parameter_dic["thread"]

    megahit_command = ("megahit "
                       + " ".join(xml_dic["megahit"])
                       + " --num-cpu-threads " + run_thread
                       + " -r " + no_plasmid_fa
                       + " -o " + megahit_out_dir)

    # final.contigs.fa in megahit_out_dir

    print(megahit_command)

    runprocess(megahit_command)

    # run contigs diamond

    print(">>> " + "contigs blastx to viral nr database..." + "\n")

    orgin_contig_out_seq = megahit_out_dir + "/final.contigs.fa"

    contig_out_seq = megahit_out_dir + "/final_reformat.contigs.fa"

    reformat_megahit_headers(orgin_contig_out_seq, contig_out_seq)  # 改变序列名称格式

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
                                       + " --max-target-seqs 1"
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

    # 过滤nr库
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

    # 过滤hit_nr_result结果
    # 保留命中到病毒的,剔除命中到非病毒的
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

    selected_file1 = contig_filter_dir1 + "/meets_the_conditions_" + str(out_evalue_list[0]) + ".txt"

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

    selected_file2 = contig_filter_dir2 + "/meets_the_conditions_" + str(out_evalue_list[1]) + ".txt"

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

    selected_file3 = contig_filter_dir3 + "/meets_the_conditions_" + str(out_evalue_list[2]) + ".txt"

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
