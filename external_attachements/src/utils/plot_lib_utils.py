'''
class that contains some utility functions of making plots and drawing graphics
'''
#contains some utils functions that manipulate numpy objects
#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.pylab as plb
from matplotlib.font_manager import FontProperties

class PlotlibDrawer():
	colors = ["red",
	"blue",
	"green",
	"black",
	"magenta",
	"yellow",
	"cyan",
	"orange",
	"darkred",
	"beige",
	"blueviolet",
	"brown",
	"gray",
	"lightpink",
	"purple",
	"turquoise",
	"darkgreen",
	"darkgray",
	"lightyellow",
	"lightskyblue" ]
	
	'''
	makes a 2D plot given the y values vector, and the labels of each corresponding x.
	For example if we have the y_values [1,2] and x_labels [day1, day2] then the plot 
	will have the label day1 below the value 1 and day2 below the value 2.
	
	The nb_labels indicates the number of labels that are desired in the graph.
	For a hight dimensional vector, plotting all the labels will make the text superposed and not readable
	
	need to call the show method to be able to see the graph
	
	y_values is an array
	'''
	@staticmethod
	def plot_1(x_labels, y_values, x_label, y_label, title, nb_labels):
		#transfom inputs to nump arrays
		x = np.arange(len(y_values))
		y = np.array(y_values)
		labels = np.array(x_labels)
		
		y_max = np.amax(y)
		
		fig, ax = plt.subplots()
		ax.plot(x, y, 'bo-')
		plt.xlabel(x_label)
		plt.ylabel(y_label)
		plt.title(title)
		
		jump_step = len(y_values)/nb_labels

		
		label_indexes = np.arange(1,len(y_values),jump_step)
		
		
		for (X, Y, Z) in zip(x[label_indexes], y[label_indexes], labels[label_indexes]):
			ax.annotate('{}'.format(Z), xy=(X,Y), xytext=(X, (-0.1*y_max)), rotation=90, ha='center', size=10,
						textcoords='data')
		
		fig.tight_layout(pad=4)
		plt.draw()
	
	'''shows the different plot and draws done since the running of the program'''
	@staticmethod	
	def show():
		plt.show()
	
	'''
	the same as plot(x_labels, y_values, x_label, y_label, title, nb_labels) except that it plots many curves in one plot
	and also their corresponding legends.
	
	y_values_matrix is a list of list where each entry represents the y_points of one curve.
	legends is a list of string where the first entry is the legend for the first curve, the second entry 
	the legend for the second curve ect..
	Note that len(y_values_matrix) and len(legends) should be the same.
	if no x_labels are needed, give the x_labels argument the None value
	
	y_values_matrix is a matrix
	'''
	@staticmethod	
	def plot_2(x_labels, y_values_matrix, legends, x_label, y_label, title, nb_x_labels):
		x = np.arange(len(y_values_matrix[0]))
		
		
		fig, ax = plt.subplots()
		
		y_max =0
		curve_number = 0
		for curve in y_values_matrix:
			numpy_curve = np.array(curve)
			if y_max < np.amax(numpy_curve):
				y_max = np.amax(numpy_curve)
			
			ax.plot(x, numpy_curve, label=legends[curve_number], color=PlotlibDrawer.colors[(curve_number%len(PlotlibDrawer.colors))] )
			curve_number+=1
			
		
		
		plt.xlabel(x_label)
		plt.ylabel(y_label)
		plt.title(title)
		fontP = FontProperties()
		fontP.set_size('small')
		plt.legend(loc='lower right', prop=fontP)
		
		if x_labels != None:
			labels = np.array(x_labels)
			jump_step = len(labels)/nb_x_labels

			
			label_indexes = np.arange(1,len(labels),jump_step)
			
			
			for (X, Z) in zip(x[label_indexes], labels[label_indexes]):
				ax.annotate('{}'.format(Z), xy=(X,0), xytext=(X, (-0.1*y_max)), rotation=90, ha='center', size=10,
							textcoords='data')
		
		fig.tight_layout(pad=4)
		plt.draw()
		
		
	
	'''
	the same as plot(x_labels, y_values_matrix, legends, x_label, y_label, title, nb_x_labels) except that it takes
	a numpy array matrix at the input
	y_values_matrix is a numpy array matrix
	legends is a list of string where the first entry is the legend for the first curve, the second entry 
	the legend for the second curve ect.
	if no x_labels are needed, give the x_labels argument the None value
	'''
	@staticmethod	
	def plot_np(x_labels, y_values_matrix, legends, x_label, y_label, title, nb_x_labels):
		x = np.arange(len(y_values_matrix[0]))
		
		fig, ax = plt.subplots()
		
		y_max =0
		curve_number = 0
		for numpy_curve in y_values_matrix:
			if y_max < np.amax(numpy_curve):
				y_max = np.amax(numpy_curve)
			
			ax.plot(x, numpy_curve, label=legends[curve_number], color=PlotlibDrawer.colors[(curve_number%len(PlotlibDrawer.colors))] )
			curve_number+=1
			
		
		
		plt.xlabel(x_label)
		plt.ylabel(y_label)
		plt.title(title)
		fontP = FontProperties()
		fontP.set_size('small')
		plt.legend(loc='lower right', prop=fontP)
		
		if x_labels != None:
			labels = np.array(x_labels)
			jump_step = len(labels)/nb_x_labels

			
			label_indexes = np.arange(1,len(labels),jump_step)
			
			for (X, Z) in zip(x[label_indexes], labels[label_indexes]):
				ax.annotate('{}'.format(Z), xy=(X,0), xytext=(X, (-0.1*y_max)), rotation=90, ha='center', size=10,
							textcoords='data')
		
		fig.tight_layout(pad=4)
		plt.draw()
		
		
	'''
	x_labels: labels for the given x values
	x_values_np: x values as an np array 
	y_values_np: y values as an np array 
	x_label: the x axis legend 
	y_label: the y axis legend
	title: title of the plot
	nb_x_labels: see plot(x_labels, y_values_matrix, legends, x_label, y_label, title, nb_x_labels) 
	style: the style of the curve
	
	style can take:
		'ro' for bullets
		'bs' for triangles
		if none, draw a simple line
		
	'''
	@staticmethod	
	def plot_np_simple(x_labels, x_values_np, y_values_np, x_label, y_label, title, nb_x_labels, style):
		x = np.arange(len(y_values_np))
		
		fig, ax = plt.subplots()
		if style != None:
			ax.plot(x_values_np, y_values_np, style)
		else:
			ax.plot(x_values_np, y_values_np)
		
		
		
			
		
		
		plt.xlabel(x_label)
		plt.ylabel(y_label)
		plt.title(title)
		fontP = FontProperties()
		fontP.set_size('small')
		plt.legend(loc='lower right', prop=fontP)
		
		if x_labels != None:
			labels = np.array(x_labels)
			jump_step = len(labels)/nb_x_labels

			
			label_indexes = np.arange(1,len(labels),jump_step)
			
			for (X, Z) in zip(x[label_indexes], labels[label_indexes]):
				ax.annotate('{}'.format(Z), xy=(X,0), xytext=(X, (-0.1*y_max)), rotation=90, ha='center', size=10,
							textcoords='data')
		
		fig.tight_layout(pad=4)
		plt.draw()
		
	