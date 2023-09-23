#! /usr/bin/env python3
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import pandas as pd
import os

BASE_DIR = os.path.dirname(__file__)

# Set style
plt.style.use('default')
plt.rcParams['font.size'] = 15

color = {
    'SelectFuzz':'forestgreen',
    'AFLGo': 'dodgerblue',
    'WindRanger':  'plum',
    'Beacon': 'darkorange',
    'DAFL': 'orangered',
}

markers = {
    'SelectFuzz': 's',
    'AFLGo': 'o',
    'WindRanger': 'D',
    'Beacon': 'x',
    'DAFL': 'd',
}


def draw_figure6(input_dir):
    output_dir = input_dir
    input_path = os.path.join(input_dir, "figure6.csv")

    df = pd.read_csv(input_path,  header=None)
    df=df.transpose()
    df.rename(columns=df.iloc[0],inplace=True)
    df = df.drop(df.index[0])

    tools = list(df)

    tool_dict = {}
    all_meds_10 = []
    all_meds_2040 = []

    for tool in tools:
        iters = [int(x) for x in list(df[tool])]
        global_med = np.median(iters)
        
        medians_10 = []
        for i in range(0, 160, 10):
            medians_10.append(np.median(iters[i:i+10]))
            all_meds_10 += medians_10

        medians_20 = []
        for i in range(0, 160, 20):
            medians_20.append(np.median(iters[i:i+20]))
            all_meds_2040 += medians_20

        medians_40 = []
        for i in range(0, 160, 40):
            medians_40.append(np.median(iters[i:i+40]))
        

        tool_dict[tool] = {
            'global_med': global_med,
            '10': medians_10,
            '20': medians_20,
            '40': medians_40
        }
        all_meds_10 += medians_10
        all_meds_2040 += medians_20
        all_meds_2040 += medians_40

        
    max_10 = np.max(all_meds_10)
    max_2040 = np.max(all_meds_2040)


    fig = plt.figure(figsize=(15, 9))
    gs = gridspec.GridSpec(2, 2, height_ratios=[2, 1.5])
    ax1 = plt.subplot(gs[0, :],zorder=2)
    ax2 = plt.subplot(gs[1, 0])
    ax3 = plt.subplot(gs[1, 1])



    for tool in tool_dict:
        ax1.plot(tool_dict[tool]["10"], label=tool, marker=markers[tool], linestyle='-', color=color[tool])
        ax2.plot(tool_dict[tool]["20"], label=tool, marker=markers[tool], linestyle='-', color=color[tool])
        ax3.plot(tool_dict[tool]["40"], label=tool, marker=markers[tool], linestyle='-', color=color[tool])
        
    plt.ylim([0,min(max_10 * (11/10), 86400)])

    # plt.ylim([0,1200])


    labels_16 = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", ]
    labels_8 = ["1", "2", "3", "4", "5", "6", "7", "8", ]
    labels_4 = ["1", "2", "3", "4", ]

    ax1.set_xticks(range(0,16), )
    ax2.set_xticks(range(0,8), )
    ax3.set_xticks(range(0,4),)

    ax1.set_xticklabels( labels_16)
    ax2.set_xticklabels(labels_8)
    ax3.set_xticklabels( labels_4)

    ax1.text(0.5, 1.1, '10 repetitions per trial', ha='center', va='center', transform=ax1.transAxes, fontsize=20)
    ax1.set_ylabel('Median TTE (sec)', fontsize=17)
    ax1.set_xlabel('Trials', fontsize=19)

    ax2.text(0.5, 1.1, '20 repetitions per trial', ha='center', va='center', transform=ax2.transAxes, fontsize=20)
    ax2.set_ylabel('Median TTE (sec)', fontsize=17)
    ax2.set_xlabel('Trials', fontsize=19)


    ax3.text(0.5, 1.1, '40 repetitions per trial', ha='center', va='center', transform=ax3.transAxes, fontsize=20)
    ax3.set_ylabel('Median TTE (sec)', fontsize=17)
    ax3.set_xlabel('Trials', fontsize=19)


    ax1.set_ylim(0,min(max_10 * (11/10), 86400))
    ax2.set_ylim(0,min(max_2040 * (12/10), 86400))
    ax3.set_ylim(0,min(max_2040 * (12/10), 86400))

    legend = ax1.legend(loc='upper right', ncol=3, fontsize=16)
    legend.set_zorder(1)

    plt.tight_layout()
    plt.subplots_adjust(top=0.93, hspace=0.35, wspace=0.2,left=0.075, bottom=0.09)


    plt.savefig(os.path.join(output_dir,'figure6.pdf'))


def draw_figure7(input_dir):

    output_dir = input_dir
    input_path = os.path.join(input_dir, "figure7.csv")

    df = pd.read_csv(input_path,  header=None)
    df=df.transpose()
    df.rename(columns=df.iloc[0],inplace=True)
    df = df.drop(df.index[0])

    tools = list(df)

    tool_dict = {}
    all_ttes = []
    for tool in tools:
        iters = [int(x) for x in list(df[tool]) if int(x) < 86400]
        iters.sort()
        all_ttes+= iters
        global_med = np.median(iters)
        tool_dict[tool] = {
            'ttes': iters
        }

    global_max = np.max(all_ttes)
    print("global max is %d" % global_max)

    # Draw linear scale cactus plot


    fig, ax = plt.subplots(figsize= (17,10))
    ax.tick_params(labelsize=40) 


    for tool in tool_dict:
        plt.step(range(1, len(tool_dict[tool]["ttes"]) + 1), tool_dict[tool]["ttes"] , label=tool, marker='+', linewidth=5, color=color[tool])

    
    x_ticks = [0, 20, 40, 60, 80, 100, 120, 140, 160]  # Set the positions of the x-axis ticks
    x_tick_labels = [str(x) for x in x_ticks]  # Set the x-ticks labels
    plt.xticks(x_ticks, x_tick_labels)

    y_ticks = [0, 5000, 10000, 15000, 20000]
    y_tick_labels = [str(x) for x in y_ticks]
    plt.yticks(y_ticks, y_tick_labels)


    plt.ylim([0,min(global_max , 86400)])
    plt.tight_layout()

    plt.legend( loc='upper left', fontsize=40,)

    plt.savefig(os.path.join(output_dir,'figure7-a.pdf'))



    # Draw log scale cactus plot

    fig, ax = plt.subplots(figsize= (17,10))
    ax.tick_params(labelsize=40) 

    ax.set_yscale('log')

    for tool in tool_dict:
        plt.step(range(1, len(tool_dict[tool]["ttes"]) + 1), tool_dict[tool]["ttes"] , label=tool, marker='+', linewidth=5, color=color[tool])

    
    x_ticks = [0, 20, 40, 60, 80, 100, 120, 140, 160]  # Set the positions of the x-axis ticks
    x_tick_labels = [str(x) for x in x_ticks]  # Set the x-ticks labels
    plt.xticks(x_ticks, x_tick_labels)

    y_ticks = [1, 10, 100, 1000, 10000]
    y_tick_labels = [r'$10^0$', r'$10^1$', r'$10^2$', r'$10^3$', r'$10^4$']
    plt.yticks(y_ticks, y_tick_labels)


    plt.ylim([0,min(global_max , 86400)])
    plt.tight_layout()

    plt.savefig(os.path.join(output_dir,'figure7-b.pdf'))


def draw_result(output_dir, target):
    if target == "figure6":
        draw_figure6(output_dir)
    elif target == "figure7":
        draw_figure7(output_dir)
    else:
        print("Plotting not supported for this set of targets!")