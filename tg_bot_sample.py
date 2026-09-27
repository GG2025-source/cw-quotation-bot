
# $0 本地試驗版 - TG Bot Polling 模式，唔使VPS唔使ngrok
# 用法: pip install -r requirements.txt, 填好 .env, python tg_bot_sample.py

import os, json, pathlib
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from intent_parser_sample import parse_intent, DB
from generate_pdf_sample import generate_quotation

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# 模擬 gmail_draft - 實際你會有 gmail_draft.py
DRAFTS = []

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "CW Quotation Bot 試驗版已啟動\n"
        "試下打: 金城 南丫島 四千蚊\n"
        "或: 中水 隧道 12000\n"
        "我會自動出PDF，仲會提示你平均價。"
    )

async def handle_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    data = parse_intent(text)

    # 價格記憶提示 (對應你 Plan 入面 Phase A)
    avg_price = DB.get(data['client'], {}).get('avg_price')
    warning = ""
    if avg_price and data['total'] and abs(data['total']-avg_price)/avg_price > 0.3:
        warning = f"\n⚠️ 提示: {data['client']} 近期平均 HKD {avg_price:,}, 而家 {data['total']:,} 偏差 >30%"

    pdf_path, q_no = generate_quotation(data)

    # 回覆按鈕 - 對應你個「先核對再送草稿」需求
    keyboard = [
        [InlineKeyboardButton("✅ 出 Gmail 草稿", callback_data=f"draft|{q_no}")],
        [InlineKeyboardButton("✏️ 改金額", callback_data=f"edit|{q_no}")]
    ]

    caption = (
        f"已解析:\n"
        f"客: {data['client']}\n"
        f"Attention: {data['attention']}\n"
        f"項目: {data['project']}\n"
        f"金額: HKD {data['total']:,}{warning}\n"
        f"單號: {q_no}"
    )

    await update.message.reply_document(
        document=open(pdf_path, 'rb'),
        caption=caption,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    # 記低呢單，俾 callback 用
    ctx.user_data[q_no] = {"data": data, "pdf": pdf_path}

async def handle_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action, q_no = query.data.split('|')
    info = ctx.user_data.get(q_no)
    if not info:
        await query.edit_message_caption(caption="草稿已過期，請重發")
        return
    if action == "draft":
        DRAFTS.append(info)
        await query.edit_message_caption(caption=query.message.caption + "\n\n✅ 已寫入 Gmail 草稿 (模擬，實際會 call gmail_draft.py)")
        # 呢度 call 你真實嘅 gmail_draft.py
    else:
        await query.message.reply_text("請直接回覆新金額，例如: 4500")

if __name__ == "__main__":
    if not TOKEN:
        print("未設定 TELEGRAM_BOT_TOKEN，請去 .env 填")
        exit(1)
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CallbackQueryHandler(handle_callback))
    print("Bot running... 去 Telegram 試下打: 金城 南丫島 四千蚊")
    app.run_polling()
