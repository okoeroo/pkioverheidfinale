./main.py -i samples/pkioverheid.txt -o samples/pkioverheid.expanded-output.csv

if [ "$?" != 0 ]; then
    echo "failed"
    exit 1
fi


cat samples/pkioverheid.expanded-output.csv | grep -i "overheid" > samples/pkioverheid.IN_scope.expanded-output.csv
cat samples/pkioverheid.expanded-output.csv | grep -v -i "overheid" > samples/pkioverheid.OUT_of_scope.expanded-output.csv

echo "done"
