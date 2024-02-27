#!/usr/bin/env bash
# @author      : denstiny (2254228017@qq.com)
# @file        : setenv
# @created     : 星期日 2月 25, 2024 21:12:30 CST 
# @github      : https://github.com/denstiny
# @blog        : https://denstiny.github.io



docker pull docker.elastic.co/elasticsearch/elasticsearch:8.12.2

docker run  --name es -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" -e "discovery.type=single-node" -v es-data:/usr/share/elasticsearch/data -v es-plugins:/usr/share/elasticsearch/plugins --privileged --network es-net -p 9200:9200 -p 9300:9300 elasticsearch:8.12.2
sysctl -w vm.max_map_count=262144   
docker cp ./li es01:/usr/share/elasticsearch/plugins/ik
docker restart es01               

curl -X GET "http://localhost:9200"
