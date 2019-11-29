# Colaboratory2LaTeX
## 概要
Google Colaboratoryで作成したipynbファイルをLaTeX形式のファイルにしたのちにPDFにするプログラムです。
## 使い方
このプログラムにはchromedriverが使用されています。google chromeのダウンロードがまず必要なのと、 https://chromedriver.chromium.org/downloads から、自身のパソコンにインストールされているgoogle chromeに対応するバージョンのchrome driverを、パスが通っている場所に配置する必要があります。
### 1.settings.yamlの設定
まずはじめにsettings/settings.yamlの設定を行ってください。
google_loginのidには自身のgmailアドレスを、passwordのところには自身のパスワードに書き換えてください。
画像やグラフがあるファイルを読み込む場合は、figuredirectoryのところにディレクトリを書いておいてください。（注意：製作者のパソコンではホームディレクトリ直下のフォルダでないとextractbbがどうとかでエラーがでました）
#### 各パラメータの説明
- title,author,date
texファイルのtitle,author,dateにあたる設定です。なにも書かなければtitleはgoogle colaboratoryのファイル名になり、authorとdateは表示なしとなります。今日の日付を入れる場合はdateはtodayとしてください。
- figuredirectory
画像やグラフがあるファイルを読み込む場合に、そのファイルから読み込まれた画像が格納されるフォルダを指定します。
- remove
それぞれ拡張子aux、dvi、log、out、texに対応するファイルをコンパイル後に削除するかどうかを設定します。Trueで削除、Falseで残す設定となります。
- google_login
googleアカウントにログインするためのパラメータです。
    - id:gmailのアドレス
    - password:パスワード
となります。
### 2.起動
settings.yamlの設定が完了したらsrc/main.pyを起動します。
main.pyを起動するとgoogle colaboratoryのアドレスを入力するように求められるので、自身がtexファイルに変換したいgoogle colaboratoryのアドレスを入力してください。
アドレスを入力しなかった場合はサンプルとして https://colab.research.google.com/notebooks/charts.ipynb がpdf化されて出力されます。ただし、後半部分はプログラムが対応していないため図は表示されません。
### 3.出力
エラーが発生しなければPDFが出力されます。
google colaboratoryから変換したtexファイルはcolaboratoryフォルダに格納されます。その中のファイルをinputでPDFとして出力されるtexファイル（distフォルダに格納）で読み込んでいます。
エラーがあった場合や、図表が思ったように出力されていない場合などはがんばってエラーを読んだり、tableの位置を探すなどしてcolaboratoryフォルダ内にある生のtexファイルをいじってください。
エラーの原因の1つとしてtexの方で使用する記号とgoogle colaboratory上の記号のバッティングがあります。現在、このプログラムでは、tex上でgoogle colaboratoryのコードセル部分の色を忠実に再現するために、listings.styパッケージのescapecharを~ 記号で設定しています。google colaboratoryの方で記号 ~ を使っている場合は、src/colaboratory2latex.pyで ~ の文字をすべてgoogle colaboratoryの方で使用していない記号（!、?などの半角記号）に置換してください。
（この問題にはそのうち対応予定）
## その他
サンプルとして生成されるファイルがdistとcolaboratoryフォルダ内に入っています。