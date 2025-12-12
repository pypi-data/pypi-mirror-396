import os
# import cv2
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import numpy as np
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import pandas as pd
import seaborn as sns
# general settings
pal_raw = sns.color_palette("Set3", as_cmap=False)
assert isinstance(pal_raw, list) 
pal_set3 = [
    pal_raw[0], pal_raw[2], pal_raw[3], pal_raw[4], pal_raw[5], pal_raw[6], pal_raw[7],
]

def boot_trap_ste(data: np.ndarray,  axis: int, num_boot: int=10):

    data_stds = []
    n = data.shape[axis]
    sample_size = n
    for _ in range(num_boot):
        data_index = np.random.choice(n, sample_size, replace=True)
        sample = np.take(data, data_index, axis=axis)
        _std = np.std(sample, axis=axis, ddof=1)
        data_stds.append(_std)
    return np.mean(data_stds,  axis = 0)/np.sqrt(n)

# colors = ["#81B2D3", "#FDBE6E", "#CE91BE"]
# select_rk = 1

def create_figure(rows: int, cols: int, row_size: int=4, col_size: int=10, **kwargs):
    # 创建一个大的Figure对象，设置为3x3网格
    fig = plt.figure(dpi=300, figsize=(col_size*cols, row_size*rows))
    # 通过 GridSpec 创建一个3x3的布局
    axs = GridSpec(rows, cols, figure=fig, **kwargs)
    return fig, axs
    # ax = fig.add_subplot(outer_gs[i, j])
    
def save_ylim(ax, axs_ylim, ylim_all):
    axs_ylim.append(ax)
    ylim_all.append(ax.get_ylim())
    
def set_ylim_all(axs, ylim_all, low_value=None):
    # 批量设置子图的y轴范围
    for ax in axs:
        if low_value is None:
            ax.set_ylim(np.min(ylim_all), np.max(ylim_all))
        else:
            ax.set_ylim(low_value, np.max(ylim_all))
        # if max(ylim_all)<300:
        #     major_locator = MultipleLocator(50)
        #     ax.yaxis.set_major_locator(major_locator)
        # elif max(ylim_all)<600:
        #     major_locator = MultipleLocator(100)
        #     ax.yaxis.set_major_locator(major_locator)

def plot_mean_function(ax, rank, data, data_labels, title, pos, lbs, axvline_lbs):
    data = data(rank)
    data_labels = data_labels(rank)

    for item in range(6):
        kwargs = {"label": f"item{item+1}", 
                "color": pal_set3[item], 
                "linewidth": 2}

        trial_idx = data_labels == (item+1)
        data_mean = np.mean(data[trial_idx, :], axis=0)
        ax.plot(data_mean, **kwargs)

        data_std = boot_trap_ste(data[trial_idx, :], axis=0)
        upper_bound = data_mean + data_std
        lower_bound = data_mean - data_std
        if "label" in kwargs:
            kwargs['label'] = None
        ax.fill_between(range(data_mean.shape[0]), lower_bound, upper_bound, alpha=0.1, **kwargs)

    ax.set_title(title)
    ax.set_xticks(ticks=pos, labels=lbs, rotation=45, ha='right')
    for lbs_i in axvline_lbs:
        ax.axvline(pos[lbs.index(lbs_i)], color='black', ls="--", alpha=0.1,)
    ax.legend(loc='best')

def apply_rank(template: dict, rank: int):
    """
    把模板里的 lambda 递归地替换成实际值。
    如果某个 value 是 list, 还会把 list 里的 callable 也递归展开。
    """
    def resolve(obj):
        if callable(obj):
            return obj(rank)
        elif isinstance(obj, list):
            return [resolve(el) for el in obj]
        elif isinstance(obj, dict):
            return {k: resolve(v) for k, v in obj.items()}
        else:
            return obj

    return {k: resolve(v) for k, v in template.items()}
    
def plot_raw_function(ax, rank, data, title, pos, lbs, axvline_lbs):
    data = data(rank)
    
    for item in range(6):
        kwargs = {"label": f"item{item+1}", 
                "color": pal_set3[item], 
                "linewidth": 2}

        ax.plot(data[:, item], **kwargs)
        
    ax.set_title(title)
    ax.set_xticks(ticks=pos, labels=lbs, rotation=45, ha='right')
    for lbs_i in axvline_lbs:
        ax.axvline(pos[lbs.index(lbs_i)], color='black', ls="--", alpha=0.1,)

