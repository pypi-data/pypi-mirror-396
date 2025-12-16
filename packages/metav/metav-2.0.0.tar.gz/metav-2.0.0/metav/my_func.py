# -*- coding: utf-8 -*-

"""
Author: Zhou Zhi-Jian
Time: 2023/12/16 ‏‎12:54

"""

import os
import re

import xml.etree.ElementTree as ET


def my_mkdir(path):
    """
    create a directory
    :param path: Specify a path of directory
    :return: None
    """

    path = path.strip()
    path = path.rstrip("\\")

    is_exists = os.path.exists(path)

    if not is_exists:

        os.makedirs(path)

    else:
        pass

    return



def parse_xml(xml_path):
    """
    read xml file
    :param xml_path: the path of xml file
    :return: a dictionary
    """

    tree = ET.parse(xml_path)

    root = tree.getroot()

    para_dic = {}

    for app in root:
        name = app.get('name')

        app_para_list = [i.text.replace("\n", "").replace("\t"," ").strip() for i in app]

        para_dic[name] = app_para_list

    return para_dic



def get_name(file_path):

    file_path = file_path.replace("\\", "/")

    inputfile_name = file_path.split("/")[-1]

    out_prefix = inputfile_name.replace(".", "_")

    return out_prefix


def read_fasta_dic(input_file_path):
    """
     read *.fasta file
    :param input_file_path: the path of *.fasta file
    :return: a dictionary that stores sequences
    """

    seq_dic = {}

    seq_name = ""

    with open(input_file_path, "r", encoding="utf-8") as gen_file:
        for line in gen_file:
            line = line.strip()

            if line.startswith(">"):
                seq_name = line.split(" ")[0].replace(">","")
                """
                The return result of diamond is only the name of the query 
                sequence before the space, which is processed here in order 
                to match the original reads later
                """


                seq_dic[seq_name] = []

            elif line != "":
                seq_dic[seq_name].append(line.upper())

        for key, value in seq_dic.items():
            seq_dic[key] = "".join(value)

    return seq_dic


def fast_read_fasta(input_file_path):
    seq_tab = []
    seq_dic = {}
    seq_name_list = []
    seq_name = ""

    with open(input_file_path, "r", encoding="utf-8") as gen_file:
        for line in gen_file:
            line = line.strip()
            if line.startswith(">"):
                seq_name = line.strip(">")
                seq_name_list.append(seq_name)
                seq_dic[seq_name] = []
            elif line != "":
                seq_dic[seq_name].append(line)

        for each_seqname in seq_name_list:
            seq = "".join(seq_dic[each_seqname]).upper()
            seq_tab.append([each_seqname, seq])

    return seq_tab


def reformat_megahit_headers(input_fasta, output_fasta):

    with open(input_fasta, "r") as infile, open(output_fasta, "w") as outfile:
        for line in infile:
            line = line.strip()

            if line.startswith(">"):
                header = line[1:]

                new_header = header.replace("flag=", "F")
                new_header = new_header.replace("multi=", "M")
                new_header = new_header.replace("len=", "L")
                new_header = new_header.replace(" ", "_")
                outfile.write(f">{new_header}\n")
            else:
                outfile.write(f"{line}\n")

    return output_fasta


def single_find(re_pattern, context):
    """
    the regular expression matching
    :param re_pattern: match pattern
    :param context: The text used for matching
    :return: match results
    """

    results = "Unknow"

    find_list = re_pattern.findall(context)  # return a match list

    if find_list == []:
        results = results

    else:

        results = find_list[0].strip()  # the first one in the match list

    return results


def fq_to_fas_re1(fq_file_path, out_fas_path):
    """
    *.fastq to *.fasta
    :param fq_file_path: the input path of *.fastq file
    :param out_fas_path：the output path of *.fasta file
    :return:
    """

    file_fq = open(fq_file_path, "r", encoding="utf-8")

    out_fas = open(out_fas_path, "w", encoding="utf-8")

    fq_contein = file_fq.readlines()

    # print(type(fq_contein))

    for n in range(len(fq_contein)):
        line = fq_contein[n].strip()
        if line.startswith("@") and n % 4 == 0:
            if line.find(" ") != -1:
                end_str = line.split(" ")[-1]

                line = line.replace(" " + end_str, "_1")

            else:
                line = line + "_1"

            out_fas.write(line.replace("@", ">") + "\n" + fq_contein[n + 1])

    file_fq.close()
    out_fas.close()

    return


