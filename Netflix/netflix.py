from __future__ import print_function

import sys
import re
from operator import add
from pyspark import SparkContext

if __name__ == "__main__":
    if len(sys.argv) != 3:
        # too few/many arguments
        print("Needs three args: netflix <input_file> <user_id> <output_file>", file=sys.stderr)
        exit(-1)

    #create a SparkContext
    sc = SparkContext(appname="Netflix")
    # read in the input from text
    data = sc.textFile(sys.argv[1], 1) \
            .map(lambda x: x.split()) \
            .map(lambda x: (x[1], (x[0], x[2])))
    UserX = sys.argv[2]

    # get UserX's movies
    dataYes = data.filter(lambda x : UserX in x[1][0])
    # get other users' movies
    dataNo = data.filter(lambda x : UserX not in x[1][0])

    # join RDDs to get a dual-key thing
    # filter out items where UserX's rating does not match UserY's
    # emit a 1 for every row
    # reduce by summing all the 1s
    # flip the map so we can sort better
    # sort (by the number of matched ratings, which is the "new" key
    dataResult = dataYes.join(dataNo) \
                        .filter(lambda x : x[1][0][1] in x[1][1][1]) \
                        .map(lambda x : (x[1][1][0], 1)) \
                        .reduceByKey(lambda x, y: x + y) \
                        .map(lambda x : (x[1], x[0])) \
                        .sortByKey()

    dataResult.saveAsTextFile(sys.argv[3])
    sc.stop()



