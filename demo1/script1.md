# demo 腳本1 (機器人跟隨照護服務)

### 前往第一個房間(A房)巡視

1. (語) 照護員發出語音指令: 機器人跟我去訪視大家 (送**follow_me**給平台)
2. (平) 平台收到**follow_me**, 根據條件送出**start_agv_follow**
3. (機) 機器人收到訊息, 開始跟照護員行走
4. (語) 照護員到目的地後, 會發出語音指令: 停下來 (送**stop**給平台)
5. (平) 平台收到**stop**, 根據條件送出**end_agv_follow**
6. (機) 機器人停止移動
    1. 此時機器人停在隨機位置, 非中繼點
7. (bio) 照護員移至住民1，量體溫，然後打開App掃住民1的名牌，再用App讀取體溫與血氧值。生理量測後台應能同步顯示讀取到的數值。


### 前往第二個房間(B房)巡視

1. (語) 任務完成後, 照護員再發出語音指令: 機器人跟我去訪視大家(送**follow_me**給平台)
2. (平) 平台收到**follow_me**, 根據條件送出**start_agv_follow**
3. (機) 機器人收到訊息, **回覆：「我不在中繼點上，最近的中繼點為311房門口，請先將我移到中繼點」.**
    1. 等移動到中繼點後再重新發出語音指令 (送follow_me給平台)
    2. 平台收到follow_me, 根據條件送出start_agv_follow
    3. 機器人收到訊息, 開始跟照護員行走
4. (語) 照護員到目的地後, 會發出語音指令: 停下來 (送**stop**給平台)
ps. 請開螢幕分享, 讓大家可以看到目前的運作畫面. 結束後可關閉螢幕
1. (平) 平台收到**stop**, 根據條件送出**end_agv_follow**
2. (機) 機器人停止移動
3. (bio) start to measure bio-signal. When the task is finished, send **measure_done** to platform
ps. please share the screen to show the progress on the smartphone. Close share screen when the task is done.

### 任務結束, 返回護理站

環境假設: 目前人在B房, 需要先把機器人移動到中繼點, 作為預設的起點位置, 然後再進行下列動作

1. (語) 照護員發出語音指令: 機器人回去護理站 (送**go_to_nursing_station**給平台)
ps. 請開螢幕分享, 讓大家可以看到目前的運作畫面. 結束後可關閉螢幕
ps. 機器人要先移動到中繼點(預設的起點位置), 才能下指令返回護理站
2. (平) 平台收到**go_to_nursing_station**, 根據條件送出**self_move_BO**
3. (機) 機器人收到訊息, 自行返回護理站, 到達目的地後會自動停止