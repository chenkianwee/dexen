@echo on
c:
mkdir -p "%temp%/dexen_db"
start mongod --dbpath %temp%/dexen_db
timeout 5

start db --log-path dexen_server_backend.log
timeout 5
start df --log-path dexen_server_frontend.log
timeout 5
start dn --log-path dexen_node.log
timeout 5