import time

from utils import log_print_util
from utils.player import Player

def clean_up(player_list: list[Player], max_retry_times=5):
    # 关闭线程。
    if player_list is not None and len(player_list) > 0:
        closed_player_num = 0
        for player in player_list:
            if player.exit_flag:
                closed_player_num = closed_player_num + 1
                continue
            else:
                player.tear_down()
                retry_times = 0
                while retry_times < max_retry_times:
                    time.sleep(1)
                    log_print_util.log_print(f"{player.account_id}的exit_flag：{player.exit_flag}")
                    if player.exit_flag:
                        closed_player_num = closed_player_num + 1
                        break
                    retry_times = retry_times + 1
        log_print_util.log_print(f"{closed_player_num}个玩家已关闭.")
    else:
        log_print_util.log_print(f"player_list为空！")

def clean_up_by_account_id(player_list: list[Player], specific_account_id):
    # 关闭指定玩家的线程
    for player in player_list:
        if player.account_id == specific_account_id:
            player.tear_down()
            break
    log_print_util.log_print(f"{specific_account_id}已关闭.")