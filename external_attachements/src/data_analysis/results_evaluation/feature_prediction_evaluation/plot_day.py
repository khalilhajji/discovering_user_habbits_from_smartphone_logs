import numpy as np
import matplotlib.pyplot as plt
import matplotlib.pylab as plb
from matplotlib.font_manager import FontProperties

k=[1,10,20,30,50,70]
ighcm_mdt=[0.7469530469840443,0.6775148219010433,0.7018103820624696,0.7132649861575795,0.7008975455669249,0.7141201234748287]

ilda=[0.7469530469840443,0.6562424315575239,0.6952607031543273,0.6988855712182336,0.6937066830046966,0.7257080785349752]

ilcbmf=[0.6594691760163023,0.700890724795895,0.5944620282733271,0.603593774686465,0.6430478763509073,0.6173702494037554]

ihcm_mdt=[0.7469530469840443,0.6526322297671937,0.6882691549977952,0.6885876199718878,0.6876290691824867,0.6767082381163217]

isvd=[0.6594691760163023,0.6562085074742263,0.7120849111056449,0.7281911218571253,0.7359174538611646,0.7466949824679152]

imost_frequent=[0.7469530469840443, 0.7469530469840443, 0.7469530469840443, 0.7469530469840443, 0.7469530469840443, 0.7469530469840443]



k=[1,10,20,30,50,70]

aghcm_mdt=[0.5,0.6849796721785008, 0.6903347378390465,0.6890195877048368,0.6589276067068971, 0.6685571749360015]

alda=[0.5,0.6698218671852955,0.6820851735757666,0.6797806259056186,0.6580499358353694,0.6899521231406637]

alcbmf=[0.5, 0.6407015284293307,0.5754801569748763, 0.5633210717089954, 0.5561865785343527, 0.5558338715378903]

ahcm_mdt=[0.5 ,0.569361941343322, 0.5778134054092243,0.6064760393631989,0.5850951534677727,0.5903233236421297]

asvd=[0.5, 0.6518093244606462, 0.5855636491631833, 0.5261549911561438, 0.49957866028684156, 0.4998204667863555]

amost_frequent=[0.5, 0.5, 0.5, 0.5, 0.5, 0.5]

x_label="Number of hidden classes k"
ay_label="Day prediction average accuracy"
atitle="Day prediction: average accuracy on 5 users"
iy_label="Day prediction accuracy"
ititle="Day prediction: accuracy on 5 users"
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
ax.plot(k, np.array(ighcm_mdt), label="DMR", linestyle='--', color="blue")
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


