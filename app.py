import base64
import json
from datetime import datetime
import pytz
import requests
import streamlit as st
from PIL import Image

# Page Configuration
st.set_page_config(
    page_title="Shawkat MT5 & Crypto Chart Analyzer",
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
    if "BTC" in asset_upper:
        return "₿"
    if "ETH" in asset_upper:
        return "Ξ"
    if "SOL" in asset_upper:
        return "🟣"
    if "XRP" in asset_upper:
        return "✕"
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


def generate_vision_signal_with_fallback(api_key: str, image_bytes: bytes, asset: str, market_type: str):
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    local_tz = pytz.timezone("Asia/Karachi")
    now_local = datetime.now(local_tz)
    current_local_time = now_local.strftime("%H:%M:%S")

    context_str = "Forex and XAUUSD institutional" if market_type == "Forex & Gold" else "Cryptocurrency high-volatility spot/futures"

    prompt = f"""
    You are an elite {context_str} algorithmic trader with a legendary win rate. Current local time: {current_local_time}.
    Deeply analyze this chart screenshot for asset: {asset}.
    Evaluate trend structure, market liquidity, multi-timeframe confirmation, and candlestick action to determine an ultra-high probability, surgical BUY/LONG or SELL/SHORT execution setup. 
    Ensure the Stop Loss (SL) is placed safely behind major structural wicks or key support/resistance blocks so it has maximum protection against false breakouts, and the Take Profit (TP) offers at least a 1:2 or 1:3 risk-to-reward ratio.

    CRITICAL INSTRUCTIONS:
    - Output ONLY valid raw JSON. Do NOT include markdown code blocks.
    - Provide exact keys: "asset", "entry_price", "signal", "sl_price", "tp_price", "accuracy", "technical_analysis", "reason".
    - "signal" must be strictly either "BUY" or "SELL".
    """

    # Fallback model chain on OpenRouter (fastest & highest quality multimodal models)
    models = [
        "google/gemini-2.5-flash",
        "anthropic/claude-3.5-sonnet",
        "openai/gpt-4o",
        "deepseek/deepseek-chat"
    ]

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://streamlit.app",
        "X-OpenRouter-Title": "Shawkat Vision Scanner",
    }

    for model in models:
        try:
            payload = {
                "model": model,
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
                "max_tokens": 400,
                "temperature": 0.2,
            }

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=25,
            )

            if response.status_code == 200:
                raw_text = response.json()["choices"][0]["message"]["content"]
                data = parse_json_response(raw_text)
                data["execution_time"] = current_local_time
                data["ai_model_used"] = model
                return data
        except Exception:
            continue

    raise Exception("All OpenRouter models failed to respond. Please check your API key or image format.")


# ------------------------------------------------------------------------------
# Session State Initialization
# ------------------------------------------------------------------------------
if "session_active" not in st.session_state:
    st.session_state.session_active = False
if "balance" not in st.session_state:
    st.session_state.balance = 0.0
if "risk_mode" not in st.session_state:
    st.session_state.risk_mode = "Low Risk"
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
st.sidebar.title("⚙️ Trading Control Panel")

# OpenRouter Key Input
api_key = st.sidebar.text_input("OpenRouter API Key", type="password")

st.sidebar.markdown("---")

# Capital Management Session Setup with Automatic Lot/Position Calculation
st.sidebar.subheader("💰 Account Risk Setup")
starting_balance_choice = st.sidebar.number_input(
    "Account Balance ($)", min_value=10.0, max_value=100000.0, value=500.0, step=100.0
)

risk_selection = st.sidebar.radio(
    "Select Risk Strategy",
    ["Low Risk", "High Risk"],
    index=0,
    help="Low Risk: Conservative sizing to safeguard capital against SL hits. High Risk: Aggressive sizing for faster growth."
)

if st.sidebar.button("Initialize Trading Session"):
    bal = float(starting_balance_choice)
    st.session_state.balance = bal
    st.session_state.risk_mode = risk_selection
    
    # Automatic Lot/Size calculation based on balance and risk profile
    if risk_selection == "Low Risk":
        st.session_state.lot_size = max(0.01, round((bal / 1000.0) * 0.05, 2))
    else:
        st.session_state.lot_size = max(0.01, round((bal / 500.0) * 0.15, 2))

    st.session_state.tp = bal * 0.15
    st.session_state.sl = bal * 0.08
    st.session_state.current_pnl = 0.0
    st.session_state.session_active = True
    st.sidebar.success(f"Initialized! Sizing set to {st.session_state.lot_size} ({risk_selection})")

