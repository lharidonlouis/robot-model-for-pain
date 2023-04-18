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
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns



filename1 =  str(sys.argv[1])+".csv"
#filename1 = "/Users/lharidonlouis/Documents/Thesis/Work/pain_model/robot-model-for-pain/data_analysis/20220727-214436.csv"
#filename1 = "/Users/lharidonlouis/Documents/Thesis/Work/pain_model/robot-model-for-pain/data_analysis/expe.csv"
print(filename1)

#names = ['iter', 'time', 'val_energy', 'val_temperature', 'def_energy', 'def_temperature', 'stim_food', 'stim_shade', 'stim_wall', 'mot_hunger', 'mot_cold', 'motor_left', 'motor_right', 'reactive', 'sensor_us_0', 'sensor_us_1', 'sensor_us_2', 'sensor_us_3', 'sensor_us_4', 'sensor_prox_0', 'sensor_prox_1', 'sensor_prox_2', 'sensor_prox_3', 'sensor_prox_4', 'sensor_prox_5', 'sensor_prox_6', 'sensor_prox_7', 'sensor_prox_8', 'sensor_prox_9', 'sensor_prox_10', 'sensor_prox_11', 'sensor_gnd_0', 'sensor_gnd_1', 'sensor_gnd_2', 'sensor_gnd_3', 'sensor_gnd_4', 'sensor_gnd_5', 'sensor_gnd_6', 'sensor_gnd_7', 'sensor_gnd_8', 'sensor_gnd_9', 'sensor_gnd_10', 'sensor_gnd_11', 'speed_1', 'speed_2', 'speed_3', 'speed_4', 'speed_5', 'speed_6', 'speed_7', 'speed_8', 'speed_9', 'speed_10', 'speed_11', 'speed_12', 'circ_1', 'circ_2', 'circ_3', 'circ_4', 'circ_5', 'circ_6', 'circ_7', 'circ_8', 'circ_9', 'circ_10', 'circ_11', 'circ_12', 'noci_1', 'noci_2', 'noci_3', 'noci_4', 'noci_5', 'noci_6', 'noci_7', 'noci_8', 'noci_9', 'noci_10', 'noci_11', 'noci_12', 'Unnamed:70']

df = pd.read_csv(
    filename1,
    delimiter=",",
    skiprows=0
)
list(df.columns)


# df = pd.read_csv(
#     filename1,
#     name = columns,
#     delimiter=",",
#     skiprows=1
# )


df.time = df.time.div(1000)

#for each line in df, write the name of the max row between mot_hunger and mot_cold
df['mot'] = df[['mot_hunger', 'mot_cold']].idxmax(axis=1)

plt.style.use(matplotx.styles.pacoty) 
#plt.style.use("cyberpunk")

#mpl.use('pdf')

