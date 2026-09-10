import base64
import json
from datetime import datetime, timedelta
import pytz
import requests
import streamlit as st
from PIL import Image

# Page Configuration
st.set_page_config(
    page_title="Shawkat All-In-One AI Trading Hub",
    page_icon="⚡",
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
    if "OTC" in asset_upper:
        return "🌐"
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


def generate_forex_vision_signal(api_key: str, image_bytes: bytes, asset: str):
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    local_tz = pytz.timezone("Asia/Karachi")
    now_local = datetime.now(local_tz)
    signal_time_str = (now_local + timedelta(seconds=15)).strftime("%H:%M:%S")

    prompt = f"""
    You are an elite Forex and Gold institutional algorithmic trader. Current local time: {now_local.strftime('%H:%M:%S')}.
    Analyze this chart screenshot for asset: {asset}.
    Provide a high-probability trading signal keyed to the exact signal timestamp rather than a fixed entry price. Determine the precise signal execution time, BUY or SELL direction, recommended Stop Loss (SL), and Take Profit (TP).

    CRITICAL INSTRUCTIONS:
    - Output ONLY valid raw JSON. Do NOT include markdown code blocks.
    - Provide exact keys: "asset", "signal_time", "signal", "sl_price", "tp_price", "accuracy", "technical_analysis", "reason".
    - "signal" must be strictly either "BUY" or "SELL".
    - "signal_time" must be set to: "{signal_time_str}".
    """

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://streamlit.app",
        "X-OpenRouter-Title": "Shawkat Forex Scanner",
    }

    payload = {
        "model": "google/gemini-2.5-flash",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
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
        data["ai_model_used"] = "google/gemini-2.5-flash"
        return data
    else:
        raise Exception(f"API Error {response.status_code}: {response.text}")


def generate_crypto_vision_signal(api_key: str, image_bytes: bytes, asset: str):
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    local_tz = pytz.timezone("Asia/Karachi")
    now_local = datetime.now(local_tz)
    current_local_time = now_local.strftime("%H:%M:%S")

    prompt = f"""
    You are an elite cryptocurrency futures and spot algorithmic trader. Current local time: {current_local_time}.
    Deeply analyze this chart screenshot for asset: {asset}. Determine trend structure, liquidity, and candles to provide a high-probability BUY/LONG or SELL/SHORT setup with SL and TP.

    CRITICAL INSTRUCTIONS:
    - Output ONLY valid raw JSON. Do NOT include markdown code blocks.
    - Provide exact keys: "asset", "entry_price", "signal", "sl_price", "tp_price", "accuracy", "technical_analysis", "reason".
    - "signal" must be strictly either "BUY" or "SELL".
    """

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://streamlit.app",
        "X-OpenRouter-Title": "Shawkat Crypto Scanner",
    }

    payload = {
        "model": "google/gemini-2.5-flash",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
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
        data["ai_model_used"] = "google/gemini-2.5-flash"
        return data
    else:
        raise Exception(f"API Error {response.status_code}: {response.text}")


def generate_binary_text_signal(api_key: str, asset: str, timer: str, payout: int):
    local_tz = pytz.timezone("Asia/Karachi")
    now_local = datetime.now(local_tz)
    current_local_time = now_local.strftime("%H:%M:%S")
    future_entry = (now_local + timedelta(seconds=25)).strftime("%H:%M:%S")

    prompt = f"""
    You are an elite master binary options algorithmic trader. Current local time: {current_local_time}.
    Generate a high-probability technical trading signal for Quotex asset: {asset} with payout: {payout}%.

    CRITICAL INSTRUCTIONS:
    - Output ONLY valid raw JSON. Do NOT include markdown code blocks. 
    - Provide exact keys: "asset", "live_price", "signal", "accuracy", "reason", "mtg_advice".
    - "signal" must be strictly either "CALL" or "PUT".
    """

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://streamlit.app",
            "X-OpenRouter-Title": "Shawkat Quotex AI Web App",
        },
        json={
            "model": "deepseek/deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 250,
            "temperature": 0.3,
        },
        timeout=25,
    )

    if response.status_code == 200:
        raw_text = response.json()["choices"][0]["message"]["content"]
        data = parse_json_response(raw_text)
        data["execution_time"] = future_entry
        return data
    else:
        raise Exception(f"API Error {response.status_code}: {response.text}")