# Display Metrics if Session Active
if st.session_state.session_active:
    st.sidebar.markdown("---")
    st.sidebar.metric("Account Balance", f"${st.session_state.balance:.2f}")
    st.sidebar.metric("Risk Mode", st.session_state.risk_mode)
    st.sidebar.metric("Calculated Sizing", f"{st.session_state.lot_size:.2f}")
    st.sidebar.metric("Target Profit", f"+${st.session_state.tp:.2f}")
    st.sidebar.metric("Max Drawdown SL", f"-${st.session_state.sl:.2f}")
    st.sidebar.metric("Current PnL", f"${st.session_state.current_pnl:.2f}")

# ------------------------------------------------------------------------------
# Main App Layout
# ------------------------------------------------------------------------------
st.title("📸 Shawkat Chart Screenshot Analyzer (Forex, Gold & Crypto)")

if not api_key:
    st.warning("⚠️ Please enter your OpenRouter API key in the sidebar to activate the scanner.")
    st.stop()

if not st.session_state.session_active:
    st.info("👈 Please initialize your account risk parameters from the sidebar to begin.")
    st.stop()

# Target Profit / Stop Loss Lock Check
if st.session_state.current_pnl >= st.session_state.tp:
    st.success(f"🎉 **SESSION PROFIT TARGET REACHED (+${st.session_state.tp:.2f})!** Take a break.")
    st.stop()

if st.session_state.current_pnl <= -st.session_state.sl:
    st.error(f"🛑 **MAX DRAWDOWN HIT (-${st.session_state.sl:.2f})!** Trading locked for risk protection.")
    st.stop()

# ------------------------------------------------------------------------------
# Market Selector & Screenshot Scanner
# ------------------------------------------------------------------------------
st.subheader("Multi-Market Vision Scanner")
st.caption("Upload a chart screenshot. The system auto-routes across elite AI models on OpenRouter (Gemini, Claude, GPT-4o, DeepSeek) with failover protection to deliver high-accuracy setups designed to avoid premature SL hits.")

market_type = st.radio(
    "Select Market Category",
    ["Forex & Gold", "Cryptocurrency"],
    horizontal=True
)

if market_type == "Forex & Gold":
    vision_asset = st.selectbox(
        "Select Target Asset",
        ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "EURJPY", "GBPJPY"],
        key="forex_asset_sel"
    )
else:
    vision_asset = st.selectbox(
        "Select Target Asset",
        ["BTCUSD", "ETHUSD", "SOLUSD", "XRPUSD", "BNBUSD", "ADAUSD", "DOGEUSD"],
        key="crypto_asset_sel"
    )

uploaded_file = st.file_uploader(f"Upload {market_type} Chart Image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption=f"Uploaded {market_type} Chart", use_container_width=True)

    if st.button("Analyze Chart & Extract SL/TP", type="primary"):
        with st.spinner("Running multi-model OpenRouter failover scan for maximum signal reliability..."):
            try:
                img_bytes = uploaded_file.getvalue()
                sig = generate_vision_signal_with_fallback(api_key, img_bytes, vision_asset, market_type)
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
    signal_icon = "🟢 🚀 BUY / LONG" if signal_dir == "BUY" else "🔴 📉 SELL / SHORT"

    st.markdown(f"## {asset_flag} **Asset:** `{sig_data.get('asset')}`")

    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.markdown(f"### Signal: :{signal_color}[{signal_icon}]")
        st.write(f"**Entry Price:** `{sig_data.get('entry_price')}`")
        st.write(f"**Stop Loss (SL):** `{sig_data.get('sl_price')}`")
        st.write(f"**Take Profit (TP):** `{sig_data.get('tp_price')}`")

    with res_col2:
        st.write(f"**Win Accuracy:** `{sig_data.get('accuracy')}`")
        st.write(f"**Auto-Calculated Sizing:** `{st.session_state.lot_size}` (`{st.session_state.risk_mode}`)")
        st.write(f"**AI Engine Used:** `{sig_data.get('ai_model_used', 'OpenRouter AI')}`")
        st.write(f"**Signal Time:** `{sig_data.get('execution_time')}`")

    if "technical_analysis" in sig_data:
        st.info(f"**Chart Analysis:** {sig_data.get('technical_analysis')}")

    st.caption(f"**Technical Reason:** {sig_data.get('reason')}")

    # Result Logging Controls for PnL Tracking
    st.markdown("### Log Trade Result (Simulator)")
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
