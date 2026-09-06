import streamlit as st

# ページ設定
st.set_page_config(page_title="レシピ＆お買い物マネージャー", layout="centered")

# --- セッションステートの初期化 ---
# アプリをリロードしてもデータを保持するための初期設定
if 'recipes' not in st.session_state:
    st.session_state.recipes = [
        {
            "name": "豚の生姜焼き",
            "ingredients": ["豚肉", "玉ねぎ", "醤油", "みりん", "酒", "生姜"],
            "instructions": "1. 玉ねぎをスライス\n2. 調味料を合わせる\n3. 豚肉を炒め、玉ねぎと調味料を加えて絡める"
        }
    ]
if 'inventory' not in st.session_state:
    # True = 家にある, False = 家にない（買う必要がある）
    st.session_state.inventory = {
        "豚肉": False, "玉ねぎ": True, "醤油": True, 
        "みりん": False, "酒": True, "生姜": False
    }

# --- タイトル ---
st.title("🍳 レシピ＆お買い物マネージャー")

# --- タブの作成 ---
tab1, tab2, tab3 = st.tabs(["レシピ一覧（買い物リスト）", "レシピの登録", "材料管理（家の在庫）"])

# ==========================================
# タブ1: レシピ一覧（スーパーで見る画面）
# ==========================================
with tab1:
    st.header("今日作るレシピを選ぶ")
    if not st.session_state.recipes:
        st.info("レシピが登録されていません。「レシピの登録」タブから追加してください。")
    else:
        # 登録されているレシピ名リストを取得
        recipe_names = [r["name"] for r in st.session_state.recipes]
        selected_name = st.selectbox("📝 レシピを選択:", recipe_names)
        
        # 選択されたレシピのデータを取得
        selected_recipe = next(r for r in st.session_state.recipes if r["name"] == selected_name)
        
        st.divider()
        st.subheader("🛒 買い物リスト")
        
        buy_list = []
        in_stock_list = []
        
        # 材料の在庫チェック
        for ing in selected_recipe["ingredients"]:
            # 家にあるかチェック（デフォルトはFalse:ない）
            is_in_stock = st.session_state.inventory.get(ing, False)
            if is_in_stock:
                in_stock_list.append(ing)
            else:
                buy_list.append(ing)
        
        # 不足しているもの（買うもの）を強調表示
        if buy_list:
            st.error(f"**【スーパーで買うもの】**\n\n" + " / ".join(buy_list))
        else:
            st.success("✨ 必要な材料はすべて家にあります！買わなくてOK！")
            
        # 家にあるもの
        if in_stock_list:
            st.info(f"**【家にあるもの】**\n\n" + " / ".join(in_stock_list))

        st.divider()
        st.subheader("📖 作り方")
        st.write(selected_recipe["instructions"])


# ==========================================
# タブ2: レシピの登録
# ==========================================
with tab2:
    st.header("新しいレシピを登録")
    with st.form("recipe_form"):
        new_name = st.text_input("レシピ名", placeholder="例：カレーライス")
        new_ingredients_raw = st.text_area("材料（カンマ「,」区切りで入力）", placeholder="例：豚肉, じゃがいも, 人参, 玉ねぎ, カレールー")
        new_instructions = st.text_area("作り方", placeholder="1. 野菜を切る\n2. 炒める\n3. 煮込む")
        
        submit_button = st.form_submit_button("登録する")
        
        if submit_button:
            if new_name and new_ingredients_raw:
                # カンマ区切りの文字列をリストに変換し、空白を削除
                ing_list = [x.strip() for x in new_ingredients_raw.split(',') if x.strip()]
                
                # レシピを追加
                st.session_state.recipes.append({
                    "name": new_name,
                    "ingredients": ing_list,
                    "instructions": new_instructions
                })
                
                # 新しい材料を在庫リストに追加（デフォルトは「ない(False)」に設定）
                for ing in ing_list:
                    if ing not in st.session_state.inventory:
                        st.session_state.inventory[ing] = False
                        
                st.success(f"「{new_name}」を登録しました！")
            else:
                st.error("レシピ名と材料は必須です。")


# ==========================================
# タブ3: 材料管理（家の在庫）
# ==========================================
with tab3:
    st.header("🏠 家にあるもの管理")
    st.write("チェックが入っているものは「家にある」、外れているものは「切らしている（買う必要がある）」状態です。")
    
    if not st.session_state.inventory:
        st.info("管理する材料がありません。レシピを登録すると自動で追加されます。")
    else:
        # 検索フィルター
        search_query = st.text_input("材料を検索", "")
        
        # 2カラムで表示して画面をスッキリさせる
        col1, col2 = st.columns(2)
        
        # 在庫のリストをアルファベット・五十音順等にソートして表示
        sorted_ingredients = sorted(st.session_state.inventory.keys())
        
        for i, ing in enumerate(sorted_ingredients):
            # 検索フィルターに引っかからないものはスキップ
            if search_query and search_query not in ing:
                continue
                
            # 交互にカラムに配置
            with col1 if i % 2 == 0 else col2:
                # チェックボックスの状態が変わったらセッションステートを更新
                current_status = st.session_state.inventory[ing]
                new_status = st.checkbox(ing, value=current_status, key=f"inv_{ing}")
                if new_status != current_status:
                    st.session_state.inventory[ing] = new_status