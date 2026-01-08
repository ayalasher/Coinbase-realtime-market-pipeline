CREATE TABLE coinbase_ticker (
    `type` STRING,
    `sequence` BIGINT,
    `product_id` STRING,
    `price` STRING,
    `open_24h` STRING,
    `volume_24h` STRING,
    `low_24h` STRING,
    `high_24h` STRING,
    `volume_30d` STRING,
    `best_bid` STRING,
    `best_ask` STRING,
    `side` STRING,
    `time` STRING,
    `trade_id` BIGINT,
    `last_size` STRING
) WITH (
    'connector' = 'kafka',
    'topic' = 'topic_kafka_coinbase_test',
    'properties.bootstrap.servers' = 'pkc-56d1g.eastus.azure.confluent.cloud:9092',
    'properties.security.protocol' = 'SASL_SSL',
    'properties.sasl.mechanism' = 'PLAIN',
    'properties.sasl.jaas.config' = 'org.apache.kafka.common.security.plain.PlainLoginModule required username="N3VYJB3XCMQRYIYR" password="cfltAji00NeF4RU1BZpopO0dwrM209UO3P+vac63tRQ6TieDkCCL0gXbvbsmmEQw";',
    'scan.startup.mode' = 'latest-offset',
    'value.format' = 'avro-confluent',
    'value.avro-confluent.url' = 'https://psrc-4n808m2.eastus.azure.confluent.cloud',
    'value.avro-confluent.basic-auth.credentials-source' = 'USER_INFO',
    'value.avro-confluent.basic-auth.user-info' = 'W2ZXAK76E4CP7N7Y:cfltrVhlyP1p+YD/n2uytl8PM0WWzciVsY+1SGUosyPznB1+R+YOnkHUTYoFMs2g'
);