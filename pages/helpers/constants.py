import matplotlib.patches as mpatches

RPE1_COLOR = '#5895fe'
RPE23_COLOR = '#78e0df'
RPE46_COLOR = '#87e740'
RPE78_COLOR = '#f5c545'
RPE9_COLOR = '#e98031'
RPE10_COLOR = '#e35022'

RPE_COLOR_DICT = {
    1: RPE1_COLOR,
    2: RPE23_COLOR,
    3: RPE23_COLOR,
    4: RPE46_COLOR,
    5: RPE46_COLOR,
    6: RPE46_COLOR,
    7: RPE78_COLOR,
    8: RPE78_COLOR,
    9: RPE9_COLOR,
    10: RPE10_COLOR,
}

RPE_LEGEND_LIST = [
    mpatches.Patch(color=RPE1_COLOR, label='Very Light'),
    mpatches.Patch(color=RPE23_COLOR, label='Light'),
    mpatches.Patch(color=RPE46_COLOR, label='Moderate'),
    mpatches.Patch(color=RPE78_COLOR, label='Vigorous'),
    mpatches.Patch(color=RPE9_COLOR, label='Very Hard'),
    mpatches.Patch(color=RPE10_COLOR, label='Max Effort'),
]

FEATURES_2_EXTRACT = [
    'total_distance', 'hsr_dist', 'sprint_dist', 'max_speed_km_h',
    'mpe_count', 'acc_events', 'dec_events', 'mpe_avg_rec_time'
]
