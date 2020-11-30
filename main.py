from environment import environment
from agents import robot_reactive, robot_proactive
from math import floor

rows = [8] * 10
cols = [8] * 10
t = [i for i in range(5, 15)]
childs = [i for i in range(1, 8)] + [i for i in range(3, 6)]
childs.sort()
obstacles_p = [i for i in range(25, 5, -2)]
dirt_p = [i for i in range(25, 5, -2)]

def test():
    env = environment(8, 8, 10, 4, 10, 10, robot_reactive)
    print(env.simulate())
# test()

def run(robot_kind):
    sim = []
    for i in range(10):
        mean = 0
        win = 0
        lose = 0
        for seed in range(30):
            env = environment(rows[i], cols[i], t[i], childs[i], obstacles_p[i], dirt_p[i], robot_kind, seed)
            state, dirt_mean = env.simulate()
            if state == +1:
                win += 1
            if state == -1:
                lose += 1
            mean += dirt_mean
        mean /= 30
        sim.append((win, lose, mean))
    return sim

reactive_sim = run(robot_reactive)
proactive_sim = run(robot_proactive)

# print('reactive_sim')
# print(reactive_sim)
# print('proactive_sim')
# print(proactive_sim)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import six

df = pd.DataFrame()
df['t'] = t
df['Niños'] = childs
df['Obstaculos'] = obstacles_p
df['Suciedad'] = dirt_p
df['Proactivo F'] = [i[0] for i in proactive_sim]
df['Proactivo D'] = [i[1] for i in proactive_sim]
df['Proactivo P'] = [str(floor(i[2]*100000) / 100000) for i in proactive_sim]
df['Reactivo F'] = [i[0] for i in reactive_sim]
df['Reactivo D'] = [i[1] for i in reactive_sim]
df['Reactivo P'] = [str(floor(i[2]*100000) / 100000) for i in reactive_sim]

def render_mpl_table(data, col_width=8.0, row_height=0.625, font_size=14,
                     header_color='#40466e', row_colors=['#f1f1f2', 'w'], edge_color='w',
                     bbox=[0, 0, 1, 1], header_columns=0,
                     ax=None, **kwargs):
    if ax is None:
        size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
        fig, ax = plt.subplots(figsize=size)
        ax.axis('off')

    mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns, **kwargs)

    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)

    for k, cell in  six.iteritems(mpl_table._cells):
        cell.set_edgecolor(edge_color)
        if k[0] == 0 or k[1] < header_columns:
            cell.set_text_props(weight='bold', color='w')
            cell.set_facecolor(header_color)
        else:
            cell.set_facecolor(row_colors[k[0]%len(row_colors) ])
    return ax

render_mpl_table(df, header_columns=0, col_width=2.0).get_figure().savefig('fig')