with PdfPages('/Users/lharidonlouis/Documents/Thesis/Work/pain_model/robot-model-for-pain/data_analysis/'+str(sys.argv[1])+".pdf") as pdf:

     ##Page 1
     fig = plt.figure(figsize=(11.7,11.7)) #to get A4 portrait format
     fig.suptitle(str(sys.argv[2]), fontsize=25)
     #add 1cm oof space around grid
     grid = plt.GridSpec(5, 2, wspace=0.9, hspace=0.9)

     plt.rc('axes', labelsize=22 )
     plt.rc('xtick', labelsize=18)
     plt.rc('ytick', labelsize=18)
     plt.rc('legend', fontsize=18)



     ####### PLOT deficits #######
     plt.subplot(grid[0:, 0:])
     #plot df.def_energy and df.def_temperature in 2d position with color varying with time
     points = np.array([df.def_energy, df.def_temperature]).T.reshape(-1, 1, 2)
     segments = np.concatenate([points[:-1], points[1:]], axis=1)
     lc = LineCollection(segments, cmap='plasma', norm=plt.Normalize(0, df.time.max()))
     lc.set_array(df.time )
     lc.set_linewidth(2)
     lc.set_alpha(0.5)
     line = plt.gca().add_collection(lc)

     # add crosses at start and end points with color coding
     plt.plot(df.def_energy.iloc[0], df.def_temperature.iloc[0], 'm+', markersize=10, label='Start')
     plt.plot(df.def_energy.iloc[-1], df.def_temperature.iloc[-1], 'r+', markersize=10, label='End')

     plt.colorbar(line, ax=plt.gca(), label='Time (s)')
     plt.xlim([0, 1])
     plt.ylim([0, 1])
     plt.gca().spines['bottom'].set_position('zero')
     plt.gca().spines['left'].set_position('zero')
     # make the aspect ratio of the plot equal
     plt.gca().set_aspect('equal', adjustable='box')
     # add axes labels, title, and legend
     plt.xlabel('ΔEnergy')
     plt.ylabel('ΔTemperature')
     plt.title('Activity cycle')
     plt.legend(loc='upper right')
     plt.yticks(np.arange(0, 1.1, 0.25))
     plt.xticks(np.arange(0, 1.1, 0.25))
     # add overlays
     overlay1 = 'Danger: unbalanced deficit'
     #plt.text(0.05, 0.95, overlay1, color='white', fontsize=7, fontweight='bold', bbox=dict(facecolor='orange', edgecolor='none', alpha=0.5), transform=plt.gca().transAxes, ha='left', va='top')
     overlay2 = 'Danger: unbalanced deficit'
     #plt.text(0.95, 0.05, overlay2, color='white', fontsize=7, fontweight='bold', bbox=dict(facecolor='orange', edgecolor='none', alpha=0.5), transform=plt.gca().transAxes, ha='right', va='bottom')
     overlay3 = 'Danger: high deficits'
     #plt.text(0.95, 0.85, overlay3, color='white', fontsize=7, fontweight='bold', bbox=dict(facecolor='red', edgecolor='none', alpha=0.5), transform=plt.gca().transAxes, ha='right', va='bottom')
     overlay4 = 'Balanced deficits'
     #plt.text(0.35, 0.05, overlay4, color='white', fontsize=7, fontweight='bold', bbox=dict(facecolor='green', edgecolor='none', alpha=0.5), transform=plt.gca().transAxes, ha='right', va='bottom')

     plt.plot([0.5, 1], [1, 0.5], '--', color='black')
     plt.plot([0.5, 0], [1, 0.5], '--', color='black')
     plt.plot([0.5, 1], [0, 0.5], '--', color='black')
     #shade the regions defined by the lines
     plt.fill_between([0.5, 1], [1, 0.5], [1, 1], color='r', alpha=0.3)
     plt.fill_between([0.5, 0], [1, 0.5], [1, 1], color='orange', alpha=0.3)
     plt.fill_between([0.5, 1], [0, 0.5], [0, 0], color='orange', alpha=0.3)
     

     fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
     pdf.savefig(fig)


     #Page 1.2
     fig = plt.figure(figsize=(11.7,11.7)) #to get A4 portrait format
     #add 1cm oof space around grid
     grid = plt.GridSpec(4, 2, wspace=0.5, hspace=0.5)


     ####### PLOT Variables level #######
     plt.subplot(grid[1:2, 0:])
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
     plt.yticks(np.arange(0, 1.1, 0.25))
     plt.legend(['Energy', 'Temperature'], loc='upper right')
     plt.gca().set_ylim([0,1])
     plt.gca().set_xlim(left=0, right=max(df.time))

     fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
     pdf.savefig(fig)


     #Page 1.3

     fig = plt.figure(figsize=(11.7,11.7)) #to get A4 portrait format
     #add 1cm oof space around grid
     grid = plt.GridSpec(4, 2, wspace=0.5, hspace=0.5)


     ####### PLOT motivatios #######
     plt.subplot(grid[1:2, 0:])
     plt.fill_between(df.time, df.mot_danger, 0,
                    where = np.logical_and(np.greater_equal(df.mot_danger, df.mot_cold ), np.greater_equal(df.mot_danger, df.mot_hunger )),
                    color = 'r',
                    alpha = 0.3)
     plt.fill_between(df.time, df.mot_hunger, 0,
                    where = np.logical_and(np.greater_equal(df.mot_hunger, df.mot_cold ), np.greater_equal(df.mot_hunger, df.mot_danger )),
                    color = 'g',
                    alpha = 0.3)
     plt.fill_between(df.time, df.mot_cold, 0,
                    where = np.logical_and(np.greater_equal(df.mot_cold, df.mot_hunger ), np.greater_equal(df.mot_cold, df.mot_danger )),
                    color = 'b',
                    alpha = 0.3)
     plt.plot(df.time, df.mot_hunger,alpha=0.5,c='g')
     plt.plot(df.time, df.mot_cold,alpha=0.5,c='b')
     plt.xlabel('Time (s)')
     plt.ylabel('Intensity of motivation')
     plt.title('Intensity of motivations over time')
     plt.legend(['Danger','Hunger', 'Cold'], loc='upper right')
     plt.yticks(np.arange(0, 1.1, 0.25))
     plt.gca().set_ylim([0,1])
     #plt.gca().set_xlim(left=0, right=None)
     plt.gca().set_xlim(left=0, right=max(df.time))
     
     fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
     pdf.savefig(fig)
 

     ##Page 2
     fig = plt.figure(figsize=(8.27,11.7)) #to get A4 portrait format
     #add 1cm oof space around grid
     grid = plt.GridSpec(4, 2, wspace=0.5, hspace=0.5)

     ####### PLOT Hormones ########
     ax = plt.subplot(grid[0:2, 0:])

     plt.plot(df.time, df.hormonal_concentration,alpha=1,c='r')
     plt.plot(df.time, df.wellbeing,alpha=0.3,c='b')

     plt.xlabel('Time (s)')
     plt.ylabel('Cortisol')
     plt.title('Intensity of cortisol over time')
     plt.legend(['cortisol level','Wellbeing'], loc='upper right')
     plt.yticks(np.arange(0, 1.1, 0.1))
     plt.gca().set_ylim([0,1])
     plt.gca().set_xlim(left=0, right=max(df.time))

     # Define the x and y coordinates for the arrows
     n = int(df.time.size / 50)
     x = df.time[::n]  # Plot an arrow every x rows
     y = df.hormonal_concentration[::n]
     dx = np.zeros_like(x)
     dy = df.gland_release_rate[::n]

     # Plot the arrows using quiver
     ax.quiver(x, y, dx, dy, angles='xy', scale_units='xy', scale=1, color='k',alpha=0.5)



     # create a figure and axis object
     ax = plt.subplot(grid[2:4, 0:])

     # create box plots for wellbeing and pain
     ax.boxplot([df.wellbeing, df.pain])

     # add titles and labels
     ax.set_title('Box plots of Wellbeing and Pain')
     ax.set_ylabel('Value')
     ax.set_xticklabels(['Wellbeing', 'Pain'])
     plt.yticks(np.arange(0, 1.1, 0.1))
     plt.gca().set_ylim([0,1])

     #plt.show()

     fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
     pdf.savefig(fig)
     plt.close()




     ##Page 3
     fig = plt.figure(figsize=(11.7,11.7)) #to get A4 portrait format
     #add 1cm oof space around grid
     grid = plt.GridSpec(2, 2, wspace=0.25, hspace=0.25)


     plt.subplot(grid[0, 0])
     ultrasonic_sensors = ['sensor_prox_0', 'sensor_prox_1', 'sensor_prox_2', 'sensor_prox_3', 'sensor_prox_4','sensor_prox_5','sensor_prox_6']
     un = ['0', '1', '2', '3', '4','5','6']
     sns.heatmap(df[ultrasonic_sensors].transpose(), cmap='Blues',vmin=0, vmax=1)
     # add titles and labels
     plt.title('Ultrasonic Sensor Readings')
     plt.xlabel('Time (s)')
     plt.ylabel('Sensor Number')
     plt.gca().set_xlim(left=0, right=max(df.time))
     plt.yticks(np.arange(0.5, 7.5, 1), labels=un[::-1])
     plt.gca().set_ylim([0,7])

     plt.subplot(grid[0, 1])
     ultrasonic_sensors = ['noci_0', 'noci_1', 'noci_2', 'noci_3', 'noci_4','noci_5','noci_6']
     sns.heatmap(df[ultrasonic_sensors].transpose(), cmap='Blues',vmin=0, vmax=1)
     # add titles and labels
     plt.title('Nociceptors')
     plt.xlabel('Time (s)')
     plt.ylabel('Sensor Number')
     plt.gca().set_xlim(left=0, right=max(df.time))
     plt.yticks(np.arange(0.5, 7.5, 1), labels=un[::-1])
     plt.gca().set_ylim([0,7])

     plt.subplot(grid[1, 0])
     ultrasonic_sensors = ['speed_0', 'speed_1', 'speed_2','speed_3', 'speed_4', 'speed_5', 'speed_6']
     sns.heatmap(df[ultrasonic_sensors].transpose(), cmap='Blues',vmin=0, vmax=1)
     # add titles and labels
     plt.title('Speed damage')
     plt.xlabel('Time (s)')
     plt.ylabel('Sensor Number')
     plt.gca().set_xlim(left=0, right=max(df.time))
     plt.yticks(np.arange(0.5, 7.5, 1), labels=un[::-1])
     plt.gca().set_ylim([0,7])


     plt.subplot(grid[1, 1])
     ultrasonic_sensors = ['circ_0', 'circ_1','circ_2', 'circ_3', 'circ_4', 'circ_5', 'circ_6']
     sns.heatmap(df[ultrasonic_sensors].transpose(), cmap='Blues',vmin=0, vmax=1)
     # add titles and labels
     plt.title('Circular damage')
     plt.xlabel('Time (s)')
     plt.ylabel('Sensor Number')
     plt.gca().set_xlim(left=0, right=max(df.time))
     plt.yticks(np.arange(0.5, 7.5, 1), labels=un[::-1])
     plt.gca().set_ylim([0,7])

     fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
     pdf.savefig(fig)
     plt.close()


     ##Page 4
     fig = plt.figure(figsize=(11.7,8.27)) #to get A4 portrait format
     #add 1cm oof space around grid
     grid = plt.GridSpec(2, 2, wspace=0.5, hspace=0.5)
     
     plt.subplot(grid[:, :])
     # create a scatter plot
     plt.scatter(df['hormonal_concentration'], df['gland_release_rate'])

     # add titles and labels
     plt.title('Hormone Secretion Dynamics Graph')
     plt.ylabel('Gland Release Rate')
     plt.xlabel('Hormonal Concentration')
     plt.xticks(np.arange(0, 1.1, 0.1))
     plt.gca().set_ylim([0,0.05])
     plt.gca().set_xlim([0,1])

     fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
     pdf.savefig(fig)
     plt.close()


     ##Page 5
     fig = plt.figure(figsize=(8.27,11.7)) #to get A4 portrait format
     #add 1cm oof space around grid
     grid = plt.GridSpec(2, 2, wspace=0.5, hspace=0.5)
     
     plt.subplot(grid[:, :])

     # calculate the relative frequencies
     stimuli = ['stim_food', 'stim_shade', 'stim_wall']
     counts = [df[s].sum() for s in stimuli]
     total_count = sum(counts)
     frequencies = [c / total_count for c in counts]

     # create a bar chart
     plt.bar(stimuli, frequencies)

     # add titles and labels
     plt.title('Relative Frequencies of Stimuli')
     plt.xlabel('Stimulus')
     plt.ylabel('Relative Frequency')

     # show the plot


     fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
     pdf.savefig(fig)
     plt.close()

     ##Page 6
     fig = plt.figure(figsize=(8.27,11.7)) #to get A4 portrait format
     #add 1cm oof space around grid
     grid = plt.GridSpec(2, 2, wspace=0.5, hspace=0.5)
     
     plt.subplot(grid[0, :])

     # create a violin plot
     sns.violinplot(data=df[['mot_hunger', 'mot_cold']])

     # add titles and labels
     plt.title('Distribution of Motivation Scores')
     plt.xlabel('Motivation Type')
     plt.ylabel('Score')
     plt.yticks(np.arange(0, 1.1, 0.1))
     plt.gca().set_ylim([0,1])

     plt.subplot(grid[1:, :])

     # create a histogram
     plt.hist(df['pain'], bins=10, color='purple', alpha=0.5)

     # add titles and labels
     plt.title('Distribution of Pain intesity')
     plt.xlabel('Pain intensity')
     plt.ylabel('Frequency')


     fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
     pdf.savefig(fig)
     plt.close()



#plt.savefig('/Users/lharidonlouis/Documents/Thesis/Work/pain_model/robot-model-for-pain/data_analysis/'+str(sys.argv[1])+".pdf")



#plt.gca().set_xlim(left=0, right=None)