def plot_psth_mean(
    ax, 
    labels, 
    data, 
    pos,
    lbs,
    title,
    axvline_lbs):
    for item in range(6):
        kwargs = {"label": f"item{item+1}", 
                "color": pal_set3[item], 
                "linewidth": 2}

        trial_idx = labels == (item+1)
        data_mean = np.mean(data[trial_idx, :], axis=0)
        ax.plot(data_mean, **kwargs)
        
        if "label" in kwargs:
            kwargs['label'] = None
        data_std = boot_trap_ste(data[trial_idx, :], axis=0)
        upper_bound = data_mean + data_std
        lower_bound = data_mean - data_std
        ax.fill_between(range(data_mean.shape[0]), lower_bound, upper_bound, alpha=0.1, **kwargs)

    ax.set_title(title)
    ax.set_xticks(ticks=pos, labels=lbs, rotation=45, ha='right')
    for lbs_i in axvline_lbs:
        ax.axvline(pos[lbs.index(lbs_i)], color='black', ls="--", alpha=0.1,)
    ax.legend(loc='best')
    return ax

def plot_acc_std_arr(
    fig, ax, acc_arr, std_arr, pos, lbs, 
    decoder_time=None, select_rk = 1, 
    ylabel: str="", colors: list=["#81B2D3", "#FDBE6E", "#CE91BE"], alphas: list=[1.0,1.0,1.0],
    plot_legends: list=[True,True,True]
    ):

    if fig is None or ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(10, 4))

    if decoder_time is not None:
        acc_arr = acc_arr[decoder_time,:]
        std_arr = std_arr[decoder_time,:]

    ax.plot(acc_arr, c=colors[select_rk], linewidth=3, alpha=alphas[select_rk])
    ax.fill_between(
        np.arange(acc_arr.shape[0]),
        acc_arr - std_arr,
        acc_arr + std_arr,
        alpha=alphas[select_rk]/5,
        color=colors[select_rk]
    )
    # ax.set_xlabel("Time")
    ax.set_ylabel(ylabel, fontsize=14)

    ymax = max(1, (acc_arr + std_arr).max())
    if ymax >= 1.:
        ymax = 1.05
    ax.set_ylim(0, ymax)
    ax.set_xlim(0, acc_arr.shape[0] - 1)

    # ax.grid(True, ls="--", alpha=0.5)

    for p in pos:
        ax.axvline(p, ls="--", alpha=0.5, color='grey')
    ax.set_xticks(pos)
    ax.set_xticklabels(lbs, fontsize=20, rotation=45, ha='right')

    if plot_legends[select_rk]:
        legend = ax.get_legend()
        handles, labels = [], []

        if legend:
            handles = legend.legend_handles          # legend中保存的句柄
            labels = [text.get_text() for text in legend.get_texts()]  # 每个文本标签

        label = f"S{select_rk + 1}"
        if label not in labels:
            patch = mpatches.Patch(color=colors[select_rk], label=label)  # 仅用于 legend
            handles.append(patch)
            labels.append(label)
            ax.legend(handles=handles, labels=labels, loc='best', fontsize=18)

    if decoder_time is not None:
        ax.axvline(x=decoder_time, color='r', linestyle='-', alpha=0.5)
    
    return fig, ax

def plot_mean_with_std(data_mean, data_std, var_type="all", ax=None, **kwargs):
    upper_bound = data_mean + data_std
    lower_bound = data_mean - data_std

    if var_type in ("all", "fill"):
        # Fill the area between the upper and lower bounds
        if ax is None:
            plt.fill_between(range(data_mean.shape[0]), lower_bound, upper_bound, alpha=0.1, **kwargs)
        else:
            ax.plot(data_mean, **kwargs)
            if "label" in kwargs:
                kwargs['label'] = None
            ax.fill_between(range(data_mean.shape[0]), lower_bound, upper_bound, alpha=0.1, **kwargs)
            
    
    if var_type in ("all", "bar"):
        # Error bar
        if ax is None:
            plt.errorbar(range(data_mean.shape[0]), data_mean, yerr=data_std, capsize=5, **kwargs)
        else:
            ax.errorbar(range(data_mean.shape[0]), data_mean, yerr=data_std, capsize=5, **kwargs)

