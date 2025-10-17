# TFP-data
This folder presents imdb and dblp datasets used in computations of Team Formation Problem

imdbskills 1021x27 a_{ij} matrix

imdbSPdist3digits the shortest path distances p_{ij} 1021x1021

dblpskills58 12855x58 a_{ij} skill matrix

dblpNoOfPubAndDistance58 edge distances c_{ij} at the last column

The details are as follows:

IMDB network:
The nodes of the network are the actors who appeared in the movies from year 2000 to 2002 (1021 actors)
Skills are the movie genres (27 genres)

Data (IMDB_coauthor.csv and IMDB_skill.csv) is taken from https://www.dropbox.com/sh/hmus2o8owr0anj9/XB1JslGCDn via http://home.cse.ust.hk/faculty/wilfred/wangxinyu. IMDB_skill.csv is the original skill data. We also used a skill data which is randomly generated and its information can be found in the file "imdb_random_27_skills.txt"

In IMDB_coauthor.csv the line gives information about the number of movies two actors played together. For example the first line starts with Belladonna,263,Broder Todd,2,Cross Logan,2,... It means Belladone has 263 movies and 2 of them is common with Broder Todd.

For the experiment we generated intances with different number of required skills. The information related to the instances can be found in "imdb instance information.txt" for IMBD and in "dblp skill information of instances" for DBLP.

m is the number of skills required in that instances. And it takes value from the set $\{4,6,8,10,12,14,16,18,20\}$. For each $m$, 100 instances are randomly generated in a way that the set of required skills is different in each instance. The required skills are indicated in the second column. qno is the number of people who have at least one of the required skills and it is written to give an idea about the size of that specific instance.

DBLP social network generation:

database is dated 01.11.2017.

some keywords are taken as "skills".

the keywords in the file dblpkeywords.txt is searched in the titles of papers published in the following journals and conferences between years 2010-2016 {SC, AMCIS, MOBICOM, UAI, ICIS, SIGKDD, SIGMOD, VLDB, ICDE, ICDT, EDBT, PODS,WWW, KDD, SDM, PKDD, ICDM, ICML, ECML, COLT, UAI, SODA, FOCS, STOC, STACS}

If a paper title includes a keyword then the authors of the paper has that "skill". The keywords that are used as skills are listed in dblpkeywords.txt

This is how 12855x58 a_{ij} skill matrix is constructed (dblpskills58.txt)

Each skillful author is a part of the social network.

If two authors have at least 2 common papers then there is an edge connecting them. Let P_i the set of papers of author i. The distance between i and j is 1- (|P_i \cap P_j|/|P_i \cup P_j|) 

Using those distance all pair shortest path distances are found.

As the all pair shortest path distance matrix is too big for github, the edge distances are given in the last column of dblpNoOfPubAndDistance58.txt file. The order of columns in this file as follows:

Node(i) - Name(i) - Node(j) - Name(j) - NoOfPub(i) - NoOfPub(j) - NoOfCommonPubOf(i)and(j) - EdgeDistance(c_{ij})

In the excel file named "imdb TFP-SD instances and optimal solutions.xls" we present the instance details, optimal solutions and solution times of the MIP formulation and the branch-and-bound algorithm.


