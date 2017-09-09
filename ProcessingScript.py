# Julie's Processing script for Shriver Lab genotype data
# Date 9.5.17

# WHAT THIS DOES #
# -Run IBD matrix through plink
# -Update family and individual IDs
# -Update maternal and paternal IDs
# -Update sex
# -Using 1000 Genomes as a reference (this part based off Perl script by W. Rayner, 2015, wrayner@well.ox.ac.uk
#   -Removes SNPs not in 1000 Genomes
#   -Removes all A/T G/C SNPs with MAF > 40% in the reference data set
#   -Removes all SNPs with an AF difference >0.2, between reference and dataset frequency file, frequency file is
#       expected to be a plink frequency file with the same number of SNPs as the bim file
#   -Removes duplicates that may be introduced with the position update
#   -Removes indels
# -Merges your data with 1000 Genomes
# -Runs ADMIXTURE with k = 3...9
# -Phases using SHAPEIT2

# REQUIREMENTS #
# You must have plink 1.9 in the same directory as your genotype files and this script, and it should be called 'plink'.

# Getting the needed modules.
import os

to_do = input('What would you like to do?\n'
              '1) Run an IBD analysis to identify relatives. All you need are plink bed/bim/fam files.\n'
              '2) Update FID or IID information. You need a file with the following information Old FID, Old IID, '
              'New FID, New IID.\n'
              '3) Update parental IDs. You need a file with FID, IID, Paternal IID, and Maternal IID.\n'
              '4) Update sex. You need a file with FID, IID, Sex (M = 1, F = 2, Unknown = 0)\n'
              '5) Remove SNPs that are not in 1000 Genomes Phase 3\n'
              '6) Nothing\n'
              'Please enter a number (i.e. 2): ')

if to_do == '1':

    # Identity-by-descent in Plink
    # This part of the script will prune for LD, calculate IBD, and exclude individuals who have IBD < 0.2
    # The IBD results will have .genome appended to your file name. I have also included a line to convert the IBD results
    #   from whitespace to tab delimited. This will have .tab.genome appended to your filename.

    # Important values of Pi-hat
    #   -First-degree relative = 0.5
    #   -Second-degree relative = 0.25
    #   -Third-degree relative = 0.125
    #   -Fourth-degree relative = 0.0625
    #   -Fifth-degree relative = 0.03125

    geno_name = input('Please enter the name of the genotype files (without bed/bim/fam extension: ')
    print("Your IBD results in a tab delimited file will have the name " + geno_name + ".tab.genome. You should use "
                                                                                       "this file to investigate your "
                                                                                       "relatives and possibly update "
                                                                                       "the FID and IIDs in your file.")
    os.system('plink --bfile ' + geno_name + ' --indep 50 5 2 --out ' + geno_name)
    os.system('plink --bfile ' + geno_name + ' --exclude ' + geno_name + '.prune.out --genome --min 0.2 --out ' + geno_name)
    os.system('sed -r "s/\s+/\t/g" ' + geno_name + '.genome > ' + geno_name + '.tab.genome')
        # Comment out this line if you prefer whitespace delimited files
    print("Analysis finished")
    # Now your job is to use the .tab.genome file to investigate relatives and possibly update FID/IID and parents.

elif to_do == '2':
    # File for updating FID should have four fields
    #  1) Old FID
    #  2) Old IID
    #  3) New FID
    #  4) New IID

    geno_name = input('Please enter the name of your genotype files (without bed/bim/fam extension): ')
    update_fid_filename = input('Please enter the name of your text file for updating FID or IID (with file extension): ')
    print("Your genotype files with the FID updated will have the name " + geno_name + "_FIDUpdated")
    os.system('plink --bfile ' + geno_name + ' --update-ids ' + update_fid_filename + ' --make-bed --out ' + geno_name +
            '_FIDUpdated')

