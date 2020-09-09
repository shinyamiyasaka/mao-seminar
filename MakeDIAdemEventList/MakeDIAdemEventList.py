"""
Created on Aug 28 2020

@author: miyasaka
"""

import glob
import pandas as pd
import os
import pathlib
from configparser import ConfigParser
import datetime

# input_TriggerEventListフォルダーに抽出したトリガーイベントリスト(excel)を格納
# input_TriggerEventListフォルダー内にあるトリガーイベントリストのファイル名を抽出
# トリガーイベントリスト(excel)に関する変数に_mf4をつける
# DIAdem用イベントリストに関する変数に_diademをつける

# 設定ファイル(Trigger_configuration.ini)から条件を読み込み
config = ConfigParser()
config.read('.\Trigger_configuration.ini')

# input_TriggerEventListフォルダー内の全てのexcelファイルのパスを抽出してfilesに格納
# excelファイルはmf4から抽出したイベントリスト
files_mf4 = glob.glob('./input_TriggerEventList/*.xlsx')

# input_TriggerEventListフォルダー内のexcelファイルが複数の場合も対応するためにfor文で処理
# filepath_mf4にそれぞれ格納
for filepath_mf4 in files_mf4:
# パスからファイル名を抽出
    filepath_mf4 = str(filepath_mf4)
    # print(filepath_mf4)
    # ファイルのパスを利用してファイル名を抽出、filename_diademに格納。
    filename_diadem = filepath_mf4.replace('./input\\', '')
    # print(filename_diadem)
    # DIAdemイベントリストを作成するためにトリガーイベントリストから必要な情報を取り出す。
    # sheet_name=1とする理由は2番目のシートに必要な情報が含まれているため。(1番目のシートはSummary)
    # 必要な列のみ抽出(０：ID, 1:flag, 6:trigger_rel_minute, 7:trigger_rel_second, 21:file_name)
    df_eventlist_diadem = pd.read_excel(filepath_mf4, sheet_name=1, usecols=[0,1,6,7,21])
    # 評価データが格納してあるフォルダーのパスを設定ファイルから取得
    DataDirectoryPath = config['Setting']['data_directory_path']
    df_eventlist_diadem['file_name'] = str(DataDirectoryPath)+ str('\\') + df_eventlist_diadem['file_name']
    #print(df_eventlist_diadem)
    # DIAdem用イベントリストに合わせた名前に変更
    df_eventlist_diadem.columns = ['ID','Flag','Trigger  Point(Minute)','Trigger Point (Sec)','File']
    # 動画用の'Movie'列(空列)を追加
    df_eventlist_diadem['Movie'] = ''
    # 'Movie'列に'File'列をコピー
    # 動画とMF4ファイルは拡張子以外同じ名前(ファイル名同じ)なのでMF4⇒aviに変える処理をする
    df_eventlist_diadem['Movie'] = df_eventlist_diadem['File']
    MoviePathes = df_eventlist_diadem['Movie']
    for MoviePath in MoviePathes:
        #print(MoviePath)
        MoviePath = str(MoviePath)
        MoviePath = MoviePath[:-3] + str('avi')
        #print(MoviePath)
        df_eventlist_diadem['Movie'] = MoviePath

    # 画像用の'Image'列(空列)を追加
    df_eventlist_diadem['Image'] = ''
    # memo欄追加
    df_eventlist_diadem['Field 1'] = ''
    df_eventlist_diadem['Field2'] = ''
    df_eventlist_diadem['Field3'] = ''
    df_eventlist_diadem['Field4'] = ''
    df_eventlist_diadem['Field5'] = ''
    # DIAdemイベントリストのFlag名を読んで、設定ファイルの対応した条件をデータフレームに反映したい
    # Flagを順次読み込んで設定ファイルと照合する
    # columnはDIAdemイベントリストの何行目のデータを読み取るか
    column = 0
    for flag in df_eventlist_diadem['Flag']:
        #print(flag)
        #print(config[str(0)]['Trigger_name'])
        print()
        print("EXCEL行", str(column+2), "行目をチェック")
        # 設定ファイルのトリガー条件が15種類ある
        # DIAdemイベントリストのFlag(flag)と設定ファイルの'Trigger_name'が一致したら各条件をcsvへ反映
        for x in range(15):
            if (config[str(x)]['Trigger_name'] == flag):
                #print(config[str(x)]['Trigger_name'])
                #print(column)
                df_eventlist_diadem.loc[column, 'Pre Trigger(Sec)'] = config[str(x)]['PreTrigger_time']
                df_eventlist_diadem.loc[column, 'Post Trigger(Sec)'] = config[str(x)]['PostTrigger_time']
                df_eventlist_diadem.loc[column, 'View'] = config[str(x)]['ViewFormat']
                df_eventlist_diadem.loc[column, 'Field 1'] = config[str(x)]['memo1']
                df_eventlist_diadem.loc[column, 'Field2'] = config[str(x)]['memo2']
                df_eventlist_diadem.loc[column, 'Field3'] = config[str(x)]['memo3']
                df_eventlist_diadem.loc[column, 'Field4'] = config[str(x)]['memo4']
                df_eventlist_diadem.loc[column, 'Field5'] = config[str(x)]['memo5']
                print("　Flag検出⇒", str(config[str(x)]['Trigger_name']))

            else:
                print("　    　　　", str(config[str(x)]['Trigger_name']),)
        column = column + 1

# イベントリストの列の順序を整える
# （ID,Flag,File,Movie,Image,Trigger  Point(Minute),Trigger Point (Sec),
# Pre Trigger(Sec),Post Trigger(Sec),View,Field 1,Field2,Field3,Field4,Field5）
ChangeColumnOrder_df_eventlist_diadem = df_eventlist_diadem.reindex(columns=['ID', 'Flag', \
                                    'File', 'Movie', 'Image', 'Trigger  Point(Minute)', 'Trigger Point (Sec)',\
                                     'Pre Trigger(Sec)', 'Post Trigger(Sec)', 'View', 'Field 1', 'Field2', 'Field3', 'Field4', 'Field5'])

# outputフォルダーにイベントリストを出力
ChangeColumnOrder_df_eventlist_diadem.to_csv('./output_DIAdemEventList/DIAdemEventList.csv', index=False)

# ファイル名に日付と時刻を加える処理
os.chdir('./output_DIAdemEventList')
now = datetime.datetime.now()
old = 'DIAdemEventList.csv'
new = '{0:%Y%m%d_%H%M%S}_DIAdemEventList.csv'.format(now)
os.rename(old,new)

print()
print("DIAdem用イベントリストの作成が完了しました。")
print()
print("output_DIAdemEventListフォルダーにリストを出力しました。")
print("ファイル名は　",str(new),"　です。")

