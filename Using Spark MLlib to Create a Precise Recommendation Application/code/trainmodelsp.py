# coding:utf-8
import os
from pyspark import SparkConf,SparkContext
from pyspark.mllib.regression import LabeledPoint 
from pyspark.mllib.recommendation import ALS, MatrixFactorizationModel, Rating
import user_utill


def print_title(title=""):
    print("=" * 15 + " %s " % title + "=" * 15)


def train_model():
    
    print_title("download iris data!")
    local_data_path = user_utill.download_data("ratings.csv")
    print_title("load data!")

    conf = SparkConf().setAppName("testapr").setMaster("local")
    sc = SparkContext(conf=conf)
    data = sc.textFile(local_data_path)
    ratings = data.map(lambda l: l.split(',')).map(lambda l: Rating(int(l[0]), int(l[1]), float(l[2])))

    rank = 10
    numIterations = 10
    lambda_ = 0.02
    blocks = 100
    model = ALS.train(ratings, rank, numIterations, lambda_, blocks)

    testdata = ratings.map(lambda p: (p[0], p[1]))
    predictions = model.predictAll(testdata).map(lambda r: ((r[0], r[1]), r[2]))
    ratesAndPreds = ratings.map(lambda r: ((r[0], r[1]), r[2])).join(predictions)
    #print ratesAndPreds
    MSE = ratesAndPreds.map(lambda r: (r[1][0] - r[1][1])**2).mean()
    print("Mean Squared Error = " + str(MSE))
    user_predict = model.recommendProductsForUsers(10).collect()

    print_title("upload model to obs!")
    user_utill.upload_model("Spark_MLlib",model,"recommendmodel",sc)
    ## set schema config for model. 
    # "Spark_MLlib" is the engine type
    # ["number","number"] refers to the type of input arguments. input arguments are named as "input_n"
    # "number" refers to the type of output arguments.
    user_utill.create_config("Spark_MLlib",["number","number"],"number")
 

if __name__ == '__main__':
    train_model()
