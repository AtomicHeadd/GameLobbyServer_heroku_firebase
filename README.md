# GameLobbyApp

前提としてP2P通信のIP、ポート交換用のサーバーです。
これ自体にゲームロジックの同期機能はありません。

このサーバーを介してマッチングした後に各クライアントで対戦相手に対して
P2P通信接続を行う、と言う形で使います。

またNAT越えのためのSTUNやそれに準ずる対策はクライアント側で用意してください。