# DevDay 2026 — 新機能照合 v2.0

一次資料: [DevDay 2026 Recap](https://openai.com/index/devday-2026-recap/)、公開日: 2026-09-29、確認日: 2026-10-18。

この表は記事にある25項目を審査用に整理したもの。**発表内容**と**対応を支える証拠の例**を分ける。証拠の例はOpenAIが指定する参加条件ではない。API名・必須ファイル名・SDKの実装仕様を定義する表ではない。

通常の審査ではこの版を使い、最新ニュースでイベントの対象範囲を広げない。記事の動的な表示が空でも発表がなかったと結論しない。表の範囲で判定できない場合は不確実性を残す。全作品に同じ参照版を適用する。

| ID | 記事の項目 | 発表の要点 | 対応を支える証拠の例（審査上の解釈） |
| --- | --- | --- | --- |
| DD01 | Dots | 継続して仕事を担う常時稼働エージェント | 継続する責務、起動条件、状態保持、介入・引継ぎの仕組み |
| DD02 | GPT-6.1 Sol | コーディング・computer use・専門業務向けのモデル更新 | 実際のモデル設定と到達する利用箇所、その能力が価値に効く設計 |
| DD03 | Ultrafast | Codex/API向けの高速な生成ティア | 対象ティアの利用設定、応答時間を前提に成立する体験。通常のstreamingだけと区別 |
| DD04 | Private Intelligence | Private Safety ProcessingとPrivate Inferenceのプレビュー | 該当サービスの利用・境界、データ保護を前提にした用途。一般的な暗号化だけと区別 |
| DD05 | Codex in the cloud | クラウドでの利用と再利用できる開発環境 | 共有環境の定義、クラウドで継続する開発タスクとの結びつき |
| DD06 | A refreshed Codex CLI | 音声、/agents、セッションやworktreeの操作改善 | 新しいCLI体験を使う手順やワークフロー、追跡可能な開発記録 |
| DD07 | Code Review | 複数プロジェクトの変更確認と自動レビュー | 差分・レビュー・フィードバックを成果につなぐ仕組みや利用記録 |
| DD08 | Codex Security Cloud | リポジトリや新規commitの継続的な検査と修正支援 | 対象、起動、検査結果、重複処理、修正へつなぐフロー |
| DD09 | Decisions API | 有限の事前定義回答を使うリアルタイム判断 | 文脈と問い・選択肢、接続部分、回答を使う分類やルーティング |
| DD10 | Agents API with Computer use | computer useや複数エージェント等を提供する実行基盤 | 到達するエージェント実装、ツール境界、画面操作、状態・コンテキストの扱い |
| DD11 | Bedrock Managed Agents, powered by OpenAI | OpenAIのエージェント機能をAWS環境に統合 | 該当基盤の設定、AWS資源・権限とタスクの具体的接続 |
| DD12 | Plugin extensions | サイドバー、対話と並行するパネル、ファイルviewer | 拡張定義、対応する表示・操作、会話との連携 |
| DD13 | Improved plugin creation, submission, and discovery | 作成・提出・発見の改善、利用者によるアクセス承認 | Plugin Creator等の新しい制作・配布フローの記録や対応物。プラグインであるだけと区別 |
| DD14 | Sites can now host plugins | Sites上のプラグインと各利用者の接続・権限 | Siteとプラグインの連携、利用者ごとのデータ・権限の扱い |
| DD15 | MCP events for plugin automations | 接続先のイベントを契機にする自動化 | イベント購読・受信と後続処理。MCPの通常のtool定義だけと区別 |
| DD16 | ChatGPT Space | 人・ChatGPT・dotが共有知識で共同作業 | 共有コンテキスト、整理の指示、継続的な共同作業の成果 |
| DD17 | Pages | 人とエージェントが共同作業する文書 | ページ上の情報・操作・共同編集を活かす具体的な成果物 |
| DD18 | Collaborative slides | 共同作成・編集、提示・出力ができるスライド | 共同制作フローやその出力。単なるスライド生成との違い |
| DD19 | Create teams and share tasks | 共有成果物と予定・イベントによるチームタスク | 共有単位、タスク条件、接続ツール、結果の引継ぎ |
| DD20 | @ChatGPT in Slack and Microsoft Teams | 会話内のメンションから共有権限で仕事を依頼 | メンション起点の文脈、権限、処理、チームへの結果提示 |
| DD21 | Meetings plugin | 会議メモ・要約・アクションをSpaceへ保存 | 会議から記録・後続作業へつながる設計、公開範囲と音声の扱い |
| DD22 | Shareable profiles | Sitesやプラグイン等をプロフィールから発見・共有 | 発見・再利用への導線。単なる自己紹介ページと区別 |
| DD23 | Sign in with ChatGPT | ChatGPTでの認証と、対応ツールでのプラン利用 | 該当認証・接続の導線、利用枠を扱う統合。一般的なログインと区別 |
| DD24 | A new Pro tier | Pro 500プランの追加 | プランの能力・利用条件を具体的に活かす設計。加入の主張だけと区別 |
| DD25 | OpenAI Marketplace | 企業のOpenAI契約をパートナーソフトウェアに活用 | 当該調達・提供フローに結びつく成果物。一般的なマーケット一覧と区別 |

## 提供制約の読み方

この記事はすべての項目が誰にでも同じ条件で使えるとは述べていない。例えばDecisions APIはlimited preview、Private Inferenceは今後のpreview、GPT-6.1 SolのUltrafastはcoming soonとして記載されている。地域・プラン・管理者設定の条件がある発表も含まれる。

利用可能性や参加者のアクセス権を推測しない。APIの存在・接続仕様がこの表で確定するわけでもない。接続を検証できない場合は`implemented_unverified`等で示し、未知のメソッド名だけを根拠に架空APIと断定しない。モックを実接続として加点することも避ける。

## 対応の分類

候補ごとにID、成果物のどこに対応するか、証拠ID、関係の種類、実装状態を記す。

- 関係の種類: `core`（主価値）、`supporting`（意味のある補助）、`development_only`（制作過程のみ）、`inspiration`（着想・体験の応用）、`mention_only`（名称の記載のみ）。
- 実装状態: `connected`（到達するコード上に接続がある。実動作の確認を意味しない）、`implemented_unverified`（接続を確証できないが該当処理がある）、`mock`（代替データ・処理）、`planned`（計画のみ）、`not_applicable`（利用記録や名称等で接続分類が適用されない）。

単なるOpenAI API利用は特定発表への適合を証明しない。通常のMCP、チャットUI、一般的なエージェントというだけではDD15、DD12、DD10に自動対応させない。Codexで作ったという主張だけを強い適合にしない。逆にREADMEに発表名がなくても、対応する仕組みと価値が確認できれば拾う。

## feature_useの記録と採点との関係

`reference_version`は`devday-2026-v2.0`、`source_url`は上記RecapのURL。25項目のIDは維持する。表の例は対応を説明する例であり、全方式に同一の探索順・ファイル群の網羅を要求するものではない。

各mappingは`announcement_id`、`announcement`、`relationship`、`basis`、`implementation`、`evidence_ids`、`contribution`を持つ。`basis`は`product_use`（当該製品・機能の利用）、`experience_application`（発表固有の体験の独自応用）、`concept_only`（構想・言及）。制作過程の当該製品利用はproduct_useとdevelopment_onlyの組合せで示す。独自応用を製品への接続と報告しない。

対応なしならmappingsは`[]`。`feature_use`には点数・合否を持たせない。活用の点数は`criteria.new_feature`だけで、アンカーは[rubric.md](rubric.md)にある。

正の新機能点には少なくとも1つの証拠付きmappingが必要。3点以上ならmention_only以外の具体的な対応が必要。これは分類による実装状態の得点上限ではなく、名称だけでは活用の根拠にならないという最低限の契約である。mappingの証拠はnew_featureのevidence_idsにも含める。0点やnullでも、調べた候補・主張の記録は残せる。mappingがあることだけで正の点や高得点を強制しない。

`contribution`は能力が目的・利用価値・制作成果へどう効くか、どこまでが設計・主張かを具体的に示す。`counterfactual`は能力を外す／以前の方法へ替えた場合の意味のある差を記す。対応なし・判断不能の場合はその旨を示す。弱い対応の数で加減点せず、最も強く支持される活用を軸に全体を判断する。モック・計画・制作過程という分類だけでは上限を設けない。

## 対応を過大認定しないための境界

| 発表 | これだけでは発表固有の活用を支持しない例 |
| --- | --- |
| DD01 | cronで動く一般的なbot。継続する責務や介入・引継ぎの具体化もない |
| DD02–DD04 | モデル名、通常のstreaming、一般的な暗号化 |
| DD05–DD08 | クラウド配置、worktree、一般的なレビューや脆弱性スキャナー |
| DD09–DD11 | if文の分類、一般的な画面操作、AWSに配置しただけ |
| DD12–DD15 | 任意のサイドバー、プラグイン宣言、Webサイト、通常のMCP toolや独自webhook |
| DD16–DD19 | 共有フォルダ、文書エディター、スライド生成、定期タスクだけ。人とエージェントの共同作業との対応がない |
| DD20–DD22 | 一般的なSlack bot、文字起こし、自己紹介ページ |
| DD23–DD25 | 一般的なOAuth、上位プランへの加入、商品一覧 |

発表固有のイベント連携を詳細に設計したモックは、新機能活用の深さを評価できるが、外部接続と実現効果は未確認になる。汎用webhookをMCP eventsと呼び替えただけでは高得点を支持しない。新CLIの音声・/agents等を工程に組み込み、作業と成果への寄与を具体的に記録した作品は制作過程として評価できる。単なる「Codexで作った」はその証拠にならない。これらは境界の説明であり、校正済みの正解点ではない。

参加条件は遵守済みの前提であり、この照合で参加資格や大会ルールの充足を判定しない。
