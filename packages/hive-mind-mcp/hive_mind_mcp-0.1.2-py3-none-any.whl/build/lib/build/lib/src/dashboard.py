import streamlit as st
import pandas as pd
import json
import os
import glob
import plotly.express as px
from datetime import datetime, timedelta

# Page Configuration
st.set_page_config(
    page_title="MCP Orchestrator Dashboard", 
    layout="wide", 
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #4B5563;
        margin-top: -10px;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #F3F4F6;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #E5E7EB;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<div class="main-header">📊 MCP Orchestrator Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Observability & Cost Management Center</div>', unsafe_allow_html=True)
with col2:
    st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")

# --- Icons & Colors ---
PROVIDER_ICONS = {
    "openai": "🧠", "anthropic": "🤖", "deepseek": "⚡", "google": "🌐", 
    "gemini": "💎", "mistral": "🌪️", "groq": "🚀", "openrouter": "🔗", "generic": "🔌"
}
PROVIDER_COLORS = {
    "openai": "#10a37f",    # OpenAI Green
    "anthropic": "#d97757", # Anthropic Clay
    "deepseek": "#4e6b9f",  # DeepSeek Blue
    "google": "#4285F4",    # Google Blue
    "gemini": "#4285F4",    # Gemini Blue
    "mistral": "#fd6f22",   # Mistral Orange
    "groq": "#f55036",      # Groq Red
    "openrouter": "#6366f1",# OpenRouter Indigo
    "generic": "#888888"    # Gray
}

# --- Data Loading Helper ---
def load_usage():
    path = os.path.expanduser("~/.mcp_orchestrator/usage.json")
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except: return {}
    return {}

def load_sessions(artifacts_dir=".hive_mind"):
    if not os.path.exists(artifacts_dir):
        return []
    
    sessions = []
    # Sort type directories to ensure stability
    for type_dir in sorted(glob.glob(os.path.join(artifacts_dir, "*"))):
        if os.path.isdir(type_dir):
            session_type = os.path.basename(type_dir)
            # Sort session directories
            for session_path in sorted(glob.glob(os.path.join(type_dir, "*")), reverse=True):
                if os.path.isdir(session_path):
                    meta_path = os.path.join(session_path, "metadata.json")
                    # Parse full timestamp from directory name (YYYY-MM-DD_HH-MM-SS)
                    parts = os.path.basename(session_path).split("_")
                    date_str = parts[0]
                    time_str = parts[1].replace("-", ":") if len(parts) > 1 else ""
                    display_time = f"{date_str} {time_str}".strip()

                    meta = {}
                    if os.path.exists(meta_path):
                        try:
                            with open(meta_path, "r") as f: meta = json.load(f)
                        except: pass
                    
                    sessions.append({
                        "Type": session_type,
                        "Topic": meta.get("topic") or meta.get("prompt") or f"{session_type.replace('_', ' ').title()} ({meta.get('content_length', '?')} chars)",
                        "Time": meta.get("start_time") or display_time,
                        "Path": session_path,
                        "Files": len(glob.glob(os.path.join(session_path, "*"))),
                        "Cost": meta.get("cost", 0.0) 
                    })
    return sessions

# --- Load Data ---
usage_data = load_usage()
sessions_data = load_sessions()
df_sessions = pd.DataFrame(sessions_data)

# Convert Time to Datetime objects for filtering
if not df_sessions.empty:
    df_sessions['Datetime'] = pd.to_datetime(df_sessions['Time'], errors='coerce')

# --- Layout: Tabs ---
tab_cost, tab_analytics, tab_explorer, tab_models = st.tabs(["💰 Budget & Cost", "📈 Analytics", "🗂️ Session Explorer", "🤖 Model Catalog"])

# --- TAB 1: BUDGET & COST ---
with tab_cost:
    st.markdown("### Cost Overview")
    
    # 1. Base Data
    df_usage = pd.DataFrame(usage_data.get("history", []))
    if not df_usage.empty:
        df_usage['timestamp'] = pd.to_datetime(df_usage['timestamp'], unit='s')
        
    # 2. Controls (Identical to Session Explorer style)
    c_filter, c_void = st.columns([2, 1]) # Adjusted ratio
    with c_filter:
        c_date, c_prov = st.columns(2)
        with c_date:
            # Default to last 7 days + today
            today = datetime.now()
            last_week = today - timedelta(days=7)
            date_range = st.date_input(
                "Filter Date Range",
                value=(last_week, today),
                key="cost_date_filter"
            )
        with c_prov:
            all_providers = sorted(df_usage['provider'].unique()) if not df_usage.empty else []
            selected_providers = st.multiselect(
                "Filter by Provider",
                all_providers,
                default=all_providers,
                key="cost_prov_filter"
            )
    
    # 3. Apply Filter
    df_filtered = df_usage.copy()
    if not df_filtered.empty:
        # Date Filter
        if len(date_range) == 2:
            start_date = pd.Timestamp(date_range[0])
            end_date = pd.Timestamp(date_range[1]) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
            mask = (df_filtered['timestamp'] >= start_date) & (df_filtered['timestamp'] <= end_date)
            df_filtered = df_filtered.loc[mask]
            
        # Provider Filter
        if selected_providers:
            df_filtered = df_filtered[df_filtered['provider'].isin(selected_providers)]
    
    # 4. Metrics Calculation
    
    # Global Totals
    total_usd_global = usage_data.get("total_usd", 0.0)
    daily_limit = float(os.getenv("DAILY_BUDGET_USD", "2.00"))
    
    # Filtered View logic
    filtered_usd = df_filtered['cost'].sum() if not df_filtered.empty else 0.0
    
    remaining = max(0, daily_limit - total_usd_global) # Budget is usually daily/global, but let's stick to global for budget logic
    pct_used = min(1.0, total_usd_global / daily_limit) if daily_limit > 0 else 0
    
    # Hero Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric(
        "Filtered Cost / Total", 
        f"${filtered_usd:.4f}", 
        delta=f"of ${total_usd_global:.4f} Total"
    )
    c2.metric("Daily Limit", f"${daily_limit:.2f}")
    c3.metric("Remaining Budget", f"${remaining:.4f}", delta_color="normal")
    
    st.markdown(f"**Budget Usage (Today):** {pct_used*100:.1f}%")
    st.progress(pct_used)
    
    st.divider()
    