def fq_to_fas_re2(fq_file_path, out_fas_path):
    """
    *.fastq to *.fasta
    :param fq_file_path: the input path of *.fastq file
    :param out_fas_path：the output path of *.fasta file
    :return:
    """

    file_fq = open(fq_file_path, "r", encoding="utf-8")

    out_fas = open(out_fas_path, "w", encoding="utf-8")

    fq_contein = file_fq.readlines()

    # print(type(fq_contein))

    for n in range(len(fq_contein)):
        line = fq_contein[n].strip()
        if line.startswith("@") and n % 4 == 0:
            if line.find(" ") != -1:
                end_str = line.split(" ")[-1]

                line = line.replace(" " + end_str, "_2")

            else:
                line = line + "_2"

            out_fas.write(line.replace("@", ">") + "\n" + fq_contein[n + 1])

    file_fq.close()
    out_fas.close()

    return



def fq_to_fas(fq_file_path,out_fas_path):
    """
    *.fastq to *.fasta
    :param fq_file_path: the input path of *.fastq file
    :param out_fas_path：the output path of *.fasta file
    :return:
    """

    file_fq = open(fq_file_path, "r",encoding="utf-8")

    out_fas = open(out_fas_path, "w",encoding="utf-8")

    fq_contein = file_fq.readlines()

    # print(type(fq_contein))

    for n in range(len(fq_contein)):
        line = fq_contein[n].strip()
        if line.startswith("@") and n % 4 == 0:
            out_fas.write(line.replace("@",">") + "\n" + fq_contein[n+1])

    file_fq.close()
    out_fas.close()

    return


def nr_filter_viruses(hit_nr_result,viral_taxid,out_dir,rf_evalue_list):

    viral_taxid_set = set()

    candidate_list = []

    delete_list = []

    with open(viral_taxid,"r", encoding="utf-8") as inputs:
        for line in inputs:
            viral_taxid_set.add(line.strip())


    with open(hit_nr_result,"r", encoding="utf-8") as inputs:

        for line in inputs:
            line_list = line.strip().split("\t")

            qseqid = line_list[0].strip()
            sseqid = line_list[1].strip()
            staxids = line_list[3].strip().split(";")[0].strip()  # 分类
            evalue = float(line_list[7].strip())

            if  staxids in viral_taxid_set:  # 如果是命中到病毒
                if evalue < rf_evalue_list[0]:  # 宽松条件确认
                    candidate_list.append([qseqid,sseqid,staxids,str(evalue)])

                else:
                    delete_list.append([qseqid,sseqid,staxids,str(evalue)])

            else:  # 如果不是命中到病毒，严格条件做剔除
                if evalue <= rf_evalue_list[1]:
                   delete_list.append([qseqid, sseqid, staxids, str(evalue)])

                else:
                   candidate_list.append([qseqid,sseqid,staxids,str(evalue)])

    with open(out_dir + "/viral_candidate.txt","w") as out_file:

        out_file.write("\t".join(["qseqid","sseqid","staxids","evalue"]) + "\n")

        for each in candidate_list:
            out_file.write("\t".join(each) + "\n")

    with open(out_dir + "/non-viral_delete.txt","w") as out_file:
        out_file.write("\t".join(["qseqid","sseqid","staxids","evalue"]) + "\n")

        for each in delete_list:
            out_file.write("\t".join(each) + "\n")


    return candidate_list,delete_list


