import pandas as pd

voting = pd.read_csv("data/processed/hart_voting.csv")
trades = pd.read_csv("data/raw/traded_players.csv")

voting = voting.merge(trades[["season", "player_id", "final_team"]],
                      on=["season", "player_id"], how="left")
voting["team_id"] = voting["final_team"].fillna(voting["team_id"])
voting = voting.drop(columns="final_team")

print("TOT rows left:", (voting["team_id"] == "TOT").sum())   # expect 0
print("Rows:", len(voting))                                    # expect 758

voting.to_csv("data/processed/hart_voting_fixed.csv", index=False)