# --- CUSTOM COMPONENT OVERRIDE ---
import hashlib
import inspect
from streamlit_adjustable_columns import _component_func, HidableContainer

def condensed_adjustable_columns(
    spec=None,
    labels=None,
    gap="small",
    vertical_alignment="top",
    border=False,
    return_widths=False,
    initial_hidden=None,
    key=None,
):
    """
    Custom version of adjustable_columns with REDUCED HEIGHT (20px instead of 60px)
    to eliminate the empty header space when labels are empty.
    """
    # Handle spec parameter (same logic as st.columns)
    if spec is None:
        spec = 2  # Default to 2 equal columns

    if isinstance(spec, int):
        widths = [1] * spec
    elif hasattr(spec, "__iter__"):
        widths = list(spec)
    else:
        raise ValueError("spec must be an integer or an iterable of numbers")

    # Validate widths
    if not widths:
        raise ValueError("spec must specify at least one column")
    if any(w <= 0 for w in widths):
        raise ValueError("Column widths must be positive numbers")

    # Set default labels
    if labels is None:
        labels = [f"Col {i+1}" for i in range(len(widths))]
    elif len(labels) != len(widths):
        raise ValueError("labels must have the same length as the number of columns")

    # Validate initial_hidden parameter
    if initial_hidden is not None:
        if len(initial_hidden) != len(widths):
            raise ValueError(
                "initial_hidden must have the same length as the number of columns"
            )
        if not all(isinstance(x, bool) for x in initial_hidden):
            raise ValueError("initial_hidden must contain only boolean values")
    else:
        initial_hidden = [False] * len(widths)

    # Create unique identifier for this set of columns
    if key is None:
        caller = inspect.currentframe().f_back
        try:
            src = f"{caller.f_code.co_filename}:{caller.f_lineno}"
        finally:
            del caller
        unique_id = hashlib.md5(src.encode()).hexdigest()[:8]
    else:
        unique_id = key

    # Create session state keys for storing current widths and hidden state
    session_key = f"adjustable_columns_widths_{unique_id}"
    hidden_key = f"adjustable_columns_hidden_{unique_id}"

    # Initialize or get current widths from session state
    if session_key not in st.session_state:
        st.session_state[session_key] = widths.copy()

    current_widths = st.session_state[session_key]

    # Initialize or get hidden state from session state
    if hidden_key not in st.session_state:
        st.session_state[hidden_key] = initial_hidden.copy()

    hidden_columns = st.session_state[hidden_key]

    # Ensure we have the right number of widths and hidden states
    if len(current_widths) != len(widths):
        current_widths = widths.copy()
        st.session_state[session_key] = current_widths

    if len(hidden_columns) != len(widths):
        hidden_columns = initial_hidden.copy()
        st.session_state[hidden_key] = hidden_columns

    # Prepare configuration for the resizer component
    config = {
        "widths": current_widths,
        "labels": labels,
        "gap": gap,
        "border": border,
        "hidden": hidden_columns,
    }

    # Create the resize handles component with REDUCED HEIGHT
    component_value = _component_func(
        config=config,
        key=f"resizer_{unique_id}",
        default={"widths": current_widths, "hidden": hidden_columns},
        height=20,  # MODIFIED: Reduced from 60 to 20 to fit better
    )

    # Update current widths and hidden state from component if it has been modified
    if component_value:
        needs_update = False

        if "widths" in component_value:
            new_widths = component_value["widths"]
            if new_widths != current_widths:
                st.session_state[session_key] = new_widths
                current_widths = new_widths
                needs_update = True

        if "hidden" in component_value:
            new_hidden = component_value["hidden"]
            if new_hidden != hidden_columns:
                st.session_state[hidden_key] = new_hidden
                hidden_columns = new_hidden
                needs_update = True

        if needs_update:
            st.rerun()

    # Add CSS to ensure perfect alignment between resize handles and columns
    alignment_css = """
    <style>
    /* Ensure the resize handles iframe has no extra spacing */
    iframe[title="streamlit_adjustable_columns.streamlit_adjustable_columns"] {
        border: none !important;
        background: transparent !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    .element-container:has(iframe[title="streamlit_adjustable_columns.streamlit_adjustable_columns"]) {
        margin-bottom: 0 !important;
    }
    .element-container:has(iframe[title="streamlit_adjustable_columns.streamlit_adjustable_columns"]) + div[data-testid="column"] {
        margin-top: 0 !important;
    }
    </style>
    """
    st.markdown(alignment_css, unsafe_allow_html=True)

    # Create the actual Streamlit columns with current widths
    MIN_WIDTH_RATIO = 0.06
    total_width = sum(current_widths)
    min_width_absolute = MIN_WIDTH_RATIO * total_width

    streamlit_widths = [max(width, min_width_absolute) for width in current_widths]

    st_columns = st.columns(
        spec=streamlit_widths,
        gap=gap,
        vertical_alignment=vertical_alignment,
        border=border,
    )

    wrapped_columns = [
        HidableContainer(col, is_hidden=hidden)
        for col, hidden in zip(st_columns, hidden_columns)
    ]

    if return_widths:
        return {
            "columns": wrapped_columns,
            "widths": current_widths,
            "hidden": hidden_columns,
        }
    else:
        return wrapped_columns

