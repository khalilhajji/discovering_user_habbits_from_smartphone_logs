In this folder we write a code that extracts a categorized representation of the dataset.
We take as input the cleaned version of the dataset.

The categorized dataset is the first step to the matrix representation:
In this representation, an attribute that can take 10 possible values will have an id from 0-9 representing the index of the value taken.
If the value is negative (which means that a certain attribute takes a false value , for example non present), then it will take -1.

Thus we add a metadata information representing for each feature and each attribute the meaning of the ids.