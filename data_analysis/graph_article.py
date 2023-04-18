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
from sklearn.cluster import KMeans


filename1 =  "C1_2.csv"
filename2 =  "C2_test.csv"
filename3 =  "C3_1.csv"
filename4 =  "C4_test.csv"

# filename1 =  "N1_1.csv"
# filename2 =  "N2_2.csv"
# filename3 =  "N3_1.csv"
# filename4 =  "N4_1.csv"

df1 = pd.read_csv(
    filename1,
    delimiter=",",
    skiprows=0
)
list(df1.columns)
df1.time = df1.time.div(1000)

df2 = pd.read_csv(
    filename2,
    delimiter=",",
    skiprows=0
)
list(df2.columns)
df2.time = df2.time.div(1000)

df3 = pd.read_csv(
    filename3,
    delimiter=",",
    skiprows=0
)
list(df3.columns)
df3.time = df3.time.div(1000)

df4 = pd.read_csv(
    filename4,
    delimiter=",",
    skiprows=0
)
list(df4.columns)
df4.time = df4.time.div(1000)




fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(11.7, 11.7))


# j=0
# for i, df in enumerate([df1, df2, df3, df4]):
#     row, col = divmod(i, 2)
#     ax = axes[row, col]

#     #plot df.def_energy and df.def_temperature in 2d position with color varying with time
#     points = np.array([df.def_energy, df.def_temperature]).T.reshape(-1, 1, 2)
#     segments = np.concatenate([points[:-1], points[1:]], axis=1)
#     lc = LineCollection(segments, cmap='plasma', norm=plt.Normalize(0, df.time.max()))
#     lc.set_array(df.time )
#     lc.set_linewidth(2)
#     lc.set_alpha(0.5)
#     line = ax.add_collection(lc)

#     # add crosses at start and end points with color coding
#     ax.plot(df.def_energy.iloc[0], df.def_temperature.iloc[0], 'm+', markersize=10, label='Start')
#     ax.plot(df.def_energy.iloc[-1], df.def_temperature.iloc[-1], 'r+', markersize=10, label='End')

#     plt.colorbar(line, ax=ax, label='Time (s)')
#     ax.set_xlim([0, 1])
#     ax.set_ylim([0, 1])
#     ax.spines['bottom'].set_position('zero')
#     ax.spines['left'].set_position('zero')
#     # make the aspect ratio of the plot equal
#     ax.set_aspect('equal', adjustable='box')
#     # add axes labels, title, and legend
#     ax.set_xlabel('ΔEnergy')
#     ax.set_ylabel('ΔTemperature')
#     ax.set_title('Activity cycle for N'+str(j+1))
#     ax.legend(loc='upper right')
#     ax.set_yticks(np.arange(0, 1.1, 0.25))
#     ax.set_xticks(np.arange(0, 1.1, 0.25))
#     # add overlays
#     overlay1 = 'Danger: unbalanced deficit'
#     #ax.text(0.05, 0.95, overlay1, color='white', fontsize=7, fontweight='bold', bbox=dict(facecolor='orange', edgecolor='none', alpha=0.5), transform=ax.transAxes, ha='left', va='top')
#     overlay2 = 'Danger: unbalanced deficit'
#     #ax.text(0.95, 0.05, overlay2, color='white', fontsize=7, fontweight='bold', bbox=dict(facecolor='orange', edgecolor='none', alpha=0.5), transform=ax.transAxes, ha='right', va='bottom')
#     overlay3 = 'Danger: high deficits'
#     #ax.text(0.95, 0.85, overlay3, color='white', fontsize=7, fontweight='bold', bbox=dict(facecolor='red', edgecolor='none', alpha=0.5), transform=ax.transAxes, ha='right', va='bottom')
#     overlay4 = 'Balanced deficits'
#     #ax.text(0.35, 0.05, overlay4, color='white', fontsize=7, fontweight='bold', bbox=dict(facecolor='green', edgecolor='none', alpha=0.5), transform=plt.gca().transAxes, ha='right', va='bottom')

