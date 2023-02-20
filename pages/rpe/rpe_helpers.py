from datetime import timedelta
from pages.helpers.constants import RPE_COLOR_DICT
import pandas as pd


def get_rpe_questioneer_df(worksheet) -> pd.DataFrame:
    rows = worksheet.get_all_values()
    df = pd.DataFrame(rows)
    df.columns = df.iloc[0]
    df = df.iloc[1:]

    df = df.rename(columns={
        'Timestamp': 'timestamp',
        'Имя Фамилия / Player': 'name',
        'Дата / Session date': 'session_date',
        'RPE': 'rpe'
    })
    df.name = df.name.str.replace('\t', '')
    df.name = df.name.str.upper()
    # reverse player names
    # df.name = df.name.str.replace(r'(.+)\s(.+)', r'\2 \1')
    df.timestamp = pd.to_datetime(df.loc[:, 'timestamp'])
    df = df.dropna()

    df.loc[:, 'session_date'] = df.apply(lambda r: f'{r.session_date}/{r.timestamp.year}', axis=1)
    df.session_date = pd.to_datetime(df.session_date)

    # move to the correct timezone
    df.timestamp = df.loc[:, 'timestamp'].apply(lambda r: r + timedelta(hours=1))
    return df


def extract_players_rpe_mean_and_std(session_df: pd.DataFrame, all_df: pd.DataFrame) -> tuple:
    before_df = all_df[all_df.session_date < session_df.iloc[0].session_date]
    players = session_df.name.unique()
    mean_list = []
    std_list = []
    for player in players:
        player_df = before_df[before_df.name == player]
        mean_list.append(player_df.rpe.mean())
        std_list.append(player_df.rpe.std())
    return mean_list, std_list


def define_colors_depending_on_std(session_df: pd.DataFrame, mean_list: list, std_list: list) -> list:
    players = session_df.name.unique()

    DANGER = 'tomato'
    WARNING = '#ffcc00'
    NORMAL = 'skyblue'
    colors = []
    for player, p_mean, p_std in zip(players, mean_list, std_list):
        value = session_df[session_df.name == player].rpe.iloc[0]

        if ((p_mean - 2 * p_std) > value) or (value > (p_mean + 2 * p_std)):
            colors.append(DANGER)
        elif ((p_mean - p_std) > value) or (value > (p_mean + p_std)):
            colors.append(WARNING)
        else:
            colors.append(NORMAL)
    return colors


def define_RPE_colors(values: list) -> list:
    colors = []
    for value in values:
        for rpe_value, rpe_color in RPE_COLOR_DICT.items():
            if int(round(value, 0)) == rpe_value:
                colors.append(rpe_color)
    return colors