def plot_box_of_data(data, ax=None, **kwargs):
    if ax is None:
        bplot = plt.boxplot(data, patch_artist=True, **kwargs)
    else:
        bplot = ax.boxplot(data, patch_artist=True, **kwargs)
    return bplot

def plot_mean_with_var(data_mean, data_var, var_type="all", ax=None, **kwargs):
    upper_bound = data_mean + np.sqrt(data_var)
    lower_bound = data_mean - np.sqrt(data_var)

    if var_type in ("all", "fill"):
        # Fill the area between the upper and lower bounds
        if ax is None:
            plt.fill_between(range(data_mean.shape[0]), lower_bound, upper_bound, alpha=0.1, **kwargs)
        else:
            ax.fill_between(range(data_mean.shape[0]), lower_bound, upper_bound, alpha=0.1, **kwargs)
    
    if var_type in ("all", "bar"):
        # Error bar
        if ax is None:
            plt.errorbar(range(data_mean.shape[0]), data_mean, yerr=np.sqrt(data_var), capsize=5, fmt="o--", **kwargs)
        else:
            ax.errorbar(range(data_mean.shape[0]), data_mean, yerr=np.sqrt(data_var), capsize=5, fmt="o--", **kwargs)

def plot_violin(ax, effect_value, value_title):
    df = pd.DataFrame(effect_value)
    df_melted = df.melt(var_name='Group', value_name='Log Effect Size')
    sns.violinplot(data=df_melted, x='Group', y='Log Effect Size',
                    hue='Group', inner='quart', palette='muted', ax=ax)
    ax.set_title(value_title, fontsize=8)
    return ax

# def create_mp4(CONFIG, seq_len, test_decoders, num_times, mp4_name):

#     seq_type = f"seqLen{seq_len}"
#     pos = CONFIG[CONFIG['data_type']]['stretched_wds'][seq_type]['pos']
#     lbs = CONFIG[CONFIG['data_type']]['stretched_wds'][seq_type]['lbs']

#     for decoder_time in range(num_times):
#         rows = seq_len
#         cols = 1
#         fig, axs = create_figure(rows, cols)
#         fig.suptitle("Pure Item Information", fontsize=22)
#         sub_i = 0
#         for decoder_i in range(seq_len):
#             ax = fig.add_subplot(axs[sub_i // cols, sub_i % cols])
#             sub_i += 1
            
#             for test_rank in range(seq_len):
#                 acc_arr = test_decoders[f'rank{decoder_i+1}Decoder'][f'test_on_rank{test_rank+1}']['acc_mat']
#                 std_arr = test_decoders[f'rank{decoder_i+1}Decoder'][f'test_on_rank{test_rank+1}']['std_mat']
#                 plot_acc_std_arr(fig, ax, acc_arr, std_arr, pos=pos, lbs=lbs, decoder_time=decoder_time,
#                                     select_rk = test_rank, ylabel=f"Rank{decoder_i+1}")

#         plt.tight_layout()
#         plt.savefig(f'decoder_time_{decoder_time}.jpg')
#         plt.close()


#     # 获取所有jpg文件并按数字顺序排序
#     image_files = sorted([f for f in os.listdir() if f.startswith(f'decoder_time_') and f.endswith('.jpg')],
#                         key=lambda x: int(x.split('_')[-1].split('.')[0]))

#     # 读取第一张图片获取尺寸
#     frame = cv2.imread(image_files[0])
#     height, width, _ = frame.shape

#     # 创建视频写入器
#     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#     out = cv2.VideoWriter(f'{mp4_name}', fourcc, 2, (width, height))

#     # 逐帧写入
#     for image_file in image_files:
#         frame = cv2.imread(image_file)
#         out.write(frame)

#     # 释放资源
#     out.release()

#     # 删除临时jpg文件
#     for image_file in image_files:
#         os.remove(image_file)