def seq_filter(diamond_result_list,
               selected_path,
               unselected_path,
               length,
               pident,
               evalue):
    """
    the filters (filter matching reads)
    :param diamond_result_list: the file path of results of diamond
    :param selected_path: sequences that meet the criteria and are selected
    :param unselected_path: sequences that do not meet the criteria are not selected
    :param length: the threshold for matching length (measured in the number of amino acids), sequences above this threshold are selected.
    :param pident: the threshold of sequence identity in the match region (above this threshold)
    :param evalue: the threshold of the e-value (below this threshold)
    :return: None
    """

    title = ("qseqid" + "\t" + "sseqid" + "\t" + "stitle" + "\t" + "bitscore"
            + "\t" + "pident" + "\t" + "nident" + "\t" + "evalue" + "\t"
            + "gaps" + "\t" + "length" + "\t" + "qstart" + "\t" + "qend"
            + "\t" + "sstart" + "\t" + "send")

    out_file = open(selected_path, "w",encoding="utf-8")

    out_other = open(unselected_path, "w",encoding="utf-8")

    out_file.write(title + "\n")
    out_other.write(title + "\n")

    for each_line in diamond_result_list:
        if not each_line.startswith("qseqid"):

            line_list = each_line.strip().split("\t")

            """
            Note: the output format of diamond set by me, column 5 is pident, 
            column 7 is evalue, and column 9 is length
            """


            if (float(line_list[4]) >= float(pident) and
                    float(line_list[6]) <= float(evalue) and
                    float(line_list[8]) >= float(length)):

                out_file.write(each_line.strip() + "\n")

            else:
                out_other.write(each_line.strip() + "\n")

    out_file.close()
    out_other.close()

    return


