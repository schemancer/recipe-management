import streamlit as st
import requests
import json

st.set_page_config(page_title="レシピ＆お買い物マネージャー", layout="wide") # 画面を広く使えるように "wide" に変更

# ==========================================
# ⚠️ 注意: 以下の "" の中に、GASのURLを貼り付けてください
# ==========================================
GAS_URL = "https://script.google.com/macros/s/AKfycbxPyDnc_ey2LLrGd9TZsRz6Q46zq2UXkNNohB6fozgijvGQtGahsmMXfHI3289-PRL9mg/exec"

# --- 共通関数 ---
def load_data():
    try:
        response = requests.get(GAS_URL)
        if response.status_code == 200:
            data = response.json()
            if data:
                return data
        else:
            st.error(f"読み込みエラー: {response.status_code}")
    except Exception as e:
        st.error(f"データの読み込みに失敗しました: {e}")
    return None

def save_data():
    data_to_save = {
        "recipes": st.session_state.recipes,
        "inventory": st.session_state.inventory
    }
    try:
        response = requests.post(
            GAS_URL, 
            json=data_to_save,
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code != 200:
            st.error(f"保存エラー: {response.status_code}")
    except Exception as e:
        st.error(f"データの保存に失敗しました: {e}")

def parse_ingredients(raw_text):
    result = []
    for line in raw_text.strip().split('\n'):
        if line.strip():
            parts = line.split(',')
            name = parts[0].strip()
            amount = parts[1].strip() if len(parts) > 1 else "適量"
            result.append({"name": name, "amount": amount})
    return result

def unparse_ingredients(ing_list):
    lines = []
    for ing in ing_list:
        lines.append(f"{ing['name']}, {ing['amount']}")
    return "\n".join(lines)

# --- コールバック関数（ボタンを押したときの自動入力処理） ---
def add_food_to_draft(name):
    current = st.session_state.draft_foods
    if current and not current.endswith("\n"):
        st.session_state.draft_foods += f"\n{name}, "
    elif current:
        st.session_state.draft_foods += f"{name}, "
    else:
        st.session_state.draft_foods = f"{name}, "

def add_seasoning_to_draft(name):
    current = st.session_state.draft_seasonings
    if current and not current.endswith("\n"):
        st.session_state.draft_seasonings += f"\n{name}, "
    elif current:
        st.session_state.draft_seasonings += f"{name}, "
    else:
        st.session_state.draft_seasonings = f"{name}, "


# --- セッションステートの初期化 ---
# 入力途中のテキストを保持するための準備
if 'draft_name' not in st.session_state:
    st.session_state.draft_name = ""
if 'draft_foods' not in st.session_state:
    st.session_state.draft_foods = ""
if 'draft_seasonings' not in st.session_state:
    st.session_state.draft_seasonings = ""
if 'draft_instructions' not in st.session_state:
    st.session_state.draft_instructions = ""

if 'initialized' not in st.session_state:
    st.info("🔄 クラウドデータベース（スプレッドシート）と通信中...")
    saved_data = load_data()
    
    if saved_data and "recipes" in saved_data:
        st.session_state.recipes = saved_data.get("recipes", [])
        st.session_state.inventory = saved_data.get("inventory", {})
    else:
        st.session_state.recipes = []
        st.session_state.inventory = {}
    st.session_state.initialized = True
    st.rerun()

# ---------------------------------------------
# 画面の表示レイアウト
# ---------------------------------------------
st.title("🍳 レシピ＆お買い物マネージャー")

tab1, tab2, tab3 = st.tabs(["レシピ一覧（買い物リスト）", "レシピの登録", "調味料の在庫管理"])

# ==========================================
# タブ1: レシピ一覧（スーパーで見る画面）
# ==========================================
with tab1:
    st.header("今日作るレシピを選ぶ")
    if not st.session_state.recipes:
        st.info("レシピが登録されていません。")
    else:
        all_food_ingredients = set()
        for r in st.session_state.recipes:
            for f in r["foods"]:
                all_food_ingredients.add(f["name"])
        
        st.markdown("##### 🔍 使いたい食材で絞り込む（逆引き検索）")
        selected_search_ingredients = st.multiselect(
            "消費したい食材を選んでください",
            options=sorted(list(all_food_ingredients)),
            placeholder="例：豚肉、玉ねぎ..."
        )
        
        filtered_recipes = []
        for r in st.session_state.recipes:
            if not selected_search_ingredients:
                filtered_recipes.append(r)
            else:
                recipe_foods = [f["name"] for f in r["foods"]]
                if all(ing in recipe_foods for ing in selected_search_ingredients):
                    filtered_recipes.append(r)
        
        st.divider()
        
        if not filtered_recipes:
            st.warning("条件に合うレシピが見つかりませんでした。別の食材を選んでください。")
        else:
            recipe_names = [r["name"] for r in filtered_recipes]
            selected_name = st.selectbox("📝 レシピを選択:", recipe_names)
            
            selected_recipe = next(r for r in filtered_recipes if r["name"] == selected_name)
            
            st.divider()
            st.subheader("🛒 買い物リスト")
            
            foods_to_buy = [f"・{f['name']} （{f['amount']}）" for f in selected_recipe["foods"]]
            
            seasonings_to_buy = []
            seasonings_in_stock = []
            for s in selected_recipe["seasonings"]:
                if st.session_state.inventory.get(s["name"], False):
                    seasonings_in_stock.append(f"・{s['name']} （{s['amount']}）")
                else:
                    seasonings_to_buy.append(f"・{s['name']} （{s['amount']}）")
            
            st.error("**【スーパーで買うもの】**")
            if foods_to_buy:
                st.markdown("**🥩 食材（毎回買う）**")
                st.markdown("\n".join(foods_to_buy))
            if seasonings_to_buy:
                st.markdown("**🧂 調味料（切らしている！）**")
                st.markdown("\n".join(seasonings_to_buy))
            if not foods_to_buy and not seasonings_to_buy:
                st.write("買うものはありません！")
                
            st.success("**【家にあるもの（買わなくてOK）】**")
            if seasonings_in_stock:
                st.markdown("\n".join(seasonings_in_stock))
            else:
                st.write("なし")

            st.divider()
            st.subheader("📋 材料一覧")
            
            col_foods, col_seasonings = st.columns(2)
            with col_foods:
                st.markdown("**🥩 食材**")
                if selected_recipe["foods"]:
                    for f in selected_recipe["foods"]:
                        st.write(f"・{f['name']} （{f['amount']}）")
                else:
                    st.write("なし")
            with col_seasonings:
                st.markdown("**🧂 調味料**")
                if selected_recipe["seasonings"]:
                    for s in selected_recipe["seasonings"]:
                        st.write(f"・{s['name']} （{s['amount']}）")
                else:
                    st.write("なし")

            st.divider()
            st.subheader("📖 作り方")
            st.write(selected_recipe["instructions"])

            st.divider()
            with st.expander("🛠️ このレシピを編集・削除する"):
                st.subheader("✏️ レシピの編集")
                with st.form(key=f"edit_form_{selected_recipe['name']}"):
                    edit_name = st.text_input("レシピ名", value=selected_recipe["name"])
                    
                    foods_text = unparse_ingredients(selected_recipe["foods"])
                    seasonings_text = unparse_ingredients(selected_recipe["seasonings"])
                    
                    st.markdown("---")
                    edit_foods_raw = st.text_area("🥩 食材（毎回買うもの）", value=foods_text, height=100)
                    edit_seasonings_raw = st.text_area("🧂 調味料（在庫管理するもの）", value=seasonings_text, height=100)
                    st.markdown("---")
                    edit_instructions = st.text_area("作り方", value=selected_recipe["instructions"], height=150)
                    
                    update_button = st.form_submit_button("更新する")
                    
                    if update_button:
                        if edit_name:
                            foods_list = parse_ingredients(edit_foods_raw)
                            seasonings_list = parse_ingredients(edit_seasonings_raw)
                            
                            target_idx = next(i for i, r in enumerate(st.session_state.recipes) if r["name"] == selected_recipe["name"])
                            st.session_state.recipes[target_idx] = {
                                "name": edit_name,
                                "foods": foods_list,
                                "seasonings": seasonings_list,
                                "instructions": edit_instructions
                            }
                            
                            for s in seasonings_list:
                                if s["name"] not in st.session_state.inventory:
                                    st.session_state.inventory[s["name"]] = False
                            
                            save_data()
                            st.success("レシピを更新しました！")
                            st.rerun()
                        else:
                            st.error("レシピ名は必須です。")
                
                st.divider()
                st.subheader("🗑️ レシピの削除")
                st.warning("この操作は取り消せません。")
                if st.button("このレシピを削除する", type="primary"):
                    target_idx = next(i for i, r in enumerate(st.session_state.recipes) if r["name"] == selected_recipe["name"])
                    st.session_state.recipes.pop(target_idx)
                    save_data()
                    st.success(f"「{selected_recipe['name']}」を削除しました。")
                    st.rerun()

# ==========================================
# タブ2: レシピの登録
# ==========================================
with tab2:
    st.header("新しいレシピを登録")
    st.write("材料は **「名前, 分量」** とカンマで区切って入力します。右のリストを押すと自動入力されます。")
    
    # 画面を「入力フォーム側」と「リスト側」の左右2列に分割
    col_form, col_list = st.columns([2, 1])
    
    # ─── 右側：カンニングリスト ───
    with col_list:
        st.subheader("💡 登録済みリスト")
        
        all_food_names = set()
        all_seasoning_names = set()
        for r in st.session_state.recipes:
            for f in r["foods"]:
                all_food_names.add(f["name"])
            for s in r["seasonings"]:
                all_seasoning_names.add(s["name"])
                
        # 縦長になりすぎないようスクロール領域を作成
        with st.container(height=550):
            st.markdown("**🥩 食材**")
            if not all_food_names:
                st.caption("まだ登録されていません")
            else:
                for f_name in sorted(list(all_food_names)):
                    # ボタンが押されたら自動入力関数を呼び出す
                    st.button(f_name, key=f"btn_f_{f_name}", on_click=lambda name=f_name: add_food_to_draft(name))
            
            st.markdown("---")
            st.markdown("**🧂 調味料**")
            if not all_seasoning_names:
                st.caption("まだ登録されていません")
            else:
                for s_name in sorted(list(all_seasoning_names)):
                    st.button(s_name, key=f"btn_s_{s_name}", on_click=lambda name=s_name: add_seasoning_to_draft(name))

    # ─── 左側：入力フォーム ───
    with col_form:
        # ※ 自動入力と連動させるため、st.formを使わずに直接ウィジェットを配置しています
        st.text_input("レシピ名", placeholder="例：カレーライス", key="draft_name")
        
        st.markdown("---")
        st.text_area("🥩 食材（毎回買うもの）", placeholder="豚肉, 200g\nじゃがいも, 2個", height=150, key="draft_foods")
        st.text_area("🧂 調味料（在庫管理するもの）", placeholder="カレールー, 1/2箱", height=150, key="draft_seasonings")
        st.markdown("---")
        st.text_area("作り方", placeholder="1. 野菜を切る\n2. 炒める\n3. 煮込む", height=150, key="draft_instructions")
        
        # 登録ボタン
        if st.button("登録する", type="primary"):
            new_name = st.session_state.draft_name
            new_foods_raw = st.session_state.draft_foods
            new_seasonings_raw = st.session_state.draft_seasonings
            new_instructions = st.session_state.draft_instructions
            
            if new_name:
                foods_list = parse_ingredients(new_foods_raw)
                seasonings_list = parse_ingredients(new_seasonings_raw)
                
                st.session_state.recipes.append({
                    "name": new_name,
                    "foods": foods_list,
                    "seasonings": seasonings_list,
                    "instructions": new_instructions
                })
                
                for s in seasonings_list:
                    if s["name"] not in st.session_state.inventory:
                        st.session_state.inventory[s["name"]] = False
                
                save_data()
                
                # 登録完了後に入力欄をリセット
                st.session_state.draft_name = ""
                st.session_state.draft_foods = ""
                st.session_state.draft_seasonings = ""
                st.session_state.draft_instructions = ""
                
                st.success(f"「{new_name}」を登録し、データを保存しました！")
                st.rerun()
            else:
                st.error("レシピ名は必須です。")


# ==========================================
# タブ3: 調味料の在庫管理
# ==========================================
with tab3:
    st.header("🏠 調味料の在庫管理")
    st.write("チェックが入っているものは「家にある」、外れているものは「切らしている（買う必要がある）」状態です。")
    
    if not st.session_state.inventory:
        st.info("管理する調味料がありません。レシピを登録すると自動で追加されます。")
    else:
        search_query = st.text_input("調味料を検索", "")
        col1, col2 = st.columns(2)
        sorted_seasonings = sorted(st.session_state.inventory.keys())
        
        for i, ing in enumerate(sorted_seasonings):
            if search_query and search_query not in ing:
                continue
                
            with col1 if i % 2 == 0 else col2:
                current_status = st.session_state.inventory[ing]
                new_status = st.checkbox(ing, value=current_status, key=f"inv_{ing}")
                
                if new_status != current_status:
                    st.session_state.inventory[ing] = new_status
                    save_data()
                    st.rerun()
