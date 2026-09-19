#!/usr/bin/env python3
"""Translate Pokemon Showdown replay HTML (battle-log-inline) to Japanese.

Processes all *.html files under ../win/ and ../lose/ (relative to this script),
and replaces English text in the static battle log with Japanese equivalents.

Important: the `<script class="battle-log-data">` region is preserved verbatim
because the animated replay player reads it as a protocol stream and requires
the original English species/move IDs.

Usage:
    python3 translate.py                 # translate all files under ../win and ../lose
    python3 translate.py path/to/foo.html # translate a specific file

See README.md for details on extending the translation tables.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SHOWDOWN_DIR = SCRIPT_DIR.parent

# =================== POKEMON ===================
POKEMON = {
    # Mega / form variants (longer first)
    "Charizard-Mega-X": "メガリザードンX",
    "Gallade-Mega": "メガエルレイド",
    "Gyarados-Mega": "メガギャラドス",
    "Glimmora-Mega": "メガキラフロル",
    "Heracross-Mega": "メガヘラクロス",
    "Victreebel-Mega": "メガウツボット",
    "Gengar-Mega": "メガゲンガー",
    "Dragonite-Mega": "メガカイリュー",
    "Aggron-Mega": "メガボスゴドラ",
    "Aegislash-Blade": "ギルガルド(ブレードフォルム)",
    "Mimikyu-Busted": "ミミッキュ(ばれたすがた)",
    "Goodra-Hisui": "ヌメルゴン(ヒスイのすがた)",
    "Rotom-Wash": "ウォッシュロトム",
    # "Mega X" inline mentions
    "Mega Charizard": "メガリザードン",
    "Mega Gallade": "メガエルレイド",
    "Mega Gyarados": "メガギャラドス",
    "Mega Glimmora": "メガキラフロル",
    "Mega Heracross": "メガヘラクロス",
    "Mega Victreebel": "メガウツボット",
    "Mega Gengar": "メガゲンガー",
    "Mega Dragonite": "メガカイリュー",
    "Mega Aggron": "メガボスゴドラ",
    # Regular species
    "Aegislash": "ギルガルド",
    "Aggron": "ボスゴドラ",
    "Archaludon": "ブリジュラス",
    "Basculegion": "イダイトウ",
    "Beedrill": "スピアー",
    "Bellibolt": "ハラバリー",
    "Blastoise": "カメックス",
    "Ceruledge": "ソウブレイズ",
    "Charizard": "リザードン",
    "Clawitzer": "ブロスター",
    "Clefable": "ピクシー",
    "Corviknight": "アーマーガア",
    "Decidueye": "ジュナイパー",
    "Ditto": "メタモン",
    "Dragapult": "ドラパルト",
    "Dragonite": "カイリュー",
    "Espathra": "クエスパトラ",
    "Forretress": "フォレトス",
    "Gallade": "エルレイド",
    "Garchomp": "ガブリアス",
    "Gardevoir": "サーナイト",
    "Gengar": "ゲンガー",
    "Glimmora": "キラフロル",
    "Goodra": "ヌメルゴン",
    "Gyarados": "ギャラドス",
    "Hatterene": "ブリムオン",
    "Hawlucha": "ルチャブル",
    "Heracross": "ヘラクロス",
    "Hippowdon": "カバルドン",
    "Hydreigon": "サザンドラ",
    "Jolteon": "サンダース",
    "Kingambit": "ドドゲザン",
    "Mamoswine": "マンムー",
    "Meowscarada": "マスカーニャ",
    "Mimikyu": "ミミッキュ",
    "Sableye": "ヤミラミ",
    "Scizor": "ハッサム",
    "Scovillain": "スコヴィラン",
    "Skeledirge": "ラウドボーン",
    "Snorlax": "カビゴン",
    "Sneasler": "オオニューラ",
    "Talonflame": "ファイアロー",
    "Toxapex": "ドヒドイデ",
    "Typhlosion": "バクフーン",
    "Umbreon": "ブラッキー",
    "Victreebel": "ウツボット",
}

# =================== MOVES ===================
MOVES = {
    "Kowtow Cleave": "ドゲザン",
    "Dragon Dance": "りゅうのまい",
    "Draco Meteor": "りゅうせいぐん",
    "Swords Dance": "つるぎのまい",
    "Flame Charge": "ニトロチャージ",
    "Flamethrower": "かえんほうしゃ",
    "Thunder Punch": "かみなりパンチ",
    "Thunder Wave": "でんじは",
    "Bullet Punch": "バレットパンチ",
    "Bitter Blade": "むねんのつるぎ",
    "Dazzling Gleam": "マジカルシャイン",
    "Sacred Sword": "せいなるつるぎ",
    "Stored Power": "アシストパワー",
    "Strength Sap": "ちからをすいとる",
    "Triple Axel": "トリプルアクセル",
    "Volt Switch": "ボルトチェンジ",
    "Will-O-Wisp": "おにび",
    "Acid Spray": "アシッドボム",
    "Energy Ball": "エナジーボール",
    "Icicle Crash": "つららおとし",
    "Shadow Ball": "シャドーボール",
    "Shadow Claw": "シャドークロー",
    "Shadow Sneak": "かげうち",
    "Spiky Shield": "ニードルガード",
    "Baton Pass": "バトンタッチ",
    "Body Press": "ボディプレス",
    "Brave Bird": "ブレイブバード",
    "Dark Pulse": "あくのはどう",
    "Dire Claw": "フェイタルクロー",
    "Fake Out": "ねこだまし",
    "Foul Play": "イカサマ",
    "Giga Drain": "ギガドレイン",
    "Ice Shard": "こおりのつぶて",
    "Iron Head": "アイアンヘッド",
    "Knock Off": "はたきおとす",
    "Light Screen": "ひかりのかべ",
    "Power Gem": "パワージェム",
    "Rock Blast": "ロックブラスト",
    "Rock Slide": "いわなだれ",
    "Slack Off": "なまける",
    "Sucker Punch": "ふいうち",
    "Torch Song": "フレアソング",
    "Waterfall": "たきのぼり",
    "Calm Mind": "めいそう",
    "Earthquake": "じしん",
    "Substitute": "みがわり",
    "Encore": "アンコール",
    "Reflect": "リフレクター",
    "U-turn": "とんぼがえり",
    "Protect": "まもる",
    "Roost": "はねやすめ",
    "Toxic": "どくどく",
    "Curse": "のろい",
    "Wish": "ねがいごと",
    "Yawn": "あくび",
}

# =================== ABILITIES ===================
ABILITIES = {
    "Cursed Body": "のろわれボディ",
    "Mold Breaker": "かたやぶり",
    "Rough Skin": "さめはだ",
    "Speed Boost": "かそく",
    "Supreme Overlord": "そうだいしょう",
    "Toxic Debris": "どくげしょう",
    "Electromorphosis": "でんきにかえる",
    "Innards Out": "うちだすポンプ",
    "Technician": "テクニシャン",
    "Opportunist": "びんじょう",
    "Disguise": "ばけのかわ",
    "Imposter": "かわりもの",
    "Intimidate": "いかく",
    "Oblivious": "どんかん",
    "Protean": "へんげんじざい",
    "Blaze": "もうか",
}

# =================== ITEMS ===================
ITEMS = {
    "Charizardite X": "リザードナイトX",
    "Glimmoranite": "キラフロナイト",
    "Victreebelite": "ウツボットナイト",
    "Aegislashite": "ギルガルドナイト",
    "Dragoninite": "カイリューナイト",
    "Heracronite": "ヘラクロスナイト",
    "Gyaradosite": "ギャラドスナイト",
    "Galladite": "エルレイドナイト",
    "Gengarite": "ゲンガナイト",
    "Aggronite": "ボスゴドラナイト",
    "Haban Berry": "ハバンのみ",
    "Sitrus Berry": "オボンのみ",
    "Key Stone": "キーストーン",
    "Leftovers": "たべのこし",
    "Quick Claw": "せんせいのツメ",
}

# =================== STATS ===================
STATS = {
    "Sp. Atk": "とくこう",
    "Sp. Def": "とくぼう",
    "Attack": "こうげき",
    "Defense": "ぼうぎょ",
    "Speed": "すばやさ",
}

# =================== PHRASES ===================
PHRASES = {
    # Header / rules
    "Species Clause:": "種族制限:",
    "Item Clause:": "道具制限:",
    "Limit one of each Pokémon": "同じポケモンは 1体まで",
    "Limit 1 of each item": "同じ道具は 1つまで",
    "Format:": "フォーマット:",
    "Rated battle": "レーティングバトル",
    "Battle Options": "バトルオプション",
    "Battle timer is ON: inactive players will automatically lose when time's up.": "バトルタイマーが ON: 時間切れで 自動的に 敗北になる。",
    "(requested by ": "(設定者: ",
    # Timer remaining messages
    " has 60 seconds left.": " は 残り 60 秒。",
    " has 55 seconds left.": " は 残り 55 秒。",
    " has 30 seconds left.": " は 残り 30 秒。",
    " has 20 seconds left.": " は 残り 20 秒。",
    " has 15 seconds left.": " は 残り 15 秒。",
    " has 10 seconds left.": " は 残り 10 秒。",
    " has 5 seconds left.": " は 残り 5 秒。",
    # Room / disconnect events
    " joined": " が 入室した",
    " left": " が 退室した",
    " disconnected and has a minute to reconnect!": " は 接続が 切れた！ 再接続まで 1分 の 猶予。",
    " reconnected and has 30 seconds left.": " は 再接続した。 残り 30 秒。",
    " reconnected and has 55 seconds left.": " は 再接続した。 残り 55 秒。",
    " forfeited.": " は 降参した。",
    # Team header
    "'s team:": "の パーティ:",
    # Switch in / out
    " sent out ": " は 繰り出した： ",
    "Go! ": "ゆけ！ ",
    ", come back!": "、 もどれ！",
    " went back to ": " は のところへ もどった： ",
    " withdrew ": " は 引っ込めた： ",
    # Effectiveness
    "It's super effective!": "こうかは ばつぐんだ！",
    "It's not very effective...": "こうかは いまひとつの ようだ…",
    "A critical hit!": "きゅうしょに あたった！",
    "It doesn't affect ": "こうかが ないようだ… ",
    "But it failed!": "しかし うまく きまらなかった！",
    # Faint / win
    " fainted!": " は たおれた！",
    " won the battle!": " は バトルに 勝利した！",
    # Mega evolve (reaction phrase; main mega-evolve handled via regex)
    " is reacting to the Key Stone!": " が キーストーンに 反応している！",
    # Aegislash form
    "Changed to Blade Forme!": "ブレードフォルムに フォルムチェンジした！",
    "Changed to Shield Forme!": "シールドフォルムに フォルムチェンジした！",
    # Mimikyu
    "Its disguise served it as a decoy!": "ばけのかわが みがわりに なった！",
    "'s disguise was busted!": "の ばけのかわが はがれた！",
    # Substitute
    " put in a substitute!": " は みがわりを つくった！",
    "The substitute took damage for ": "みがわりが ダメージを うけた： ",
    "'s substitute faded!": "の みがわりが きえた！",
    # Curse
    " cut its own HP and put a curse on ": " は HPを けずって のろいを かけた： ",
    " is afflicted by the curse!": " は のろいの ダメージを うけた！",
    # Status
    " was burned!": " は やけどを おった！",
    " was hurt by its burn!": " は やけどの ダメージを うけた！",
    " was hurt by poison!": " は どくの ダメージを うけた！",
    " was badly poisoned!": " は もうどく状態に なった！",
    " is paralyzed! It may be unable to move!": " は まひして わざが でにくくなった！",
    " is paralyzed! It can't move!": " は まひして うごけない！",
    " grew drowsy!": " は ねむけが おそってきた！",
    " avoided the attack!": " は こうげきを かわした！",
    " was disabled!": " は 使用できなくなった！",
    # HP restore / drain
    " had its HP restored.": " は HPが 回復した。",
    "'s wish came true!": "の ねがいごとが 叶った！",
    " had its energy drained!": " は エネルギーを すいとられた！",
    # Roost
    " loses Flying type this turn.": " は このターン ひこうタイプを うしなう。",
    # Recoil
    " was damaged by the recoil!": " は はんどうで ダメージを うけた！",
    # Stat change (possessive form)
    "'s Attack rose sharply!": "の こうげきが ぐーんと あがった！",
    "'s Defense rose sharply!": "の ぼうぎょが ぐーんと あがった！",
    "'s Sp. Atk rose sharply!": "の とくこうが ぐーんと あがった！",
    "'s Sp. Def rose sharply!": "の とくぼうが ぐーんと あがった！",
    "'s Speed rose sharply!": "の すばやさが ぐーんと あがった！",
    "'s Attack fell harshly!": "の こうげきが がくっと さがった！",
    "'s Defense fell harshly!": "の ぼうぎょが がくっと さがった！",
    "'s Sp. Atk fell harshly!": "の とくこうが がくっと さがった！",
    "'s Sp. Def fell harshly!": "の とくぼうが がくっと さがった！",
    "'s Speed fell harshly!": "の すばやさが がくっと さがった！",
    "'s Attack rose!": "の こうげきが あがった！",
    "'s Defense rose!": "の ぼうぎょが あがった！",
    "'s Sp. Atk rose!": "の とくこうが あがった！",
    "'s Sp. Def rose!": "の とくぼうが あがった！",
    "'s Speed rose!": "の すばやさが あがった！",
    "'s Attack fell!": "の こうげきが さがった！",
    "'s Defense fell!": "の ぼうぎょが さがった！",
    "'s Sp. Atk fell!": "の とくこうが さがった！",
    "'s Sp. Def fell!": "の とくぼうが さがった！",
    "'s Speed fell!": "の すばやさが さがった！",
    # Screens
    "Reflect made your team stronger against physical moves!": "リフレクターで 味方チームの 物理耐久が 上がった！",
    "Light Screen made your team stronger against special moves!": "ひかりのかべで 味方チームの 特殊耐久が 上がった！",
    "Reflect made the opposing team stronger against physical moves!": "リフレクターで 相手チームの 物理耐久が 上がった！",
    "Light Screen made the opposing team stronger against special moves!": "ひかりのかべで 相手チームの 特殊耐久が 上がった！",
    "Your team's Reflect wore off!": "味方チームの リフレクターが 切れた！",
    "Your team's Light Screen wore off!": "味方チームの ひかりのかべが 切れた！",
    "The opposing team's Reflect wore off!": "相手チームの リフレクターが 切れた！",
    "The opposing team's Light Screen wore off!": "相手チームの ひかりのかべが 切れた！",
    # Supreme Overlord
    " gained strength from the fallen!": " は たおれた なかまから 力を もらった！",
    # Mold Breaker
    " breaks the mold!": " は かたやぶりで 特性を 無視する！",
    # Quick Claw
    " can act faster than normal, thanks to its Quick Claw!": " は せんせいのツメで こうどうが 速くなった！",
    # Toxic Debris
    "Poison spikes were scattered on the ground all around your team!": "毒びしが 味方チームの 足元に ばらまかれた！",
    "Poison spikes were scattered on the ground all around the opposing team!": "毒びしが 相手チームの 足元に ばらまかれた！",
    # Flinch
    " flinched and couldn't move!": " は ひるんで うごけなかった！",
    # Prankster note
    "(Since gen 7, Dark is immune to Prankster moves.)": "(第7世代以降、いたずらごころ の 変化技は あくタイプに 効かない。)",
    # Protect
    " protected itself!": " は みを まもった！",
    # Rough Skin damage
    " was hurt!": " は ダメージを うけた！",
    # Type change (Protean)
    "'s type changed to Ice!": "の タイプが こおりに かわった！",
    "'s type changed to Fire!": "の タイプが ほのおに かわった！",
    "'s type changed to Water!": "の タイプが みずに かわった！",
    "'s type changed to Grass!": "の タイプが くさに かわった！",
    "'s type changed to Electric!": "の タイプが でんきに かわった！",
    "'s type changed to Psychic!": "の タイプが エスパーに かわった！",
    "'s type changed to Dark!": "の タイプが あくに かわった！",
    "'s type changed to Ghost!": "の タイプが ゴーストに かわった！",
    "'s type changed to Dragon!": "の タイプが ドラゴンに かわった！",
    "'s type changed to Fighting!": "の タイプが かくとうに かわった！",
    "'s type changed to Flying!": "の タイプが ひこうに かわった！",
    "'s type changed to Ground!": "の タイプが じめんに かわった！",
    "'s type changed to Rock!": "の タイプが いわに かわった！",
    "'s type changed to Bug!": "の タイプが むしに かわった！",
    "'s type changed to Steel!": "の タイプが はがねに かわった！",
    "'s type changed to Poison!": "の タイプが どくに かわった！",
    "'s type changed to Fairy!": "の タイプが フェアリーに かわった！",
    # Multi-hit
    "The Pokémon was hit 2 times!": "ポケモンは 2回 攻撃を うけた！",
    "The Pokémon was hit 3 times!": "ポケモンは 3回 攻撃を うけた！",
    "The Pokémon was hit 4 times!": "ポケモンは 4回 攻撃を うけた！",
    "The Pokémon was hit 5 times!": "ポケモンは 5回 攻撃を うけた！",
    # Transform (Imposter)
    " transformed into ": " は 変身した： ",
    # Invalid choice msg
    "[Invalid choice] There's nothing to cancel": "[無効な選択] 取り消せるものが ない",
    # Rating
    "'s rating:": "の レート:",
    # Possessive context
    "The opposing ": "相手の ",
    "the opposing ": "相手の ",
    # "X used Y!" (runs last so earlier phrases win)
    " used ": " の ",
    # Pokémon common word
    "Pokémon": "ポケモン",
}

# =================== PRE-REGEX (run before string replacements) ===================
PRE_REGEX = [
    # Title (any format name)
    (re.compile(r'<title>([^<]+?) replay: ([^<]+)</title>'),
     r'<title>\1 リプレイ: \2</title>'),
    # HP loss  "(X lost 51.4% of its health!)"
    (re.compile(r'\(([^()\n]*?) lost (<abbr[^>]*>[^<]*</abbr>|[\d.]+%) of its health!\)'),
     r'(\1の HPが \2 減った！)'),
    # Rating change
    (re.compile(r'\(\+(\d+) for winning\)'), r'(勝利+\1)'),
    (re.compile(r'\(\+(\d+) for losing\)'), r'(敗北+\1)'),
    (re.compile(r'\(-(\d+) for losing\)'), r'(敗北-\1)'),
    (re.compile(r'\(-(\d+) for winning\)'), r'(勝利-\1)'),
    # Knock Off flavor
    (re.compile(r' knocked off the opposing (\S+?)&#x27;s ([^!]+)!'),
     r' は 相手の \1 の \2 を はたき落とした！'),
    (re.compile(r" knocked off the opposing (\S+?)'s ([^!]+)!"),
     r' は 相手の \1 の \2 を はたき落とした！'),
    # Battle started between X and Y!
    (re.compile(r'Battle started between (\S+) and (\S+)!'),
     r'バトルが 始まった： \1 と \2！'),
    # "A and B joined"
    (re.compile(r'(\S+) and (\S+) joined'),
     r'\1 と \2 が 入室した'),
    # "X has Mega Evolved into Mega Y!"
    (re.compile(r'(\S+?) has Mega Evolved into (Mega [^!]+)!'),
     r'\1 は \2に メガシンカした！'),
    # "(X ate its Y!)"
    (re.compile(r'\(([^()]+?) ate its ([^!]+)!\)'),
     r'(\1 は \2 を たべた！)'),
    # "X restored HP using its Y!" variants
    (re.compile(r' restored a little HP using its ([^!]+)!'),
     r' は \1 で HPを 少し 回復した！'),
    (re.compile(r' restored HP using its ([^!]+)!'),
     r' は \1 で HPを 回復した！'),
]

# =================== POST-REGEX (cleanup after string replacements) ===================
POST_REGEX = [
    (re.compile(r'<h2 class="battle-history">Turn (\d+)</h2>'),
     r'<h2 class="battle-history">ターン \1</h2>'),
    # Stray possessive cleanup
    (re.compile(r"(\w)'s "), r"\1の "),
    (re.compile(r"(\w)'s\]"), r"\1の]"),
    (re.compile(r"(\w)'s<"), r"\1の<"),
    # Haban Berry / berry damage reduction
    (re.compile(r'The (\S+のみ) weakened the damage to (\S+?)!'),
     r'\1 で \2 への ダメージが 弱まった！'),
    # Oblivious / stat not lowered
    (re.compile(r' was not lowered!'), r' は 下がらなかった！'),
]


def apply_table(text: str, table: dict[str, str]) -> str:
    for key in sorted(table.keys(), key=len, reverse=True):
        text = text.replace(key, table[key])
    return text


def translate(text: str) -> str:
    for pattern, repl in PRE_REGEX:
        text = pattern.sub(repl, text)
    combined: dict[str, str] = {}
    for table in (PHRASES, ABILITIES, MOVES, ITEMS, POKEMON, STATS):
        combined.update(table)
    for key in sorted(combined.keys(), key=len, reverse=True):
        text = text.replace(key, combined[key])
    for pattern, repl in POST_REGEX:
        text = pattern.sub(repl, text)
    return text


def process_file(path: Path) -> None:
    content = path.read_text(encoding="utf-8")
    m = re.search(
        r'(<script type="text/plain" class="battle-log-data">)(.*?)(</script>)',
        content, re.DOTALL)
    if not m:
        print(f"[skip] no battle-log-data in {path.name}")
        return
    placeholder = "@@BATTLE_LOG_DATA_PLACEHOLDER@@"
    saved_data = m.group(2)
    content_stripped = content.replace(saved_data, placeholder)
    translated = translate(content_stripped)
    final = translated.replace(placeholder, saved_data)
    path.write_text(final, encoding="utf-8")
    print(f"[ok]   {path.relative_to(SHOWDOWN_DIR)}")


def discover_files() -> list[Path]:
    files: list[Path] = []
    for sub in ("win", "lose"):
        d = SHOWDOWN_DIR / sub
        if d.is_dir():
            files.extend(sorted(d.glob("*.html")))
    return files


def main(argv: list[str]) -> int:
    if len(argv) > 1:
        targets = [Path(a).resolve() for a in argv[1:]]
    else:
        targets = discover_files()
    if not targets:
        print("no files found under ../win or ../lose", file=sys.stderr)
        return 1
    for path in targets:
        process_file(path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