def generate_binary_vision_signal(api_key: str, image_bytes: bytes):
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    local_tz = pytz.timezone("Asia/Karachi")
    now_local = datetime.now(local_tz)
    current_local_time = now_local.strftime("%H:%M:%S")
    future_entry = (now_local + timedelta(seconds=20)).strftime("%H:%M:%S")

    prompt = f"""
    You are an elite master binary options algorithmic trader. Current local time: {current_local_time}.
    Deeply analyze this 1-minute binary options chart screenshot. Determine expiry duration and direction.

    CRITICAL INSTRUCTIONS:
    - Output ONLY valid raw JSON. Do NOT include markdown code blocks.
    - Provide exact keys: "asset", "live_price", "signal", "expiry", "accuracy", "wick_and_candle_analysis", "mtg_advice", "reason".
    - "signal" must be strictly either "CALL" or "PUT".
    - "expiry" must be specified clearly (e.g., "1 Minute", "2 Minutes", "3 Minutes", "5 Minutes").
    """

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://streamlit.app",
            "X-OpenRouter-Title": "Shawkat Quotex AI Web App",
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
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
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
        data["execution_time"] = future_entry
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
if "risk_mode" not in st.session_state:
    st.session_state.risk_mode = "Low Risk"
if "trade_size" not in st.session_state:
    st.session_state.trade_size = 0.01
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
st.sidebar.title("⚙️ Trading Hub Control Panel")

api_key = st.sidebar.text_input("OpenRouter API Key", type="password")

st.sidebar.markdown("---")
st.sidebar.subheader("💰 Account Capital & Risk Setup")
starting_balance_choice = st.sidebar.number_input(
    "Starting Balance ($)", min_value=10.0, max_value=100000.0, value=500.0, step=50.0
)

risk_selection = st.sidebar.selectbox(
    "Risk Profile", ["Low Risk", "High Risk", "Binary Mode (Fixed 10%)"]
)

if st.sidebar.button("Initialize All-In-One Session"):
    bal = float(starting_balance_choice)
    st.session_state.balance = bal
    st.session_state.risk_mode = risk_selection
    
    if "Binary" in risk_selection:
        st.session_state.trade_size = bal * 0.1
        st.session_state.tp = bal * 0.4
        st.session_state.sl = bal * 0.2
    elif risk_selection == "Low Risk":
        st.session_state.trade_size = max(0.01, round((bal / 1000.0) * 0.05, 2))
        st.session_state.tp = bal * 0.15
        st.session_state.sl = bal * 0.08
    else:
        st.session_state.trade_size = max(0.01, round((bal / 500.0) * 0.15, 2))
        st.session_state.tp = bal * 0.25
        st.session_state.sl = bal * 0.12

    st.session_state.current_pnl = 0.0
    st.session_state.session_active = True
    st.sidebar.success(f"Session Active! Balance: ${bal:.2f}")

if st.session_state.session_active:
    st.sidebar.markdown("---")
    st.sidebar.metric("Balance", f"${st.session_state.balance:.2f}")
    st.sidebar.metric("Position Size / Lot", f"{st.session_state.trade_size:.2f}")
    st.sidebar.metric("Target Profit", f"+${st.session_state.tp:.2f}")
    st.sidebar.metric("Stop Loss Limit", f"-${st.session_state.sl:.2f}")
    st.sidebar.metric("Current PnL", f"${st.session_state.current_pnl:.2f}")

# ------------------------------------------------------------------------------
# Main Hub Layout
# ------------------------------------------------------------------------------
st.title("⚡ Shawkat All-In-One AI Trading Hub")

if not api_key:
    st.warning("⚠️ Please enter your OpenRouter API key in the sidebar to activate the hub.")
    st.stop()

if not st.session_state.session_active:
    st.info("👈 Please initialize your account parameters in the sidebar to begin.")
    st.stop()

if st.session_state.current_pnl >= st.session_state.tp:
    st.success(f"🎉 **TARGET PROFIT REACHED (+${st.session_state.tp:.2f})!** Take a break.")
    st.stop()

if st.session_state.current_pnl <= -st.session_state.sl:
    st.error(f"🛑 **STOP LOSS HIT (-${st.session_state.sl:.2f})!** Trading locked.")
    st.stop()

# ------------------------------------------------------------------------------
# Mode Tabs
# ------------------------------------------------------------------------------
tab_forex, tab_crypto, tab_binary = st.tabs(
    [
        "📈 Forex & Gold (Signal Time Mode)",
        "🪙 Crypto Scanner",
        "⏱️ Binary Options (Quotex AI)",
    ]
)

