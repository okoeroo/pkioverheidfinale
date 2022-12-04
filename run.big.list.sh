
./main.py \
    --verbose \
    -i samples/pkioverheid-zonder-preprod-test-acc.txt \
    -o samples/pkioverheid.expanded-output.csv \
    --dns 1.1.1.1,9.9.9.9

#    --dns 127.0.0.1:8853


if [ "$?" != 0 ]; then
    echo "failed"
    exit 1
fi


# Header
cat samples/pkioverheid.expanded-output.csv | \
    head -n 1 > samples/pkioverheid.IN_scope.expanded-output.csv

# Body
cat samples/pkioverheid.expanded-output.csv | \
    grep -i "PKIoverheid Server CA 2020" \
        >> samples/pkioverheid.IN_scope.expanded-output.csv


echo "done"
