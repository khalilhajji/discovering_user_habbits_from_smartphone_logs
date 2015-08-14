import numpy as np
import matplotlib.pyplot as plt
import matplotlib.pylab as plb
from matplotlib.font_manager import FontProperties

k=[1,10,20,30,50,70]
ighcm_mdt=[0.5473594729519218,0.7457403274450934,0.7405571316801414,0.7332348738771248, 0.7405571316801414,0.7300858654054332]
ilda=[0.5473594729519218,0.7319248252030321,0.7245486373812716,0.7414576092249122, 0.7347934873547817,0.7356984849830991]
ilcbmf=[0.5473594729519218,0.6684430183935905,0.5461628396130043,0.5969390598567326,0.5653649337025458,0.3421583118501168]
ihcm_mdt=[0.5473594729519218,0.6603913492625721,0.6627882328849483,0.6452558372367677,0.6902307406590789 ,0.6756997048892404]
isvd=[0.5473594729519218,0.7148160409276294,0.6631207944694848,0.5855386718468153,0.5473594729519218,0.4184250943224212]
imost_frequent=[0.5473594729519218,0.5473594729519218,0.5473594729519218,0.5473594729519218,0.5473594729519218,0.5473594729519218]



k=[1,10,20,30,50,70]
aghcm_mdt=[0.3333333333333333,0.6588902800853121,0.653083500733102,0.6504278701089974,0.653083500733102,0.643496178162225]
alda=[0.3333333333333333,0.6496097592893433,0.6179911740716311,0.6475246858464188,0.6178106314346506,0.6294700924317297]
alcbmf=[0.3333333333333333,0.6460132604100601,0.5643018498666926,0.5682883454224006,0.5206484596221035,0.3947129189883026]
ahcm_mdt=[0.3333333333333333,0.5693527550198032,0.5792680917777446,0.5474376724131373,0.5855951790195272 ,0.5659047421021738]
asvd=[0.3333333333333333,0.5659961070267521, 0.4539535411467345,0.36687449411756645,0.3333333333333333,0.33305570245020266]
amost_frequent=[0.3333333333333333,0.3333333333333333,0.3333333333333333,0.3333333333333333,0.3333333333333333,0.3333333333333333]

x_label="Number of hidden classes k"
ay_label="Location prediction average accuracy"
atitle="Location prediction: average accuracy on 5 users"
iy_label="Location prediction accuracy"
ititle="Location prediction: accuracy on 5 users"
#line styles = ['-', '--', '-.', ':']
#colors = ["red","blue","green","black","magenta","yellow","cyan","orange"]
#drawstyle	[default | steps | steps-pre | steps-mid | steps-post]

#----------------------------MAKE PLOT-------------------#		
fig, ax = plt.subplots()	
ax.plot(k, np.array(aghcm_mdt), label="DLMR", linestyle='--', color="blue")
ax.plot(k, np.array(alda), label="LDA", linestyle='-', color="red")
ax.plot(k, np.array(ahcm_mdt), label="LMR", linestyle=':', color="green", linewidth=3.0)
ax.plot(k, np.array(alcbmf), label="LCBMF", linestyle=':', color="black",  linewidth=3.0)
ax.plot(k, np.array(asvd), label="SVD", linestyle='-.', color="black")
ax.plot(k, np.array(amost_frequent), label="MOST_FREQ", linestyle='-', color="black")
			
		
		
plt.xlabel(x_label)
plt.ylabel(ay_label)
plt.title(atitle)
fontP = FontProperties()
fontP.set_size('small')
plt.legend(loc='lower right', prop=fontP)

fig.tight_layout(pad=4)
plt.draw()

fig, ax = plt.subplots()	
ax.plot(k, np.array(ighcm_mdt), label="DLMR", linestyle='--', color="blue")
ax.plot(k, np.array(ilda), label="LDA", linestyle='-', color="red")
ax.plot(k, np.array(ihcm_mdt), label="LMR", linestyle=':', color="green", linewidth=3.0)
ax.plot(k, np.array(ilcbmf), label="LCBMF", linestyle=':', color="black",  linewidth=3.0)
ax.plot(k, np.array(isvd), label="SVD", linestyle='-.', color="black")
ax.plot(k, np.array(imost_frequent), label="MOST_FREQ", linestyle='-', color="black")
			
		
		
plt.xlabel(x_label)
plt.ylabel(iy_label)
plt.title(ititle)
fontP = FontProperties()
fontP.set_size('small')
plt.legend(loc='lower right', prop=fontP)

fig.tight_layout(pad=4)
plt.draw()
plt.show()


