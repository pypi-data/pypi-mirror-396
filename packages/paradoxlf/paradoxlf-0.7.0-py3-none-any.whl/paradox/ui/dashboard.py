import streamlit as st
import numpy as np
import os
import sys
import pandas as pd
import plotly.express as px

# Ensure we can import paradox
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from paradox.engine import LatentMemoryEngine
from paradox.media.image import SimpleImageEncoder, SimpleImageDecoder
from paradox.mixer import ParadoxMixer
from paradox.simulation import SimulationEnv

# Page Config
st.set_page_config(
    page_title="Paradox Latent Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Stylized Title
st.title("🧠 Paradox Latent Engine")
st.markdown("*\"Don't store the Cake. Store the Recipe.\"*")

# --- Sidebar: Engine Control ---
st.sidebar.header("⚙️ Engine Settings")
dim = st.sidebar.slider("Vector Dimension", 32, 1024, 64, step=32)
backend = st.sidebar.selectbox("Compute Backend", ["numpy", "torch"])

@st.cache_resource
def get_engine():
    # Singleton Engine for the session
    print("Initializing Engine...")
    eng = LatentMemoryEngine(dimension=dim, backend=backend)
    
    # Setup Media capabilities
    encoder = SimpleImageEncoder(64, 64)
    decoder = SimpleImageDecoder(64, 64)
    eng.set_encoder(encoder)
    eng.set_decoder(decoder)
    
    return eng, encoder, decoder

engine, encoder, decoder = get_engine()

# --- Tabs for Features ---
tab1, tab2, tab3 = st.tabs(["Media Studio", "Latent Laboratory", "Simulation"])

# === TAB 1: Media Studio ===
with tab1:
    st.header("🖼️ Media Studio")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Encode & Store")
        uploaded_file = st.file_uploader("Upload an Image", type=["png", "jpg", "jpeg"])
        obj_name = st.text_input("Memory Name (e.g. 'cat')", "my_image")
        
        if uploaded_file and st.button("🧠 Memorize to Latent Space"):
            from PIL import Image
            img = Image.open(uploaded_file)
            eid = engine.add(img, {"name": obj_name})
            st.success(f"Memorized as Object ID: {eid} | Vector stored.")
            st.image(img, width=150, caption="Original")

    with col2:
        st.subheader("Latent Memory Viewer")
        if engine.count > 0:
            st.write(f"Total Memories: {engine.count}")
            # Show table
            data = []
            for uid, meta in engine.objects.items():
                data.append({"ID": uid, "Name": meta.get("name", "Unknown")})
            st.dataframe(pd.DataFrame(data))
            
            # Reconstruction Test
            recon_id = st.number_input("Reconstruct ID", min_value=0, max_value=engine.count-1, step=1)
            if st.button("Reconstruct from Vector"):
                vec = engine.vectors[recon_id]
                img = decoder.decode(vec)
                st.image(img, width=150, caption=f"Reconstructed ID {recon_id}")
        else:
            st.info("Memory is empty. Upload images to fill it.")

# === TAB 2: Laboratory ===
with tab2:
    st.header("🧪 Latent Laboratory")
    st.write("Blend existing memories to create new concepts.")
    
    if engine.count >= 2:
        colA, colB, colRes = st.columns([1, 1, 1])
        
        with colA:
            id_a = st.selectbox("Concept A", options=range(engine.count), format_func=lambda x: engine.objects[x]['name'])
            img_a = decoder.decode(engine.vectors[id_a])
            st.image(img_a, width=100, caption="Concept A")
            
        with colB:
            id_b = st.selectbox("Concept B", options=range(engine.count), index=1, format_func=lambda x: engine.objects[x]['name'])
            img_b = decoder.decode(engine.vectors[id_b])
            st.image(img_b, width=100, caption="Concept B")
            
        ratio = st.slider("Blending Ratio (0=A, 1=B)", 0.0, 1.0, 0.5)
        
        with colRes:
            st.subheader("Result")
            vec_mix = ParadoxMixer.interpolate(engine.vectors[id_a], engine.vectors[id_b], ratio)
            img_mix = decoder.decode(vec_mix)
            st.image(img_mix, width=100, caption="Blended Concept")
            
            if st.button("Save New Concept"):
                new_name = f"Blend({engine.objects[id_a]['name']}+{engine.objects[id_b]['name']})"
                engine.add(img_mix, {"name": new_name})
                st.success(f"Saved as '{new_name}'")
    else:
        st.warning("Need at least 2 memories to blend.")

# === TAB 3: Simulation ===
with tab3:
    st.header("⚛️ Simulation View")
    
    if engine.count > 0:
        # Dimensionality Reduction for Visualization
        from sklearn.decomposition import PCA
        
        if engine.count >= 3:
            pca = PCA(n_components=2)
            coords = pca.fit_transform(engine.vectors)
            
            df_plot = pd.DataFrame(coords, columns=["x", "y"])
            df_plot["name"] = [engine.objects[i]["name"] for i in range(engine.count)]
            
            fig = px.scatter(df_plot, x="x", y="y", text="name", title="Latent Space Map (PCA)", color="name")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("Need at least 3 points for PCA visualization.")
            
        if st.button("Run Random Physics Step"):
            sim = SimulationEnv(engine)
            def drift_physics(vecs, dt, backend):
                return np.random.randn(*vecs.shape) * 0.1
            
            sim.step(drift_physics)
            st.experimental_rerun()
            
    else:
        st.write("Engine empty.")

st.markdown("---")
st.text("Paradox v0.5.0 Alpha | Built with Streamlit")
