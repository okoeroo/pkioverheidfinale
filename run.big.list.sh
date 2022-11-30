./main.py \
    -i samples/pkioverheid.txt \
    -o samples/pkioverheid.expanded-output.csv \
    --dns 1.1.1.1,9.9.9.9


if [ "$?" != 0 ]; then
    echo "failed"
    exit 1
fi


cat samples/pkioverheid.expanded-output.csv | head -n 1 > samples/pkioverheid.IN_scope.expanded-output.csv
cat samples/pkioverheid.expanded-output.csv | grep -i "overheid" | grep -vi "private" >> samples/pkioverheid.IN_scope.expanded-output.csv

cat samples/pkioverheid.expanded-output.csv | head -n 1 > samples/pkioverheid.OUT_of_scope.expanded-output.csv
cat samples/pkioverheid.expanded-output.csv | grep -v -i "overheid" | grep -vi "private" >> samples/pkioverheid.OUT_of_scope.expanded-output.csv

echo "done"
