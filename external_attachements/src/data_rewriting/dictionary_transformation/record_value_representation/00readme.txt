This folder contains a code that writes the data in a record-value structure.

this data is written as a dictionary represented in the following way: 
dictionary data[r_id]: Array[values_id , 1] values if ids (v_ids) that appears in record r (that has the id r_id).  ex [v1,v1,v2,...,v3]
Values are any possible realization of a couple of (feature,value). For example Activity_running is a value, Notification_mail is another.
         
		  
As the dictionary contains only integers (that represents ids) some additional files are written to the disk with the dictionary that specifies the strings representing the different ids