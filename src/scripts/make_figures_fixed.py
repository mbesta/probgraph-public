# -*- coding: utf-8 -*-
"""
Created on Wed May 19 12:01:18 2021
@author: Paolo
"""

import os
import math
import argparse
import matplotlib.pyplot as plt
import pandas as pd
import itertools
from matplotlib.lines import Line2D
import matplotlib.font_manager
from matplotlib import rcParams, rcParamsDefault
import numpy as np;
from matplotlib import colors
from cycler import cycler
from math import log

# Global Parameter to enable or disable LaTeX
latex_en = True

def adapt_graph_names(graph_names):
    graph_names_fixed = []
    name_map = {
        "Si10H16.el" : "ch-Si10H16.el",
        "SiO.el" : "ch-SiO.el",
        "ca-AstroPh.el" : "int-citAsPh.el",
        "gupta3.el" : "sc-OptGupt.el",
        "ted_AB.el" : "sc-ThermAB.el",
        "p-hat1500-3.el" : "dimacs-hat1500-3.el",
        }
    for name in graph_names:
        if name in name_map:
            graph_names_fixed.append(name_map[name])
        else:
            graph_names_fixed.append(name)
    return graph_names_fixed

def bsh(text):
    return "`" + text + "`"

def make_title(dictionary):
    title = ""
    for key in dictionary:
        title += "key: " + str(dictionary[key]) + "\n";
    return title;

def plot_comparison_fixed_all_schemes(problem = "TC", thresholds = {"BF" : 0.5,"MH" : 0.01}, x = 'speed_up_count_only', xlabel = "Speed-up vs baseline", y = 'count_ratio', ylabel = "Relative count"):

    plt.rcParams['text.usetex'] = latex_en
    plt.rcParams['font.size'] = 24

    if problem == "TC":
        thresholds["Sampling"] = 0;
        thresholds["Coloring"] = 0;
    
    thresholds["Exact"] = 0;
    savename = "comparison_fixed_all_schemes_" + exp_name + "_" + x + "_vs_" + y + "_" + problem + "_b_-1" + ".pdf"; 
    fig = plt.figure()


    fig, ax = plt.subplots(1,1, figsize = (6,6))
    plt.subplots_adjust(left = 0.1, top = 0.95, bottom = 0.15, right = 0.85)
    
    #ax.set_ylim(0);
    #ax.set_xlim(0);

    plt.grid(b=True, which='major', color='#666666', linestyle='-', alpha = 0.4)
    plt.minorticks_on()
    plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2, linewidth=0.5)


    marker = {"BF":'^', 
         "MH": 's', 
         "Sampling":'X', 
         "Coloring": 'o',
         "Exact": '*'}
         
    ymax = 0;

    for scheme, threshold in thresholds.items():
        q = "Problem==@problem and `approximation-scheme`==@scheme and " + x + ">0 and " + y +" >0"
        if scheme == "MH" or scheme == "BF":
            q += "and treshold==@threshold";
        x = x;
        y = y;
        tmp_df = df.query(q).sort_values(by=x)
        xlist  = np.array(tmp_df[x]); 
        ylist  = np.array(tmp_df[y]);
        if len(xlist) == 0 or len(ylist) == 0:
            continue

        ymax = max(ymax, np.max(ylist))
        clist = np.array(tmp_df["mem_ratio"])
        if scheme == "Exact":
            s = 200;
        else:
            s = 100;
        sc = ax.scatter(x = xlist, y = ylist, c = clist, linewidth=0.5, s=s, label = scheme, marker = marker[scheme], cmap = "Greys", edgecolor = "black", vmin = 1, vmax = 3, alpha = 0.8)
        #for i, txt in enumerate(tlist):
        #    ax.annotate(str(txt)[0:3], (xlist[i], ylist[i]))



    if ymax < 1.5: ymax = 1.5;
    if ymax > 5: ymax = 5;
    ax.set_ylim(bottom = 0, top = ymax);
    ax.set_aspect(1./ax.get_data_ratio())
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.colorbar(sc).set_label(label="Relative memory")
    plt.legend(prop={"size":20} ,labelspacing = 0.1, handletextpad=0.02, loc = "upper center", ncol = 3, bbox_to_anchor=(0.5, 1.23), borderpad = 0.1, columnspacing = 0.1, handlelength = 1.5)
    
    folder = image_folder + "comparison_fixed_thresh_all_schemes/"
    try:
        os.mkdir(folder)
    except OSError as error:
        print(error) 

    plt.savefig(folder + savename, format = 'pdf', dpi=300, bbox_inches = "tight")
    plt.close();