#     ax.plot([0.5, 1], [1, 0.5], '--', color='black')
#     ax.plot([0.5, 0], [1, 0.5], '--', color='black')
#     ax.plot([0.5, 1], [0, 0.5], '--', color='black')
#     #shade the regions defined by the lines
#     ax.fill_between([0.5, 1], [1, 0.5], [1, 1], color='r', alpha=0.3)
#     ax.fill_between([0.5, 0], [1, 0.5], [1, 1], color='orange', alpha=0.3)
#     ax.fill_between([0.5, 1], [0, 0.5], [0, 0], color='orange', alpha=0.3)
#     j=j+1

# fig.savefig('AC_N.png', dpi=300, bbox_inches='tight')

# j=0
# for i, df in enumerate([df1, df2, df3, df4]):
#     row, col = divmod(i, 2)
#     ax = axes[row, col]

#     ax.plot(df.time, df.hormonal_concentration,alpha=1,c='r')
#     ax.plot(df.time, df.wellbeing,alpha=0.3,c='b')

#     ax.set_xlabel('Time (s)')
#     ax.set_ylabel('Cortisol')
#     ax.set_title('Intensity of cortisol over time for C'+str(j+1))
#     ax.legend(['cortisol level','Wellbeing'], loc='upper left')
#     ax.set_yticks(np.arange(0, 1.1, 0.1))
#     ax.set_ylim([0,1])
#     ax.set_xlim(left=0, right=max(df.time))

#     # Define the x and y coordinates for the arrows
#     n = int(df.time.size / 50)
#     x = df.time[::n]  # Plot an arrow every x rows
#     y = df.hormonal_concentration[::n]
#     dx = np.zeros_like(x)
#     dy = df.gland_release_rate[::n]

#     # Plot the arrows using quiver
#     ax.quiver(x, y, dx, dy, angles='xy', scale_units='xy', scale=1, color='k',alpha=0.5)
#     j=j+1

# fig.savefig('IOC.png', dpi=300, bbox_inches='tight')



def find_optimal_clusters(X):
    # calculate the within-cluster sum of squares (WSS) for different number of clusters
    wss_values = []
    for i in range(1, 11):
        kmeans = KMeans(n_clusters=i, random_state=42)
        kmeans.fit(X)
        wss_values.append(kmeans.inertia_)


    # find the "elbow" in the plot and return the corresponding number of clusters
    diff = np.diff(wss_values)
    diff_r = diff[1:] / diff[:-1]
    k_opt = 2 + diff_r.argmin()
    return k_opt



# j=0
# for i, df in enumerate([df1, df2, df3, df4]):
#     row, col = divmod(i, 2)
#     ax = axes[row, col]

#     X = df[['hormonal_concentration', 'gland_release_rate']].values
#     # set the number of clusters you want
#     if j == 0 or j == 3:
#         n_clusters = 1
#     else:
#         n_clusters = find_optimal_clusters(X)

#     # perform KMeans clustering
#     kmeans = KMeans(n_clusters=n_clusters, random_state=42)
#     labels = kmeans.fit_predict(X)


    
#     scatter = ax.scatter(X[:, 0], X[:, 1], c=labels, s=10)
#     #legend1 = ax.legend(*scatter.legend_elements(),
#     #                    loc="lower left", title="Clusters")
#     #ax.add_artist(legend1)

#     # add titles and labels
#     ax.set_title('Hormone Secretion Dynamics Graph for C'+str(j+1))
#     ax.set_ylabel('Gland Release Rate')
#     ax.set_xlabel('Hormonal Concentration')
#     ax.set_xticks(np.arange(0, 1.1, 0.1))
#     ax.set_ylim([0,0.05])
#     ax.set_xlim([0,1])
#     j=j+1

# fig.savefig('HVSRRCL.png', dpi=300, bbox_inches='tight')



# j=0
# for i, df in enumerate([df1, df2, df3, df4]):
#     row, col = divmod(i, 2)
#     ax = axes[row, col]