# ------------------------------------------------------------------------------
# Tab 1: Forex & Gold (Signal Time Mode)
# ------------------------------------------------------------------------------
with tab_forex:
    st.subheader("Forex & Gold Chart Screenshot Analyzer")
    st.caption("Upload a Forex/Gold chart screenshot. The AI provides a precise signal timestamp, execution direction (BUY/SELL), and protective SL/TP.")

    forex_asset = st.selectbox(
        "Select Forex / Gold Asset",
        ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "EURJPY", "GBPJPY"],
        key="forex_asset_input"
    )

    forex_file = st.file_uploader("Upload Forex/Gold Chart", type=["jpg", "jpeg", "png"], key="forex_uploader")

    if forex_file is not None:
        st.image(Image.open(forex_file), caption="Uploaded Forex Chart", use_container_width=True)
        if st.button("Generate Forex Signal (Signal Time Mode)", type="primary"):
            with st.spinner("Analyzing Forex market structure..."):
                try:
                    sig = generate_forex_vision_signal(api_key, forex_file.getvalue(), forex_asset)
                    st.session_state.last_signal = sig
                    st.session_state.signal_category = "Forex"
                except Exception as e:
                    st.error(str(e))

# ------------------------------------------------------------------------------
# Tab 2: Crypto Scanner
# ------------------------------------------------------------------------------
with tab_crypto:
    st.subheader("Cryptocurrency Vision Scanner")
    st.caption("Upload crypto spot or futures charts for high-volatility trade setups.")

    crypto_asset = st.selectbox(
        "Select Crypto Asset",
        ["BTCUSD", "ETHUSD", "SOLUSD", "XRPUSD", "BNBUSD", "ADAUSD", "DOGEUSD"],
        key="crypto_asset_input"
    )

    crypto_file = st.file_uploader("Upload Crypto Chart", type=["jpg", "jpeg", "png"], key="crypto_uploader")

    if crypto_file is not None:
        st.image(Image.open(crypto_file), caption="Uploaded Crypto Chart", use_container_width=True)
        if st.button("Analyze Crypto Setup", type="primary"):
            with st.spinner("Running crypto multi-model failover scan..."):
                try:
                    sig = generate_crypto_vision_signal(api_key, crypto_file.getvalue(), crypto_asset)
                    st.session_state.last_signal = sig
                    st.session_state.signal_category = "Crypto"
                except Exception as e:
                    st.error(str(e))

# ------------------------------------------------------------------------------
# Tab 3: Binary Options (Quotex AI)
# ------------------------------------------------------------------------------
with tab_binary:
    st.subheader("Binary Options AI (Quotex Mode)")
    
    bin_subtab1, bin_subtab2 = st.tabs(["Manual Signal Generator", "Screenshot Analyzer"])

    with bin_subtab1:
        col1, col2, col3 = st.columns(3)
        with col1:
            bin_asset = st.selectbox("Currency Pair / OTC", ["EUR/USD", "GBP/USD", "EUR/JPY", "EUR/USD OTC", "USD/JPY"], key="bin_asset")
        with col2:
            bin_timer = st.selectbox("Expiry", ["1 Minute", "2 Minutes", "3 Minutes", "5 Minutes"], key="bin_timer")
        with col3:
            bin_payout = st.slider("Payout %", 80, 95, 88, key="bin_payout")

        if st.button("Generate Binary Signal", type="primary"):
            with st.spinner("Calculating binary options entry..."):
                try:
                    sig = generate_binary_text_signal(api_key, bin_asset, bin_timer, bin_payout)
                    st.session_state.last_signal = sig
                    st.session_state.signal_category = "Binary"
                    st.session_state.last_signal_timer = bin_timer
                    st.session_state.last_signal_payout = bin_payout
                except Exception as e:
                    st.error(str(e))

    with bin_subtab2:
        bin_file = st.file_uploader("Upload 1-Min Quotex Chart", type=["jpg", "jpeg", "png"], key="bin_uploader")
        if bin_file is not None:
            st.image(Image.open(bin_file), caption="Quotex Chart", use_container_width=True)
            if st.button("Analyze Binary Chart", type="primary"):
                with st.spinner("Analyzing candles & wicks..."):
                    try:
                        sig = generate_binary_vision_signal(api_key, bin_file.getvalue())
                        st.session_state.last_signal = sig
                        st.session_state.signal_category = "Binary"
                        st.session_state.last_signal_timer = sig.get("expiry", "1 Minute")
                        st.session_state.last_signal_payout = 90
                    except Exception as e:
                        st.error(str(e))