def bar_plot(graph_list, problem, 
        thresholds = {"BF" : 0.1,"MH" : 0.001}):

    plt.rcParams['text.usetex'] = latex_en 
    plt.rcParams['font.size'] = 24

    x_tick_size = 10;
    scheme_list = ["BF","MH"];
    if problem == "TC":
        scheme_list.append("Sampling");
        scheme_list.append("Coloring");
    scheme_list.append("Exact")

    n_schemes = len(scheme_list);

    measures = ["speed_up_count_only", "count_ratio", "mem_ratio"];
    names = {mes : n for mes,n in zip(measures, ["   SPEED-UP   ","RELATIVE COUNT","RELATIVE MEMORY"])}
    values = {mes : {} for mes in measures};

    for mes in measures:
        values[mes] = {};
        for scheme in scheme_list:
            values[mes][scheme] = {g : -1 for g in graph_list};

    used_graphs = []
    failed_graphs = {};

    q = "Problem==@problem";
    for graph in graph_list:                
        graph_ok = True;
        tmp_q = q + " and `graph-name`==@graph"

        for mes in measures:
            values[mes]["Exact"][graph] = 1.

        for scheme in scheme_list:
            if (scheme != "Exact"):
                if (scheme != "Coloring" and scheme != "Sampling"):
                    threshold = thresholds[scheme];         
                    tmp_q_2 = tmp_q + " and `approximation-scheme`==@scheme and `treshold`==@threshold";
                else:
                    tmp_q_2 = tmp_q + " and `approximation-scheme`==@scheme";

                try:
                    for mes in measures:
                            val = df.query(tmp_q_2)[mes].values[0];
                            values[mes][scheme][graph] = val;
                            if val < 0:
                                raise ValueError('Negative value found for mes' + mes + " and scheme " + scheme)
                except Exception as e:
                    if debug != "False" : print("error: ",e, "for graph", graph, " and scheme ", scheme)
                    graph_ok = False;            
                    
        if graph_ok:        
            used_graphs.append(graph)


    plt.style.use('grayscale')    
    width = 12 if len(used_graphs) < 25 else 18
    fig, axs = plt.subplots(3, figsize = (width,9), sharex= True)
    plt.subplots_adjust(wspace=0, hspace=0.2)

    colormap = plt.cm.Greys
    for ax in axs:
        ax.tick_params(axis='x', colors='grey')
        ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.3, linewidth=0.6)
        ax.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2, linewidth=0.4)
        ax.set_prop_cycle(color=[colormap(i) for i in np.linspace(0, 1,n_schemes)])

    graph_names_adapted = adapt_graph_names(used_graphs)
    graph_names = [g.split(".")[0].replace("_","\_") for g in graph_names_adapted]
    positions = np.array(range(len(used_graphs)));
    space = 0.2;
    width = (1. - space)/len(scheme_list);


    #BARPLOTS
    for ax, mes in zip(axs, measures):
        rel_pos = (-1. + space)/2
        for scheme in scheme_list:
            ax.bar(positions + rel_pos,[values[mes][scheme][g] for g in used_graphs], width = width, label = scheme, edgecolor = "black", lw = 0.3);
            ax.set_title(names[mes], fontsize = 18, ha = "left", x = 0)
            """
            ax.text(0.01, 0.5, names[mes], rotation=90,
                verticalalignment='center', horizontalalignment='center',
                transform=ax.transAxes,
                bbox=dict(boxstyle="square",facecolor='grey', edgecolor='black'),
                color='white', fontsize=9)
            """

            rel_pos += width;
    

    #XTICKS and graph names
    for ax in axs[:-1]:
        ax.xaxis.set_visible(False)
    axs[-1].set_xticks(positions);
    axs[-1].minorticks_off();
    axs[-1].set_xticklabels(graph_names, color = "black");
    axs[-1].xaxis.set_visible(True)

    #YTICKS 
    (ymin, ymax) = axs[1].get_ylim()
    axs[1].set_ylim(0,min(ymax, 10))
    for ax in axs:
        (ymin, ymax) = ax.get_ylim()
        positions = [x * math.ceil(ymax) / 4 for x in range(5)]
        ax.set_yticks(positions);

    fig.autofmt_xdate(rotation=45)  

    #LEGEND 
    h, l = axs[0].get_legend_handles_labels() # Extracting handles and labels
    ph = [plt.plot([],marker="", ls="")[0]] # Canvas
    plt.legend(h, l, loc='upper left', ncol = 3, frameon=False,prop={"size":20},bbox_to_anchor=(0, 3.45))


    folder = image_folder + "bar_plots/"
    try:
        os.mkdir(folder)
    except OSError as error:
        print(error) 

    savename = "barplot_test_" + exp_name + problem + "." + img_format;
    plt.savefig(folder + savename, format = img_format, dpi=resolution, bbox_inches = "tight")
    plt.close();

    return used_graphs;



