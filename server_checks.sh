#! /bin/bash

if [ $# -eq 0 ]; then
    echo "No address provided (default is http://0.0.0.0:8050 - perhaps try using the default next time). Exiting"
    exit 1
fi


############################
#### Inserting user in DB
############################

echo 'Checking inserting/ updating a user in the db'
 curl -X PUT -H "Content-Type:application/json" $1/insert_update_user_info -d '{"user_ID": "TvI1m", "ITS": {"values": [50], "dates": ["2017-11-26T00:15:10.508371"]}, "Disp": {"values": [-1, 1, -2, -2], "dates": ["2017-10-03T19:20:42.994400", "2017-12-27T12:46:52.319677", "2018-02-15T04:17:56.169551", "2018-06-19T17:38:41.151667"]}, "Mturn": {"values": [132.86874663558206, 91.80843895999732, 233.2721083950576, 228.46259343138453, 311.2676211810235, 154.88994148221175, 376.37177324363034, 352.0472408072494, 361.51481263231193, 57.04725590922836, 464.1876839906812, 261.95532524046337], "dates": ["2017-09-03T00:15:00.167009", "2017-09-10T05:18:35.798197", "2017-10-03T19:20:42.994400", "2017-11-06T03:33:14.952269", "2017-12-05T22:45:20.343604", "2017-12-27T12:46:52.319677", "2017-12-30T05:43:39.623543", "2018-01-19T10:47:10.307799", "2018-02-15T04:17:56.169551", "2018-04-29T22:00:15.660924", "2018-05-09T13:37:03.043645", "2018-06-19T17:38:41.151667"]}, "Mbehav": {"values": [1, 5, 1, 5], "dates": ["2017-10-03T19:20:42.994400", "2017-12-27T12:46:52.319677", "2018-02-15T04:17:56.169551", "2018-06-19T17:38:41.151667"]}, "Mab": {"values": [2137.6997173778423, 1954.4145979325017, 1765.9382275381843, 761.4698585403921, 2294.6143381183474,953.7462389359928, 1231.541898587919, 1840.4304006874547, 1594.2275757000662, 1519.0731678030795, 1007.1449950958902, 1814.8087781332144], "dates": ["2017-09-03T00:15:00.167009", "2017-09-10T05:18:35.798197", "2017-10-03T19:20:42.994400", "2017-11-06T03:33:14.952269", "2017-12-05T22:45:20.343604", "2017-12-27T12:46:52.319677", "2017-12-30T05:43:39.623543", "2018-01-19T10:47:10.307799", "2018-02-15T04:17:56.169551", "2018-04-29T22:00:15.660924", "2018-05-09T13:37:03.043645", "2018-06-19T17:38:41.151667"]}, "ZTF": {"values": [0]}, "Mtxns": {"values": [5, 5, 35, 58, 19, 45, 0, 36, 11, 12, 47, 35], "dates": ["2017-09-03T00:15:00.167009", "2017-09-10T05:18:35.798197", "2017-10-03T19:20:42.994400", "2017-11-06T03:33:14.952269", "2017-12-05T22:45:20.343604", "2017-12-27T12:46:52.319677", "2017-12-30T05:43:39.623543", "2018-01-19T10:47:10.307799", "2018-02-15T04:17:56.169551", "2018-04-29T22:00:15.660924", "2018-05-09T13:37:03.043645", "2018-06-19T17:38:41.151667"]}, "ccITS": {"values": [1, 1, 0, 1], "dates": ["2017-10-03T19:20:42.994400", "2017-12-27T12:46:52.319677", "2018-02-15T04:17:56.169551", "2018-06-19T17:38:41.151667"]}}'
echo 'response should be'
echo '{"Status":"User TvI1m successfully inserted/updated in DB."}'
echo ''

#######################################
#### Checking the user info in the DB
#######################################

echo 'Checking the user info in the db'
curl -X PUT -H "Content-Type:application/json" $1/get_user_info -d '{"user_ID": "TvI1m"}'
echo 'response should be'
echo '{"Disp":{"dates":["2017-10-03T19:20:42.994400","2017-12-27T12:46:52.319677","2018-02-15T04:17:56.169551","2018-06-19T17:38:41.151667"],"values":[-1.0,1,-2.0,-2.0]},"ITS":{"dates":["2017-11-26T00:15:10.508371"],"values":[50]},"Mab":{"dates":["2017-09-03T00:15:00.167009","2017-09-10T05:18:35.798197","2017-10-03T19:20:42.994400","2017-11-06T03:33:14.952269","2017-12-05T22:45:20.343604","2017-12-27T12:46:52.319677","2017-12-30T05:43:39.623543","2018-01-19T10:47:10.307799","2018-02-15T04:17:56.169551","2018-04-29T22:00:15.660924","2018-05-09T13:37:03.043645","2018-06-19T17:38:41.151667"],"values":[2137.6997173778423,1954.4145979325017,1765.9382275381843,761.4698585403921,2294.6143381183474,953.7462389359928,1231.541898587919,1840.4304006874547,1594.2275757000662,1519.0731678030795,1007.1449950958902,1814.8087781332144]},"Mbehav":{"dates":["2017-10-03T19:20:42.994400","2017-12-27T12:46:52.319677","2018-02-15T04:17:56.169551","2018-06-19T17:38:41.151667"],"values":[1,5,1,5]},"Mturn":{"dates":["2017-09-03T00:15:00.167009","2017-09-10T05:18:35.798197","2017-10-03T19:20:42.994400","2017-11-06T03:33:14.952269","2017-12-05T22:45:20.343604","2017-12-27T12:46:52.319677","2017-12-30T05:43:39.623543","2018-01-19T10:47:10.307799","2018-02-15T04:17:56.169551","2018-04-29T22:00:15.660924","2018-05-09T13:37:03.043645","2018-06-19T17:38:41.151667"],"values":[132.86874663558206,91.80843895999732,233.2721083950576,228.46259343138453,311.2676211810235,154.88994148221175,376.37177324363034,352.0472408072494,361.51481263231193,57.04725590922836,464.1876839906812,261.95532524046337]},"Mtxns":{"dates":["2017-09-03T00:15:00.167009","2017-09-10T05:18:35.798197","2017-10-03T19:20:42.994400","2017-11-06T03:33:14.952269","2017-12-05T22:45:20.343604","2017-12-27T12:46:52.319677","2017-12-30T05:43:39.623543","2018-01-19T10:47:10.307799","2018-02-15T04:17:56.169551","2018-04-29T22:00:15.660924","2018-05-09T13:37:03.043645","2018-06-19T17:38:41.151667"],"values":[5,5,35,58,19,45,0,36,11,12,47,35]},"ZTF":{"values":[0]},"ccITS":{"dates":["2017-10-03T19:20:42.994400","2017-12-27T12:46:52.319677","2018-02-15T04:17:56.169551","2018-06-19T17:38:41.151667"],"values":[1,1,0,1]}}'
echo ''

#######################################
#### Calculating the TS from the DB
#######################################

echo 'Calculating the TS from the DB'
curl -X PUT -H "Content-Type:application/json" $1/TS_from_db -d '{"user_ID": "TvI1m"}'
echo 'response should be'
echo '{"TS":67.20651106742326}'
echo ''

####################################################################
#### Checking making updates and recalculating the TS from the DB
####################################################################

echo 'Checking making updates and recalculating the TS from the DB'
 curl -X PUT -H "Content-Type:application/json" $1/compute_TS_update_DB -d '{"user_ID": "TvI1m", "Mbehav": {"values": [15, 10], "dates": ["2018-07-15T04:17:56.169551", "2018-07-19T17:38:41.151667"]}}'
echo 'response should be'
echo '{"TS":43.137599835601264}'
echo ''

####################################################################
#### Checks if user information can be completely overwritten
####################################################################

echo 'Checks if user information can be completely overwritten'
curl -X PUT -H "Content-Type:application/json" $1/overwrite_insert_user_info -d '{"user_ID": "TvI1m", "ITS": {"values": [50], "dates": ["2017-11-26T00:15:10.508371"]}, "Disp": {"values": [-3], "dates": ["2017-11-03T19:20:42.994400"]}, "Mturn": {"values": [100], "dates": ["2018-06-03T00:15:00.167009"]}, "Mab": {"values": [2137.6997173778423], "dates": ["2017-09-03T00:15:00.167009"]}, "ZTF": {"values": [0]}, "Mtxns": {"values": [35], "dates": ["2018-06-19T17:38:41.151667"]}}'
echo 'response should be'
echo '{"Status":"User TvI1m successfully overwritten in DB."}'
echo ''


#### Checking that overwriting was successful
echo 'Checking that the user info was overwritten'
curl -X PUT -H "Content-Type:application/json" $1/get_user_info -d '{"user_ID": "TvI1m"}'
echo 'response should be'
echo '{"Disp":{"dates":["2017-11-03T19:20:42.994400"],"values":[-3.0]},"ITS":{"dates":["2017-11-26T00:15:10.508371"],"values":[75]},"Mab":{"dates":["2017-09-03T00:15:00.167009"],"values":[2137.6997173778423]},"Mbehav":{},"Mturn":{"dates":["2018-06-03T00:15:00.167009"],"values":[100]},"Mtxns":{"dates":["2018-06-19T17:38:41.151667"],"values":[35]},"ZTF":{"values":[0]},"ccITS":{}}'
echo ''

