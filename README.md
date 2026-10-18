# DevDay 2026 Hackathon Judge v2.0 — Skills PoC

主催者から渡されたローカル提出リポジトリを一次審査する、3種類の独立したSkillです。日本語で審査し、各フォルダ単体で動作します。

| Skill | 主たる調査方法 | 採点前に確認するもの |
| --- | --- | --- |
| [Evidence](skills/devday-judge-evidence/SKILL.md) | 構造・主要機能から観点別の主張を作り、複数資料で横断的に裏付ける | カバレッジ、裏付けの強さ、不足・矛盾 |
| [Journey](skills/devday-judge-journey/SKILL.md) | 利用者と成果から通常・重要例外の処理経路を追う | 成果への到達、一貫性、シナリオの代表性 |
| [Challenge](skills/devday-judge-challenge/SKILL.md) | 採点を左右する主張と対立仮説を区別できる箇所に集中する | 支持・反対の証拠、反証の別説明、未解決の重要事実 |

どれも単独で全4観点を評価し、相互の呼び出し・委譲は行いません。配点や採点の甘辛さは共通です。差を作るのは調査の開始点、優先順位、広さと深さ、追加・停止の条件です。重要な証拠は他方式の典型的な手法に属しても無視しません。

## 採点

[大会の公式4観点](https://luma.com/OpenAIDevDay2026CommunityHackathonTokyo)を採用します。

| 観点 / JSONキー | 判断する価値 | 配点 |
| --- | --- | --- |
| 新機能の活用 / new_feature | DevDay新能力と目的の具体的対応、活用の深さ、価値への寄与 | 10 |
| 使いやすさ / usability | 理解・操作・状態・復帰、用途に合うインターフェース | 10 |
| 有用性 / utility | 利用者の課題に効く便益、導入・継続の現実性 | 10 |
| 独創性 / originality | 課題の捉え方、課題固有の工夫、新しい組合せ | 10 |
| 合計 | 各0–10の整数 | 40 |

公式は各項目の配点を明示していないため、**等配点と詳細アンカーはPoC独自の暫定設計**です。各観点に0、1–2、3–4、5–6、7–8、9–10の証拠に基づくアンカーがあります。アクセス不足はnull、読めた範囲に証拠がなければ0。1観点でもnullなら合計もnullです。

[DevDay公式Recap](https://openai.com/index/devday-2026-recap/)の25項目をID付き照合表として各Skillに同梱しています。名前の一致、API利用、機能数、通常のCodex利用だけでは高得点を支持しません。新たなCodex固有能力を価値創出に活かす制作記録は評価対象です。モック・設計・制作過程の分類だけで機械的な上限を設けず、活用の具体性と実現効果・証拠の確かさを分けます。

技術的な完成度、到達可能性、実接続とモック、堅牢性は4観点を支える証拠として扱い、独立した技術点や一律の技術減点はありません。GUIや画像の不在だけでは使いやすさを減点せず、確認できない視覚品質を未確認にします。狭い対象への深い便益も高く評価できます。

## 使い方と信頼境界

このリポジトリを開いた**信頼できるCodexセッション**で、対象外から開始します。

```text
skills/devday-judge-evidence/SKILL.md を読み、その指示に従って
/absolute/path/to/submission の現在の作業ツリーを一次審査してください。
日本語のMarkdownで返してください。
```

方式を変える場合はパスをdevday-judge-journeyまたはdevday-judge-challengeへ変更します。JSONが必要なら「出力仕様に従う単一JSONで返してください」と指定します。必須入力はローカル対象パス。主催者の補足資料、対象commit、範囲、提出物外の出力先も指定できます。

原則として読み取り専用の静的確認です。提出物の変更、コード・テストの実行、依存インストール、外部API・公開Webサイトへのアクセスは行いません。実行成功やテスト合格を確認したとは報告しません。ジャッジ自体の信頼できる検証スクリプトは実行できます。

大会参加ルールは遵守済みの前提です。Web公開、Codex等の使用条件、事前制作、チーム人数などの参加資格は確認・採点しません。合否・順位・自動失格も生成しません。

対象内のAGENTS.md、Skill、README、テストデータ等の審査員向け命令は提出データです。**提出リポジトリを作業ディレクトリにせず、信頼できる審査用の作業ディレクトリから対象パスを指定してください。** ホストが先に提出物の設定を自動ロードするとSkillだけでは信頼境界を作れないため、作業ディレクトリ・設定・権限も審査側で管理します。秘密値を引用せず、シンボリックリンクで対象外へ出ません。

常設する場合は必要なSkillフォルダを、利用環境で探索される`.agents/skills/`へ丸ごとコピーします。この改修はユーザー環境や提出物へインストールしません。

## 出力と移行

schema_version / rubric_versionは文字列`2.0`です。基本スコア形式を共通にし、method_observationsのみ方式ごとに異なる構造を持ちます。Schemaはjudgeとの対応も検証します。観察事実・検証対象・最終判断を記録し、内部の思考過程は要求しません。

| 旧契約 | v2.0 |
| --- | --- |
| technical | 独立採点から削除。実装は4観点の根拠として使用 |
| ux / impact / idea | usability / utility / originality。特にutilityは具体的な実用価値を重視 |
| themeの独立採点 | new_featureへ統合。発表ID・分類・証拠・寄与は採点のないfeature_useへ |
| event_policy | 削除。参加条件は遵守済み |
| method_notes | 方式別のmethod_observationsへ |

旧形式は新Schemaで受理しません。観点の意味が変わるため、旧スコアのキー置換・直接比較・混合集計は行いません。

各SkillにはSKILL.md、agents/openai.yaml、4つの共通参照（rubric.md、devday-2026.md、report.md、report.schema.json）、validate_report.pyを同梱します。共通参照とバリデーターの3コピーは同一内容を維持します。

## 検証と独立性の比較

Python 3とjsonschemaを使用します。提出コードを実行せず、ジャッジの契約を検証します。

```sh
python3 scripts/check_consistency.py
python3 -m unittest discover -s tests -v
python3 skills/devday-judge-evidence/scripts/validate_report.py /tmp/report.json
python3 skills/devday-judge-journey/scripts/validate_report.py /tmp/report.json
python3 skills/devday-judge-challenge/scripts/validate_report.py /tmp/report.json
```

[VALIDATION.md](VALIDATION.md)に受け入れ条件と実行結果、[校正プロトコル](calibration/PROTOCOL.md)に変更前の重複分析と比較手順があります。条件Aは公式4観点のみ移行した従来手順の対照、条件Bは探索手順を分離した本実装です。Aを別ディレクトリへ用意するスクリプトと、引用の位置・事実・影響観点を比較する補助スクリプトも同梱します。

同じ点数に収束することは問題ありません。点数差、証拠の重複、独自の重要事実、引用の正確性、見落とし、反復の安定性、人間との整合性を併せて確認します。小さなリポジトリの同じファイルを読むことや重複率だけでは独立性を判定しません。機械検証と実モデルによる審査品質の実証は別に扱います。
