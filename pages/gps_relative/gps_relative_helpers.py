import pandas as pd


def extract_max_for_player(all_sessions_df: pd.DataFrame, player_name: str, feature_name: str) -> float:
    player_session_df = all_sessions_df[all_sessions_df.athlete == player_name]
    matches_df = all_sessions_df[all_sessions_df.is_match]

    if player_session_df.empty:
        return matches_df[feature_name].max()
    return player_session_df[feature_name].max()


def extract_max_features(all_sessions_df: pd.DataFrame, players_list: list, param_name: str) -> list:
    max_features = []
    for player_name in players_list:
        value = extract_max_for_player(all_sessions_df, player_name, param_name)
        if value == 0:
            value = all_sessions_df[param_name].max()
        max_features.append(value)
    return max_features
