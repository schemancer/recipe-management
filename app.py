import streamlit as st

st.set_page_config(page_title="レシピ＆お買い物マネージャー", layout="centered")

# --- セッションステートの初期化 ---
if 'recipes' not in st.session_state:
    st.session_state.recipes = [
        {
            "name": "豚の生姜焼き",
            "foods": [
                {"name": "豚肉", "amount": "200g"},
                {"name": "玉ねぎ", "amount": "1/2個"}
            ],
            "seasonings": [
                {"name": "醤油", "amount": "大さじ2"},
                {"name": "みりん", "amount": "大さじ1"},
                {"name": "酒", "amount": "大さじ1"},
                {"name": "生姜（チューブ）", "amount": "3cm"}
            ],
            "instructions": "1. 玉ねぎをスライス\n2. 調味料を合わせる\n3. 豚肉を炒め、玉ねぎと調味料を加えて絡める"
        }
    ]
if 'inventory' not in st.session_state:
    st.session_state.inventory = {
        "醤油": True, "みりん": False, "酒": True, "生姜（チューブ）": False
    }

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
        # --- 🔍 逆引き検索機能 ---
        # 登録されている全レシピから、存在する食材・調味料のリストを抽出
        all_ingredients = set()
        for r in st.session_state.recipes:
            for f in r["foods"]:
                all_ingredients.add(f["name"])
            for s in r["seasonings"]:
                all_ingredients.add(s["name"])
        
        st.markdown("##### 🔍 使いたい食材で絞り込む（逆引き検索）")
        selected_search_ingredients = st.multiselect(
            "消費したい食材や調味料を選んでください",
            options=sorted(list(all_ingredients)),
            placeholder="例：豚肉、玉ねぎ..."
        )
        
        # 絞り込みロジック（選択した食材がすべて含まれるレシピを残す）
        filtered_recipes = []
        for r in st.session_state.recipes:
            if not selected_search_ingredients:
                filtered_recipes.append(r)
            else:
                # このレシピに含まれるすべての材料名を取得
                recipe_ingredients = [f["name"] for f in r["foods"]] + [s["name"] for s in r["seasonings"]]
                
                # 検索条件の食材が「すべて」含まれているかチェック
                if all(ing in recipe_ingredients for ing in selected_search_ingredients):
                    filtered_recipes.append(r)
        
        st.divider()
        
        # --- レシピ選択・表示 ---
        if not filtered_recipes:
            st.warning("条件に合うレシピが見つかりませんでした。絞り込みを解除するか、別の食材を選んでください。")
        else:
            recipe_names = [r["name"] for r in filtered_recipes]
            selected_name = st.selectbox("📝 レシピを選択:", recipe_names)
            
            selected_recipe = next(r for r in filtered_recipes if r["name"] == selected_name)
            
            # --- 1. 買い物リスト ---
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

            # --- 2. 材料一覧 ---
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

            # --- 3. 作り方 ---
            st.divider()
            st.subheader("📖 作り方")
            st.write(selected_recipe["instructions"])


# ==========================================
# タブ2: レシピの登録
# ==========================================
with tab2:
    st.header("新しいレシピを登録")
    st.write("材料は **「名前, 分量」** とカンマで区切って、1行ずつ入力してください。")
    
    with st.form("recipe_form"):
        new_name = st.text_input("レシピ名", placeholder="例：カレーライス")
        
        st.markdown("---")
        new_foods_raw = st.text_area(
            "🥩 食材（毎回買うもの）", 
            placeholder="豚肉, 200g\nじゃがいも, 2個\n玉ねぎ, 1個",
            height=100
        )
        new_seasonings_raw = st.text_area(
            "🧂 調味料（在庫管理するもの）", 
            placeholder="カレールー, 1/2箱\nサラダ油, 大さじ1",
            height=100
        )
        st.markdown("---")
        new_instructions = st.text_area("作り方", placeholder="1. 野菜を切る\n2. 炒める\n3. 煮込む")
        
        submit_button = st.form_submit_button("登録する")
        
        if submit_button:
            if new_name:
                def parse_ingredients(raw_text):
                    result = []
                    for line in raw_text.strip().split('\n'):
                        if line.strip():
                            parts = line.split(',')
                            name = parts[0].strip()
                            amount = parts[1].strip() if len(parts) > 1 else "適量"
                            result.append({"name": name, "amount": amount})
                    return result
                
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
                        
                st.success(f"「{new_name}」を登録しました！")
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