# ------------------------------------------------------------------------------
# Active Signal Display & Result Logging
# ------------------------------------------------------------------------------
if st.session_state.last_signal:
    st.markdown("---")
    sig_data = st.session_state.last_signal
    cat = st.session_state.get("signal_category", "Forex")
    asset_flag = get_pair_flag(sig_data.get("asset", ""))
    
    signal_dir = sig_data.get("signal", "BUY").upper()
    signal_color = "green" if signal_dir in ["BUY", "CALL"] else "red"
    signal_icon = f"🟢 🚀 {signal_dir}" if signal_color == "green" else f"🔴 📉 {signal_dir}"

    st.markdown(f"## {asset_flag} **Asset:** `{sig_data.get('asset')}` [{cat} Mode]")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"### Signal: :{signal_color}[{signal_icon}]")
        if cat == "Forex":
            st.write(f"**Signal Timestamp:** `{sig_data.get('signal_time')}`")
            st.write(f"**Stop Loss (SL):** `{sig_data.get('sl_price')}`")
            st.write(f"**Take Profit (TP):** `{sig_data.get('tp_price')}`")
        elif cat == "Crypto":
            st.write(f"**Entry Price:** `{sig_data.get('entry_price')}`")
            st.write(f"**Stop Loss (SL):** `{sig_data.get('sl_price')}`")
            st.write(f"**Take Profit (TP):** `{sig_data.get('tp_price')}`")
        else:
            st.write(f"**Estimated Price:** `{sig_data.get('live_price')}`")
            st.write(f"**Expiry Timer:** `{st.session_state.get('last_signal_timer', '1 Minute')}`")
            st.write(f"**Execution Time:** `{sig_data.get('execution_time')}`")

    with col_b:
        st.write(f"**Win Accuracy:** `{sig_data.get('accuracy')}`")
        st.write(f"**Trade Size / Lot:** `{st.session_state.trade_size}`")
        if cat == "Binary":
            st.write(f"**MTG Advice:** `{sig_data.get('mtg_advice', 'None')}`")
        st.write(f"**AI Engine:** `{sig_data.get('ai_model_used', 'OpenRouter AI')}`")

    if "technical_analysis" in sig_data:
        st.info(f"**Analysis:** {sig_data.get('technical_analysis')}")
    if "wick_and_candle_analysis" in sig_data:
        st.info(f"**Wick Analysis:** {sig_data.get('wick_and_candle_analysis')}")

    st.caption(f"**Reason:** {sig_data.get('reason')}")

    # Result Logger
    st.markdown("### Log Trade Result")
    r_col1, r_col2 = st.columns(2)

    if cat == "Binary":
        payout_rate = float(st.session_state.get("last_signal_payout", 90)) / 100.0
        if r_col1.button("✅ WIN", type="secondary", use_container_width=True):
            profit = st.session_state.trade_size * payout_rate
            st.session_state.balance += profit
            st.session_state.current_pnl += profit
            st.session_state.last_signal = None
            st.success(f"Added +${profit:.2f} profit!")
            st.rerun()
        if r_col2.button("❌ LOSS", type="secondary", use_container_width=True):
            loss = st.session_state.trade_size
            st.session_state.balance -= loss
            st.session_state.current_pnl -= loss
            st.session_state.last_signal = None
            st.error(f"Deducted -${loss:.2f} loss.")
            st.rerun()
    else:
        if r_col1.button("✅ HIT TAKE PROFIT (TP)", type="secondary", use_container_width=True):
            profit = st.session_state.trade_size * 150.0 if cat == "Crypto" else 120.0
            st.session_state.balance += profit
            st.session_state.current_pnl += profit
            st.session_state.last_signal = None
            st.success(f"Added +${profit:.2f} profit!")
            st.rerun()
        if r_col2.button("❌ HIT STOP LOSS (SL)", type="secondary", use_container_width=True):
            loss = st.session_state.trade_size * 100.0 if cat == "Crypto" else 80.0
            st.session_state.balance -= loss
            st.session_state.current_pnl -= loss
            st.session_state.last_signal = None
            st.error(f"Deducted -${loss:.2f} loss.")
            st.rerun()