#     ax.plot(df.time, df.val_energy,alpha=0.5,c='m')
#     ax.plot(df.time, df.val_temperature,alpha=0.5,c='b')
#     ax.axhline(y=0.95, color='r', linestyle='--')
#     ax.axhline(y=0.05, color='r', linestyle='--')
#     ax.fill_between(df.time, 1.0, 0.95, color='g', alpha=0.3)
#     ax.fill_between(df.time, 0, 0.05, color='g', alpha=0.3)
#     ax.text(20,0.92,'critical temperature level',horizontalalignment='left',
#         verticalalignment='center',fontsize = 10)
#     ax.text(20,0.07,'critical energy level',horizontalalignment='left',
#         verticalalignment='center', fontsize = 10)
#     ax.text(5,0.98,'energy ideal values',horizontalalignment='left',
#         verticalalignment='center',fontsize = 10)
#     ax.text(5,0.02,'temperature ideal values',horizontalalignment='left',
#         verticalalignment='center', fontsize = 10)

#     ax.set_xlabel('Time (s)')
#     ax.set_ylabel('Value')
#     ax.set_title('Value of physiological variables over time for C'+str(j+1))
#     ax.set_yticks(np.arange(0, 1.1, 0.25))
#     ax.legend(['Energy', 'Temperature'], loc='upper right')
#     ax.set_ylim([0,1])
#     ax.set_xlim(left=0, right=max(df.time))
#     j=j+1


# fig.savefig('MOOT.png', dpi=300, bbox_inches='tight')



# fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(16, 9))
# df=df3
# plt.plot(df.time, df.val_energy,alpha=0.5,c='m')
# plt.plot(df.time, df.val_temperature,alpha=0.5,c='b')
# plt.axhline(y=0.95, color='r', linestyle='--')
# plt.axhline(y=0.05, color='r', linestyle='--')
# plt.fill_between(df.time, 1.0, 0.95, color='g', alpha=0.3)
# plt.fill_between(df.time, 0, 0.05, color='g', alpha=0.3)
# plt.text(20,0.92,'critical temperature level',horizontalalignment='left',
#     verticalalignment='center',fontsize = 10)
# plt.text(20,0.07,'critical energy level',horizontalalignment='left',
#     verticalalignment='center', fontsize = 10)
# plt.text(5,0.98,'energy ideal values',horizontalalignment='left',
#     verticalalignment='center',fontsize = 10)
# plt.text(5,0.02,'temperature ideal values',horizontalalignment='left',
#     verticalalignment='center', fontsize = 10)

# plt.xlabel('Time (s)')
# plt.ylabel('Value')
# plt.title('Value of physiological variables over time for C3')
# plt.yticks(np.arange(0, 1.1, 0.25))
# plt.legend(['Energy', 'Temperature'], loc='upper right')
# plt.gca().set_ylim([0,1])
# plt.gca().set_xlim(left=0, right=max(df.time))


# fig.savefig('PVC3.png', dpi=300, bbox_inches='tight')


# fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(10, 3))
# df=df3
# plt.fill_between(df.time, df.mot_danger, 0,
#             where = np.logical_and(np.greater_equal(df.mot_danger, df.mot_cold ), np.greater_equal(df.mot_danger, df.mot_hunger )),
#             color = 'r',
#             alpha = 0.3)
# plt.fill_between(df.time, df.mot_hunger, 0,
#             where = np.logical_and(np.greater_equal(df.mot_hunger, df.mot_cold ), np.greater_equal(df.mot_hunger, df.mot_danger )),
#             color = 'g',
#             alpha = 0.3)
# plt.fill_between(df.time, df.mot_cold, 0,
#             where = np.logical_and(np.greater_equal(df.mot_cold, df.mot_hunger ), np.greater_equal(df.mot_cold, df.mot_danger )),
#             color = 'b',
#             alpha = 0.3)
# plt.plot(df.time, df.mot_hunger,alpha=0.5,c='g') 
# plt.plot(df.time, df.mot_cold,alpha=0.5,c='b')
# plt.xlabel('Time (s)')
# plt.ylabel('Intensity of motivation')
# plt.title('Intensity of motivations over time')
# plt.legend(['Danger','Hunger', 'Cold'], loc='upper right')
# plt.yticks(np.arange(0, 1.1, 0.25))
# plt.gca().set_ylim([0,1])
# #plt.gca().set_xlim(left=0, right=None)
# plt.gca().set_xlim(left=0, right=max(df.time))