def reads_diamond_class(reads_path,
                  filter_result_path,
                  refer_spiece_path,
                  out_dir):
    """
    hit reads classifier
    :param reads_path: the path of reads
    :param filter_result_path: the path of the filter file of diamond
    :param refer_spiece_path: the file-path of taxonomic information of viruses
    :param out_dir: the output directory
    :return: None
    """

    qst_list = []

    with open(filter_result_path, "r",encoding="utf-8") as filter_result_file:
        filter_result_list = filter_result_file.read().strip().split("\n")

    for n in range(1, len(filter_result_list)):
        line = filter_result_list[n]

        qseqid = line.split("\t")[0]  # the ID of reads (query sequence)

        sseqid = line.split("\t")[1]  # the subject ID (from protein database)

        stitle = line.split("\t")[2].replace(sseqid, "").strip()

        qst = (qseqid + "\t" + sseqid + "\t" + stitle)

        qst_list.append(qst)

    out_dir = out_dir + "/" + "hit_summary"

    my_mkdir(out_dir)

    with open(refer_spiece_path, "r", encoding="utf-8") as refer_spiece_file:

        refer_spiece_lsit = refer_spiece_file.readlines()

    qst_AlesDae_path = out_dir + r"/hit_reads_taxonomy_information.txt"

    qst_AlesDae = open(qst_AlesDae_path, "w", encoding="utf-8")

    taxonomy_dic = {}

    for every_record in refer_spiece_lsit:
        every_record = every_record.strip()

        every_record_list = every_record.split("\t")

        protein_id = every_record_list[0]

        ales_match = every_record_list[1]

        dae_match = every_record_list[2]

        organism_match = every_record_list[-1]

        taxonomy_dic[protein_id] = [ales_match, dae_match, organism_match]

    for each_qsv in qst_list:
        each_qsv = each_qsv.strip()

        qseqid, sseqid, stitle = each_qsv.split("\t")

        qst_AlesDae.write(each_qsv + "\t"
                          + "\t".join(taxonomy_dic[sseqid]) + "\n")

    qst_AlesDae.close()


    # count the number of reads

    with open(qst_AlesDae_path, "r",encoding="utf-8") as qst_AlesDae_input:
        qst_AlesDae_list = qst_AlesDae_input.readlines()

    virus_ale_dic = {}  # dictionary that stores hit order

    virus_dae_dic = {}  # dictionary that stores hit family

    virus_strain_dic = {}  # dictionary that stores hit strain


    for each_line in qst_AlesDae_list:

        each_line = each_line.strip()

        each_line_list = each_line.split("\t")

        virus_ale_name = each_line_list[-3].strip()

        virus_dae_name = each_line_list[-2].strip()

        virus_name = each_line_list[-1].strip()


        if virus_name not in virus_strain_dic:
            virus_strain_dic[virus_name] = 1
        else:
            virus_strain_dic[virus_name] += 1


        if virus_ale_name not in virus_ale_dic:
            virus_ale_dic[virus_ale_name] = 1
        else:
            virus_ale_dic[virus_ale_name] += 1


        if virus_dae_name not in virus_dae_dic:
            virus_dae_dic[virus_dae_name] = 1
        else:
            virus_dae_dic[virus_dae_name] += 1


    # output
    # reads count based on hit strain
    with open(out_dir + r"/reads_hit_strain_count.csv", "w",encoding="utf-8") as virus_strain_out:
        virus_strain_out.write("hit strain" + "," + "reads count" + "\n")
        for key in list(virus_strain_dic.keys()):
            virus_strain_out.write(key + "," + str(virus_strain_dic[key])
                                   + "\n")
    
    # reads count based on hit order
    with open(out_dir + r"/reads_hit_order_count.csv", "w",encoding="utf-8") as virus_ales_out:
        virus_ales_out.write("hit order" + "," + "reads count" + "\n")
        for key in list(virus_ale_dic.keys()):
            virus_ales_out.write(key + "," + str(virus_ale_dic[key]) + "\n")

    # reads count based on hit family
    with open(out_dir + r"/reads_hit_family_count.csv", "w",encoding="utf-8") as virus_dae_out:
        virus_dae_out.write("hit family" + "," + "reads count" + "\n")
        for key in list(virus_dae_dic.keys()):
            virus_dae_out.write(key + "," + str(virus_dae_dic[key]) + "\n")

    # get the original sequence
    reads_dic = {}

    with open(reads_path, "r",encoding="utf-8") as reads_file:
        reads_list = reads_file.readlines()


    for n in range(len(reads_list)):
        each_read = reads_list[n].strip().split(" ")[0]
        """
        The return result of diamond is only the name of the query sequence 
        before the space, which is processed here in order to match the original 
        reads later
        """

        if each_read.startswith(">"):
            reads_dic[each_read.replace(">", "")] = reads_list[n + 1].strip()

    with open(qst_AlesDae_path, "r",encoding="utf-8") as file_input:
        qst_AlesDae_list = file_input.readlines()

    for each_qsv_AlesDae in qst_AlesDae_list:
        qseqid, sseqid, stitle, ales, dae,organism = each_qsv_AlesDae.strip().split("\t")

        virus_name = (stitle.split("[")[-1]).replace("]", "")
        virus_name = virus_name.replace("/", "_").replace(":", " ")


        ales_dae_dir = out_dir + "/hit_reads_seq/" + ales + "/" + dae

        my_mkdir(ales_dae_dir)


        virus_ales_dae = open(ales_dae_dir + "/hit_" + virus_name + ".fasta", "a",
                              encoding="utf-8")

        virus_ales_dae.write(">hit_" + virus_name.replace(" ", "_") + "_" + sseqid
                             + "_" + qseqid + "\n" + reads_dic[qseqid] + "\n")

    return