elif to_do == '3':
    # File for updating parents should have four fields:
    #   1) FID
    #   2) IID
    #   3) New paternal IID
    #   4) New maternal IID

    geno_name = input('Please enter the name of your genotype files (without bed/bim/fam extension). Remember, if you '
                      'just updated FIDs, then your genotype name should have FIDUpdated at the end of it.: ')
    update_parents_filename = input('Please enter the name of your text file for updating parents (with file extension): ')
    print("Your genotype files with parents updated will have the name " + geno_name + "_ParentsUpdated")
    os.system('plink --bfile ' + geno_name + ' --update-parents ' + update_parents_filename + ' --make-bed --out ' +
              geno_name + '_ParentsUpdated')

elif to_do == '4':
    # File for updating sex should have:
    #   1) FID
    #   2) IID
    #   3) Sex (1 = M, 2 = F, 0 = missing)

    geno_name = input('Please enter the name of your genotype files (without bed/bim/fam extension). Remember, if you '
                      'just updated FIDs, then your genotype name should have _FIDUpdated at the end of it. If you just '
                      'updated parents, then your genotype name should have _ParentsUpdated at the end of it.: ')
    update_sex_filename = input('Please enter the name of your text file for updating sex (with file extension): ')
    print("Your genotype files with sex updated will have the name " + geno_name + "_SexUpdated")
    os.system('plink --bfile ' + geno_name + ' --update-sex ' + update_sex_filename + ' --make-bed --out ' + geno_name
              + '_SexUpdated')

elif to_do == '5':
    # Remove SNPs not in 1000 Genomes.
    # Match the position in 1000 genomes with the position in our genotype file, on a chromosome by chromosome basis.

    import pandas as pd

    geno_name = input('Please enter the name of the genotype files (without bed/bim/fam extension: ')
    bim_file = pd.read_csv(geno_name + '.bim', sep="\t", header=None)
    # Columns of bim_file: chr, rsid, cm, bp, allele1, allele2
    # Columns of legend: id, position, a0, a1, type, AFR, AMR, EAS, EUR, SAS, ALL

    file_save_names = ['chr%d_position_file' % x for x in range(1, 23)]
    legend_file_names = ['1000GP_Phase3_chr%d.legend' % x for x in range(1, 23)]

# Write lists of SNPs that are in 1000 Genomes
    for i in range(0, len(file_save_names)):
        current_legend_file = pd.read_csv(legend_file_names[i], sep=" ", header=0)
        print('Successfully read in chr' + str(i + 1) + ' legend file')
        file_save_names[i] = pd.merge(left=bim_file.loc[bim_file[0] == i + 1], right=current_legend_file, how='inner',
                                      left_on=3, right_on='position')
        print('chr' + str(i + 1) + ' complete')

# Create new plink files only with these SNPs.
    all_chr_files = [file_save_names[0], file_save_names[1], file_save_names[2], file_save_names[3], file_save_names[4],
                 file_save_names[5], file_save_names[6], file_save_names[7], file_save_names[8], file_save_names[9],
                 file_save_names[10], file_save_names[11], file_save_names[12], file_save_names[13], file_save_names[14],
                 file_save_names[15], file_save_names[16], file_save_names[17], file_save_names[18], file_save_names[19],
                 file_save_names[20], file_save_names[21]]
    all_snps_in_1000g = pd.concat(all_chr_files)
    print(all_snps_in_1000g.head(3))
    unique_snps_in_1000g = all_snps_in_1000g.drop_duplicates(subset = 1, keep = 'first', inplace = False)
    unique_snps_in_1000g[1].to_csv('SNPs_in_1000G.txt', sep = '\t', header = False, index = False)
    os.system('plink --bfile ' + geno_name + ' --extract SNPs_in_1000G.txt --make-bed --out ' + geno_name
              + '_SNPsIn1000G')

elif to_do == '6':
    print("You go, couch potato")

else:
    print("Please enter a number 1-5.")



