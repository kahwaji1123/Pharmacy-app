import sqlite3
import streamlit as st

# إعداد قاعدة البيانات
def init_db():
    conn = sqlite3.connect("pharmacy.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()

init_db()

st.title("📱 نظام إدارة الصيدلية")

# تبويب للتحكم (إضافة / بيع / عرض)
tab1, tab2 = st.tabs(["📦 إدارة المخزون", "💰 عمليات البيع"])

with tab1:
    st.header("إضافة دواء جديد")
    name = st.text_input("اسم الدواء")
    qty = st.number_input("الكمية", min_value=1, step=1)
    price = st.number_input("السعر", min_value=0.0, step=0.25)
    
    if st.button("إضافة للمخزون"):
        if name:
            conn = sqlite3.connect("pharmacy.db")
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO inventory (name, quantity, price) VALUES (?, ?, ?)", (name, qty, price))
                conn.commit()
                st.success(f"تم إضافة {name} بنجاح!")
            except sqlite3.IntegrityError:
                st.error("هذا الدواء موجود بالفعل!")
            finally:
                conn.close()
        else:
            st.error("يرجى كتابة اسم الدواء")

    st.header("📋 المخزون الحالي")
    conn = sqlite3.connect("pharmacy.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, quantity, price FROM inventory")
    rows = cursor.fetchall()
    conn.close()
    
    if rows:
        for r in rows:
            st.write(f"**[{r[0]}] {r[1]}** | الكمية: {r[2]} | السعر: {r[3]:.2f} ريال")
    else:
        st.info("المخزن فارغ حالياً.")

with tab2:
    st.header("إتمام عملية بيع")
    conn = sqlite3.connect("pharmacy.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM inventory")
    med_list = [r[0] for r in cursor.fetchall()]
    conn.close()
    
    if med_list:
        selected_med = st.selectbox("اختر الدواء للمبيعات", med_list)
        sell_qty = st.number_input("الكمية المراد بيعها", min_value=1, step=1)
        
        if st.button("تأكيد البيع"):
            conn = sqlite3.connect("pharmacy.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id, quantity, price FROM inventory WHERE name = ?", (selected_med,))
            med_data = cursor.fetchone()
            
            if med_data:
                med_id, current_qty, price = med_data
                if sell_qty > current_qty:
                    st.error(f"المخزون غير كافٍ! المتوفر: {current_qty}")
                else:
                    new_qty = current_qty - sell_qty
                    if new_qty == 0:
                        cursor.execute("DELETE FROM inventory WHERE id = ?", (med_id,))
                    else:
                        cursor.execute("UPDATE inventory SET quantity = ? WHERE id = ?", (new_qty, med_id))
                    conn.commit()
                    
                    total = sell_qty * price
                    st.success(f"تم البيع بنجاح! الإجمالي: {total:.2f}")
            conn.close()
    else:
        st.info("لا توجد أدوية للبيع.")