def render_dashboard(df_source=None):
    # Cost History Chart
    if df_source is not None:
        df_usage = df_source.copy()
    else:
        df_usage = pd.DataFrame(usage_data.get("history", []))

    if not df_usage.empty:
        # Ensure timestamp is datetime if not already
        if not pd.api.types.is_datetime64_any_dtype(df_usage['timestamp']):
             df_usage['timestamp'] = pd.to_datetime(df_usage['timestamp'], unit='s')

        # --- LAYOUT CONTROLS ---
        # Using CUSTOM condensed splitter for minimal header height
        # Layout: Chart (Left) | Nucleus (Right)
        col_chart, col_nucleus = condensed_adjustable_columns([2, 1], labels=["", ""])
        
        # --- NUCLEUS VISUALIZATION (RIGHT COLUMN) ---
        with col_nucleus:
            st.subheader("Hive Mind")
            
            # 1. Calculate Metrics (Using the dataframe we prepared)
            provider_counts = df_usage['provider'].value_counts()
            total_calls = len(df_usage)
            
            # 2. SVG Generator Helper
            def render_nucleus_diagram(counts, total):
                import math
                import glob
                import os
                import base64
                
                # Helper to load icon as base64
                def get_icon_b64(provider_name):
                    base_dir = "src/assets/icons"
                    for ext in ["svg", "png", "jpg"]:
                        path = os.path.join(base_dir, f"{provider_name}.{ext}")
                        if os.path.exists(path):
                            with open(path, "rb") as f:
                                data = f.read()
                                b64 = base64.b64encode(data).decode('utf-8')
                                mime = f"image/svg+xml" if ext == "svg" else f"image/{ext}"
                                return f"data:{mime};base64,{b64}"
                    return None

                # Discovery Logic
                discovered = set()
                for f in glob.glob("src/providers/*.py"):
                    name = os.path.basename(f).replace(".py", "")
                    if name not in ["base", "__init__"]:
                        if name == "openai_compatible": name = "generic"
                        discovered.add(name)
                for f in glob.glob("plugins/*.py"):
                    name = os.path.basename(f).replace(".py", "")
                    if name != "__init__": discovered.add(name)
                    
                active_providers = set(counts.index.tolist())
                all_providers = sorted(list(discovered.union(active_providers)))

                # Layout
                cx, cy = 400, 300 # Moved down slightly to accommodate top labels
                radius = 220      # Increased radius for larger spread
                
                # Responsive SVG: Tighter viewBox to "zoom in" (800x600 canvas cropped to 100-700 x)
                # Added margin-top: 40px to align visually with the chart center
                lines = []
                lines.append(f'<svg viewBox="100 0 600 600" style="width: 100%; height: auto; margin-top: 20px;" xmlns="http://www.w3.org/2000/svg">')
                lines.append('<defs>')
                lines.append('<filter id="shadow" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.2"/></filter>')
                lines.append('</defs>')
                
                lines.append('<style>')
                lines.append('@keyframes flow { to { stroke-dashoffset: -20; } }')
                lines.append('.flow-line { stroke-dasharray: 5, 5; animation: flow 1s linear infinite; }')
                lines.append('</style>')
                
                # Central Nucleus
                lines.append(f'<circle cx="{cx}" cy="{cy}" r="60" fill="#1E3A8A" stroke="#3B82F6" stroke-width="4" filter="url(#shadow)" />')
                lines.append(f'<text x="{cx}" y="{cy}" font-family="Arial" font-size="45" text-anchor="middle" dominant-baseline="middle" fill="white">🔮</text>')
                lines.append(f'<text x="{cx}" y="{cy+85}" font-family="Arial" font-size="18" text-anchor="middle" fill="#1E3A8A" font-weight="bold">HIVE MIND</text>')
                
                count = len(all_providers)
                for i, provider in enumerate(all_providers):
                    angle = (2 * math.pi * i) / count
                    px = cx + radius * math.cos(angle)
                    py = cy + radius * math.sin(angle)
                    
                    calls = counts.get(provider, 0)
                    isActive = calls > 0
                    pct = (calls / total * 100) if total > 0 else 0
                    width = max(2, min(12, (pct / 8))) 
                    
                    # Resolve Icon
                    icon_b64 = get_icon_b64(provider.split(':')[0])
                    fallback_emoji = PROVIDER_ICONS.get(provider.split(':')[0], "🔌")
                    
                    if isActive:
                        lines.append(f'<line x1="{cx}" y1="{cy}" x2="{px}" y2="{py}" stroke="#93C5FD" stroke-width="{width}" class="flow-line" />')
                        
                        # Node Circle
                        lines.append(f'<circle cx="{px}" cy="{py}" r="40" fill="white" stroke="#6B7280" stroke-width="2" filter="url(#shadow)" />')
                        
                        if icon_b64:
                            lines.append(f'<defs><clipPath id="clip-{i}"><circle cx="{px}" cy="{py}" r="30" /></clipPath></defs>')
                            lines.append(f'<image href="{icon_b64}" x="{px-30}" y="{py-30}" width="60" height="60" clip-path="url(#clip-{i})" />')
                        else:
                            lines.append(f'<text x="{px}" y="{py}" font-family="Arial" font-size="35" text-anchor="middle" dominant-baseline="middle">{fallback_emoji}</text>')
                        
                        lines.append(f'<text x="{px}" y="{py+55}" font-family="Arial" font-size="16" text-anchor="middle" font-weight="bold" fill="#374151">{provider.upper()}</text>')
                        lines.append(f'<text x="{px}" y="{py+75}" font-family="Arial" font-size="14" text-anchor="middle" fill="#6B7280">{calls} calls ({pct:.1f}%)</text>')
                    else:
                        lines.append(f'<circle cx="{px}" cy="{py}" r="35" fill="#F3F4F6" stroke="#D1D5DB" stroke-width="1" />')
                        if icon_b64:
                             lines.append(f'<image href="{icon_b64}" x="{px-25}" y="{py-25}" width="50" height="50" opacity="0.6" />')
                        else:
                            lines.append(f'<text x="{px}" y="{py}" font-family="Arial" font-size="30" text-anchor="middle" dominant-baseline="middle" opacity="0.6">{fallback_emoji}</text>')
                        lines.append(f'<text x="{px}" y="{py+55}" font-family="Arial" font-size="14" text-anchor="middle" fill="#9CA3AF">{provider.upper()}</text>')
                        
                lines.append('</svg>')
                return "".join(lines)

            # Render
            st.markdown(render_nucleus_diagram(provider_counts, total_calls), unsafe_allow_html=True)
            
        # --- CHART VISUALIZATION (LEFT COLUMN) ---
        with col_chart:
            df_chart = df_usage.copy()
            df_chart['Color_Key'] = df_chart['provider'].apply(lambda p: p.split(':')[0])

            # Resample: Bin data by 1 min, keeping empty bins to ensure flat cumulative line
            # 1. Sum cost (missing = 0)
            # 2. First provider/color (missing = None, we'll filter these for bars)
            df_resampled = df_chart.set_index('timestamp').resample('1min').agg({
                'cost': 'sum', 
                'Color_Key': 'first', 
                'provider': 'first'
            })
            
            # Fill missing costs with 0 for correct cumulative calculation
            df_resampled['cost'] = df_resampled['cost'].fillna(0)
            df_resampled['cumulative_cost'] = df_resampled['cost'].cumsum()
            
            # Reset index to get timestamp back as column
            df_full = df_resampled.reset_index()
            
            # Create a separate DF for Bars (only non-zero usage) to avoid empty bars in legend/hover
            df_bars = df_full[df_full['cost'] > 0].copy()

            st.subheader("Spending Trend")
            
            # Custom HTML Legend (same as before)
            def render_html_legend(providers):
                 import base64
                 
                 def get_src(p_name):
                     base_dir = "src/assets/icons"
                     for ext in ["svg", "png", "jpg"]:
                         path = os.path.join(base_dir, f"{p_name}.{ext}")
                         if os.path.exists(path):
                             with open(path, "rb") as f:
                                 d = base64.b64encode(f.read()).decode()
                                 return f"data:image/{ext if ext!='svg' else 'svg+xml'};base64,{d}"
                     return None

                 items = []
                 for p in providers:
                     name = p.split(':')[0]
                     color = PROVIDER_COLORS.get(name, "#888888")
                     src = get_src(name)
                     emoji = PROVIDER_ICONS.get(name, "🔌")
                     
                     if src:
                         icon_img = f'<img src="{src}" style="width:20px; height:20px; margin-right:5px; vertical-align:middle; border-radius:50%;">'
                     else:
                         icon_img = f'<span style="font-size:18px; margin-right:5px;">{emoji}</span>'
                     
                     # Build item as a single line string
                     item_html = (
                        f'<div style="display:flex; align-items:center; margin-right:15px; margin-bottom:10px;">'
                        f'<div style="width:12px; height:12px; background-color:{color}; border-radius:3px; margin-right:8px;"></div>'
                        f'{icon_img}'
                        f'<span style="font-weight:600; color:#374151; font-size:14px;">{p.upper()}</span>'
                        f'</div>'
                     )
                     items.append(item_html)
                 
                 return f'<div style="display:flex; flex-wrap:wrap; margin-bottom:10px; justify-content:start;">{"".join(items)}</div>'
            
            # Render Legend (Active providers only)
            unique_providers = sorted(df_bars['provider'].unique())
            st.markdown(render_html_legend(unique_providers), unsafe_allow_html=True)
            
            # Plotly Graph Objects for Dual Axis (Bar + Line)
            import plotly.graph_objects as go
            
            fig = go.Figure()
            
            # Bar Trace (Diff Cost) - Use df_bars
            for p in unique_providers:
                p_data = df_bars[df_bars['provider'] == p]
                color = PROVIDER_COLORS.get(p.split(':')[0], "#888888")
                fig.add_trace(go.Bar(
                    x=p_data['timestamp'], 
                    y=p_data['cost'],
                    name=p,
                    marker_color=color,
                    showlegend=False 
                ))

            # Cumulative Line Trace (Secondary Axis)
            fig.add_trace(go.Scatter(
                x=df_full['timestamp'],
                y=df_full['cumulative_cost'],
                name="Accumulated Cost",
                line=dict(color="#22d3ee", width=3, dash='dot'), # Cyan for dark mode visibility
                mode='lines',
                yaxis='y2'
            ))

            fig.update_layout(
                title=None,
                margin=dict(t=10, l=0, r=10),
                yaxis=dict(title="Cost Interval (USD)", showgrid=False),
                yaxis2=dict(
                    title="Total Accumulated (USD)", 
                    overlaying='y', 
                    side='right',
                    showgrid=True,
                    gridcolor='rgba(128,128,128,0.2)' # Lighter gray for grid
                ),
                legend=dict(
                    orientation="h", 
                    yanchor="bottom", 
                    y=1.02, 
                    xanchor="right", 
                    x=1,
                    font=dict(color="white") # Ensure legend text is visible
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
            )
            
            st.plotly_chart(fig, width="stretch")
    else:
        st.info("No spending history recorded yet.")


# --- TAB 2: ANALYTICS ---
# --- TAB 2: ANALYTICS ---
with tab_analytics:
    if not df_sessions.empty:
        st.markdown("### Operational Insights")
        
        # 1. Filters
        c_filter, c_void = st.columns([2, 1])
        with c_filter:
            c_date, c_type = st.columns(2)
            with c_date:
                # Default to last 7 days + today
                today = datetime.now()
                last_week = today - timedelta(days=7)
                date_range = st.date_input(
                    "Filter Date Range",
                    value=(last_week, today),
                    key="analytics_date_filter"
                )
            with c_type:
                all_types = sorted(df_sessions['Type'].unique())
                selected_types = st.multiselect(
                    "Filter by Type",
                    all_types,
                    default=all_types,
                    key="analytics_type_filter"
                )
        
        # 2. Apply Filters
        df_analytics = df_sessions.copy()
        
        # Date Filter
        if len(date_range) == 2:
            start_date = pd.Timestamp(date_range[0])
            end_date = pd.Timestamp(date_range[1]) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
            # Ensure filtering respects the chosen dates (inclusive)
            # df_sessions has 'Datetime' column
            mask = (df_analytics['Datetime'] >= start_date) & (df_analytics['Datetime'] <= end_date)
            df_analytics = df_analytics.loc[mask]
            
        # Type Filter
        if selected_types:
            df_analytics = df_analytics[df_analytics['Type'].isin(selected_types)]
            
        st.divider()

        # 3. Visualizations (Using Filtered Data)
        if not df_analytics.empty:
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Sessions", len(df_analytics))
            m2.metric("Avg Files/Session", f"{df_analytics['Files'].mean():.1f}")
            m3.metric("Most Active Type", df_analytics['Type'].mode()[0] if not df_analytics.empty else "N/A")
            
            c1, c2 = st.columns(2)
            
            with c1:
                st.subheader("Sessions by Type")
                type_counts = df_analytics['Type'].value_counts().reset_index()
                type_counts.columns = ['Type', 'Count']
                fig_pie = px.pie(type_counts, values='Count', names='Type', hole=0.4)
                st.plotly_chart(fig_pie, width="stretch")
                
            with c2:
                st.subheader("Activity Timeline")
                # Convert rough timestamp to datetime if possible, simplistic approach
                try:
                    # Assuming format YYYY-MM-DD
                    # If Time is mostly date strings, this works. If it's a mix, might be noisy.
                    df_analytics['Date'] = pd.to_datetime(df_analytics['Time']).dt.date
                    date_counts = df_analytics['Date'].value_counts().sort_index()
                    st.bar_chart(date_counts)
                except:
                    st.warning("Could not parse timestamps for timeline.")
        else:
             st.warning("No sessions found for the selected filters.")
    else:
        st.info("No sessions available for analytics.")

# --- TAB 3: SESSION EXPLORER (Original Logic Enhanced) ---
with tab_explorer:
    st.markdown("### Artifact Inspector")
    
    if not df_sessions.empty:
        # Filters in an expander to keep it clean
        with st.expander("🔎 Filter & Search", expanded=True):
            f1, f2, f3 = st.columns([1, 1, 2])
            with f1:
                all_types = sorted(df_sessions['Type'].unique())
                selected_types = st.multiselect("Filter by Type", all_types, default=all_types)
            with f2:
                # Date Range Filter
                min_date = df_sessions['Datetime'].min().date()
                max_date = df_sessions['Datetime'].max().date()
                date_range = st.date_input("Filter by Date Range", value=(min_date, max_date))
            with f3:
                search_term = st.text_input("Search Topic", placeholder="e.g., 'Refactor', 'Budget'...")
        
        # Apply Filters
        filtered_df = df_sessions[df_sessions['Type'].isin(selected_types)]
        
        # Apply Date Filter
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
            # Ensure filtering respects the chosen dates (inclusive)
            filtered_df = filtered_df[
                (filtered_df['Datetime'].dt.date >= start_date) & 
                (filtered_df['Datetime'].dt.date <= end_date)
            ]
        elif isinstance(date_range, tuple) and len(date_range) == 1:
             # Handle single date selection case
             filtered_df = filtered_df[filtered_df['Datetime'].dt.date == date_range[0]]
            
        if search_term:
            filtered_df = filtered_df[filtered_df['Topic'].str.contains(search_term, case=False)]
            
        st.dataframe(
            filtered_df[["Type", "Topic", "Time", "Files"]],
            hide_index=True
        )
        
        st.divider()
        st.markdown(f"**Showing {len(filtered_df)} Session(s)**")
        
        # Detailed Cards
        for idx, row in filtered_df.iterrows():
            with st.expander(f"{row['Type'].upper()}: {row['Topic']} ({row['Time']})"):
                st.caption(f"📂 Path: `{row['Path']}`")
                
                # List files sorted
                files = sorted(glob.glob(os.path.join(row['Path'], "*")))
                file_names = [os.path.basename(f) for f in files]
                
                c_sel, c_view = st.columns([1, 2])
                with c_sel:
                    # Use PATH hash for key stability
                    safe_key = str(hash(row['Path']))
                    selected_file_name = st.radio("Select Artifact", file_names, key=f"sel_{safe_key}")
                
                with c_view:
                    if selected_file_name:
                        full_path = os.path.join(row['Path'], selected_file_name)
                        with open(full_path, "r") as f:
                            content = f.read()
                        
                        st.markdown(f"**📄 {selected_file_name}**")
                        if selected_file_name.endswith(".json"):
                            try:
                                st.json(json.loads(content))
                            except json.JSONDecodeError:
                                st.warning("Invalid or Empty JSON file")
                                st.code(content)
                        elif selected_file_name.endswith(".md"):
                            st.markdown(content)
                        else:
                            st.code(content)
    else:
        st.warning("No session artifacts found.")

# --- RENDER DASHBOARD (Budget Tab) ---
with tab_cost:
    render_dashboard(df_filtered)


# --- TAB 4: MODEL CATALOG ---
with tab_models:
    st.markdown("### 🤖 Available Models")
    st.caption("Browse all models currently discovered by the MCP Orchestrator.")
    
    # 1. Load Models (Cached)
    @st.cache_data(ttl=3600)
    def fetch_all_models():
        import sys
        # Ensure src is in path
        if os.getcwd() not in sys.path:
            sys.path.append(os.getcwd())
            
        try:
            from src.tools import LLMManager
            from dotenv import load_dotenv
            load_dotenv()
            
            manager = LLMManager()
            # Manager will run discovery
            return manager.list_models()
        except Exception as e:
            return {"error": str(e)}

    # Fetch models
    with st.spinner("Discovering models..."):
        models_data = fetch_all_models()
    
    # Refresh Button
    if st.button("🔄 Refresh Models"):
        fetch_all_models.clear()
        st.rerun()
        
    if "error" in models_data:
        st.error(f"Failed to load models: {models_data['error']}")
    else:
        # 2. Search & Filter
        search_query = st.text_input("🔍 Search Models", placeholder="Type to filter (e.g., 'claude', 'gpt-4', '32b')...")
        
        # Flatten for search
        all_flat = []
        for provider, m_list in models_data.items():
            for m in m_list:
                all_flat.append({"Provider": provider, "Model ID": m, "Full ID": f"{provider}:{m}"})
                
        df_models = pd.DataFrame(all_flat)
        if df_models.empty and "Full ID" not in df_models.columns:
            df_models = pd.DataFrame(columns=["Provider", "Model ID", "Full ID"])
        
        if search_query:
            mask = df_models["Full ID"].str.contains(search_query, case=False)
            df_filtered = df_models[mask]
        else:
            df_filtered = df_models
            
        # 3. Categorized Display
        # Group by Provider again based on filtered results
        
        if not df_filtered.empty:
            providers = sorted(df_filtered["Provider"].unique())
            
            # Show summarized count
            st.info(f"Showing **{len(df_filtered)}** models across **{len(providers)}** providers.")

            for prov in providers:
                prov_models = df_filtered[df_filtered["Provider"] == prov]["Model ID"].tolist()
                
                # Determine color/icon
                color = PROVIDER_COLORS.get(prov, "#888888")
                icon = PROVIDER_ICONS.get(prov, "🔌")
                
                with st.expander(f"{icon} **{prov.upper()}** ({len(prov_models)} models)", expanded=(search_query != "")):
                    # Allow copying IDs in a copy-friendly code block if useful, or table
                    
                    # Group by common prefixes if too many (optional, but good for OpenRouter)
                    if len(prov_models) > 20:
                         st.write(f"_{len(prov_models)} models available. Use search to find specific ones._")
                         
                    st.dataframe(
                        pd.DataFrame(prov_models, columns=["Model ID"]), 
                        use_container_width=True,
                        hide_index=True
                    )
        else:
            st.warning("No models found matching your search.")

