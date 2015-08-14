This folder contains a code that writes the data in a record-feature-value structure.

this data is written as a dictionary represented in the following way: 
dictionary data[r_id][f_id]: Array[values_id , 1] values of feature f (that has the id f_id) that appears in record r (that has the id r_id). 
Features could be location, notification ... Values of feature location could be location 1, location 2. Each value has attributed an id representing the id of the feature.
          ex [v1,v1,v2,...,v3]
		  
As the dictionary contains only integers (that represents ids) some additional files are written to the disk with the dictionary that specifies the strings representing the different ids