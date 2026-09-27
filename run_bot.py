
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from intent_parser_sample import parse_intent, DB
from generate_pdf_sample import generate_quotation
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "CW 智能報價機械人 (免費版) 已上線✅\n"
        "試下打: 金城 南丫島 四千蚊\n"
        "或: 中水 隧道 12000"
    )

async def handle_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    data = parse_intent(text)
    avg_price = DB.get(data['client'], {}).get('avg_price')
    warning = ""
    if avg_price and data['total'] and abs(data['total']-avg_price)/avg_price > 0.3:
        warning = f"\n⚠️ 提示: {data['client']} 近期平均 HKD {avg_price:,}, 而家 {data['total']:,} 偏差 >30%"

    pdf_path, q_no = generate_quotation(data)
    keyboard = [
        [InlineKeyboardButton("✅ 出 Gmail 草稿", callback_data=f"draft|{q_no}")],
        [InlineKeyboardButton("✏️ 改金額", callback_data=f"edit|{q_no}")]
    ]
    caption = f"已解析:\n客: {data['client']}\n項目: {data['project']}\n金額: HKD {data['total']:,}{warning}\n單號: {q_no}"
    await update.message.reply_document(
        document=open(pdf_path, 'rb'),
        caption=caption,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    ctx.user_data[q_no] = {"data": data, "pdf": pdf_path}

async def handle_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action, q_no = query.data.split('|')
    if action == "draft":
        await query.edit_message_caption(caption=query.message.caption + "\n\n✅ 已寫入 Gmail 草稿 (模擬)")

def main():
    if not TOKEN:
        print("未設定 TELEGRAM_BOT_TOKEN")
        return
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CallbackQueryHandler(handle_callback))
    print("Bot running... 24小時在線 (免費版)")
    app.run_polling()

if __name__ == "__main__":
    main()
