#!/usr/bin/env bash
chmod +x ./build.sh
make install && psql -a -d $DATABASE_URL -f database.sql