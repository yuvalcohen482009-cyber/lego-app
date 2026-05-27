import streamlit as st
import trimesh
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="ממיר לגו אוטומטי", layout="wide")

st.title("🧱 מייצר מודלי לגו מתלת-ממד")
st.write("העלה קובץ תלת-ממד (OBJ או STL) של האובייקט שלך, והאתר יבנה אותו בלגו!")

# 1. רכיב העלאת קבצים
uploaded_file = st.file_uploader("בחר קובץ תלת-ממד מהמחשב", type=["obj", "stl"])

if uploaded_file is not None:
    # שמירת הקובץ הזמני
    with open("temp_model.obj", "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    try:
        # 2. טעינת המודל והפיכתו לקוביות
        mesh = trimesh.load("temp_model.obj")
        
        # סליידר לשליטה ברזולוציה
        pitch = st.slider("רמת פירוט (גודל קובייה - נמוך יותר משמעו יותר קוביות)", 0.2, 2.0, 0.8, step=0.1)
        
        voxel_grid = mesh.voxelized(pitch=pitch)
        matrix = voxel_grid.matrix
        
        # 3. סינון שכבות (הוראות שלב אחר שלב)
        max_layers = matrix.shape[2]
        st.sidebar.header("🔧 הוראות בנייה")
        layer_filter = st.sidebar.slider("הצג עד שכבה:", 1, max_layers, max_layers)
        
        # חילוץ מיקומי הקוביות
        x_indices, y_indices, z_indices = np.where(matrix[:, :, :layer_filter])
        
        # 4. יצירת הגרף התלת-ממדי
        fig = go.Figure(data=[go.Scatter3d(
            x=x_indices,
            y=y_indices,
            z=z_indices,
            mode='markers',
            marker=dict(
                size=10,
                symbol='square',
                color=z_indices,
                colorscale='Viridis',
                opacity=0.9,
                line=dict(color='black', width=2)
            )
        )])
        
        fig.update_layout(
            scene=dict(
                xaxis_title="X",
                yaxis_title="Y",
                zaxis_title="שכבה (Z)"
            ),
            margin=dict(l=0, r=0, b=0, t=0),
            height=600
        )
        
        # הצגת הגרף באתר
        st.plotly_chart(fig, use_container_width=True)
        
        # מדד כמויות
        st.success(f"המודל מוכן! סך הכל קוביות נדרשות: {len(x_indices)}")
        st.info(f"אתה צופה כרגע בשכבות 1 עד {layer_filter} מתוך {max_layers}")
        
    except Exception as e:
        st.error(f"שגיאה בעיבוד הקובץ. וודא שהקובץ תקין. פרטי השגיאה: {e}")
