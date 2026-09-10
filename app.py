import base64
import json
from datetime import datetime
import pytz
import requests
import streamlit as st
from PIL import Image

# Page Configuration
st.set_page_config(
    page_title="Shawkat MT5 Chart Analyzer",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------------------------


def get_pair_flag(asset_name: str) -> str:
    asset_upper = asset_name.upper()
    if "EUR" in asset_upper and "USD" in asset_upper:
        return "🇪🇺🇺🇸"
    if "GBP" in asset_upper and "USD" in asset_upper:
        return "🇬🇧🇺🇸"
    if "USD" in asset_upper and "JPY" in asset_upper:
        return "🇺🇸🇯🇵"
    if "AUD" in asset_upper and "CAD" in asset_upper:
        return "🇦🇺🇨🇦"
    if "EUR" in asset_upper and "GBP" in asset_upper:
        return "🇪🇺🇬🇧"
    if "GBP" in asset_upper and "JPY" in asset_upper:
        return "🇬🇧🇯🇵"
    if "EUR" in asset_upper and "JPY" in asset_upper:
        return "🇪🇺🇯🇵"
    if "CAD" in asset_upper and "JPY" in asset_upper:
        return "🇨🇦🇯🇵"
    if "AUD" in asset_upper and "JPY" in asset_upper:
        return "🇦🇺🇯🇵"
    if "EUR" in asset_upper and "CAD" in asset_upper:
        return "🇪🇺🇨🇦"
    if "AUD" in asset_upper and "CHF" in asset_upper:
        return "🇦🇺🇨🇭"
    if "GBP" in asset_upper and "AUD" in asset_upper:
        return "🇬🇧🇦🇺"
    if "EUR" in asset_upper and "AUD" in asset_upper:
        return "🇪🇺🇦🇺"
    if "CHF" in asset_upper and "JPY" in asset_upper:
        return "🇨🇭🇯🇵"
    if "GBP" in asset_upper and "CAD" in asset_upper:
        return "🇬🇧🇨🇦"
    if "GBP" in asset_upper and "CHF" in asset_upper:
        return "🇬🇧🇨🇭"
    if "USD" in asset_upper and "CHF" in asset_upper:
        return "🇺🇸🇨🇭"
    if "EUR" in asset_upper and "CHF" in asset_upper:
        return "🇪🇺🇨🇭"
    if "XAU" in asset_upper or "GOLD" in asset_upper:
        return "🥇"
    return "📈"


def parse_json_response(raw_content: str) -> dict:
    content = raw_content.strip()
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()

    if "{" in content and "}" in content:
        start_idx = content.find("{")
        end_idx = content.rfind("}") + 1
        content = content[start_idx:end_idx]

    return json.loads(content)


def generate_vision_signal(api_key: str, image_bytes: bytes, asset: str):
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    local_tz = pytz.timezone("Asia/Karachi")
    now_local = datetime.now(local_tz)
    current_local_time = now_local.strftime("%H:%M:%S")

    prompt = f"""
    You are an elite institutional Forex and XAUUSD algorithmic trader. Current local time: {current_local_time}.
    Deeply analyze this MT5 or TradingView chart screenshot for asset: {asset}.
    Evaluate trend structure, support/resistance, and candlestick action to determine an exact BUY or SELL execution setup with Stop Loss (SL) and Take Profit (TP).

    CRITICAL INSTRUCTIONS:
    - Output ONLY valid raw JSON. Do NOT include markdown code blocks.
    - Provide exact keys: "asset", "entry_price", "signal", "sl_price", "tp_price", "accuracy", "technical_analysis", "reason".
    - "signal" must be strictly either "BUY" or "SELL".
    """

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://streamlit.app",
            "X-OpenRouter-Title": "Shawkat MT5 Vision Scanner",
        },
        json={
            "model": "google/gemini-2.5-flash",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            "max_tokens": 300,
            "temperature": 0.3,
        },
        timeout=30,
    )

    if response.status_code == 200:
        raw_text = response.json()["choices"][0]["message"]["content"]
        data = parse_json_response(raw_text)
        data["execution_time"] = current_local_time
        return data
    else:
        raise Exception(f"API Error {response.status_code}: {response.text}")


# ------------------------------------------------------------------------------
# Session State Initialization
# ------------------------------------------------------------------------------
if "session_active" not in st.session_state:
    st.session_state.session_active = False
if "balance" not in st.session_state:
    st.session_state.balance = 0.0
if "lot_size" not in st.session_state:
    st.session_state.lot_size = 0.01
if "tp" not in st.session_state:
    st.session_state.tp = 0.0
if "sl" not in st.session_state:
    st.session_state.sl = 0.0
if "current_pnl" not in st.session_state:
    st.session_state.current_pnl = 0.0
if "last_signal" not in st.session_state:
    st.session_state.last_signal = None

# ------------------------------------------------------------------------------
# Sidebar Configuration
# ------------------------------------------------------------------------------
st.sidebar.title("⚙️ MT5 Control Panel")

# OpenRouter Key Input
api_key = st.sidebar.text_input("OpenRouter API Key", type="password")

st.sidebar.markdown("---")

# Capital Management Session Setup
st.sidebar.subheader("💰 Account Risk Setup")
starting_balance_choice = st.sidebar.number_input(
    "Account Balance ($)", min_value=100.0, max_value=100000.0, value=1000.0, step=100.0
)
lot_size_input = st.sidebar.number_input(
    "Default Lot Size", min_value=0.01, max_value=10.00, value=0.10, step=0.01
)

