## demo 腳本

[呼叫的部分]

1. 腦波帽將移動指令傳送到平台(move)
    - move的指令會在腦波團隊那邊過濾, 應該可以只傳一次move過來
2. 判斷機器人的所在地 (定位資訊)
    - 定位系統會週期性的傳送位置資訊過來, 定位結果為編號資訊 (空間中有設計20個點), 然後再看事先定義的地圖得知在哪個區域
        
        (A) 如果定位在護理站(O), 就發送 self_move_OA: 從護理站來A房
        
        (B) 如果定位在A房, 就發送 self_move_AO: 從A房回護理站
        
    - 如果機器人忙碌中, 平台會送回饋訊息給腦波介面，螢幕上會顯示
        - 機器人啟動前往配膳間: robot_goto_kitchen
        - 等候服務人員放水瓶: caregiver_busy
        - 機器人正在過來: robot_coming
        - 機器人正在回護理站: robot_goback_nursing_station
        - 機器人待機: robot_idle
        - 機器人忙錄中: robot_busy