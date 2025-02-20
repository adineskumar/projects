from __future__ import print_function

import sys
import re

from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.sql import Row, SparkSession

from pyspark.streaming.kafka import KafkaUtils

def getSparkSessionInstance(sparkConf):
        if ('sparkSessionSingletonInstance' not in globals()):
                globals()['sparkSessionSingletonInstance'] = SparkSession\
            .builder\
            .config(conf=sparkConf)\
            .getOrCreate()
        return globals()['sparkSessionSingletonInstance']
		
if __name__ == "__main__":
    #if len(sys.argv) != 3:
    #    print("Usage: sql_network_wordcount.py <hostname> <port> ", file=sys.stderr)
    #    exit(-1)
    #host, port = sys.argv[1:]
        def parse_apache_log_line(logline):
                match = re.search(APACHE_ACCESS_LOG_PATTERN,logline)
                return Row(ip_address = match.group(1), method = match.group(5), endpoint = match.group(6), response = match.group(8))

        APACHE_ACCESS_LOG_PATTERN = '^(\S+) (\S+) (\S+) \[([\w:/]+\s[+\-]\d{4})\] "(\S+) (\S+) (\S+)" (\d{3}) (\d+)'

        kafkaParams = {"metadata.broker.list" : "10.68.112.217:9092,10.68.112.219:9092,10.68.112.220:9092" , "auto.offset.reset" : "smallest"}
        topic = "metrics_test"
        sc = SparkContext(appName="PythonSqlKafkaLogParser")
        ssc = StreamingContext(sc, 10)

    # Create a socket stream on target ip:port and count the
    # words in input stream of \n delimited text (eg. generated by 'nc')
    #lines = ssc.socketTextStream(host, int(port))
    #words = lines.flatMap(lambda line: line.split(" "))
        kafkaDStream = KafkaUtils.createDirectStream( ssc, [topic], kafkaParams )
        kafkaMessage = kafkaDStream.map(lambda x : x[1])

    # Convert RDDs of the words DStream to DataFrame and run SQL query
        def process(time, rdd):
                print("========= %s =========" % str(time))

                try:
                        # Get the singleton instance of SparkSession
                        spark = getSparkSessionInstance(rdd.context.getConf())

                        # Convert RDD[String] to RDD[Row] to DataFrame
                        rowRdd = rdd.map(lambda record: parse_apache_log_line(record))
                        wordsDataFrame = spark.createDataFrame(rowRdd)

                        # Creates a temporary view using the DataFrame.
                        wordsDataFrame.createOrReplaceTempView("ACCESS_LOG")

                        # Using SQL and print it
                        accessLogDataFrame = \
                                spark.sql("SELECT * FROM ACCESS_LOG")
                        accessLogDataFrame.show()
                except:
                        pass

        kafkaMessage.foreachRDD(process)
        ssc.start()
        ssc.awaitTermination()

		