# fig.savefig('MOOTC3.png', dpi=300, bbox_inches='tight')




df = df3
un = ['0', '1', '2', '3', '4', '5', '6']
ylim = [0, 7]



fig = plt.figure(figsize=(10, 12))
gs = GridSpec(3, 3, figure=fig,wspace=0.5, hspace=0.2)

ax1 = fig.add_subplot(gs[0:2, :])
ultrasonic_sensors = ['noci_0', 'noci_1', 'noci_2', 'noci_3', 'noci_4', 'noci_5', 'noci_6']
ax1.set_title('Nociceptors')
ax1.set_xlabel('Time (s)')
ax1.set_ylabel('Sensor Number')
ax1.set_xlim(left=0, right=max(df.time))
ax1.set_yticks(np.arange(0.5, 7.5, 1), labels=un[::-1])
ax1.set_ylim(ylim)
sns.heatmap(df[ultrasonic_sensors].transpose(), cmap='Blues', vmin=0, vmax=1, ax=ax1)


ax2 = fig.add_subplot(gs[2, 0])
ultrasonic_sensors = ['sensor_prox_0', 'sensor_prox_1', 'sensor_prox_2', 'sensor_prox_3', 'sensor_prox_4', 'sensor_prox_5', 'sensor_prox_6']
sns.heatmap(df[ultrasonic_sensors].transpose(), cmap='Blues', vmin=0, vmax=1, ax=ax2)
ax2.set_title('Ultrasonic Sensor')
ax2.set_xlabel('Time (s)')
ax2.set_ylabel('Sensor Number')
ax2.set_xlim(left=0, right=max(df.time))
ax2.set_yticks(np.arange(0.5, 7.5, 1), labels=un[::-1])
ax2.set_ylim(ylim)


ax3 = fig.add_subplot(gs[2, 1])
ultrasonic_sensors = ['speed_0', 'speed_1', 'speed_2', 'speed_3', 'speed_4', 'speed_5', 'speed_6']
sns.heatmap(df[ultrasonic_sensors].transpose(), cmap='Blues', vmin=0, vmax=1, ax=ax3)
ax3.set_title('Speed damage')
ax3.set_xlabel('Time (s)')
ax3.set_ylabel('Sensor Number')
ax3.set_xlim(left=0, right=max(df.time))
ax3.set_yticks(np.arange(0.5, 7.5, 1), labels=un[::-1])
ax3.set_ylim(ylim)

ax4 = fig.add_subplot(gs[2, 2])
ultrasonic_sensors = ['circ_0', 'circ_1','circ_2', 'circ_3', 'circ_4', 'circ_5', 'circ_6']
sns.heatmap(df[ultrasonic_sensors].transpose(), cmap='Blues',vmin=0, vmax=1,ax=ax4)
# add titles and labels
ax4.set_title('Circular damage')
ax4.set_xlabel('Time (s)')
ax4.set_ylabel('Sensor Number')
ax4.set_xlim(left=0, right=max(df.time))
ax4.set_yticks(np.arange(0.5, 7.5, 1), labels=un[::-1])
ax4.set_ylim(ylim)





# set the background color of the first plot to white and remove the axis labels and ticks
ax1.set_facecolor('white')
ax1.axis('off')
# plot the other three figures
ax2.plot([1, 2, 3], [4, 5, 6])
ax3.plot([1, 2, 3], [6, 5, 4])
ax4.plot([1, 2, 3], [2, 4, 6])


for ax in [ax1, ax2, ax3, ax4]:
    ratio = 1.0
    x_left, x_right = ax.get_xlim()
    y_low, y_high = ax.get_ylim()
    ax.set_aspect(abs((x_right-x_left)/(y_low-y_high))*ratio)



fig.savefig('noci.png', dpi=300, bbox_inches='tight')