def contig_diamond_class(contig_path,
                         filter_result_path,
                         refer_spiece_path,
                         out_dir):
    """
    hit contigs classifier
    :param contig_path: the path of hit contigs
    :param filter_result_path: the path of the filter file of diamond
    :param refer_spiece_path: the file-path of taxonomic information of viruses
    :param out_dir: the output directory
    :return: None
    """

    qst_list = []

    with open(filter_result_path, "r", encoding="utf-8") as filter_result_file:
        filter_result_list = filter_result_file.read().strip().split("\n")

    for n in range(1, len(filter_result_list)):
        line = filter_result_list[n]

        qseqid = line.split("\t")[0]

        sseqid = line.split("\t")[1]


        stitle = line.split("\t")[2].replace(sseqid, "").strip()


        qst = (qseqid + "\t" + sseqid + "\t" + stitle)

        qst_list.append(qst)

    out_dir = out_dir + "/" + "hit_summary"

    my_mkdir(out_dir)

    with open(refer_spiece_path, "r", encoding="utf-8") as refer_spiece_file:

        refer_spiece_lsit = refer_spiece_file.readlines()

    qst_AlesDae_path = out_dir + r"/hit_contigs_taxonomy_information.txt"

    qst_AlesDae = open(qst_AlesDae_path, "w", encoding="utf-8")

    taxonomy_dic = {}

    for every_record in refer_spiece_lsit:
        every_record = every_record.strip()

        every_record_list = every_record.split("\t")

        protein_id = every_record_list[0]

        ales_match = every_record_list[1]

        dae_match = every_record_list[2]

        organism_match = every_record_list[-1]

        taxonomy_dic[protein_id] = [ales_match, dae_match,organism_match]


    for each_qsv in qst_list:
        each_qsv = each_qsv.strip()

        qseqid, sseqid, stitle = each_qsv.split("\t")

        qst_AlesDae.write(each_qsv + "\t"
                          + "\t".join(taxonomy_dic[sseqid]) + "\n")


    qst_AlesDae.close()


   # open "reads_taxonomy_information.txt"
    with open(qst_AlesDae_path, "r", encoding="utf-8") as qst_AlesDae_input:
        qst_AlesDae_list = qst_AlesDae_input.readlines()

    virus_ale_dic = {}

    virus_dae_dic = {}

    virus_strain_dic = {}


    for each_line in qst_AlesDae_list:

        each_line = each_line.strip()

        each_line_list = each_line.split("\t")

        virus_ale_name = each_line_list[-3].strip()

        virus_dae_name = each_line_list[-2].strip()

        virus_name = each_line_list[-1].strip()


        # contig count based on hit strains
        if virus_name not in virus_strain_dic:
            virus_strain_dic[virus_name] = 1
        else:
            virus_strain_dic[virus_name] += 1

        # contig count based on hit order
        if virus_ale_name not in virus_ale_dic:
            virus_ale_dic[virus_ale_name] = 1
        else:
            virus_ale_dic[virus_ale_name] += 1

        # contig count based on hit family
        if virus_dae_name not in virus_dae_dic:
            virus_dae_dic[virus_dae_name] = 1
        else:
            virus_dae_dic[virus_dae_name] += 1


    with open(out_dir + r"/contigs_hit_strain_count.csv", "w",
              encoding="utf-8") as virus_strain_out:
        virus_strain_out.write("hit strain" + "," + "contig count" + "\n")
        for key in list(virus_strain_dic.keys()):
            virus_strain_out.write(key + "," + str(virus_strain_dic[key])
                                   + "\n")

    with open(out_dir + r"/contigs_hit_order_count.csv", "w",
              encoding="utf-8") as virus_ales_out:
        virus_ales_out.write("hit order" + "," + "contig count" + "\n")
        for key in list(virus_ale_dic.keys()):
            virus_ales_out.write(key + "," + str(virus_ale_dic[key]) + "\n")

    with open(out_dir + r"/contigs_hit_family_count.csv", "w",
              encoding="utf-8") as virus_dae_out:
        virus_dae_out.write("hit family" + "," + "contig count" + "\n")
        for key in list(virus_dae_dic.keys()):
            virus_dae_out.write(key + "," + str(virus_dae_dic[key]) + "\n")

    contig_dic = read_fasta_dic(contig_path)


    with open(qst_AlesDae_path, "r", encoding="utf-8") as file_input:
        qst_AlesDae_list = file_input.readlines()

    for each_qsv_AlesDae in qst_AlesDae_list:
        qseqid, sseqid, stitle, ales, dae,organism = each_qsv_AlesDae.strip().split("\t")

        virus_name = (stitle.split("[")[-1]).replace("]", "")
        virus_name = virus_name.replace("/", "_").replace(":", " ")

        ales_dae_dir = out_dir + "/hit_contigs_seq/" + ales + "/" + dae

        my_mkdir(ales_dae_dir)

        virus_ales_dae = open(ales_dae_dir + "/hit_" + virus_name + ".fasta", "a",
                              encoding="utf-8")

        virus_ales_dae.write(">hit_" + virus_name.replace(" ", "_") + "_" + sseqid
                             + "_" + qseqid + "\n" + contig_dic[qseqid] + "\n")


    return