if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Make images from an experiments csv (obtained with collect_into_csv.py)")
    
    parser.add_argument("--input-csv", default="?",
        help="csv file with experiments data")
    parser.add_argument("--image-folder", default="?",
        help="ouput folder for images")   
    parser.add_argument("--max-vertices", default=2000000,
        help="ouput folder for images")   
    parser.add_argument("--kron", default="True",
        help="using kroneckers?")  
    parser.add_argument("--img_format", default="pdf",
        help="image format")  
    parser.add_argument("--resolution", default=300,
        help="image resolution")  
    parser.add_argument("--bf", default=0.5,
        help="BF thresh to use")  
    parser.add_argument("--mh", default=0.01,
        help="MH thresh to use")
    parser.add_argument("--debug", default="False",
        help="print debug")


    args = parser.parse_args()

    csv_filename = args.input_csv;
    image_folder = args.image_folder;
    max_vertices = int(args.max_vertices);
    kron = args.kron == "True";
    img_format = args.img_format;
    resolution = int(args.resolution)
    debug = args.debug;





    selected_threshold = {
        "BF" : float(args.bf),
        "MH" : float(args.mh)
        #"KMV" : 0.01,
        #"KH" : 0.01
    }
    font = {'fontsize'   : 10, "weight" : "ultralight"}
    
    df = pd.read_csv(csv_filename);

    forbidden_graphs = ["movielens-10m-noRatings.el","ia-retweet-pol.el","email-dnc.el","bio-human-gene2.el","ia-wikiquote-user-edits.el","web-NotreDame.el","jester2.el","CO.el","appu.el","fb-messages.el"]

    allowed_graphs = ["bio-CE-CX.el","bio-HS-CX.el","bio-WormNet-v3.el","gupta3.el","econ-beaflw.el","econ-psmigr2.el","SiO.el",
                        "bio-CE-PG.el","bio-HS-LC.el","ca-AstroPh.el","econ-mbeacxc.el","p-hat1500-3.el","ted_AB.el",
                        "bio-DM-CX.el","bio-DR-CX.el","bio-SC-HT.el","econ-beacxc.el","econ-psmigr1.el","Si10H16.el","bn-mouse_brain_1.el","bio-SC-GT.el","econ-orani678.el"]


    df.replace(to_replace="1H", value="MH", inplace = True)
    df.replace(to_replace="DOULION", value="Sampling", inplace = True)
    df.replace(to_replace="COLORFUL", value="Coloring", inplace = True)
    df.replace(to_replace="BASE", value="Exact", inplace = True)


    #use the proper kronekers name
    def kronecker_fix_name(x):
        name = ""
        if (x["graph-name"] == "kronecker"):
            name =  "KR-" + str(int(log(int(x["vertices"]),2))) + "-" + str(int(x["edges"]/x["vertices"]))
        else:
            name=  x["graph-name"]
        return name

    if kron:
        exp_name = "kron_"
        df.drop(df[df['graph-name'] != "kronecker"].index, inplace = True)
        df["graph-name"] = df.apply(kronecker_fix_name, axis=1)
    else:
        exp_name = "real_"
        for graph in forbidden_graphs:
            df.drop(df[df['graph-name'] == graph].index, inplace = True)
        df = df.loc[df['graph-name'].isin(allowed_graphs)]


    #fixing some graph names
    df.replace(to_replace="Sio.el", value="ch-SiO.el", inplace = True)
    df.replace(to_replace="ca-AstroPh.el", value="int-citAsPh.el", inplace = True)
    df.replace(to_replace="gupta3.el", value="sc-OptGupt.el", inplace = True)
    df.replace(to_replace="ted-AB.el", value="sc-ThermAB.el", inplace = True)
    df.replace(to_replace="p-hat1500-3.el", value="dimacs-hat1500-3.el", inplace = True)


    graph_list = list(df.sort_values(["vertices"], ascending = False)["graph-name"].unique())
    #collect exact values for each graph and use them to create the ratio column; 
    true_counts = {};
    base_time = {};
    Coloring_time = {};
    Sampling_time = {};

    for g in graph_list:
        

        try:
            true_counts[g] = int((df[(df["graph-name"]==g) & (df["approximation-scheme"]=="Exact")])['approximated-count'].values[0]);
            if true_counts[g] == 0:
                true_counts[g] = -1;
            base_time[g] = (df[(df["graph-name"]==g) & (df["approximation-scheme"]=="Exact")])['total-runtime'].values[0];
        except:
            base_time[g] = -1;
            true_counts[g] = -1;



        try:
            Coloring_time[g] = (df[(df["graph-name"]==g) & (df["approximation-scheme"]=="Coloring")])['total-runtime'].values[0];
            Sampling_time[g] = (df[(df["graph-name"]==g) & (df["approximation-scheme"]=="Sampling")])['total-runtime'].values[0];
        except:
            Coloring_time[g] = -1;
            Sampling_time[g] = -1;


    df["density"] = df.apply(lambda x: float(x['edges'])/float(x['vertices']**2), axis=1)
    df["count_ratio"] = df.apply(lambda x: float(x['approximated-count'])/float(true_counts[x['graph-name']]), axis=1)
    df["mem_ratio"] = df.apply(lambda x: float(x['total-size'])/float(x['CSR-size']), axis=1)
    df["time_vs_baseline"] = df.apply(lambda x: x['total-runtime']*1./base_time[x['graph-name']], axis=1)
    df["time_vs_baseline_count_only"] = df.apply(lambda x: x['tc-time']*1./base_time[x['graph-name']], axis=1)
    df["time_vs_baseline_prep_only"] = df.apply(lambda x: x['preprocessing-time']*1./base_time[x['graph-name']], axis=1)
    df["speed_up"] = df.apply(lambda x: base_time[x['graph-name']]*1./x['total-runtime'], axis=1)
    df["speed_up_count_only"] = df.apply(lambda x: base_time[x['graph-name']]*1./x['tc-time'], axis=1)


    graph_names = graph_list;
    #graph selection /deactivated for the moment

    problem_list = list(df["Problem"].unique())
    problem = problem_list[0];
        
#GENERAL VARIABLES: 
#type,Problem,approximation-scheme,baseline,graph-name,thread-count,vertices,edges,treshold,b,m,approximated-count

#PERFORMANCE VARIABLES
#preprocessing-time,tc-time,total-runtime"

#SIZE VARIABLES: 
#size-of-BF,CSR-size,total-size

#make Table
#columns = ["vertices", "edges", "avg_degree", "best_threshold", "ratio_at_best_tresh"] 
#the_table = plt.table(cellText=cell_text,
#                    rowLabels=graph_list
#                    colLabels=columns,
#                    loc='bottom')


graph_names = bar_plot(graph_names, problem, selected_threshold);
df = df.loc[df['graph-name'].isin(graph_names)]


plot_comparison_fixed_all_schemes(problem = problem, thresholds = selected_threshold);

x = 'time_vs_baseline_prep_only'
y = 'time_vs_baseline_count_only'
