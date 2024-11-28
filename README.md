# business-history-bk
business-history-bk

pandas-2.2.3
python 3.10


## Servelress Framework
- Serverless Framework

```
node version 18.0
npm install -g serverless@3
serverless --version
このプラグインはローカルで実行出来るプラグインなのでデプロイには意味が無いので削除
serverless plugin uninstall --name  serverless-offline
serverless plugin uninstall --name  serverless-dynamodb-local
```


## deploy方法
### Lambda
```
serverless deploy --stage dev --verbose
serverless deploy --stage poc --verbose
```


### Lambda-Layer
deploy
```
cd layer\common-layer
serverless deploy --stage dev
serverless deploy --stage poc
```

destroy
```
cd layer\common-layer
serverless remove --stage dev
serverless remove --stage poc
```


zipファイルは、wsl上でライブラリ作成してアップ

1. python 仮想環境作成してそこでライブラリをインストールする
2. ライブラリと同じフォルダを作成する(Pythonのバージョンに応じてパスを変更)
   mkdir -p python/lib/python3.10/site-packages  
3. ライブラリをコピーする
   cp -r venv/lib/python3.10/site-packages/* python/lib/python3.10/site-packages/.
4. コピーしたフォルダを圧縮
   zip -r python-layer.zip python
5. マネージメントコンソールでLayerアップロードもしくはコマンド

Pandas以外を下記の方法で作成(WSL上で作成した)
https://docs.aws.amazon.com/ja_jp/lambda/latest/dg/python-layers.html#python-layer-manylinux
https://pypi.org/project/numpy/#files
https://zenn.dev/oizawa/articles/77887544925a76

Pandasは下記を設定する
https://github.com/keithrozario/Klayers
arn:aws:lambda:ap-northeast-1:770693421928:layer:Klayers-p310-pandas:18