if st.sidebar.button("Initialize MT5 Session"):
    st.session_state.balance = float(starting_balance_choice)
    st.session_state.lot_size = float(lot_size_input)
    st.session_state.tp = float(starting_balance_choice) * 0.1
    st.session_state.sl = float(starting_balance_choice) * 0.05
    st.session_state.current_pnl = 0.0
    st.session_state.session_active = True
    st.sidebar.success("MT5 Risk Parameters Initialized!")

# Display Metrics if Session Active
if st.session_state.session_active:
    st.sidebar.markdown("---")
    st.sidebar.metric("Account Balance", f"${st.session_state.balance:.2f}")
    st.sidebar.metric("Lot Size", f"{st.session_state.lot_size:.2f}")
    st.sidebar.metric("Target Profit", f"+${st.session_state.tp:.2f}")
    st.sidebar.metric("Max Drawdown SL", f"-${st.session_state.sl:.2f}")
    st.sidebar.metric("Current PnL", f"${st.session_state.current_pnl:.2f}")

# ------------------------------------------------------------------------------
# Main App Layout
# ------------------------------------------------------------------------------
st.title("📸 Shawkat MT5 Chart Screenshot Analyzer")

if not api_key:
    st.warning("⚠️ Please enter your OpenRouter API key in the sidebar to activate the scanner.")
    st.stop()

if not st.session_state.session_active:
    st.info("👈 Please initialize your MT5 account risk parameters from the sidebar to begin.")
    st.stop()

# Target Profit / Stop Loss Lock Check
if st.session_state.current_pnl >= st.session_state.tp:
    st.success(f"🎉 **SESSION PROFIT TARGET REACHED (+${st.session_state.tp:.2f})!** Take a break.")
    st.stop()

if st.session_state.current_pnl <= -st.session_state.sl:
    st.error(f"🛑 **MAX DRAWDOWN HIT (-${st.session_state.sl:.2f})!** Trading locked for risk protection.")
    st.stop()

# ------------------------------------------------------------------------------
# Screenshot Analyzer Mode (Sole Focus)
# ------------------------------------------------------------------------------
st.subheader("MT5 / TradingView Vision Scanner")
st.caption("Upload a screenshot from MetaTrader 5 or TradingView to extract BUY/SELL setups with automated SL and TP.")

vision_asset = st.selectbox(
    "Select Target Asset for Screenshot",
    ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "EURJPY", "GBPJPY"],
    key="vision_asset_sel"
)

uploaded_file = st.file_uploader("Upload MT5 Chart Image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded MT5 Chart", use_container_width=True)

    if st.button("Analyze Chart & Extract SL/TP", type="primary"):
        with st.spinner("Analyzing price action, support/resistance, and generating levels via AI..."):
            try:
                img_bytes = uploaded_file.getvalue()
                sig = generate_vision_signal(api_key, img_bytes, vision_asset)
                st.session_state.last_signal = sig
            except Exception as e:
                st.error(str(e))

# ------------------------------------------------------------------------------
# Display Active Signal & Trade Logging Area
# ------------------------------------------------------------------------------
if st.session_state.last_signal:
    st.markdown("---")
    sig_data = st.session_state.last_signal
    asset_flag = get_pair_flag(sig_data.get("asset", ""))
    signal_dir = sig_data.get("signal", "BUY").upper()

    signal_color = "green" if signal_dir == "BUY" else "red"
    signal_icon = "🟢 🚀 BUY" if signal_dir == "BUY" else "🔴 📉 SELL"

    st.markdown(f"## {asset_flag} **Asset:** `{sig_data.get('asset')}`")

    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.markdown(f"### Signal: :{signal_color}[{signal_icon}]")
        st.write(f"**Entry Price:** `{sig_data.get('entry_price')}`")
        st.write(f"**Stop Loss (SL):** `{sig_data.get('sl_price')}`")
        st.write(f"**Take Profit (TP):** `{sig_data.get('tp_price')}`")

    with res_col2:
        st.write(f"**Win Accuracy:** `{sig_data.get('accuracy')}`")
        st.write(f"**Assigned Lot Size:** `{st.session_state.lot_size}`")
        st.write(f"**Signal Time:** `{sig_data.get('execution_time')}`")

    if "technical_analysis" in sig_data:
        st.info(f"**Chart Analysis:** {sig_data.get('technical_analysis')}")

    st.caption(f"**Technical Reason:** {sig_data.get('reason')}")

    # Result Logging Controls for PnL Tracking
    st.markdown("### Log Trade Result (MT5 Simulator)")
    btn_win, btn_loss = st.columns(2)

    if btn_win.button("✅ HIT TAKE PROFIT (TP)", type="secondary", use_container_width=True):
        estimated_profit = st.session_state.lot_size * 150.0  
        st.session_state.balance += estimated_profit
        st.session_state.current_pnl += estimated_profit
        st.session_state.last_signal = None
        st.success(f"Added +${estimated_profit:.2f} profit to balance!")
        st.rerun()

    if btn_loss.button("❌ HIT STOP LOSS (SL)", type="secondary", use_container_width=True):
        estimated_loss = st.session_state.lot_size * 100.0
        st.session_state.balance -= estimated_loss
        st.session_state.current_pnl -= estimated_loss
        st.session_state.last_signal = None
        st.error(f"Deducted -${estimated_loss:.2f} loss from balance.")
        st.rerun()
