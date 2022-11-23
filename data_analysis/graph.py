# importing the required module
from turtle import color
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys
import matplotlib.ticker as ticker
import mplcyberpunk
import matplotx
import vapeplot
from matplotlib.gridspec import GridSpec
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
import matplotlib.animation as animation


filename1 =  str(sys.argv[1])+".csv"
#filename1 = "/Users/lharidonlouis/Documents/Thesis/Work/pain_model/robot-model-for-pain/data_analysis/20220727-214436.csv"
#filename1 = "/Users/lharidonlouis/Documents/Thesis/Work/pain_model/robot-model-for-pain/data_analysis/expe.csv"
print(filename1)

columns=["time","val_energy","val_temperature","def_energy","def_temperature","stim_food","stim_shade","stim_wall","mot_hunger","mot_cold","motor_left","motor_right","reactive"]

df = pd.read_csv(
    filename1,
    names= columns,
    delimiter=",",
    skiprows=1
)

#print(res.to_string())

df.time = df.time.div(200)

#for each line in df, write the name of the max row between mot_hunger and mot_cold
df['mot'] = df[['mot_hunger', 'mot_cold']].idxmax(axis=1)

plt.style.use(matplotx.styles.pacoty) 
#plt.style.use("cyberpunk")

#mpl.use('pdf')
fig = plt.figure(figsize=(8.27,11.7)) #to get A4 portrait format
#add 1cm oof space around grid
grid = plt.GridSpec(4, 2, wspace=0.5, hspace=0.5)


plt.subplot(grid[0:2, 0:])
#plot df.def_energy and df.def_temperature in 2d position with color varying with time
points = np.array([df.def_energy, df.def_temperature]).T.reshape(-1, 1, 2)
segments = np.concatenate([points[:-1], points[1:]], axis=1)
lc = LineCollection(segments, cmap='plasma', norm=plt.Normalize(0, df.time.max()))
lc.set_array(df.time)
lc.set_linewidth(2)
lc.set_alpha(0.5)
line = plt.gca().add_collection(lc)
plt.colorbar(line, ax=plt.gca(), label='Time (s)')
plt.xlabel('ΔEnergy')
plt.ylabel('ΔTemperature')
plt.title('Activity cycle')
plt.legend(['Symetric initialization'], loc='upper right')
plt.yticks(np.arange(0, 1.1, 0.1))
plt.xticks(np.arange(0, 1.1, 0.1))
plt.gca().set_ylim([0,1])
plt.gca().set_xlim([0,1])





plt.subplot(grid[2, 0:])
plt.plot(df.time, df.val_energy,alpha=0.5,c='m')
plt.plot(df.time, df.val_temperature,alpha=0.5,c='b')
plt.axhline(y=0.95, color='r', linestyle='--')
plt.axhline(y=0.05, color='r', linestyle='--')
plt.fill_between(df.time, 1.0, 0.95, color='g', alpha=0.3)
plt.fill_between(df.time, 0, 0.05, color='g', alpha=0.3)
plt.text(20,0.92,'critical temperature level',horizontalalignment='left',
     verticalalignment='center',fontsize = 6)
plt.text(20,0.07,'critical energy level',horizontalalignment='left',
     verticalalignment='center', fontsize = 6)
plt.text(5,0.98,'energy ideal values',horizontalalignment='left',
     verticalalignment='center',fontsize = 6)
plt.text(5,0.02,'temperature ideal values',horizontalalignment='left',
     verticalalignment='center', fontsize = 6)

plt.xlabel('Time (s)')
plt.ylabel('Value')
plt.title('Value of physiological variables over time')
plt.yticks(np.arange(0, 1.1, 0.1))
plt.legend(['Energy', 'Temperature'], loc='upper left')
plt.gca().set_ylim([0,1])
plt.gca().set_xlim(left=0, right=max(df.time))


# plt.subplot(grid[2, 1])
# plt.plot(df.time, df.mot, alpha=0.5, c='g')
# plt.gca().set_ylabel(["Hunger","Cold"])
# plt.xlabel('Time (s)')
# plt.ylabel('Selected motivation')
# plt.title('Selected motivation over time')

plt.subplot(grid[3, 0:])
plt.fill_between(df.time, df.mot_hunger, 0,
                 where = (df.reactive == True),
                 color = 'r',
                 alpha = 0.3)
plt.fill_between(df.time, df.mot_hunger, 0,
                 where = (df.mot_hunger > df.mot_cold),
                 color = 'g',
                 alpha = 0.3)
plt.fill_between(df.time, df.mot_cold, 0,
                 where = (df.mot_cold > df.mot_hunger),
                 color = 'b',
                 alpha = 0.3)
plt.plot(df.time, df.mot_hunger,alpha=0.5,c='g')
plt.plot(df.time, df.mot_cold,alpha=0.5,c='b')
plt.xlabel('Time (s)')
plt.ylabel('Intensity of motivation')
plt.title('Intensity of motivations over time')
plt.legend(['Reactive','Hunger', 'Cold'], loc='upper right')
plt.yticks(np.arange(0, 1.1, 0.1))
plt.gca().set_ylim([0,1])
#plt.gca().set_xlim(left=0, right=None)
plt.gca().set_xlim(left=0, right=max(df.time))





#mplcyberpunk.add_glow_effects()
#fig.tight_layout(pad=15.0)


#plt.show()



fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
fig.suptitle(str(sys.argv[2]), fontsize=16)

plt.savefig('/Users/lharidonlouis/Documents/Thesis/Work/pain_model/robot-model-for-pain/data_analysis/'+str(sys.argv[1])+".pdf")


